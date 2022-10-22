import copy
from http import client
import time, os, threading, subprocess, random
import paho.mqtt.client as mqtt
import json
from threading import Semaphore



def get_host_name():
    bashCommandName = 'echo $HOSTNAME'
    host = subprocess \
        .check_output(['bash', '-c', bashCommandName])\
        .decode("utf-8")[0:-1]
    return host


RANDOMIZE_SENSORS_INTERVAL = 60  # seconds
MQTT_SERVER = os.getenv("MQTT_SERVER_ADDRESS")
MQTT_SERVER_PORT_1 = int(os.getenv("MQTT_SERVER_PORT_1"))
MQTT_SERVER_PORT_2 = int(os.getenv("MQTT_SERVER_PORT_2"))
ROOM_ID = get_host_name()

flag = "0"


indoor_light_sem = Semaphore(1)
outside_light_sem = Semaphore(1)
blind_sem = Semaphore(1)
air_conditioner_sem = Semaphore(1)
presence_sem = Semaphore(1)
temperature_sem = Semaphore(1)


room_number = ""


CONFIG_TOPIC = "hotel/rooms/" + ROOM_ID + "/config"
COMMAND_TOPIC = ""
AIR_CONDITIONER_COMMAND_TOPIC = ""
TELEMETRY_TOPIC = ""
INDOOR_LIGHT_TOPIC = ""
OUTSIDE_LIGHT_TOPIC = ""
AIR_CONDITIONER_TOPIC = ""
BLIND_TOPIC = ""
PRESENCE_TOPIC = ""
TEMPERATURE_TOPIC = ""
INDOOR_LIGHT_ACTIVE_TOPIC = ""
INDOOR_LIGHT_LEVEL_TOPIC = ""
OUTSIDE_LIGHT_ACTIVE_TOPIC = ""
OUTSIDE_LIGHT_LEVEL_TOPIC = ""
BLIND_ACTIVE_TOPIC = ""
BLIND_LEVEL_TOPIC = ""
DISCONNECT_TOPIC = "hotel/rooms/disconnect"

air_mode_change = 0
air_conditioner_mode = ""
air_conditioner_command_sem = Semaphore(1)

indoor_light_active_change = 0
indoor_light_active = ""
indoor_light_active_command_sem = Semaphore(1)

indoor_light_level_change = 0
indoor_light_level = ""
indoor_light_level_command_sem = Semaphore(1)

outside_light_active_change = 0
outside_light_active = ""
outside_light_active_command_sem = Semaphore(1)

outside_light_level_change = 0
outside_light_level = ""
outside_light_level_command_sem = Semaphore(1)

blind_active_change = 0
blind_active = ""
blind_active_command_sem = Semaphore(1)

blind_level_change = 0
blind_level = ""
blind_level_command_sem = Semaphore(1)

raspi_connected = False
raspi_connected_sem = Semaphore(1)

commands_buffer = []
commands_buffer_sem = Semaphore(1)


def createDict():
    newSensors = {
        "indoor_light": {
            "active": False,
            "level": 0
        },
        "outside_light": {
            "active": False,
            "level": 0
        },
        "blind": {
            "active": False,
            "level": 0
        },
        "air_conditioner": {
            "active": False,
            "level": 0,
            "mode": 2
        },
        "temperature": {
            "active": False,
            "level": 0
        },
        "presence": {
            "active": False,
            "level": 0
        }
    }
    return newSensors


old_sensors = copy.deepcopy(createDict())
sensors = copy.deepcopy(createDict())


def randomize_sensors():
    newSensors = {
        "indoor_light":{
            "active": True if random.randint(0, 1) == 1 else False,
            "level": random.randint(0, 100)
        },
        "outside_light":{
            "active": True if random.randint(0, 1) == 1 else False,
            "level": random.randint(0, 100)
        },
        "blind":{
            "active": True if random.randint(0, 1) == 1 else False,
            "level": random.randint(0, 100)
        },
        "air_conditioner":{
            "active": True if random.randint(0, 1) == 1 else False,
            "level": random.randint(0, 100),
            "mode": random.randint(0, 3)
        },
        "temperature":{
            "active": True if random.randint(0, 1) == 1 else False,
            "level": random.randint(0, 100)
        },
        "presence": {
            "active": True if random.randint(0, 1) == 1 else False,
            "level": random.randint(0, 1)
        }
    }
    return newSensors


