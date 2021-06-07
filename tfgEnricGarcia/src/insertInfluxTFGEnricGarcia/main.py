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
    "end_device_ids": str,
    "correlation_ids": List[str],
    "received_at": str,
    "uplink_msg": str
}




def init_main() -> Tuple:
    """
    Initialitation of the main program.
    """
    try:
        file_mqtt = open('../../config/mqtt_local.yml', 'r')
        file_db_conf = open('../../config/influx.yml', 'r')

        Lmqtt = yaml.safe_load(file_mqtt)
        Lmqtt["TOPICS"] = [
            "v3/tfg-enric-garcia@ttn/devices/ttn-node-dev-1/up",
            "v3/tfg-enric-garcia@ttn/devices/heltec-esp32-lora/up"
        ]
       
        iDBconf = yaml.safe_load(file_db_conf)
        result = (Lmqtt, iDBconf)
    except:
        result = ({}, {})
    finally:
        file_mqtt.close()
        file_db_conf.close()

    return result


def msg_parse(msg: Json_Msg_t) -> Parsed_Msg_t:
    """
    It collects the data from the MQTT message payload and it parses the payload to a python dictionary (Parsed_Msg_t) 
    """
    parsed_msg = json.loads(msg)

    end_device_info = parsed_msg["end_device_ids"] 
    uplink_msg = parsed_msg["uplink_message"]
    received_at = parsed_msg["received_at"][:-4]
    result = {
        "end_device_info": end_device_info,
        "uplink_message": uplink_msg,
        "received_at": received_at
    }
    return result


def influx_point(device_id: str, timestamp: int, measurement: str, value: float) -> dict: 

    result = {
        "measurement": measurement,
        "tags": {
            "sensor_id": id
        },
        "time": timestamp,
        "fields": {
            "value": value
        }
    }
    return result

def get_msg_info(msg_dict: Parsed_Msg_t) -> Tuple:
    """
    Returned value (tuple):
    (device_id: int, sens_data: dict, timestamp: time)

    sens_data format: 
    {
    "sens_type_0": float,
    "sens_type_1": float,
    ...
    }
    """
    device_id = msg_dict["end_device_info"]["device_id"]
    sens_data = msg_dict["uplink_message"]["decoded_payload"]
    timestamp = time.mktime(time.strptime(msg_dict["received_at"], "%Y-%m-%dT%H:%M:%S.%f"))

    if (device_id == "ttn-node-dev-1"):
        sens_data.pop("event")

    return (device_id, sens_data, timestamp)

def influx_points(msg_dict: Parsed_Msg_t) -> list:
    """
    Appends the points from every sensor in a device's message.
    """
    try:
        if "decoded_payload" not in msg_dict["uplink_message"].keys():
            raise(ValueError)

        device_id, sens_data, timestamp = get_msg_info(msg_dict)

        result = []
        for sensor, value in sens_data.items():
            result.append(influx_point(device_id + sensor, int(timestamp), sensor, float(value)))
    except ValueError:
        print(colored("EXCEPTION - Not information in the message", "red"))
        result = []
    return result


def influx_insert(iDBconf: dict, msg_dict: Parsed_Msg_t):
    """
    Insert the data from device's sensors into DDBB
    """
    try:
        client = InfluxDBClient(iDBconf["HOST"],
                                iDBconf["PORT"],
                                iDBconf["USR"],
                                iDBconf["PWD"], 
                                iDBconf["DB"])

        client.write_points(influx_points(msg_dict))
    finally:
        client.close()


def main():

    Lmqtt, iDBconf = init_main()
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

            msg_dict = msg_parse(MQTT_message.payload)
            #print(msg_dict)
            print(colored("Message received from device: \n\t" + msg_dict["end_device_info"]["device_id"], "green"))
            influx_insert(iDBconf, msg_dict)
    except KeyboardInterrupt:
        result = 0
    #except Exception as exc:
    #    print(exc)
    #    result = 1
    return result
    
    
if __name__ == "__main__":

    status = main()
    sys.exit(status)
    
