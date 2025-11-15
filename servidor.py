#!/usr/bin/env python3
"""
Servidor RPC Asíncrono para gestión de productos en XML

Este servidor maneja operaciones concurrentes de inserción y consulta
sobre productos almacenados en un archivo XML. Las operaciones de
inserción tienen mayor prioridad que las de consulta.
"""

import socket
import threading
import xml.etree.ElementTree as ET
import json
import time
import queue
from typing import Dict, Tuple, Optional
import os

# Constantes
XML_FILE = "productos.xml"
HOST = "localhost"
PORT = 8888
INSERTION_DELAY = 3  # Segundos de espera para simular carga en inserciones
PRIORITY_INSERT = 1  # Mayor prioridad (menor número)
PRIORITY_QUERY = 2   # Menor prioridad (mayor número)


class ProductManager:
    """Gestiona las operaciones sobre el archivo XML de productos"""
    
    def __init__(self, xml_file: str):
        self.xml_file = xml_file
        self.lock = threading.RLock()  # Reentrant lock para operaciones anidadas
        self._ensure_xml_exists()
    
    def _ensure_xml_exists(self):
        """Asegura que el archivo XML existe con la estructura correcta"""
        if not os.path.exists(self.xml_file):
            root = ET.Element("productos")
            tree = ET.ElementTree(root)
            tree.write(self.xml_file, encoding="UTF-8", xml_declaration=True)
    
    def _load_xml(self) -> ET.ElementTree:
        """Carga el archivo XML en memoria"""
        tree = ET.parse(self.xml_file)
        return tree
    
    def _save_xml(self, tree: ET.ElementTree):
        """Guarda el árbol XML al archivo"""
        tree.write(self.xml_file, encoding="UTF-8", xml_declaration=True)
    
    def insert_product(self, product_id: str, nombre: str, precio: float) -> int:
        """
        Inserta un producto en el XML y devuelve su posición
        
        Args:
            product_id: ID del producto
            nombre: Nombre del producto
            precio: Precio del producto
            
        Returns:
            Posición del producto en el XML (0-indexed) o -1 si ya existe
        """
        with self.lock:
            print(f"[INSERT] Iniciando inserción de producto ID: {product_id}")
            time.sleep(INSERTION_DELAY)  # Simular carga del servidor
            
            tree = self._load_xml()
            root = tree.getroot()
            
            # Verificar si el producto ya existe
            for idx, producto in enumerate(root):
                if producto.get("id") == product_id:
                    print(f"[INSERT] Producto {product_id} ya existe en posición {idx}")
                    return -1
            
            # Crear nuevo elemento producto
            producto = ET.Element("producto")
            producto.set("id", product_id)
            producto.set("nombre", nombre)
            producto.set("precio", str(precio))
            
            root.append(producto)
            position = len(root) - 1
            
            self._save_xml(tree)
            print(f"[INSERT] Producto {product_id} insertado en posición {position}")
            return position
    
    def query_product(self, product_id: str) -> int:
        """
        Consulta un producto por ID y devuelve su posición
        
        Args:
            product_id: ID del producto a buscar
            
        Returns:
            Posición del producto en el XML (0-indexed) o -1 si no existe
        """
        with self.lock:
            print(f"[QUERY] Consultando producto ID: {product_id}")
            tree = self._load_xml()
            root = tree.getroot()
            
            for idx, producto in enumerate(root):
                if producto.get("id") == product_id:
                    print(f"[QUERY] Producto {product_id} encontrado en posición {idx}")
                    return idx
            
            print(f"[QUERY] Producto {product_id} no encontrado")
            return -1


