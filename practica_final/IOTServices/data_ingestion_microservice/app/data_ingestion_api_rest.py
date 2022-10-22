import json
from flask import Flask, request
from flask_cors import CORS
from data_ingestion import insert_device_state
import os
import mysql
import mysql.connector

app = Flask(__name__)
CORS(app)


def connect_database ():
    mydb = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
    )
    return mydb


@app.route('/device_state', methods=['GET','POST'])
def device_state():
    if request.method == 'POST':
        params = request.get_json()
        if len(params) != 3:
            return {"response" : "Incorrect parameters"}, 401
        mycursor = insert_device_state(params)
        return {"response" : f"{mycursor.rowcount} records inserted. "}, 200
    if request.method == 'GET':
        mydb = connect_database()
        r = []
        with mydb.cursor() as mycursor:
            mycursor.execute("SELECT * FROM device_state ORDER BY date ASC")
            result = mycursor.fetchall()
        with mydb.cursor() as mySecondCursor:
            mySecondCursor.execute("SELECT * FROM connections ORDER BY date ASC")
            secondResult = mySecondCursor.fetchall()
            result = result + secondResult
            for id, room, type, value, date in result:
                r.append({
                    "room": room,
                    "type": type,
                    "value": value,
                    "date": str(date)
                })
            mydb.commit()
            mydb.close()
        return json.dumps(r, sort_keys=True), 200


HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
app.run(host=HOST, port=PORT, debug=False)