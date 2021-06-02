/* 
  Check the new incoming messages, and print via serialin 115200 baud rate.
  
  by Aaron.Lee from HelTec AutoMation, ChengDu, China
  成都惠利特自动化科技有限公司
  www.heltec.cn
  
  this project also realess in GitHub:
  https://github.com/Heltec-Aaron-Lee/WiFi_Kit_series
*/

#include "heltec.h"

#define BAND    868E6  //you can set band here directly,e.g. 868E6,915E6
#define N_SAMPLES 50
void setup() {
    //WIFI Kit series V1 not support Vext control
  Heltec.begin(true /*DisplayEnable Enable*/, true /*Heltec.LoRa Disable*/, true /*Serial Enable*/, true /*PABOOST Enable*/, BAND /*long BAND*/);
  LoRa.setSpreadingFactor(9);
  LoRa.setSignalBandwidth(125E3);
  //LoRa.setCodingRate4(5);
  Serial.println("Setup done");
}

void loop()
{
  // try to parse packets
  uint16_t count;
  count = 0;
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    // received a packet
    Serial.print("Received packet '");
    // read packet
    while (LoRa.available()) {
      Serial.print(LoRa.read());
    }
    // print RSSI of packet
    Serial.print("' with RSSI ");
    Serial.println(LoRa.packetRssi());
  }
}
