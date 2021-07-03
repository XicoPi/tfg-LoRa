import importlib
class Device(object):

    def __init__(self, device_id: str, callbackLibPath: str):
        self._device_id = device_id
        self._topics = []
        print(callbackLibPath)
        self._callbackModule = importlib.machinery.SourceFileLoader(device_id, callbackLibPath).load_module()
        #self._msgCallback = devCallback
    def __str__(self):
        return self.getId()
    def __getitem__(self, index: int) -> str:
        return self._topics[index]
    #def __setitem__(self, index: int, value: str):
    #    self._topics[index] = value
    def __contains__(self, topic: str) -> bool:
        return topic in self._topics
    def __len__(self):
        return len(self._topics)
    
    def executeCallback(self, msg) -> dict:
       return self._callbackModule.devCallback(msg)
    
    def getId(self) -> str:
        return self._device_id
    def setId(self, device_id: str):
        self._device_id = device_id

    def getTopics(self) -> list:
        return self._topics
    def addTopic(self, topic: str):
        self._topics.append(topic)
    #def getMqttTopic(self, event: str) -> str:
        
    
        
