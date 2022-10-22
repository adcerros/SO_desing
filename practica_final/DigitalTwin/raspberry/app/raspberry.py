import json
import paho.mqtt.client as mqtt
from RPi import GPIO
import time
from time import sleep
from board import *
import adafruit_dht
from threading import Semaphore
import threading
import copy


RANDOMIZE_SENSORS_INTERVAL = 30
MQTT_SERVER = "34.141.35.215"
MQTT_PORT = 1884
ROOM = "Room1"
CONFIG_TOPIC= "hotel/rooms/" + ROOM + "/config"
TELEMETRY_TOPIC = "hotel/rooms/" + ROOM + "/telemetry/"
INDOOR_LIGHT_TOPIC = TELEMETRY_TOPIC + "indoor-light"
OUTSIDE_LIGHT_TOPIC = TELEMETRY_TOPIC + "outside-light"
AIR_CONDITIONER_TOPIC = TELEMETRY_TOPIC + "air-conditioner"
BLIND_TOPIC = TELEMETRY_TOPIC + "blind"
PRESENCE_TOPIC = TELEMETRY_TOPIC + "presence"
TEMPERATURE_TOPIC = TELEMETRY_TOPIC + "temperature"
COMMAND_TOPIC = "hotel/rooms/" + ROOM + "/command"
AIR_COMMAND_TOPIC = COMMAND_TOPIC + "/air-conditioner"
INDOOR_LIGHT_ACTIVE_TOPIC = COMMAND_TOPIC + "/indoor-light-active"
INDOOR_LIGHT_LEVEL_TOPIC = COMMAND_TOPIC + "/indoor-light-level"
OUTSIDE_LIGHT_ACTIVE_TOPIC = COMMAND_TOPIC + "/outside-light-active"
OUTSIDE_LIGHT_LEVEL_TOPIC = COMMAND_TOPIC + "/outside-light-level"
BLIND_ACTIVE_TOPIC = COMMAND_TOPIC + "/blind-active"
BLIND_LEVEL_TOPIC = COMMAND_TOPIC + "/blind-level"
DISCONNECT_TOPIC = "hotel/rooms/disconnect" + "/" + ROOM

indoor_light_sem = Semaphore(1)
outside_light_sem = Semaphore(1)
blind_sem = Semaphore(1)
air_conditioner_sem = Semaphore(1)
presence_sem = Semaphore(1)
temperature_sem = Semaphore(1)
end_threads = False

is_connected = False


humidity_sensor_gpio = D12
dht11 = adafruit_dht.DHT11(humidity_sensor_gpio, use_pulseio=False)


Motor1A = 13
Motor1B = 19
Motor1E = 26
LedR = 17
LedG = 27
LedB = 22
LedEnable = 18
Button = 23
SMotor1 = 25
SMotor2 = 16
SMotor3 = 20
SMotor4 = 21


outside_led_gpio = 5
indoor_led_gpio = 4

p_motor_secuence = [[1, 1, 0, 0],
                    [0, 1, 1, 0],
                    [0, 0, 1, 1],
                    [1, 0, 0, 1]
                    ]



p_motor_secuence_revert = [[1, 0, 0, 1],
                           [0, 0, 0, 1],
                           [0, 0, 1, 1],
                           [0, 0, 1, 0],
                           [1, 1, 1, 0],
                           [0, 1, 0, 0],
                           [1, 1, 0, 0],
                           [1, 0, 0, 0]
                           ]

p_motor_gpios = [25, 16, 20, 21]
p_motor_gpios_revert = [21, 20, 16, 25]



end_threads = False


def createDict():
    newSensors = {
        "indoor_light": {
            "active": True,
            "level": 0
        },
        "outside_light": {
            "active": True,
            "level": 0
        },
        "blind": {
            "active": True,
            "level": 0
        },
        "air_conditioner": {
            "active": True,
            "level": 0,
            "mode": 2
        },
        "temperature": {
            "active": True,
            "level": 0
        },
        "presence": {
            "active": True,
            "level": 0
        }
    }
    return newSensors

old_sensors = createDict()
sensors = createDict()