class RPCServer:
    """Servidor RPC asíncrono con sistema de prioridades"""
    
    def __init__(self, host: str, port: int, xml_file: str):
        self.host = host
        self.port = port
        self.product_manager = ProductManager(xml_file)
        self.priority_queue = queue.PriorityQueue()
        self.worker_threads = []
        self.running = False
        self.worker_lock = threading.Lock()
        
    def _process_request(self, request_data: bytes, client_address: Tuple[str, int]) -> bytes:
        """
        Procesa una solicitud RPC y devuelve la respuesta
        
        Args:
            request_data: Datos de la solicitud en formato JSON
            client_address: Dirección del cliente
            
        Returns:
            Respuesta en formato JSON como bytes
        """
        try:
            request = json.loads(request_data.decode('utf-8'))
            operation = request.get("operation")
            params = request.get("params", {})
            
            if operation == "insert":
                product_id = params.get("id")
                nombre = params.get("nombre")
                precio = params.get("precio")
                position = self.product_manager.insert_product(product_id, nombre, precio)
                response = {"status": "success", "position": position}
                
            elif operation == "query":
                product_id = params.get("id")
                position = self.product_manager.query_product(product_id)
                response = {"status": "success", "position": position}
                
            else:
                response = {"status": "error", "message": f"Operación desconocida: {operation}"}
                
        except Exception as e:
            response = {"status": "error", "message": str(e)}
        
        return json.dumps(response).encode('utf-8')
    
    def _worker_thread(self):
        """Thread worker que procesa solicitudes de la cola de prioridades"""
        while self.running:
            try:
                priority, (request_data, client_address, client_socket) = \
                    self.priority_queue.get(timeout=1)
                
                print(f"[WORKER] Procesando solicitud con prioridad {priority} de {client_address}")
                response = self._process_request(request_data, client_address)
                
                # Enviar respuesta al cliente
                client_socket.sendall(response)
                client_socket.close()
                
                self.priority_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[ERROR] Error en worker thread: {e}")
    
    def _handle_client(self, client_socket: socket.socket, client_address: Tuple[str, int]):
        """
        Maneja la conexión de un cliente
        
        Args:
            client_socket: Socket del cliente
            client_address: Dirección del cliente
        """
        try:
            # Recibir datos del cliente
            data = client_socket.recv(4096)
            if not data:
                return
            
            request = json.loads(data.decode('utf-8'))
            operation = request.get("operation")
            
            # Determinar prioridad (inserciones tienen mayor prioridad)
            if operation == "insert":
                priority = PRIORITY_INSERT
            elif operation == "query":
                priority = PRIORITY_QUERY
            else:
                priority = PRIORITY_QUERY  # Default
            
            # Agregar a la cola de prioridades
            self.priority_queue.put((priority, (data, client_address, client_socket)))
            print(f"[SERVER] Solicitud {operation} de {client_address} agregada a cola con prioridad {priority}")
            
        except Exception as e:
            print(f"[ERROR] Error manejando cliente {client_address}: {e}")
            client_socket.close()
    
    def start(self, num_workers: int = 3):
        """
        Inicia el servidor con workers para procesar solicitudes
        
        Args:
            num_workers: Número de threads worker para procesar solicitudes
        """
        self.running = True
        
        # Crear threads worker
        for i in range(num_workers):
            worker = threading.Thread(target=self._worker_thread, daemon=True)
            worker.start()
            self.worker_threads.append(worker)
            print(f"[SERVER] Worker thread {i+1} iniciado")
        
        # Crear socket del servidor
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        
        print(f"[SERVER] Servidor RPC iniciado en {self.host}:{self.port}")
        print(f"[SERVER] Esperando conexiones...")
        
        try:
            while self.running:
                client_socket, client_address = server_socket.accept()
                print(f"[SERVER] Nueva conexión de {client_address}")
                
                # Crear thread para manejar cada cliente
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_address),
                    daemon=True
                )
                client_thread.start()
                
        except KeyboardInterrupt:
            print("\n[SERVER] Deteniendo servidor...")
            self.stop()
    
    def stop(self):
        """Detiene el servidor"""
        self.running = False
        print("[SERVER] Servidor detenido")


def main():
    """Función principal del servidor"""
    server = RPCServer(HOST, PORT, XML_FILE)
    try:
        server.start(num_workers=3)
    except KeyboardInterrupt:
        server.stop()


if __name__ == "__main__":
    main()