def on_connect_1883(client, userdata, flags, rc):
    print("MQTT-2 1883 connected with code ", rc, "THREAD", threading.current_thread().ident)
    # Mandamos nuestro id por el config/id del 83 y nos suscribirmos al config/id/rooms
    # Esperamos a recibir nuestro numero de habitacion el config/id/room
    # y una vez recibido modificamos la variable global
    client.publish(CONFIG_TOPIC, payload=ROOM_ID, qos=0, retain=False)
    print("Enviado MQTT-2 1883 el id", ROOM_ID, "al topic", CONFIG_TOPIC)
    client.subscribe(CONFIG_TOPIC + "/room")
    print("Subscribed 1883 to topic:" + CONFIG_TOPIC + "/room")




def connect_mqtt_1883():
    global old_sensors, sensors
    global indoor_light_sem, outside_light_sem, blind_sem, air_conditioner_sem, presence_sem, temperature_sem
    client = mqtt.Client()
    client.username_pw_set(username="dso_server", password="dso_password")
    client.on_connect = on_connect_1883
    client.on_publish = on_publish
    client.on_message = on_message_1883
    client.on_disconnect = on_disconnect
    client.will_set(DISCONNECT_TOPIC, ROOM_ID)
    client.connect(MQTT_SERVER, MQTT_SERVER_PORT_1, 60)
    client.loop_start()
    while room_number == "":
        print("WAITING ROOM NUMBER IN THREAD", threading.current_thread().ident)
        time.sleep(1)
    while True:
        indoor_light_sem.acquire()
        if old_sensors["indoor_light"] != sensors["indoor_light"]:
            client.publish(INDOOR_LIGHT_TOPIC, payload=json.dumps(sensors["indoor_light"]), qos=0, retain=False)
            print("PUBLISHED", " Indoor_light: ", sensors["indoor_light"], "IN", INDOOR_LIGHT_TOPIC)
            old_sensors["indoor_light"] = copy.deepcopy(sensors["indoor_light"])
        indoor_light_sem.release()
        outside_light_sem.acquire()
        if old_sensors["outside_light"] != sensors["outside_light"]:
            client.publish(OUTSIDE_LIGHT_TOPIC, payload=json.dumps(sensors["outside_light"]), qos=0, retain=False)
            print("PUBLISHED", " Outside_light: ", sensors["outside_light"], "IN", OUTSIDE_LIGHT_TOPIC)
            old_sensors["outside_light"] = copy.deepcopy(sensors["outside_light"])
        outside_light_sem.release()
        blind_sem.acquire()
        if old_sensors["blind"] != sensors["blind"]:
            client.publish(BLIND_TOPIC, payload=json.dumps(sensors["blind"]), qos=0, retain=False)
            print("PUBLISHED", " Blind: ", sensors["blind"], "IN", BLIND_TOPIC)
            old_sensors["blind"] = copy.deepcopy(sensors["blind"])
        blind_sem.release()
        air_conditioner_sem.acquire()
        if old_sensors["air_conditioner"] != sensors["air_conditioner"]:
            client.publish(AIR_CONDITIONER_TOPIC, payload=json.dumps(sensors["air_conditioner"]), qos=0, retain=False)
            print("PUBLISHED", " Air_conditioner: ", sensors["air_conditioner"], "IN", AIR_CONDITIONER_TOPIC)
            old_sensors["air_conditioner"] = copy.deepcopy(sensors["air_conditioner"])
        air_conditioner_sem.release()
        presence_sem.acquire()
        if old_sensors["presence"] != sensors["presence"]:
            client.publish(PRESENCE_TOPIC, payload=json.dumps(sensors["presence"]), qos=0, retain=False)
            print("PUBLISHED", " Presence: ", sensors["presence"], "IN", PRESENCE_TOPIC)
            old_sensors["presence"] = copy.deepcopy(sensors["presence"])
        presence_sem.release()
        temperature_sem.acquire()
        if old_sensors["temperature"] != sensors["temperature"]:
            client.publish(TEMPERATURE_TOPIC, payload=json.dumps(sensors["temperature"]), qos=0, retain=False)
            print("PUBLISHED", " Temperature: ", sensors["temperature"], "IN", TEMPERATURE_TOPIC)
            old_sensors["temperature"] = copy.deepcopy(sensors["temperature"])
        temperature_sem.release()
    client.loop_stop()


