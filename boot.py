# boot.py - Se ejecuta al arrancar el ESP32
import network
import time
import gc

def conectar_wifi():
    # --- TUS DATOS DE WIFI ---
    SSID = 'Telecentro-48e7'     # <--- Pon aquí el nombre exacto de tu WiFi
    PASSWORD = "WK9RH9TV94YY"      # <--- Pon aquí tu contraseña
    # -------------------------

    station = network.WLAN(network.STA_IF)
    station.active(True)

    if not station.isconnected():
        print(f'Conectando a {SSID}...')
        station.connect(SSID, PASSWORD)

        # Intentar conectar por 10 segundos
        max_intentos = 10
        while not station.isconnected() and max_intentos > 0:
            print('.', end='')
            time.sleep(1)
            max_intentos -= 1

    if station.isconnected():
        print('\n✅ WiFi Conectado!')
        print('Datos de red:', station.ifconfig()) # Imprime la IP
    else:
        print('\n❌ Falló la conexión WiFi. Revisa la contraseña.')

# 1. Ejecutar la conexión
conectar_wifi()

# 2. Limpiar memoria basura (Recomendado)
gc.collect()