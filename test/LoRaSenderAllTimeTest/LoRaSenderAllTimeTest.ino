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

uint32_t test_integer = 0;
uint32_t n = 0;
uint8_t bits = 1, BW_i = 0, sFactor = 6, txpwr = 0;
uint32_t max_lim = 255, min_lim = 0;



unsigned long t0 = 0, tf = 0;

void setup() {
  
  //WIFI Kit series V1 not support Vext control
  Heltec.begin(true /*DisplayEnable Enable*/, true /*Heltec.LoRa Disable*/, true /*Serial Enable*/, true /*PABOOST Enable*/, BAND /*long BAND*/);
  LoRa.setSpreadingFactor(6);
  LoRa.setSignalBandwidth(7.8E3);
  LoRa.setCodingRate4(5);
  LoRa.setTxPower(14,RF_PACONFIG_PASELECT_PABOOST);
  bits = random(0, 32);
  Serial.println("BIT TEST:");
}

static enum{SEND_LEN_BITS, SPREADING_FACTOR, BANDWIDTH, TX_PWR, END}experiment_state = SEND_LEN_BITS;
static const long bandwidths[9] = {7.8E3, 10.4E3, 15.6E3, 20.8E3, 31.25E3, 41.7E3, 62.5E3, 125E3, 250E3};  
static bool send_flag = true;


void loop()
{

  
  switch (experiment_state) {
    case SEND_LEN_BITS:
    
    bits = random(0, 32);
    max_lim = pow(2,bits);
    min_lim = pow(2, bits - 1);
    if (n == MAX_N) {
      n = 0;
      send_flag = false;
      experiment_state = SPREADING_FACTOR;
      bits = 32;
      max_lim = pow(2,bits);
      min_lim = pow(2, bits - 1);
      Serial.println("Spreading Factor Test:");
    }
    else {
      Serial.print(bits);
    }
    break;

    case SPREADING_FACTOR:
    sFactor = random(6, 12 + 1);
    LoRa.setSpreadingFactor(sFactor);
    if (n == MAX_N) {
      n = 0;
      send_flag = false;
      experiment_state = BANDWIDTH;
      LoRa.setSpreadingFactor(6);
      Serial.println("Bandwidth Test:");
    }
    else {
      Serial.print(sFactor);
    }
    break;

    case BANDWIDTH:
    BW_i = random(0, 9);
    LoRa.setSignalBandwidth(bandwidths[BW_i]);
    if (n == MAX_N) {
      n = 0;
      send_flag = false;
      experiment_state = TX_PWR;
      LoRa.setSignalBandwidth(7.8E3);
      Serial.println("TX POWER Test:");
    }
    else {
      Serial.print(bandwidths[BW_i]);
    }
    break;

    case TX_PWR:
    txpwr = random(0, 15);
    LoRa.setTxPower(txpwr,RF_PACONFIG_PASELECT_PABOOST);
    if (n == MAX_N) {
      n = 0;
      send_flag = false;
      experiment_state = END;
      LoRa.setTxPower(14,RF_PACONFIG_PASELECT_PABOOST);
    }
    else {
      Serial.print(txpwr);
    }
    break;

    case END:
    Serial.println("END");
    Serial.end();
    break;
  }

  test_integer = random(min_lim,max_lim);

  // send packet
  if (send_flag) {
    t0 = micros();

    LoRa.beginPacket();
/*
* LoRa.setTxPower(txPower,RFOUT_pin);
* txPower -- 0 ~ 20
* RFOUT_pin could be RF_PACONFIG_PASELECT_PABOOST or RF_PACONFIG_PASELECT_RFO
*   - RF_PACONFIG_PASELECT_PABOOST -- LoRa single output via PABOOST, maximum output 20dBm
*   - RF_PACONFIG_PASELECT_RFO     -- LoRa single output via RFO_HF / RFO_LF, maximum output 14dBm
*/

    LoRa.print(test_integer);
    LoRa.endPacket();
  
    tf = micros();
    //random(0, (2**8)-1) per un byte.
    Serial.print("\t");
    Serial.println(tf - t0);
    n++;
  }
  send_flag = true;
}
