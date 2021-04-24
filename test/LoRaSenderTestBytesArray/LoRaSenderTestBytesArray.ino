/* 
  Basic test program, send date at the BAND you seted.
  
  by Aaron.Lee from HelTec AutoMation, ChengDu, China
  成都惠利特自动化科技有限公司
  www.heltec.cn
  
  this project also realess in GitHub:
  https://github.com/Heltec-Aaron-Lee/WiFi_Kit_series
*/
#include "heltec.h"
#define BAND    868E6  //you can set band here directly,e.g. 868E6,915E6
#define MAX_N 500

uint8_t test_integer[MAX_N];
uint32_t n = 0, i = 0;
uint8_t bits = 1;
uint32_t max_lim = 255, min_lim = 0;

unsigned long t0 = 0, tf = 0;

void setup() 
{
  
  //WIFI Kit series V1 not support Vext control
  Heltec.begin(true /*DisplayEnable Enable*/, true /*Heltec.LoRa Disable*/, true /*Serial Enable*/, true /*PABOOST Enable*/, BAND /*long BAND*/);
  LoRa.setSpreadingFactor(9);
  LoRa.setSignalBandwidth(125E3);
  //LoRa.setCodingRate4(5);
  LoRa.setTxPower(14,RF_PACONFIG_PASELECT_PABOOST);
  bits = 8;
  max_lim = pow(2,bits);
  min_lim = pow(2,bits - 1);
  
  i = 0;
  n = 0;
  test_integer[0] = random(min_lim,max_lim);
  n++;
}




void loop() 
{

  if (i == 10) {
    i = 0;
    test_integer[n] = random(min_lim,max_lim);
    n++;
  }
  

  // send packet
  t0 = micros();

  LoRa.beginPacket();
 
  
  //LoRa.print(test_integer);
  LoRa.write(test_integer, n);
  LoRa.endPacket();
  tf = micros();


  //random(0, (2**8)-1) per un byte.
  Serial.print(tf - t0);
  Serial.print("\t");
  Serial.println(n);

  
  i++;


  if (n == MAX_N) {
    n = 0;
    Serial.println("End");
    Serial.end();
  }
  //digitalWrite(25, HIGH);   // turn the LED on (HIGH is the voltage level)
  //delay(1000);                       // wait for a second
  //digitalWrite(25, LOW);    // turn the LED off by making the voltage LOW
  //delay(1000);                       // wait for a second
}