def updateAndSendData():
    global old_sensors, sensors, end_threads, indoor_light_sem, outside_light_sem, blind_sem, air_conditioner_sem, presence_sem, temperature_sem
    while True:
        if end_threads is False:
            indoor_light_sem.acquire()
            if old_sensors["indoor_light"] != sensors["indoor_light"]:
                old_sensors["indoor_light"] = copy.deepcopy(sensors["indoor_light"])
                client.publish(INDOOR_LIGHT_TOPIC, payload=json.dumps(old_sensors["indoor_light"]), qos=0, retain=False)
                print("PUBLISHED", " Indoor_light: ", old_sensors["indoor_light"], "IN", INDOOR_LIGHT_TOPIC)
            indoor_light_sem.release()

            outside_light_sem.acquire()
            if old_sensors["outside_light"] != sensors["outside_light"]:
                old_sensors["outside_light"] = copy.deepcopy(sensors["outside_light"])
                client.publish(OUTSIDE_LIGHT_TOPIC, payload=json.dumps(old_sensors["outside_light"]), qos=0, retain=False)
                print("PUBLISHED", " Outside_light: ", old_sensors["outside_light"], "IN", OUTSIDE_LIGHT_TOPIC)
            outside_light_sem.release()

            blind_sem.acquire()
            if old_sensors["blind"] != sensors["blind"]:
                old_sensors["blind"] = copy.deepcopy(sensors["blind"])
                client.publish(BLIND_TOPIC, payload=json.dumps(old_sensors["blind"]), qos=0, retain=False)
                print("PUBLISHED", " Blind: ", old_sensors["blind"], "IN", BLIND_TOPIC)
            blind_sem.release()

            air_conditioner_sem.acquire()
            if old_sensors["air_conditioner"] != sensors["air_conditioner"]:
                old_sensors["air_conditioner"] = copy.deepcopy(sensors["air_conditioner"])
                client.publish(AIR_CONDITIONER_TOPIC, payload=json.dumps(old_sensors["air_conditioner"]), qos=0, retain=False)
                print("PUBLISHED", " Air_conditioner: ", old_sensors["air_conditioner"], "IN", AIR_CONDITIONER_TOPIC)
            air_conditioner_sem.release()

            presence_sem.acquire()
            if old_sensors["presence"] != sensors["presence"]:
                old_sensors["presence"] = copy.deepcopy(sensors["presence"])
                client.publish(PRESENCE_TOPIC, payload=json.dumps(old_sensors["presence"]), qos=0, retain=False)
                print("PUBLISHED", " Presence: ", old_sensors["presence"], "IN", PRESENCE_TOPIC)
            presence_sem.release()

            temperature_sem.acquire()
            if old_sensors["temperature"] != sensors["temperature"]:
                old_sensors["temperature"] = copy.deepcopy(sensors["temperature"])
                client.publish(TEMPERATURE_TOPIC, payload=json.dumps(old_sensors["temperature"]), qos=0, retain=False)
                print("PUBLISHED", " Temperature: ", old_sensors["temperature"], "IN", TEMPERATURE_TOPIC)
            temperature_sem.release()
        else:
            print("Apagando dispositivo")
            sys.exit()




def on_connect(client, userdata, flags, rc):
    global AIR_COMMAND_TOPIC, INDOOR_LIGHT_ACTIVE_TOPIC, INDOOR_LIGHT_LEVEL_TOPIC, OUTSIDE_LIGHT_ACTIVE_TOPIC, OUTSIDE_LIGHT_LEVEL_TOPIC, BLIND_ACTIVE_TOPIC, BLIND_LEVEL_TOPIC, CONFIG_TOPIC
    global is_connected
    print("Digital Twin connected with code ", rc)
    client.publish(CONFIG_TOPIC, payload=ROOM, qos=0, retain=False)
    print("Enviado el id", ROOM, " al topic ", CONFIG_TOPIC)
    client.subscribe(AIR_COMMAND_TOPIC)
    client.subscribe(INDOOR_LIGHT_ACTIVE_TOPIC)
    client.subscribe(INDOOR_LIGHT_LEVEL_TOPIC)
    client.subscribe(OUTSIDE_LIGHT_ACTIVE_TOPIC)
    client.subscribe(OUTSIDE_LIGHT_LEVEL_TOPIC)
    client.subscribe(BLIND_ACTIVE_TOPIC)
    client.subscribe(BLIND_LEVEL_TOPIC)
    is_connected = True



