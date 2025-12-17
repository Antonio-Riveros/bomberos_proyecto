import network
import time
import machine
from machine import Pin
# Importamos la librería que pusiste en la carpeta lib
from lib.mqtt import MQTTClient 

# ==========================================
# 1. CONFIGURACIÓN DEL HARDWARE
# ==========================================
# Definimos los pines según el esquema de arriba
led_sirena = Pin(26, Pin.OUT)  # Rojo
led_porton = Pin(27, Pin.OUT)  # Verde
led_luces  = Pin(14, Pin.OUT)  # Amarillo

# Aseguramos que todo arranque apagado
led_sirena.off()
led_porton.off()
led_luces.off()

# ==========================================
# 2. TUS DATOS (¡EDITA ESTO!)
# ==========================================
BROKER_IP = "192.168.0.8"           # <--- Pone la IP de tu PC (ipconfig)

# ==========================================

# Esta función se ejecuta AUTOMÁTICAMENTE cuando llega un mensaje
def al_recibir_mensaje(topic, msg):
    print(f"Orden Recibida: {msg}") 
    
    # --- LOGICA DE SIRENA (Solo Rojo) ---
    if msg == b"SIRENA_ON":
        print(">>> ACTIVANDO SIRENA")
        led_sirena.on()
        led_luces.on()  #<-- COMENTA ESTA LÍNEA si quieres que la sirena NO prenda la luz amarilla
        
    elif msg == b"SIRENA_OFF":
        print(">>> APAGANDO TODO")
        led_sirena.off()
        led_luces.off() # Apagamos todo por seguridad

    # --- LOGICA DE LUCES (Solo Amarillo - NUEVO) ---
    elif msg == b"LUCES_ON":
        print(">>> LUCES ENCENDIDAS")
        led_luces.on()
        
    elif msg == b"LUCES_OFF":
        print(">>> LUCES APAGADAS") 
        led_luces.off()

    # --- LOGICA DE PORTON --- 
    elif msg == b"PORTON_OPEN": 
        print(">>> ABRIENDO PORTON") 
        led_porton.on() 
        time.sleep(5) # Simula el tiempo que tarda en abrir
        led_porton.off() 
        print(">>> PORTON DETENIDO") 

    # --- LOGICA DE EMERGENCIA COMPLETA (Combo) ---
    elif msg == b"EMERGENCIA_ON":
        print(">>> PROTOCOLO DE EMERGENCIA ACTIVADO")
        led_sirena.on()  # Prende Rojo
        led_luces.on()   # Prende Amarillo 
        
    elif msg == b"EMERGENCIA_OFF":
        print(">>> EMERGENCIA FINALIZADA")
        led_sirena.off()
        led_luces.off()

# ==========================================
# 4. BUCLE PRINCIPAL (MAIN LOOP)
# ==========================================
def inicio():
    # 1. EL WIFI YA LO HIZO boot.py -> Pasamos directo al Broker
    
    try:
        # 2. Conectar al Broker MQTT (Tu PC)
        print(f"Conectando al Broker en {BROKER_IP}...")
        client = MQTTClient("ESP32_BOMBEROS", BROKER_IP)
        client.set_callback(al_recibir_mensaje)
        client.connect()
        
        # 3. Suscribirse al canal de comandos
        client.subscribe(b"sagired/comandos")
        print("LISTO. Esperando ordenes desde la PC...")

        # 4. Bucle Infinito (Escuchar)
        while True:
            # Revisa si hay mensajes nuevos
            client.check_msg()
            # Una pequeña pausa para no saturar el procesador
            time.sleep(0.1)

    except Exception as e:
        print("ERROR CRITICO:", e)
        print("Reiniciando en 5 segundos...")
        time.sleep(5)
        # machine.reset()  <--- ¡MANTÉN ESTO COMENTADO POR AHORA!

# Arrancar el programa
inicio()