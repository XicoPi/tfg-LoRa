#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import time
import json
import yaml
import sys
import paho.mqtt.subscribe as mqtt_subscribe

from influxdb import InfluxDBClient
from termcolor import cprint, colored
from typing import *


Json_Msg_t = str
Parsed_Msg_t = {
    "end_device_ids": db_utils.device_t,
    "correlation_ids": List[str],
    "received_at": str,
    "uplink_msg": db_utils.uplink_msg_t
}



def msg_parse(msg: Json_Msg_t) -> Parsed_Msg_t:
    """
    It collects the data from the MQTT message payload and it parses the payload to a python dictionary (Parsed_Msg_t) 
    """
    parsed_msg = json.loads(msg)

    end_device_info: db_utils.device_t = parsed_msg["end_device_ids"] 
    uplink_msg: db_utils.uplink_msg_t = parsed_msg["uplink_message"]
    result = {
        "end_device_info": end_device_info,
        "uplink_message": uplink_msg
    }
    return result

def init_main() -> Tuple:
    try:
        file_mqtt = open('../../config/mqtt_local.yml', 'r')
        file_db_conf = open('../../config/influx.yml', 'r')

        Lmqtt = yaml.load(file_mqtt)
        Lmqtt["TOPICS"] = [
            "v3/tfg-enric-garcia@ttn/devices/ttn-node-dev-1/up",
            "v3/tfg-enric-garcia@ttn/devices/heltec-esp32-lora/up"
        ]
       
        iDBconf = yaml.load(file_db_conf)
        result = (Lmqtt, iDBconf)
    except:
        result = ({}, {})
    finally:
        file_db_conf.close()
        file_db_conf.close()

    return result


def influx_point(id, t, measurement, value): 
    value = float(value)
    return {
        "measurement": measurement,
        "tags": {
            "sensor_id": id
        },
        "time": int(t * 1000000000),
        "fields": {
            "value": value
        }
    }


def influx_points(msg_dict: Parsed_Msg_t) -> list:
    try:
        device_id = msg_dict["end_device_ids"]["device_id"]

        if "decoded_payload" not in msg_dict["uplink_message"].keys():
            raise(ValueError)

        sens_data = msg_dict["uplink_message"].pop("decoded_payload")
        sens_data.pop("event")

        string_datetime = msg_dict["received_at"][:-4]
        timestamp = time.strptime(string_datetime, "%Y-%m-%dT%H:%M:%S.%f")
        # Crea la llista de punts a inserir
        result = []
        for sensor, value in sens_data.items():
            result.append(influx_point(device_id + sensor, timestamp, sensor, value))

    except ValueError:
        print(colored("EXCEPTION - Crating influx points", "red"))
        result = []
    return result

def influx_insert(iDBconf: dict, msg_dict: Parsed_Msg_t):
    try:
        client = InfluxDBClient(iDBconf["HOST"],
                                iDBconf["PORT"],
                                iDBconf["USR"],
                                iDBconf["PWD"], 
                                iDBconf["DB"])
        # print("Insert -> " + colored("id: {} ".format(d['id']), 'yellow') + "msg: " + str(d))
        client.write_points(influx_points(msg_dict))
    finally:
        client.close()
        

def on_message(client, userdata, msg):
    d = json.loads(msg.payload.decode("utf-8"))
    # print(colored("R -> topic: {}, msg: {}".format( msg.topic, d), "cyan"))
    lmsg.append(d)

def on_connect(client, userdata, flags, rc):
    print(colored("Connected with result code " + str(rc), "green"))
    client.subscribe(Lmqtt['TOPIC'], qos=Lmqtt['QOS'])

def on_disconnect(client, userdata, rc):
    print(colored("Disconnected with result code "+str(rc), "red"))

def main():

    Lmqtt, iDBconf = init_main()
    #client = mqtt.Client(client_id="mqttInfluxDB" + Lmqtt['SESSION_ID'],
    #                     clean_session=not Lmqtt['SESSION_PERSISTENT'])
    #client.on_message = on_message
    #client.on_connect = on_connect
    #client.on_disconnect = on_disconnect
    #client.username_pw_set(Lmqtt['USER'], Lmqtt['PWD'])
    #client.connect(Lmqtt['HOST'], Lmqtt['PORT'], 60)
    #client.loop_start()
    mqtt_auth_credentials = {
        "username": Lmqtt["USER"],
        "password": Lmqtt["PWD"]
    }
    try:
        while True:
            MQTT_message = mqtt_subscribe.simple(
                topics=Lmqtt["TOPICS"],
                auth=mqtt_auth_credentials,
                hostname=Lmqtt["HOST"],
                port=Lmqtt["PORT"])
            msg_dict = msg_parse(MQTT_message)
            influx_insert(MQTT_message)
    except KeyboardInterrupt:
        result = 0
    except:
        result = 1
    return result
    
    
if __name__ == "__main__":

    lmsg = []
    
    # Inicia el client mqtt.
    status = main()
    sys.exit(status)
    