def on_message_1883(client, userdata, msg):
    global air_conditioner_mode, indoor_light_active, indoor_light_level, outside_light_active, outside_light_level, blind_level, blind_active , room_number
    global air_conditioner_command_sem, outside_light_active_command_sem, outside_light_level_command_sem, indoor_light_active_command_sem, indoor_light_level_command_sem, blind_level_command_sem, blind_active_command_sem
    global AIR_CONDITIONER_COMMAND_TOPIC, INDOOR_LIGHT_ACTIVE_TOPIC, INDOOR_LIGHT_LEVEL_TOPIC, OUTSIDE_LIGHT_ACTIVE_TOPIC, OUTSIDE_LIGHT_LEVEL_TOPIC, BLIND_ACTIVE_TOPIC, BLIND_LEVEL_TOPIC, CONFIG_TOPIC
    global air_mode_change, blind_active_change, blind_level_change, indoor_light_level_change, outside_light_level_change, outside_light_active_change, indoor_light_active_change
    print("Mensaje recibido MQTT 1883", msg.topic, " con mensaje ", msg.payload.decode())
    topic = msg.topic.split('/')
    if "config" in topic:
        room_number = msg.payload.decode()
        print("Room number received as: ", room_number, "in thread ", threading.current_thread().ident)
        update_topics()
        # Nos suscribimos al encargado de recibir la informacion desde message router
        client.subscribe(AIR_CONDITIONER_COMMAND_TOPIC)
        client.subscribe(INDOOR_LIGHT_ACTIVE_TOPIC)
        client.subscribe(INDOOR_LIGHT_LEVEL_TOPIC)
        client.subscribe(OUTSIDE_LIGHT_ACTIVE_TOPIC)
        client.subscribe(OUTSIDE_LIGHT_LEVEL_TOPIC)
        client.subscribe(BLIND_ACTIVE_TOPIC)
        client.subscribe(BLIND_LEVEL_TOPIC)


    elif "command" in topic:
        print("RECIBIDO COMANDO " + str(topic[-1]))
        if topic[-1] == "air-conditioner":
            air_conditioner_command_sem.acquire()
            air_conditioner_mode = copy.deepcopy(msg.payload.decode())
            air_mode_change = 1
            air_conditioner_command_sem.release()

        if topic[-1] == "indoor-light-active":
            indoor_light_active_command_sem.acquire()
            indoor_light_active = copy.deepcopy(msg.payload.decode())
            indoor_light_active_change = 1
            indoor_light_active_command_sem.release()

        if topic[-1] == "indoor-light-level":
            indoor_light_level_command_sem.acquire()
            indoor_light_level = copy.deepcopy(msg.payload.decode())
            indoor_light_level_change = 1
            indoor_light_level_command_sem.release()

        if topic[-1] == "outside-light-active":
            outside_light_active_command_sem.acquire()
            outside_light_active = copy.deepcopy(msg.payload.decode())
            outside_light_active_change = 1
            outside_light_active_command_sem.release()

        if topic[-1] == "outside-light-level":
            outside_light_level_command_sem.acquire()
            outside_light_level = copy.deepcopy(msg.payload.decode())
            outside_light_level_change = 1
            outside_light_level_command_sem.release()

        if topic[-1] == "blind-active":
            blind_active_command_sem.acquire()
            blind_active = copy.deepcopy(msg.payload.decode())
            blind_active_change = 1
            blind_active_command_sem.release()

        if topic[-1] == "blind-level":
            blind_level_command_sem.acquire()
            blind_level = copy.deepcopy(msg.payload.decode())
            blind_level_change = 1
            blind_level_command_sem.release()


