#import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as subscribe
import json

from dataclasses import dataclass
#from typing import TypedDict
#@dataclass


Json_Msg_t = str
Parsed_Msg_t = dict





def on_msg_received(client, userdata, message):
    """
    Callback que s'activa quan arriba un missatge del topic al que s'està subscrit.
    """
    print(message.topic, message.payload)

def msg_parse(msg: Json_Msg_t) -> Parsed_Msg_t:
    """
    """
    parsed_msg = json.loads(msg)
    result = parsed_msg[]
    return result
    
if __name__ == '__main__':

    willInformation = {
        "topic": "v3/tfg-enric-garcia@ttn/devices/heltec-esp32-lora/up",
        "payload": None,
        "qos": None,
        "retain": None
    }
    ttnAuthCredentials = {
        "username": "tfg-enric-garcia",
        "password": "NNSXS.FYZDMZTFHFMNAKD2QRJL5N3CTNXCLOKXJH7EBQA.UYDB63MAB4CTWXSLRCXUM7O6NIEMUDVAPA2IBV6ARFJBIZZW4KCA"
    }
    
    subscribe.callback(callback=on_msg_received,
                       topics="v3/tfg-enric-garcia@ttn/devices/heltec-esp32-lora/up",
                       #will=willInformation,
                       auth=ttnAuthCredentials,
                       hostname="eu1.cloud.thethings.network",
                       port=1883)
    while(True):
        pass