def on_message(client, userdata, msg):
    global old_sensors, is_connected
    print("Mensaje recibido en MQTT 1884", msg.topic, " con mensaje ", msg.payload.decode())
    topic = (msg.topic).split('/')

    if "config" in topic:
        is_connected = True

    elif "command" in topic:
        payload = json.loads(msg.payload.decode())
        print("\nRecibido comando: " + topic[-1] + " con valor: " + str(payload))

        if topic[-1] == "air-conditioner":
            air_conditioner_sem.acquire()
            sensors["air_conditioner"]["mode"] = payload["mode"]
            air_conditioner_sem.release()

        if topic[-1] == "indoor-light-active":
            indoor_light_sem.acquire()
            sensors["indoor_light"]["active"] = payload["active"]
            indoor_light_sem.release()

        if topic[-1] == "indoor-light-level":
            indoor_light_sem.acquire()
            sensors["indoor_light"]["level"] = payload["level"]
            indoor_light_sem.release()

        if topic[-1] == "outside-light-active":
            outside_light_sem.acquire()
            sensors["outside_light"]["active"] = payload["active"]
            outside_light_sem.release()

        if topic[-1] == "outside-light-level":
            outside_light_sem.acquire()
            sensors["outside_light"]["level"] = payload["level"]
            outside_light_sem.release()

        if topic[-1] == "blind-active":
            blind_sem.acquire()
            sensors["blind"]["active"] = payload["active"]
            blind_sem.release()

        if topic[-1] == "blind-level":
            blind_sem.acquire()
            sensors["blind"]["level"] = payload["level"]
            blind_sem.release()


def on_publish(client, userdata, result):
    pass




def connect_mqtt():
    client.username_pw_set(username="dso_server", password="dso_password")
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_message = on_message
    client.will_set(DISCONNECT_TOPIC, ROOM)
    client.connect(MQTT_SERVER, MQTT_PORT, 600)


# AQUI EMPIEZA LO RELACIONADO CON SENSORES !!!!!!!!!!!!!!!!