def update_topics():
    global CONFIG_TOPIC, COMMAND_TOPIC, TELEMETRY_TOPIC, INDOOR_LIGHT_TOPIC, OUTSIDE_LIGHT_TOPIC, AIR_CONDITIONER_TOPIC, BLIND_TOPIC, PRESENCE_TOPIC, TEMPERATURE_TOPIC, DISCONNECT_TOPIC
    global AIR_CONDITIONER_COMMAND_TOPIC, INDOOR_LIGHT_ACTIVE_TOPIC, INDOOR_LIGHT_LEVEL_TOPIC, OUTSIDE_LIGHT_ACTIVE_TOPIC, OUTSIDE_LIGHT_LEVEL_TOPIC, BLIND_ACTIVE_TOPIC, BLIND_LEVEL_TOPIC
    global room_number
    # Una vez recibimos el numero de habitacion es cuando asignamos el valor a los topics con el valor real
    CONFIG_TOPIC = "hotel/rooms/" + room_number + "/config"
    COMMAND_TOPIC = "hotel/rooms/" + room_number + "/command"
    AIR_CONDITIONER_COMMAND_TOPIC = COMMAND_TOPIC + "/air-conditioner"
    TELEMETRY_TOPIC = "hotel/rooms/" + room_number + "/telemetry/"
    INDOOR_LIGHT_TOPIC = TELEMETRY_TOPIC + "indoor-light"
    OUTSIDE_LIGHT_TOPIC = TELEMETRY_TOPIC + "outside-light"
    AIR_CONDITIONER_TOPIC = TELEMETRY_TOPIC + "air-conditioner"
    BLIND_TOPIC = TELEMETRY_TOPIC + "blind"
    PRESENCE_TOPIC = TELEMETRY_TOPIC + "presence"
    TEMPERATURE_TOPIC = TELEMETRY_TOPIC + "temperature"
    INDOOR_LIGHT_ACTIVE_TOPIC = COMMAND_TOPIC + "/indoor-light-active"
    INDOOR_LIGHT_LEVEL_TOPIC = COMMAND_TOPIC + "/indoor-light-level"
    OUTSIDE_LIGHT_ACTIVE_TOPIC = COMMAND_TOPIC + "/outside-light-active"
    OUTSIDE_LIGHT_LEVEL_TOPIC = COMMAND_TOPIC + "/outside-light-level"
    BLIND_ACTIVE_TOPIC = COMMAND_TOPIC + "/blind-active"
    BLIND_LEVEL_TOPIC = COMMAND_TOPIC + "/blind-level"




def on_connect_1884(client, userdata, flags, rc):
    print("Connected to MQTT 1884 with code", rc)



