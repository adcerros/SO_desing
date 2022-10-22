import json
import os
import threading
from datetime import datetime

from flask import Flask, request
import paho.mqtt.client as mqtt
import requests
from flask_cors import CORS

MQTT_SERVER = os.getenv("MQTT_SERVER_ADDRESS")
MQTT_PORT = int(os.getenv("MQTT_SERVER_PORT"))

TELEMETRY_TOPIC = "hotel/rooms/+/telemetry/"
TEMPERATURE_TOPIC = TELEMETRY_TOPIC + "temperature"
AIR_CONDITIONER_TOPIC = TELEMETRY_TOPIC + "air-conditioner"
BLIND_TOPIC = TELEMETRY_TOPIC + "blind"
INDOOR_LIGHT_TOPIC = TELEMETRY_TOPIC + "indoor-light"
OUTSIDE_LIGHT_TOPIC = TELEMETRY_TOPIC + "outside-light"
PRESENCE_TOPIC = TELEMETRY_TOPIC + "presence"

CONFIG_TOPIC = "hotel/rooms/+/config"
DISCONNECT_TOPIC = "hotel/rooms/disconnect"
ALL_TOPICS = "hotel/rooms/+/telemetry/+"
DATA_INGESTION_API_URL = "http://" + os.getenv("DATA_INGESTION_API_HOST") + ":" + os.getenv("DATA_INGESTION_API_PORT")
API_HOST = os.getenv("API_HOST")
API_PORT = os.getenv("API_PORT")

index_room = 1

saved_rooms = {}
app = Flask(__name__)

def on_connect(client, userdata, flags, rc):
    print("Connected on subscriber with code ", rc)

    client.subscribe(INDOOR_LIGHT_TOPIC)
    print("Subscribed to ", INDOOR_LIGHT_TOPIC)
    client.subscribe(OUTSIDE_LIGHT_TOPIC)
    print("Subscribed to ", OUTSIDE_LIGHT_TOPIC)
    client.subscribe(BLIND_TOPIC)
    print("Subscribed to ", BLIND_TOPIC)
    client.subscribe(AIR_CONDITIONER_TOPIC)
    print("Subscribed to ", AIR_CONDITIONER_TOPIC)
    client.subscribe(PRESENCE_TOPIC)
    print("Subscribed to ", PRESENCE_TOPIC)
    client.subscribe(TEMPERATURE_TOPIC)
    print("Subscribed to ", TEMPERATURE_TOPIC)
    client.subscribe(DISCONNECT_TOPIC)
    print("Subscribed to ", DISCONNECT_TOPIC)
    client.subscribe(ALL_TOPICS)
    client.subscribe(CONFIG_TOPIC)
    print("Subscribed to all")
    print("Subscribed to ", CONFIG_TOPIC)


