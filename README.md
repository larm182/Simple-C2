# C2 en Python con Flask-SocketIO

# Descripción

Este es un sistema de Comando y Control (C2) desarrollado en Python utilizando Flask-SocketIO. Permite la administración remota de clientes, ofreciendo funcionalidades como:

Ejecución de comandos en el cliente

Captura de pantalla remota

Keylogger

Transferencia de archivos

Geolocalización del cliente

# Requisitos

Asegúrate de tener instaladas las siguientes dependencias:

pip install flask-socketio geopy pynput pyautogui requests flask folium cryptography socketio keyboard pynput opencv-python pillow

# Estructura del Proyecto
Simple - C2 /

│── static

  └──icono.png
  
│── templates

    └──login.html
    └──index.html
    └──panel.html
    
│── app.py  # Servidor Flask-SocketIO

│── client.py  # Cliente Python

└── README.md  # Documentación

# Uso

Inicia el servidor:

python app.py

Usuario 1: admin Password 1: admin
Usuario 2: usuario Password 2: password

Ejecuta el cliente en la máquina objetivo:

python client.py

# Controla la máquina desde el servidor enviando comandos.

# Advertencia

Este proyecto es solo con fines educativos y de investigación. No se debe utilizar en sistemas sin autorización. El uso indebido puede tener consecuencias legales.

# Video Demo

https://github.com/user-attachments/assets/4621c604-a8a7-4359-88bc-9fac7f5ad6a1