def connect_mqtt_1884():
    global air_conditioner_mode, indoor_light_active, indoor_light_level, outside_light_active, outside_light_level, blind_level, blind_active, room_number, sensors
    global air_conditioner_command_sem, outside_light_active_command_sem, outside_light_level_command_sem, indoor_light_active_command_sem, indoor_light_level_command_sem, blind_level_command_sem, blind_active_command_sem, raspi_connected_sem
    global INDOOR_LIGHT_ACTIVE_TOPIC, INDOOR_LIGHT_LEVEL_TOPIC, OUTSIDE_LIGHT_ACTIVE_TOPIC, OUTSIDE_LIGHT_LEVEL_TOPIC, BLIND_ACTIVE_TOPIC, BLIND_LEVEL_TOPIC
    global AIR_CONDITIONER_COMMAND_TOPIC, INDOOR_LIGHT_ACTIVE_TOPIC, INDOOR_LIGHT_LEVEL_TOPIC, OUTSIDE_LIGHT_ACTIVE_TOPIC, OUTSIDE_LIGHT_LEVEL_TOPIC, BLIND_ACTIVE_TOPIC, BLIND_LEVEL_TOPIC
    global air_mode_change, blind_active_change, blind_level_change, indoor_light_level_change, outside_light_level_change, outside_light_active_change, indoor_light_active_change, commands_buffer, commands_buffer_sem
    while room_number == "":
        print("WAITING ROOM NUMBER IN THREAD", threading.current_thread().ident)
        time.sleep(1)
    client = mqtt.Client()
    client.username_pw_set(username="dso_server", password="dso_password")
    client.on_connect = on_connect_1884
    client.on_publish = on_publish
    client.on_message = on_message_1884
    client.connect(MQTT_SERVER, MQTT_SERVER_PORT_2, 60)
    make_subscriptions_1884(client)
    client.loop_start()
    while True:
        raspi_connected_sem.acquire()
        if raspi_connected is False:
            sensors = copy.deepcopy(randomize_sensors())
            raspi_connected_sem.release()
            time.sleep(10)
            air_conditioner_command_sem.acquire()
            if air_mode_change == 1:
                commands_buffer_sem.acquire()
                commands_buffer.append([AIR_CONDITIONER_COMMAND_TOPIC, json.dumps({"mode": air_conditioner_mode})])
                commands_buffer_sem.release()
                air_mode_change = 0
            air_conditioner_command_sem.release()

            indoor_light_level_command_sem.acquire()
            if indoor_light_level_change == 1:
                commands_buffer_sem.acquire()
                commands_buffer.append([INDOOR_LIGHT_LEVEL_TOPIC, json.dumps({"level": indoor_light_level})])
                commands_buffer_sem.release()
                indoor_light_level_change = 0
            indoor_light_level_command_sem.release()

            indoor_light_active_command_sem.acquire()
            if indoor_light_active_change == 1:
                commands_buffer_sem.acquire()
                commands_buffer.append([INDOOR_LIGHT_ACTIVE_TOPIC, json.dumps({"active": indoor_light_active})])
                commands_buffer_sem.release()
                indoor_light_active_change = 0
            indoor_light_active_command_sem.release()

            outside_light_level_command_sem.acquire()
            if outside_light_level_change == 1:
                commands_buffer_sem.acquire()
                commands_buffer.append([OUTSIDE_LIGHT_LEVEL_TOPIC, json.dumps({"level": outside_light_level})])
                commands_buffer_sem.release()
                outside_light_level_change = 0
            outside_light_level_command_sem.release()

            outside_light_active_command_sem.acquire()
            if outside_light_active_change == 1:
                commands_buffer_sem.acquire()
                commands_buffer.append([OUTSIDE_LIGHT_ACTIVE_TOPIC, json.dumps({"active": outside_light_active})])
                commands_buffer_sem.release()
                outside_light_active_change = 0
            outside_light_active_command_sem.release()

            blind_level_command_sem.acquire()
            if blind_level_change == 1:
                commands_buffer_sem.acquire()
                commands_buffer.append([BLIND_LEVEL_TOPIC, json.dumps({"level": blind_level})])
                commands_buffer_sem.release()
                blind_level_change = 0
            blind_level_command_sem.release()

            blind_active_command_sem.acquire()
            if blind_active_change == 1:
                commands_buffer_sem.acquire()
                commands_buffer.append([BLIND_ACTIVE_TOPIC, json.dumps({"active": blind_active})])
                commands_buffer_sem.release()
                blind_active_change = 0
            blind_active_command_sem.release()
        else:
            raspi_connected_sem.release()
            air_conditioner_command_sem.acquire()
            if air_mode_change == 1:
                client.publish(AIR_CONDITIONER_COMMAND_TOPIC, payload=json.dumps({"mode": air_conditioner_mode}), qos=0, retain=False)
                print("PUBLISHED ", air_conditioner_mode, "IN ", AIR_CONDITIONER_COMMAND_TOPIC)
                air_mode_change = 0
            air_conditioner_command_sem.release()

            indoor_light_level_command_sem.acquire()
            if indoor_light_level_change == 1:
                client.publish(INDOOR_LIGHT_LEVEL_TOPIC, payload=json.dumps({"level": indoor_light_level}), qos=0, retain=False)
                print("PUBLISHED ", indoor_light_level, "IN ", INDOOR_LIGHT_LEVEL_TOPIC)
                indoor_light_level_change = 0
            indoor_light_level_command_sem.release()

            indoor_light_active_command_sem.acquire()
            if indoor_light_active_change == 1:
                client.publish(INDOOR_LIGHT_ACTIVE_TOPIC, payload=json.dumps({"active": indoor_light_active}), qos=0, retain=False)
                print("PUBLISHED ", indoor_light_active, "IN ", INDOOR_LIGHT_ACTIVE_TOPIC)
                indoor_light_active_change = 0
            indoor_light_active_command_sem.release()

            outside_light_level_command_sem.acquire()
            if outside_light_level_change == 1:
                client.publish(OUTSIDE_LIGHT_LEVEL_TOPIC, payload=json.dumps({"level": outside_light_level}), qos=0, retain=False)
                print("PUBLISHED ", outside_light_level, "IN ", OUTSIDE_LIGHT_LEVEL_TOPIC)
                outside_light_level_change = 0
            outside_light_level_command_sem.release()

            outside_light_active_command_sem.acquire()
            if outside_light_active_change == 1:
                client.publish(OUTSIDE_LIGHT_ACTIVE_TOPIC, payload=json.dumps({"active": outside_light_active}), qos=0, retain=False)
                print("PUBLISHED ", outside_light_active, "IN ", OUTSIDE_LIGHT_ACTIVE_TOPIC)
                outside_light_active_change = 0
            outside_light_active_command_sem.release()

            blind_level_command_sem.acquire()
            if blind_level_change == 1:
                client.publish(BLIND_LEVEL_TOPIC, payload=json.dumps({"level": blind_level}), qos=0, retain=False)
                print("PUBLISHED ", blind_level, "IN ", BLIND_LEVEL_TOPIC)
                blind_level_change = 0
            blind_level_command_sem.release()

            blind_active_command_sem.acquire()
            if blind_active_change == 1:
                client.publish(BLIND_ACTIVE_TOPIC, payload=json.dumps({"active": blind_active}), qos=0, retain=False)
                print("PUBLISHED ", blind_active, "IN ", BLIND_ACTIVE_TOPIC)
                blind_active_change = 0
            blind_active_command_sem.release()
    client.loop_stop()


