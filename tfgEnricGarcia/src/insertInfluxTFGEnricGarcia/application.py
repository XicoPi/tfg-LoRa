import yaml
#import json
from device import Device

class TTNApplication(object):
    """
    El callback de parsejat de missatge, ha de tenir el mateix nom que el device_id
    device_id = "myDevice"
    callbackLib.py:
    def myDevice(msg: str) -> dict:
    ...
    """
    def __init__(self, configPath="../../config/", applicationConfigFilename="mqtt_local.yml"):
        self._Lmqtt = {}
        self._Devices = []
        
        try:
            
            ttnApplicationConfigFile = open(configPath + applicationConfigFilename, "r")
            self._Lmqtt = yaml.safe_load(ttnApplicationConfigFile)
            self._Lmqtt["DEVICE_IDS"] = self._Lmqtt["DEVICE_IDS"]
            for device_id, callbackLibPath in self._Lmqtt["DEVICE_IDS"].items():
                print(device_id, callbackLibPath)
                self._Devices.append(Device(device_id, configPath + callbackLibPath))
        finally:
            ttnApplicationConfigFile.close()
        
        
        
    
    def __iter__(self):
        Device = self._Devices[0]
        i = 0
        while (i < len(self._Devices)):
            yield self._Devices[i]
            i += 1

    def getDevices(self):
        return self._Devices
    
    def addAllDevicesTopic(self, topicType: str):
        """
        mqtt ttn Topic constructor
        Adds the topic to all application devices
        """
        topic = "v3/" + self._Lmqtt["USER"] + "@ttn/devices/"
        for DeviceObj in self:
            DeviceObj.addTopic(topic + DeviceObj.getId() + "/" + topicType)

    def getDevicesTopics(self):
        result = []
        for DeviceObj in self:
            result += DeviceObj.getTopics()
        return result
    def getMqttConfig(self) -> dict:
        return self._Lmqtt
