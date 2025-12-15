import network
import time
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
WIFI_SSID = 'Telecentro-48e7'     # <--- Pone tu WiFi aca
WIFI_PASS = 'WK9RH9TV94YY'          # <--- Pone la clave aca
BROKER_IP = "192.168.0.8"           # <--- Pone la IP de tu PC (ipconfig)

# ==========================================
# 3. FUNCIONES DE RED
# ==========================================
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Conectando a WiFi...')
        wlan.connect(WIFI_SSID, WIFI_PASS)
        # Esperar hasta conectar
        timeout = 0
        while not wlan.isconnected():
            time.sleep(1)
            timeout += 1
            if timeout > 10:
                print("No se pudo conectar al WiFi. Revisa la clave.")
                return False
    print('WiFi Conectado! IP:', wlan.ifconfig()[0])
    return True

# Esta función se ejecuta AUTOMÁTICAMENTE cuando llega un mensaje
def al_recibir_mensaje(topic, msg):
    print(f"Orden Recibida: {msg}")
    
    # --- LOGICA DE SIRENA (Modo Interruptor) ---
    if msg == b"SIRENA_ON":
        print(">>> ACTIVANDO SIRENA Y LUCES")
        led_sirena.on()
        led_luces.on() # Las luces se prenden con la sirena
        
    elif msg == b"SIRENA_OFF":
        print(">>> APAGANDO SISTEMA")
        led_sirena.off()
        led_luces.off()

    # --- LOGICA DE PORTON (Modo Pulso) ---
    elif msg == b"PORTON_OPEN":
        print(">>> ABRIENDO PORTON (Pulso 2 seg)")
        led_porton.on()
        time.sleep(2) # Espera 2 segundos
        led_porton.off()
        print(">>> PORTON DETENIDO")

# ==========================================
# 4. BUCLE PRINCIPAL (MAIN LOOP)
# ==========================================
def inicio():
    # 1. Conectar WiFi
    if not conectar_wifi():
        return # Si falla wifi, no seguimos

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
        machine.reset()

# Arrancar el programa
inicio()