def make_subscriptions_1884(client):
    global CONFIG_TOPIC, TELEMETRY_TOPIC, INDOOR_LIGHT_TOPIC, OUTSIDE_LIGHT_TOPIC, AIR_CONDITIONER_TOPIC, BLIND_TOPIC, PRESENCE_TOPIC, TEMPERATURE_TOPIC, room_number
    client.subscribe(CONFIG_TOPIC)
    client.subscribe(INDOOR_LIGHT_TOPIC)
    client.subscribe(OUTSIDE_LIGHT_TOPIC)
    client.subscribe(AIR_CONDITIONER_TOPIC)
    client.subscribe(BLIND_TOPIC)
    client.subscribe(PRESENCE_TOPIC)
    client.subscribe(TEMPERATURE_TOPIC)
    client.subscribe(DISCONNECT_TOPIC + "/" + room_number)
    print("Subscribed 1884 to", CONFIG_TOPIC)
    print("Subscribed 1884 to", INDOOR_LIGHT_TOPIC)
    print("Subscribed 1884 to", OUTSIDE_LIGHT_TOPIC)
    print("Subscribed 1884 to", AIR_CONDITIONER_TOPIC)
    print("Subscribed 1884 to", BLIND_TOPIC)
    print("Subscribed 1884 to", PRESENCE_TOPIC)
    print("Subscribed 1884 to", TEMPERATURE_TOPIC)
    print("Subscribed 1884 to", DISCONNECT_TOPIC + "/" + room_number)



def on_message_1884(client, userdata, msg):
    global sensors, raspi_connected, room_number, old_sensors
    global indoor_light_sem, outside_light_sem, blind_sem, air_conditioner_sem, presence_sem, temperature_sem, raspi_connected_sem
    print("Mensaje recibido en MQTT-2 1884 ", msg.topic, "con mensaje ", msg.payload.decode())
    topic = msg.topic.split('/')
    if topic[-1] == "config":
        print("Id recibido: ", msg.payload.decode())
        raspi_connected_sem.acquire()
        raspi_connected = True
        send_buffered_commands(client)
        sensors = copy.deepcopy(old_sensors)
        raspi_connected_sem.release()

    elif "disconnect" in topic:
        raspi_connected_sem.acquire()
        raspi_connected = False
        raspi_connected_sem.release()
        print("Se ha desconectado el dispositivo fisico")

    elif "telemetry" in topic:
        payload = json.loads(msg.payload.decode())
        if topic[-1] == "indoor-light":
            indoor_light_sem.acquire()
            if sensors["indoor_light"] != payload:
                sensors["indoor_light"] = payload
            indoor_light_sem.release()

        if topic[-1] == "outside-light":
            outside_light_sem.acquire()
            if sensors["outside_light"] != payload:
                sensors["outside_light"] = payload
            outside_light_sem.release()

        if topic[-1] == "blind":
            blind_sem.acquire()
            if sensors["blind"] != payload:
                sensors["blind"] = payload
            blind_sem.release()

        if topic[-1] == "air-conditioner":
            air_conditioner_sem.acquire()
            if sensors["air_conditioner"] != payload:
                sensors["air_conditioner"] = payload
            air_conditioner_sem.release()

        if topic[-1] == "presence":
            presence_sem.acquire()
            if sensors["presence"] != payload:
                sensors["presence"] = payload
            presence_sem.release()

        if topic[-1] == "temperature":
            temperature_sem.acquire()
            if sensors["temperature"] != payload:
                sensors["temperature"] = payload
            temperature_sem.release()



def on_disconnect(client, userdata, rc):
    global flag
    flag = -1


def on_publish(client, userdata, result):
    pass


def send_buffered_commands(client):
    global commands_buffer, commands_buffer_sem
    time.sleep(5)
    commands_buffer_sem.acquire()
    for command in commands_buffer:
        client.publish(command[0], payload=command[1], qos=0, retain=False)
    commands_buffer.clear()
    commands_buffer_sem.release()

if __name__ == "__main__":

    t1 = threading.Thread(target=connect_mqtt_1883)
    t2 = threading.Thread(target=connect_mqtt_1884)

    t1.setDaemon(True)
    t2.setDaemon(True)

    t1.start()
    t2.start()

    t1.join()
    t2.join()
