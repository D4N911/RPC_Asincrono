#!/usr/bin/env python3
"""
Script para probar el sistema con múltiples clientes concurrentes

Este script inicia el servidor y varios clientes en threads separados
para demostrar el funcionamiento concurrente del sistema.
"""

import subprocess
import threading
import time
import sys


def run_server():
    """Ejecuta el servidor en un proceso separado"""
    print("[TEST] Iniciando servidor...")
    subprocess.run([sys.executable, "servidor.py"])


def run_client(client_id, num_operations):
    """Ejecuta un cliente con el ID y número de operaciones especificados"""
    print(f"[TEST] Iniciando cliente {client_id}...")
    subprocess.run([sys.executable, "cliente.py", client_id, str(num_operations)])


def main():
    """Función principal para pruebas concurrentes"""
    import sys
    
    # Número de clientes y operaciones por cliente
    num_clients = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    num_operations = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    print(f"[TEST] Iniciando prueba con {num_clients} clientes, {num_operations} operaciones cada uno")
    print("[TEST] Presiona Ctrl+C para detener")
    
    # Iniciar servidor en thread separado
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Esperar a que el servidor esté listo
    time.sleep(2)
    
    # Iniciar clientes
    client_threads = []
    for i in range(num_clients):
        client_id = f"CLIENT-{i+1}"
        client_thread = threading.Thread(
            target=run_client,
            args=(client_id, num_operations),
            daemon=True
        )
        client_thread.start()
        client_threads.append(client_thread)
        time.sleep(0.5)  # Pequeño delay entre inicios de clientes
    
    # Esperar a que todos los clientes terminen
    for thread in client_threads:
        thread.join()
    
    print("[TEST] Todas las pruebas completadas")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[TEST] Prueba interrumpida")

