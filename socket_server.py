"""
Módulo para gestionar la comunicación entre instancias mediante sockets
"""
import socket
import threading
import sys
import os
import time

# Configuración del socket
HOST = '127.0.0.1'  # localhost
PORT = 65432        # Puerto arbitrario no privilegiado
SOCKET_TIMEOUT = 2  # Tiempo de espera en segundos

# Variable global para el servidor
server_socket = None
server_thread = None
is_running = False

def is_server_running():
    """Comprueba si hay otra instancia del servidor ejecutándose"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect((HOST, PORT))
            s.sendall(b'PING')
            response = s.recv(1024)
            return response == b'PONG'
    except:
        return False

def start_server(trigger_callback):
    """Inicia el servidor socket en segundo plano"""
    global server_socket, server_thread, is_running
    
    if is_running:
        return
    
    def server_loop():
        global server_socket, is_running
        
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((HOST, PORT))
            server_socket.listen()
            server_socket.settimeout(SOCKET_TIMEOUT)
            
            is_running = True
            print(f"Servidor socket iniciado en {HOST}:{PORT}")
            
            while is_running:
                try:
                    conn, addr = server_socket.accept()
                    with conn:
                        data = conn.recv(1024)
                        if data == b'PING':
                            conn.sendall(b'PONG')
                        elif data == b'TRIGGER':
                            print("Recibida solicitud de transcripción desde otra instancia")
                            conn.sendall(b'OK')
                            # Llamar al callback para iniciar la transcripción
                            threading.Thread(target=trigger_callback, daemon=True).start()
                except socket.timeout:
                    # Timeout normal, continuar el ciclo
                    continue
                except Exception as e:
                    if is_running:  # Solo mostrar errores si aún estamos en ejecución
                        print(f"Error en el servidor socket: {e}")
        except Exception as e:
            print(f"Error iniciando el servidor socket: {e}")
        finally:
            if server_socket:
                server_socket.close()
            is_running = False
            print("Servidor socket detenido")
    
    server_thread = threading.Thread(target=server_loop, daemon=True)
    server_thread.start()

def stop_server():
    """Detiene el servidor socket"""
    global server_socket, is_running
    
    is_running = False
    if server_socket:
        server_socket.close()
    
    if server_thread and server_thread.is_alive():
        server_thread.join(timeout=1)

def send_trigger_command():
    """Envía un comando para activar la transcripción en la instancia principal"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3)
            s.connect((HOST, PORT))
            s.sendall(b'TRIGGER')
            response = s.recv(1024)
            return response == b'OK'
    except Exception as e:
        print(f"Error al comunicarse con la instancia principal: {e}")
        return False