#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import time, json, yaml
import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
from termcolor import cprint, colored

f = open('../../config/mqtt_ferroviari.yml', 'r')
Lmqtt = yaml.load(f)
f.close()

f = open('../../config/influx_adxl.yml', 'r')
iDBconf = yaml.load(f)
f.close()


def influx_point(id, t, measurement, value): 
    value = float(value)
    return { "measurement": measurement, "tags": {"sensor_id": id}, "time": int(t * 1000000000), "fields": {'value': value}}


def influx_points(d):
    try:
        # Es guarda l'ID
        id = d.pop('id')

        # Es guarda l'instant de temps (En cas que no existeixi desa l'actual)
        if "time" in d.keys():
            t = d.pop('time')
        else:
            t = time.time()

        # Crea la llista de punts a inserir
        l = []
        for k in d.keys():
            l.append(influx_point(id, t, k, d[k]))
        return l

    except:
        print(colored('EXCEPTION - Crating influx points', 'red'))


def influx_insert(d):
    client = InfluxDBClient(iDBconf['HOST'],
                            iDBconf['PORT'],
                            iDBconf['USR'],
                            iDBconf['PWD'], 
                            iDBconf['DB'])
    # print("Insert -> " + colored("id: {} ".format(d['id']), 'yellow') + "msg: " + str(d))
    client.write_points(influx_points(d))
    

def on_message(client, userdata, msg):
    global lmsg
    d = json.loads(msg.payload.decode("utf-8"))
    # print(colored("R -> topic: {}, msg: {}".format( msg.topic, d), "cyan"))
    lmsg.append(d)

def on_connect(client, userdata, flags, rc):
    print(colored("Connected with result code " + str(rc), "green"))
    client.subscribe(Lmqtt['TOPIC'], qos=Lmqtt['QOS'])

def on_disconnect(client, userdata, rc):
    print(colored("Disconnected with result code "+str(rc), "red"))


if __name__ == "__main__":

    lmsg = []

    # Inicia el client mqtt.
    client = mqtt.Client(client_id="mqttInfluxDB" + Lmqtt['SESSION_ID'],
                         clean_session=not Lmqtt['SESSION_PERSISTENT'])
    client.on_message = on_message
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.username_pw_set(Lmqtt['USER'], Lmqtt['PWD'])
    client.connect(Lmqtt['HOST'], Lmqtt['PORT'], 60)
    client.loop_start()

    while True:
        time.sleep(0.4)
        for msg in lmsg:
            influx_insert(lmsg.pop(0))
