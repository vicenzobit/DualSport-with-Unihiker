# -*- coding: UTF-8 -*-
from unihiker import GUI
from pinpong.board import Board, Pin
import time

# Inicializar la placa
Board().begin()

# Crear una instancia de la GUI
u_gui = GUI()

# Definir los pines de los sensores
sensor_corazon_pin = Pin(Pin.P21, Pin.ANALOG)  # Sensor de frecuencia cardíaca en Pin 21
sensor_bici_pin = Pin(Pin.P22, Pin.ANALOG)  # Sensor de bicicleta en Pin 22

# Parámetros para la bicicleta
perimetro_rueda = 1000  # en metros (modifica según el tamaño de tu rueda)
vueltas = 0
distancia_recorrida = 0.0  # en kilómetros
velocidad = 0.0  # en km/h
velocidad_maxima = 0.0  # en km/h
calorias_quemadas = 0.0
tiempo_inicio = 0
tiempo_anterior = 0
sensor_valor_anterior_bici = 512
activo = False

# Parámetros para la frecuencia cardíaca
lastBeatTime = time.time()
heartRateBPM = 0
isPeak = False
minTimeBetweenBeats = 300  # Tiempo mínimo entre latidos en milisegundos
maxTimeBetweenBeats = 2000  # Tiempo máximo entre latidos
changeThreshold = 100  # Cambio significativo entre lecturas para detectar un latido
sensor_valor_anterior_corazon = 0

# Funciones para la bicicleta
def calcular_calorias(distancia):
    return distancia * 40  # ajuste a la actividad moderada

def calcular_velocidad(tiempo_vuelta):
    global perimetro_rueda
    if tiempo_vuelta > 0:
        velocidad_m_s = perimetro_rueda / tiempo_vuelta
        return velocidad_m_s * 3.6  # Convertir de m/s a km/h
    else:
        return 0.0

# Funciones de manejo del viaje en bicicleta
def on_buttona_click_callback():
    global activo, tiempo_anterior, tiempo_inicio, vueltas, distancia_recorrida, velocidad_maxima, calorias_quemadas
    activo = True
    tiempo_inicio = time.time()
    tiempo_anterior = time.time()
    vueltas = 0
    distancia_recorrida = 0.0
    velocidad_maxima = 0.0
    calorias_quemadas = 0.0
    u_gui.clear()

def on_buttonb_click_callback():
    global activo
    activo = False
    u_gui.clear()
    tiempo_total = time.time() - tiempo_inicio
    tiempo_total_min = tiempo_total / 60  # Convertir a minutos
    u_gui.draw_text(text=f"¡Viaje Finalizado!", origin="center", x=120, y=20, font=("Arial", 20, "bold"), color="#FF0000")
    u_gui.draw_text(text=f"Distancia: {distancia_recorrida:.2f} km", x=5, y=50, font=("Arial", 16), color="#00FF00")
    u_gui.draw_text(text=f"Vel. Max: {velocidad_maxima:.2f} km/h", x=5, y=70, font=("Arial", 16), color="#0000FF")
    u_gui.draw_text(text=f"Calorías: {calorias_quemadas:.2f}", x=5, y=90, font=("Arial", 16), color="#FF00FF")
    u_gui.draw_text(text=f"Tiempo: {tiempo_total_min:.2f} min", x=5, y=110, font=("Arial", 16), color="#FFAA00")
    u_gui.draw_text(text="Presiona A para reiniciar", origin="center", x=120, y=160, font=("Arial", 12), color="#000000")
    u_gui.draw_image(x=-15, y=190, w=350, h=150, image='bici1.png')

u_gui.on_a_click(on_buttona_click_callback)
u_gui.on_b_click(on_buttonb_click_callback)

# Mostrar mensaje inicial
u_gui.clear()
u_gui.draw_text(text="Presiona A para", origin="center", x=120, y=50, font=("Arial", 18, "bold"), color="#7ed957")
u_gui.draw_text(text="iniciar tu viaje", origin="center", x=120, y=80, font=("Arial", 18, "bold"), color="#7ed957")
u_gui.draw_image(x=-15, y=120, w=350, h=150, image='bici3.png')

# Función para detectar latido
def detect_heartbeat(sensorValue):
    global isPeak, lastBeatTime, heartRateBPM, sensor_valor_anterior_corazon
    
    currentTime = time.time()
    timeDiff = (currentTime - lastBeatTime) * 1000  # Convertir a milisegundos
    
    if abs(sensorValue - sensor_valor_anterior_corazon) > changeThreshold and not isPeak:
        if minTimeBetweenBeats < timeDiff < maxTimeBetweenBeats:  # Considerar tiempos razonables
            isPeak = True
            heartRateBPM = 60000 / timeDiff  # Calcular BPM
            lastBeatTime = currentTime
            print(f"Latido detectado. Intervalo: {timeDiff} ms. BPM calculado: {heartRateBPM}")
    elif abs(sensorValue - sensor_valor_anterior_corazon) < changeThreshold and isPeak:
        isPeak = False  # Preparar para detectar el siguiente latido

    sensor_valor_anterior_corazon = sensorValue  # Actualizar el último valor leído

# Bucle principal
while True:
    if activo:
        # --- Cálculos para la bicicleta ---
        sensor_valor_bici = sensor_bici_pin.read_analog()
        
        if sensor_valor_bici < 512 and sensor_valor_anterior_bici >= 512:
            tiempo_actual = time.time()
            tiempo_vuelta = tiempo_actual - tiempo_anterior
            tiempo_anterior = tiempo_actual
            
            velocidad = calcular_velocidad(tiempo_vuelta)
            vueltas += 1
            distancia_recorrida = vueltas * perimetro_rueda / 1000  # Convertir a km
            
            if velocidad > velocidad_maxima:
                velocidad_maxima = velocidad
            
            calorias_quemadas = calcular_calorias(distancia_recorrida)
        
        # Calcular el tiempo transcurrido
        tiempo_total = time.time() - tiempo_inicio
        tiempo_total_min = tiempo_total / 60  # Convertir a minutos
        
        # --- Cálculos para la frecuencia cardíaca ---
        sensor_valor_corazon = sensor_corazon_pin.read_analog()
        detect_heartbeat(sensor_valor_corazon)
        
        # Mostrar la información en pantalla
        u_gui.clear()
        u_gui.draw_text(text=f"Velocidad: {velocidad:.2f} km/h", x=5, y=10, font=("Arial", 16), color="#0000FF")
        u_gui.draw_text(text=f"Distancia: {distancia_recorrida:.2f} km", x=5, y=40, font=("Arial", 16), color="#00FF00")
        u_gui.draw_text(text=f"Calorías: {calorias_quemadas:.2f}", x=5, y=70, font=("Arial", 16), color="#FF00FF")
        u_gui.draw_text(text=f"F.C.: {heartRateBPM:.2f} BPM", x=5, y=100, font=("Arial", 16), color="#FF0000")
        u_gui.draw_text(text=f"Tiempo: {tiempo_total_min:.2f} min", x=5, y=130, font=("Arial", 16), color="#FFAA00")
        u_gui.draw_image(x=-15, y=170, w=350, h=150, image='bici2.png')
        
        sensor_valor_anterior_bici = sensor_valor_bici
    
    time.sleep(0.5)
