#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import socket
import requests
import time
import json
import yaml
import sys
import paho.mqtt.subscribe as mqtt_subscribe

from influxdb import InfluxDBClient
from termcolor import cprint, colored
from typing import *
from curses import ascii
from application import *
from device import *
Json_Msg_t = str
Parsed_Msg_t = {
    "end_device_ids": str,
    "correlation_ids": List[str],
    "received_at": str,
    "uplink_msg": str
}


ttnApplication = TTNApplication()

def init_main() -> Tuple:
    """
    Initialitation of the main program.
    """
    try:
        file_db_conf = open('../../config/influx.yml', 'r')
        iDBconf = yaml.safe_load(file_db_conf)
    except:
        print("error")
        iDBconf = {}
    finally:
        #file_mqtt.close()
        file_db_conf.close()
        
    ttnApplication.addAllDevicesTopic("up")
    #print(ttnApplication.getDevices())
    result = iDBconf
    return result


def msg_parse(msg: Json_Msg_t) -> Parsed_Msg_t:
    """
    It collects the data from the MQTT message payload and it parses the payload to a python dictionary (Parsed_Msg_t) 
    """
    parsed_msg = json.loads(msg)

    end_device_info = parsed_msg["end_device_ids"] 
    uplink_msg = parsed_msg["uplink_message"]
    received_at = time.time() #time.mktime(time.strptime(parsed_msg["received_at"][:-4], "%Y-%m-%dT%H:%M:%S.%f"))
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
            "device_id": device_id
        },
        "time": timestamp * 1000000000,
        "fields": {
            "value": value
        }
    }

    return result

def get_lora_params(msg_dict: dict) -> dict:

    lora_data = msg_dict["uplink_message"]["settings"]["data_rate"]["lora"]
    msg_dict["uplink_message"]["settings"].pop("data_rate")
    lora_data.update(msg_dict["uplink_message"]["settings"])
    lora_data.pop("timestamp"); lora_data.pop("time"); lora_data.pop("coding_rate")

    rx_metadata = msg_dict["uplink_message"]["rx_metadata"][0]
    rx_metadata.pop("gateway_ids"); rx_metadata.pop("location"); rx_metadata.pop("uplink_token"); rx_metadata.pop("time"); rx_metadata.pop("timestamp")
    lora_data.update(rx_metadata)
    return lora_data

def get_msg_info(msg_dict: Parsed_Msg_t) -> Tuple:
    """
    Returned value (tuple):
    (device_id: int, sens_data: dict, timestamp: time)
    """
    
    device_id = msg_dict["end_device_info"]["device_id"]
    sens_data = msg_dict["uplink_message"]["decoded_payload"]
    timestamp = msg_dict["received_at"]
    print(sens_data, device_id)
    for deviceObj in ttnApplication:
        print(deviceObj.getId())
        if (deviceObj.getId() == device_id):
            sens_data = deviceObj.executeCallback(sens_data)
            break;

    #LoRa Params register
    result = {}
    result["data_sensors"] = sens_data
    result["lora_com"] = get_lora_params(msg_dict)
    
    return (device_id, result, timestamp)

def influx_points(msg_dict: Parsed_Msg_t) -> list:
    """
    Appends the points from every sensor in a device's message.
    """
    result = []
    try:
        if "decoded_payload" not in msg_dict["uplink_message"].keys():
            raise(ValueError)

        device_id, info, timestamp = get_msg_info(msg_dict)
        print(info)
        result = []
        #Uplink data sensors
        for sensor, value in info["data_sensors"].items():
            result.append(influx_point(device_id, int(timestamp), sensor, float(value)))

        for lora_communication_param, value in info["lora_com"].items():
            result.append(influx_point(device_id, int(timestamp), lora_communication_param, float(value)))
    except ValueError:
        print(colored("EXCEPTION - Not information in the message", "red"))
        result = []
    return result


def influx_insert(iDBconf: dict, msg_dict: dict):
    """
    Insert the data from device's sensors into DDBB
    """
    result = 0
    try:
        client = InfluxDBClient(iDBconf["HOST"],
                                iDBconf["PORT"],
                                iDBconf["USR"],
                                iDBconf["PWD"], 
                                iDBconf["DB"])

        client.write_points(influx_points(msg_dict))
    except requests.exceptions.ConnectionError:
        result = -1
    finally:
        client.close()
    return result


def main():

    iDBconf = init_main()
    mqtt_auth_credentials = {
        "username": ttnApplication.getMqttConfig()["USER"],
        "password": ttnApplication.getMqttConfig()["PWD"]
    }

    try:
        while True:
            try:
                MQTT_message = mqtt_subscribe.simple(
                    topics=ttnApplication.getDevicesTopics(),
                    auth=mqtt_auth_credentials,
                    hostname=ttnApplication.getMqttConfig()["HOST"],
                    port=ttnApplication.getMqttConfig()["PORT"]
                )
            except socket.timeout:
                continue
            except requests.exceptions.ConnectionError:
                result = 1
                break

            msg_dict = msg_parse(MQTT_message.payload)
            #print(msg_dict)
            print(colored("Message received from device: \n\t" + msg_dict["end_device_info"]["device_id"], "green"))
            if (influx_insert(iDBconf, msg_dict) != 0):
                result = 1
                break
    except KeyboardInterrupt:
        result = 0

    return result
    
    
if __name__ == "__main__":

    status = main()
    while (status == 1):
        status = main()
    sys.exit(status)
    
