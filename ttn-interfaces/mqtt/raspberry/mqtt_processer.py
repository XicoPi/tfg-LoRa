#import paho.mqtt.client as mqtt
import sys
import paho.mqtt.subscribe as subscribe
import json
import db_utils
import credential_manager

from typing import *

#from dataclasses import dataclass
#@dataclass


Json_Msg_t = str
Parsed_Msg_t = dict

 

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



def msg_processing(json_message: Json_Msg_t, database_obj: Type[db_utils.TTN_database]):
    """
    Function that processes the message and incert it to the database.
    """
    #print(json_message)
    msg_dict = msg_parse(json_message)
    
    database_obj.insert_app(msg_dict["end_device_info"]["application_ids"]["application_id"])
    database_obj.insert_device(msg_dict["end_device_info"])
    database_obj.insert_uplink_msg(
        msg_dict["uplink_message"],
        msg_dict["end_device_info"]["device_id"])

    
    print("A message has been received from:")
    print("\t TTN Application: " + msg_dict["end_device_info"]["application_ids"]["application_id"])
    print("\t device: " + msg_dict["end_device_info"]["device_id"])
    print("")
    #print(msg_dict)


def main():
    mqttTopics = ["v3/tfg-enric-garcia@ttn/devices/ttn-node-dev-1/up", "v3/tfg-enric-garcia@ttn/devices/heltec-esp32-lora/up"]

    cred_manager = credential_manager.Credentials_Manager("../credentials.txt", reset=False)
    
    database_obj = db_utils.TTN_database(host=cred_manager.db_auth["host"],
                                         user=cred_manager.db_auth["username"],
                                         password=cred_manager.db_auth["password"],
                                         database=cred_manager.db_auth["database"])    
    result = 0
    try:
        while (True):
            MQTT_message = subscribe.simple(
                topics=mqttTopics,
                auth=cred_manager.ttn_auth,
                hostname="eu1.cloud.thethings.network",
                port=1883)

            msg_processing(MQTT_message.payload, database_obj)
    except KeyboardInterrupt:
        result = 0
    return result


if __name__ == '__main__':

    main()
    sys.exit(0)



    
