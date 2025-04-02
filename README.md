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
  └────icono.png
│── templates
    └────login.html
    └────index.html
    └────panel.html
│── app.py  # Servidor Flask-SocketIO
│── client.py  # Cliente Python
└── README.md  # Documentación