def setup():
    global Motor1A, Motor1B, Motor1E, LedB, LedG, LedR, LedEnable, Button, outside_led_gpio, indoor_led_gpio, SMotor3, SMotor4, SMotor2, SMotor1
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(Motor1A, GPIO.OUT)
    GPIO.setup(Motor1B, GPIO.OUT)
    GPIO.setup(Motor1E, GPIO.OUT)
    GPIO.setup(LedR, GPIO.OUT)
    GPIO.setup(LedG, GPIO.OUT)
    GPIO.setup(LedB, GPIO.OUT)
    GPIO.setup(LedEnable, GPIO.OUT)
    GPIO.setup(Button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(outside_led_gpio, GPIO.OUT)
    GPIO.setup(indoor_led_gpio, GPIO.OUT)
    GPIO.setup(SMotor1, GPIO.OUT)
    GPIO.setup(SMotor2, GPIO.OUT)
    GPIO.setup(SMotor3, GPIO.OUT)
    GPIO.setup(SMotor4, GPIO.OUT)

# Apagado
def destroy():
    GPIO.cleanup()

# Se encarga de la gestion del motor
def air_conditioner_manager():
    global end_threads, sensors
    pulse_modulator = GPIO.PWM(Motor1E, 100)
    pulse_modulator.start(0)
    while True:
        # Comprobación de interrupciones de salida
        try:
            # Salida controlada
            if end_threads is True:
                GPIO.output(LedEnable, GPIO.LOW)
                GPIO.output(Motor1E, GPIO.LOW)
                sys.exit()
            else:
                air_conditioner_sem.acquire()
                if sensors["air_conditioner"]["mode"] is "0":
                    temperature_sem.acquire()
                    sensors["air_conditioner"]["level"] = min(abs(sensors["temperature"]["level"] - 20) * 10, 50)
                    temperature_sem.release()
                    sensors["air_conditioner"]["active"] = True
                    enable_air_conditioner_led("blue")
                    GPIO.output(Motor1A, GPIO.HIGH)
                    GPIO.output(Motor1B, GPIO.LOW)
                    pulse_modulator.ChangeDutyCycle(sensors["air_conditioner"]["level"])
                elif sensors["air_conditioner"]["mode"] is "1":
                    temperature_sem.acquire()
                    sensors["air_conditioner"]["level"] = min(abs(sensors["temperature"]["level"] - 20) * 10, 50)
                    temperature_sem.release()
                    sensors["air_conditioner"]["active"] = True
                    enable_air_conditioner_led("red")
                    GPIO.output(Motor1A, GPIO.HIGH)
                    GPIO.output(Motor1B, GPIO.LOW)
                    pulse_modulator.ChangeDutyCycle(sensors["air_conditioner"]["level"])
                else:
                    sensors["air_conditioner"]["active"] = False
                    pulse_modulator.ChangeDutyCycle(0)
                    GPIO.output(Motor1A, GPIO.LOW)
                    GPIO.output(Motor1B, GPIO.LOW)
                    enable_air_conditioner_led("None")
                air_conditioner_sem.release()
            sleep(1)
        except RuntimeError:
            print("Error en el motor -> Apagando")
            sys.exit()


# Se encarga de la gestion del sensor
def temperature_manager():
    global end_threads, sensors
    while True:
        # Salida controlada
        if end_threads is True:
            sys.exit()
        try:
            temperature = dht11.temperature
            if temperature != None:
                temperature_sem.acquire()
                sensors["temperature"]["level"] = temperature
                sensors["temperature"]["active"] = True
                temperature_sem.release()
        # Evita errores de lectura en el sensor
        except RuntimeError:
            print("Error de lectura en el sensor de temperatura, tomando una nueva")
            temperature_sem.acquire()
            sensors["temperature"]["active"] = False
            temperature_sem.release()
            continue
        sleep(20)




# Función comun para la definicion de colores
def defineColors(ledR, ledG, ledB):
    GPIO.output(LedR, GPIO.HIGH)
    GPIO.output(LedG, GPIO.HIGH)
    GPIO.output(LedB, GPIO.HIGH)
    if ledR == 1:
        GPIO.output(LedR, GPIO.LOW)
    if ledG == 1:
        GPIO.output(LedG, GPIO.LOW)
    if ledB == 1:
        GPIO.output(LedB, GPIO.LOW)


# Seleccion de colores
def enableColors(currentColor):
    if currentColor == "red":
        defineColors(1, 0, 0)
    elif currentColor == "green":
        defineColors(0, 1, 0)
    elif currentColor == "blue":
        defineColors(0, 0, 1)
    elif currentColor == "None":
        defineColors(0, 0, 0)


# Se encarga de la gestion del led
def enable_air_conditioner_led(led_color):
    GPIO.output(LedEnable, GPIO.LOW)
    enableColors(led_color)
    GPIO.output(LedEnable, GPIO.HIGH)


# Se encarga de la gestion del boton
def presence_manager():
    global Button
    GPIO.add_event_detect(Button, GPIO.BOTH, callback=change_button_state, bouncetime=500)


# Cambia el estado del boton
def change_button_state(channel):
    global sensors, presence_sem, old_sensors
    try:
        presence_sem.acquire()
        if not GPIO.input(channel):
            if sensors["presence"]["level"] == 0:
                sensors["presence"]["level"] = 1
            else:
                sensors["presence"]["level"] = 0
        presence_sem.release()
    except RuntimeError:
        print("Error en la lectura del boton")

def indoor_light_manager():
    global sensors, indoor_light_sem
    current_led = GPIO.PWM(indoor_led_gpio, 100)
    current_led.start(0)
    while True:
        if end_threads is True:
            GPIO.output(indoor_led_gpio, GPIO.LOW)
            sys.exit()
        try:
            indoor_light_sem.acquire()
            if sensors["indoor_light"]["active"] is '1' or sensors["indoor_light"]["active"] is True and int(sensors["indoor_light"]["level"]) > 0:
                current_led.ChangeDutyCycle(int(sensors["indoor_light"]["level"]))
            else:
                current_led.ChangeDutyCycle(0)
            indoor_light_sem.release()
            sleep(5)
        except RuntimeError:
            print("Ha ocurrido un error en el cambio de la luz interior")



def outside_light_manager():
    global sensors, outside_light_sem, outside_led_gpio
    current_led = GPIO.PWM(outside_led_gpio, 100)
    current_led.start(0)
    while True:
        if end_threads is True:
            GPIO.output(outside_led_gpio, GPIO.LOW)
            sys.exit()
        try:
            outside_light_sem.acquire()
            if sensors["outside_light"]["active"] is '1' or sensors["outside_light"]["active"] is True and int(sensors["outside_light"]["level"]) > 0:
                current_led.ChangeDutyCycle(int(sensors["outside_light"]["level"]))
            else:
                current_led.ChangeDutyCycle(0)
            outside_light_sem.release()
        except RuntimeError:
            print("Ha ocurrido un error en el cambio de la luz exterior")

def blind_manager():
    global sensors, blind_sem, SMotor2, SMotor1, SMotor3, SMotor4, p_motor_secuence, p_motor_secuence_revert
    blind_current_state = 0
    while True:
        if end_threads is True:
            for i in range(len(p_motor_gpios)):
                GPIO.output(p_motor_gpios[i], GPIO.LOW)
            sys.exit()
        try:
            blind_sem.acquire()
            if (sensors["blind"]["active"] == '1' or sensors["blind"]["active"] == True) and blind_current_state != int(sensors["blind"]["level"]):
                cicles_number, direction = calculateCicles(blind_current_state)
                if direction == 0:
                    run_p_motor(cicles_number, p_motor_secuence, 0.006)
                elif direction == 1:
                    run_p_motor(cicles_number, p_motor_secuence_revert, 0.0001)
            blind_current_state = int(copy.deepcopy(sensors["blind"]["level"]))
            blind_sem.release()
        except RuntimeError:
            print("Ha ocurrido un error en el cambio de la persiana")
            blind_sem.release()


def run_p_motor(cicles_number, secuences, sleepTime):
    global p_motor_gpios
    for i in range(len(p_motor_gpios)):
        GPIO.output(p_motor_gpios[i], GPIO.LOW)
    sleep(1)
    for j in range(cicles_number):
        for secuence in secuences:
            for i in range(4):
                if secuence[i] == 1:
                    GPIO.output(p_motor_gpios[i], GPIO.HIGH)
                else:
                    GPIO.output(p_motor_gpios[i], GPIO.LOW)
            sleep(sleepTime)


def calculateCicles(blind_current_state):
    global sensors
    direction = 0  # Antihorario
    sensor_value = int(sensors["blind"]["level"])
    if sensor_value <= 0:
        sensor_value = 0
    elif sensor_value >= 180:
        sensor_value = 180
    diference = sensor_value - int(blind_current_state)
    if diference >= 0:
        direction = 1  # Horario
    cicles_number = round(abs(diference) * 1.45)
    return cicles_number, direction

def get_sensors_data():
    setup()
    temperature_thread = threading.Thread(target=temperature_manager, args=[])
    air_conditioner_thread = threading.Thread(target=air_conditioner_manager, args=[])
    presence_thread = threading.Thread(target=presence_manager, args=[])
    indoor_light_thread = threading.Thread(target=indoor_light_manager, args=[])
    outside_light_thread = threading.Thread(target=outside_light_manager, args=[])
    blind_thread = threading.Thread(target=blind_manager, args=[])
    temperature_thread.start()
    presence_thread.start()
    air_conditioner_thread.start()
    indoor_light_thread.start()
    outside_light_thread.start()
    blind_thread.start()
    # Este join mantiene el flujo del programa activo hasta la interrupcion
    temperature_thread.join()
    air_conditioner_thread.join()
    presence_thread.join()
    indoor_light_thread.join()
    outside_light_thread.join()
    blind_thread.join()
    destroy()


def connection_manager():
    global client
    client = mqtt.Client()
    connect_mqtt()
    client.loop_start()
    while is_connected == False:
        print("Enviado el id", ROOM, " al topic ", CONFIG_TOPIC)
        time.sleep(1)
    print("Empiezo a mandar datos")
    updateAndSendData()


if __name__ == "__main__":
    try:
        connection_thread = threading.Thread(target=connection_manager, args=[])
        sensors_thread = threading.Thread(target=get_sensors_data, args=[])
        connection_thread.start()
        sensors_thread.start()
    except KeyboardInterrupt:
        end_threads = True
        connection_thread.join()
        sensors_thread.join()




