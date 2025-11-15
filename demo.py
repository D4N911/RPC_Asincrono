#!/usr/bin/env python3
"""
Script de demostración del sistema RPC asíncrono

Este script facilita la demostración del funcionamiento concurrente
del sistema iniciando el servidor y múltiples clientes automáticamente.
"""

import subprocess
import threading
import time
import sys
import os


def run_server():
    """Ejecuta el servidor"""
    print("=" * 60)
    print("INICIANDO SERVIDOR RPC")
    print("=" * 60)
    try:
        subprocess.run([sys.executable, "servidor.py"])
    except KeyboardInterrupt:
        print("\n[SERVER] Servidor detenido")


def run_client(client_id, num_operations, delay_start=0):
    """Ejecuta un cliente con delay inicial"""
    time.sleep(delay_start)
    print(f"\n[CLIENT {client_id}] Iniciando cliente...")
    try:
        subprocess.run([sys.executable, "cliente.py", client_id, str(num_operations)])
    except Exception as e:
        print(f"[CLIENT {client_id}] Error: {e}")


def main():
    """Función principal de demostración"""
    print("\n" + "=" * 60)
    print("DEMOSTRACIÓN DEL SISTEMA RPC ASÍNCRONO")
    print("=" * 60)
    print("\nEste script iniciará:")
    print("  1. Un servidor RPC")
    print("  2. Múltiples clientes que realizarán operaciones concurrentes")
    print("\nPresiona Ctrl+C para detener todo\n")
    
    # Configuración
    num_clients = 3
    num_operations = 8
    
    if len(sys.argv) > 1:
        num_clients = int(sys.argv[1])
    if len(sys.argv) > 2:
        num_operations = int(sys.argv[2])
    
    print(f"Configuración:")
    print(f"  - Clientes: {num_clients}")
    print(f"  - Operaciones por cliente: {num_operations}")
    print(f"\nIniciando en 3 segundos...\n")
    time.sleep(3)
    
    # Iniciar servidor en thread separado
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Esperar a que el servidor esté listo
    print("[DEMO] Esperando a que el servidor esté listo...")
    time.sleep(3)
    
    # Iniciar clientes
    client_threads = []
    for i in range(num_clients):
        client_id = f"CLIENT-{i+1}"
        delay = i * 1.0  # Stagger los inicios de clientes
        client_thread = threading.Thread(
            target=run_client,
            args=(client_id, num_operations, delay),
            daemon=True
        )
        client_thread.start()
        client_threads.append(client_thread)
    
    print(f"\n[DEMO] {num_clients} clientes iniciados")
    print("[DEMO] Observa las impresiones del servidor para ver:")
    print("       - Las solicitudes recibidas")
    print("       - El orden de procesamiento (inserciones primero)")
    print("       - Las posiciones devueltas\n")
    
    # Esperar a que todos los clientes terminen
    try:
        for thread in client_threads:
            thread.join()
        print("\n[DEMO] Todos los clientes han completado sus operaciones")
        print("[DEMO] El servidor seguirá ejecutándose. Presiona Ctrl+C para detenerlo.")
        
        # Mantener el servidor corriendo
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n[DEMO] Deteniendo demostración...")
        sys.exit(0)


if __name__ == "__main__":
    main()

