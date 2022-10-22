from datetime import datetime
import os
import sys
import mysql
import mysql.connector

def connect_database ():
    mydb = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    return mydb

def insert_device_state(params):
    mydb = connect_database()
    with mydb.cursor() as mycursor:
        if params["type"] == "room-state":
            sql = "INSERT INTO connections (room, type, value, date) VALUES (%s, %s, %s, %s)"
        elif params["type"] == "blind-lvl" or params["type"] == "blind-act" or params["type"] == "ind-lht-lvl" or params["type"] == "ind-lht-act" or params["type"] == "out-lht-lvl" or params["type"] == "out-lht-act" or params["type"] == "air-cmd":
            sql = "INSERT INTO commands (room, type, value, date) VALUES (%s, %s, %s, %s)"
        else:
            sql = "INSERT INTO device_state (room, type, value, date) VALUES (%s, %s, %s, %s)"
        print(sql, file=sys.stderr)
        values = (
            params["room"],
            params["type"],
            params["value"],
            datetime.now()
        )
        mycursor.execute(sql, values)
        mydb.commit()
        mydb.close()
        return mycursor