def on_message(client, userdata, msg):
    global index_room
    topic = msg.topic.split('/')
    print("Mensaje recibido en ", msg.topic, " con mensaje ", str(topic[-1]) + ": ", msg.payload.decode())
    if topic[-1] == "config":
        if saved_rooms.get(msg.payload.decode()) is None:
            room_name = "Room" + str(index_room)
            saved_rooms[msg.payload.decode()] = {"name": room_name, "state": "Connected", "timeStamp": datetime.now().strftime("%H:%M:%S")}
            print("Digital with id ", msg.payload.decode(), " saved as ", room_name)
            client.publish(msg.topic + "/room", payload=room_name, qos=0, retain=True)
            update_room_state(room_name)
            print("Publicado ", room_name, " en TOPIC ", msg.topic)
        else:
            saved_rooms[msg.payload.decode()]["state"] = "Connected"
            saved_rooms[msg.payload.decode()]["timeStamp"] = datetime.now().strftime("%H:%M:%S")
            client.publish(msg.topic + "/room", payload=saved_rooms[msg.payload.decode()]["name"], qos=0, retain=True)
            requests.post(
                DATA_INGESTION_API_URL + "/device_state",
                json={"room": saved_rooms[msg.payload.decode()]["name"], "type": "room-state", "value": 1}
            )

    if topic[-1] == "disconnect":
        try:
            saved_rooms[msg.payload.decode()]["state"] = "Disconnected"
            saved_rooms[msg.payload.decode()]["timeStamp"] = datetime.now().strftime("%H:%M:%S")
            requests.post(
                DATA_INGESTION_API_URL + "/device_state",
                json={"room": saved_rooms[msg.payload.decode()]["name"], "type": "room-state", "value": 0}
            )
        except KeyError:
            pass


    if "telemetry" in topic:
        room_name = topic[2]
        payload = json.loads(msg.payload.decode())
        value = -1

        if topic[-1] == "indoor-light":
            current_indoor_light = payload
            requests.post(
                DATA_INGESTION_API_URL + "/device_state",
                json={"room": room_name, "type": topic[-1], "value": current_indoor_light["level"]}
            )
            requests.post(
                DATA_INGESTION_API_URL + "/device_state",
                json={"room": room_name, "type": "indoor-pw", "value": current_indoor_light["active"]}
            )

        if topic[-1] == "outside-light":
            current_outside_light = payload
            requests.post(
                DATA_INGESTION_API_URL + "/device_state",
                json={"room": room_name, "type": topic[-1], "value": current_outside_light["level"]}
            )
            requests.post(
                DATA_INGESTION_API_URL + "/device_state",
                json={"room": room_name, "type": "outside-pw", "value": current_outside_light["active"]}
            )

        if topic[-1] == "blind":
            current_blind = payload
            requests.post(
                DATA_INGESTION_API_URL + "/device_state",
                json={"room": room_name, "type": topic[-1], "value": current_blind["level"]}
            )
            requests.post(
                DATA_INGESTION_API_URL + "/device_state",
                json={"room": room_name, "type": "blind-pw", "value": current_blind["active"]}
            )

        if topic[-1] == "air-conditioner":
            current_air = payload
            requests.post(
                DATA_INGESTION_API_URL + "/device_state",
                json={"room": room_name, "type": "air-level", "value": current_air["level"]}
            )
            requests.post(
                DATA_INGESTION_API_URL + "/device_state",
                json={"room": room_name, "type": "air-mode", "value": current_air["mode"]}
            )

        if topic[-1] == "presence":
            current_presence = payload
            requests.post(
                DATA_INGESTION_API_URL + "/device_state",
                json={"room": room_name, "type": topic[-1], "value": current_presence["level"]}
            )


        if topic[-1] == "temperature":
            current_temperature = payload
            requests.post(
                DATA_INGESTION_API_URL + "/device_state",
                json={"room": room_name, "type": topic[-1], "value": current_temperature["level"]}
            )




def update_room_state(room_name):
    global index_room
    requests.post(
        DATA_INGESTION_API_URL + "/device_state",
        json={"room": room_name, "type": "room-state", "value": 1}
    )
    index_room += 1


