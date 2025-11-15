#!/usr/bin/env python3
"""
Cliente RPC para operaciones sobre productos

Este cliente se conecta al servidor RPC y realiza múltiples
operaciones aleatorias de inserción y consulta.
"""

import socket
import json
import random
import threading
import time
from typing import Dict, Optional

# Constantes
HOST = "localhost"
PORT = 8888


class RPCClient:
    """Cliente RPC para comunicación con el servidor"""
    
    def __init__(self, host: str, port: int, client_id: str):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.products_inserted = []  # Lista de IDs de productos insertados por este cliente
    
    def _send_request(self, operation: str, params: Dict) -> Optional[Dict]:
        """
        Envía una solicitud al servidor y recibe la respuesta
        
        Args:
            operation: Tipo de operación ("insert" o "query")
            params: Parámetros de la operación
            
        Returns:
            Respuesta del servidor como diccionario o None si hay error
        """
        try:
            # Crear socket y conectar
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.host, self.port))
            
            # Crear solicitud
            request = {
                "operation": operation,
                "params": params,
                "client_id": self.client_id
            }
            
            # Enviar solicitud
            request_data = json.dumps(request).encode('utf-8')
            client_socket.sendall(request_data)
            
            # Recibir respuesta
            response_data = client_socket.recv(4096)
            response = json.loads(response_data.decode('utf-8'))
            
            client_socket.close()
            return response
            
        except Exception as e:
            print(f"[CLIENTE {self.client_id}] Error en solicitud: {e}")
            return None
    
    def insert_product(self, product_id: str, nombre: str, precio: float) -> int:
        """
        Inserta un producto en el servidor
        
        Args:
            product_id: ID del producto
            nombre: Nombre del producto
            precio: Precio del producto
            
        Returns:
            Posición del producto en el XML o -1 si ya existe
        """
        print(f"[CLIENTE {self.client_id}] Enviando INSERT: ID={product_id}, Nombre={nombre}, Precio={precio}")
        
        params = {
            "id": product_id,
            "nombre": nombre,
            "precio": precio
        }
        
        response = self._send_request("insert", params)
        
        if response and response.get("status") == "success":
            position = response.get("position", -1)
            if position != -1:
                self.products_inserted.append(product_id)
            print(f"[CLIENTE {self.client_id}] INSERT completado: posición={position}")
            return position
        else:
            error_msg = response.get("message", "Error desconocido") if response else "Sin respuesta"
            print(f"[CLIENTE {self.client_id}] Error en INSERT: {error_msg}")
            return -1
    
    def query_product(self, product_id: str) -> int:
        """
        Consulta un producto por ID
        
        Args:
            product_id: ID del producto a buscar
            
        Returns:
            Posición del producto en el XML o -1 si no existe
        """
        print(f"[CLIENTE {self.client_id}] Enviando QUERY: ID={product_id}")
        
        params = {"id": product_id}
        response = self._send_request("query", params)
        
        if response and response.get("status") == "success":
            position = response.get("position", -1)
            print(f"[CLIENTE {self.client_id}] QUERY completado: posición={position}")
            return position
        else:
            error_msg = response.get("message", "Error desconocido") if response else "Sin respuesta"
            print(f"[CLIENTE {self.client_id}] Error en QUERY: {error_msg}")
            return -1
    
    def run_random_operations(self, num_operations: int = 10):
        """
        Ejecuta múltiples operaciones aleatorias
        
        Args:
            num_operations: Número de operaciones a realizar
        """
        print(f"[CLIENTE {self.client_id}] Iniciando {num_operations} operaciones aleatorias...")
        
        nombres = ["Laptop", "Mouse", "Teclado", "Monitor", "Auriculares", 
                  "Webcam", "Impresora", "Tablet", "Smartphone", "Router"]
        
        for i in range(num_operations):
            # Decidir aleatoriamente entre insertar o consultar
            # 60% probabilidad de insertar, 40% de consultar
            if random.random() < 0.6 or len(self.products_inserted) == 0:
                # Operación de inserción
                product_id = f"PROD-{self.client_id}-{i+1}"
                nombre = random.choice(nombres) + f" {random.randint(1, 100)}"
                precio = round(random.uniform(10.0, 1000.0), 2)
                self.insert_product(product_id, nombre, precio)
            else:
                # Operación de consulta
                # 70% consulta productos propios, 30% productos aleatorios
                if random.random() < 0.7 and self.products_inserted:
                    product_id = random.choice(self.products_inserted)
                else:
                    product_id = f"PROD-{random.randint(1, 3)}-{random.randint(1, 10)}"
                self.query_product(product_id)
            
            # Espera aleatoria entre operaciones (0.5 a 2 segundos)
            time.sleep(random.uniform(0.5, 2.0))
        
        print(f"[CLIENTE {self.client_id}] Completadas todas las operaciones")


def main():
    """Función principal del cliente"""
    import sys
    
    # Obtener ID del cliente desde argumentos o usar default
    client_id = sys.argv[1] if len(sys.argv) > 1 else "CLIENT-1"
    num_operations = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    client = RPCClient(HOST, PORT, client_id)
    
    try:
        client.run_random_operations(num_operations)
    except KeyboardInterrupt:
        print(f"\n[CLIENTE {client_id}] Cliente detenido")


if __name__ == "__main__":
    main()