def send_command(params):
    type_dev = params["type"]
    value = params["value"]
    room = params["room"]
    COMMAND_TOPIC = "hotel/rooms/" + room + "/command"
    AIR_COMMAND_TOPIC = COMMAND_TOPIC + "/air-conditioner"
    INDOOR_LIGHT_ACTIVE_TOPIC = COMMAND_TOPIC + "/indoor-light-active"
    INDOOR_LIGHT_LEVEL_TOPIC = COMMAND_TOPIC + "/indoor-light-level"
    OUTSIDE_LIGHT_ACTIVE_TOPIC = COMMAND_TOPIC + "/outside-light-active"
    OUTSIDE_LIGHT_LEVEL_TOPIC = COMMAND_TOPIC + "/outside-light-level"
    BLIND_ACTIVE_TOPIC = COMMAND_TOPIC + "/blind-active"
    BLIND_LEVEL_TOPIC = COMMAND_TOPIC + "/blind-level"

    if type_dev == "air-conditioner-mode":
        client.publish(AIR_COMMAND_TOPIC, payload=value, qos=0, retain=True)
        print("Command message sent throuth "+AIR_COMMAND_TOPIC)
        requests.post(
            DATA_INGESTION_API_URL + "/device_state",
            json={"room": room, "type": "air-cmd", "value": value}
        )
        return {"response":"Message successfully sent"}, 200

    if type_dev == "indoor-light-active":
        client.publish(INDOOR_LIGHT_ACTIVE_TOPIC, payload=value, qos=0, retain=True)
        print("Command message sent throuth "+INDOOR_LIGHT_ACTIVE_TOPIC)
        requests.post(
            DATA_INGESTION_API_URL + "/device_state",
            json={"room": room, "type": "ind-lht-act", "value": value}
        )
        return {"response":"Message successfully sent"}, 200

    if type_dev == "indoor-light-level":
        client.publish(INDOOR_LIGHT_LEVEL_TOPIC, payload=value, qos=0, retain=True)
        print("Command message sent throuth "+INDOOR_LIGHT_LEVEL_TOPIC)
        requests.post(
            DATA_INGESTION_API_URL + "/device_state",
            json={"room": room, "type": "ind-lht-lvl", "value": value}
        )
        return {"response":"Message successfully sent"}, 200

    if type_dev == "outside-light-active":
        client.publish(OUTSIDE_LIGHT_ACTIVE_TOPIC, payload=value, qos=0, retain=True)
        print("Command message sent throuth "+OUTSIDE_LIGHT_ACTIVE_TOPIC)
        requests.post(
            DATA_INGESTION_API_URL + "/device_state",
            json={"room": room, "type": "out-lht-act", "value": value}
        )
        return {"response":"Message successfully sent"}, 200

    if type_dev == "outside-light-level":
        client.publish(OUTSIDE_LIGHT_LEVEL_TOPIC, payload=value, qos=0, retain=True)
        print("Command message sent throuth "+OUTSIDE_LIGHT_LEVEL_TOPIC)
        requests.post(
            DATA_INGESTION_API_URL + "/device_state",
            json={"room": room, "type": "ind-lht-lvl", "value": value}
        )
        return {"response":"Message successfully sent"}, 200

    if type_dev == "blind-active":
        client.publish(BLIND_ACTIVE_TOPIC, payload=value, qos=0, retain=True)
        print("Command message sent throuth "+BLIND_ACTIVE_TOPIC)
        requests.post(
            DATA_INGESTION_API_URL + "/device_state",
            json={"room": room, "type": "blind-act", "value": value}
        )
        return {"response":"Message successfully sent"}, 200

    if type_dev == "blind-level":
        client.publish(BLIND_LEVEL_TOPIC, payload=value, qos=0, retain=True)
        print("Command message sent throuth "+BLIND_LEVEL_TOPIC)
        requests.post(
            DATA_INGESTION_API_URL + "/device_state",
            json={"room": room, "type": "blind-lvl", "value": value}
        )
        return {"response":"Message successfully sent"}, 200
    else:
        return{"response":"Incorrect type param"}, 401


@app.route('/device_state', methods=['POST'])
def device_state():
    if request.method == 'POST':
        params = request.get_json()
        return send_command(params)


def mqtt_listener():
    client.loop_forever()


if __name__ == "__main__":
    #setup mqqt client
    client = mqtt.Client()
    client.username_pw_set(username="dso_server", password="dso_password")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_SERVER, MQTT_PORT, 60)
    t1 = threading.Thread(target=mqtt_listener)
    t1.setDaemon(True)
    t1.start()
    # setup API REST
    CORS(app)
    app.run(host=API_HOST, port=API_PORT, debug=False)
