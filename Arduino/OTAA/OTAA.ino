/*
 * HelTec Automation(TM) LoRaWAN 1.0.2 OTAA example use OTAA, CLASS A
 *
 * Function summary:
 *
 * - use internal RTC(150KHz);
 *
 * - Include stop mode and deep sleep mode;
 *
 * - 15S data send cycle;
 *
 * - Informations output via serial(115200);
 *
 * - Only ESP32 + LoRa series boards can use this library, need a license
 *   to make the code run(check you license here: http://www.heltec.cn/search/);
 *
 * You can change some definition in "Commissioning.h" and "LoRaMac-definitions.h"
 *
 * HelTec AutoMation, Chengdu, China.
 * 成都惠利特自动化科技有限公司
 * https://heltec.org
 * support@heltec.cn
 *
 *this project also release in GitHub:
 *https://github.com/HelTecAutomation/ESP32_LoRaWAN
*/

#include <ESP32_LoRaWAN.h>
#include <string.h>
#include <stdio.h>
#include <math.h>
#include "Arduino.h"
//temperature sensor
#include <OneWire.h>
#include <DallasTemperature.h>
//accelerometer sensor
#include <Adafruit_Sensor.h>
#include <Adafruit_ADXL345_U.h>

#define ACCEL_I2C_ADDR 0x53

/*license for Heltec ESP32 LoRaWan, quary your ChipID relevant license: http://resource.heltec.cn/search */
uint32_t  license[4] = {0x5C42E395,0xA29F3758,0xDB076E0E,0x9E193575};

/* OTAA para*/
uint8_t DevEui[] = { 0x00, 0xDE, 0xAC, 0xB0, 0xC6, 0xAB, 0xB5, 0xD2 };
uint8_t AppEui[] = { 0x70, 0xB3, 0xD5, 0x7E, 0xD0, 0x04, 0x05, 0x82 };
uint8_t AppKey[] = {0xBD, 0x5A, 0x77, 0x91, 0x20, 0x63, 0xC8, 0x31, 0x68, 0x9C, 0x86, 0x5D, 0xE6, 0x46, 0x3B, 0xDC};

/* ABP para*/
uint8_t NwkSKey[] = { 0x15, 0xb1, 0xd0, 0xef, 0xa4, 0x63, 0xdf, 0xbe, 0x3d, 0x11, 0x18, 0x1e, 0x1e, 0xc7, 0xda,0x85 };
uint8_t AppSKey[] = { 0xd7, 0x2c, 0x78, 0x75, 0x8c, 0xdc, 0xca, 0xbf, 0x55, 0xee, 0x4a, 0x77, 0x8d, 0x16, 0xef,0x67 };
uint32_t DevAddr =  ( uint32_t )0x260B897A;

/*LoraWan channelsmask, default channels 0-7*/ 
uint16_t userChannelsMask[6]={ 0x00FF,0x0000,0x0000,0x0000,0x0000,0x0000 };

/*LoraWan Class, Class A and Class C are supported*/
DeviceClass_t  loraWanClass = CLASS_A;

/*the application data transmission duty cycle.  value in [ms].*/
uint32_t appTxDutyCycle = 15000;

/*OTAA or ABP*/
bool overTheAirActivation = true;

/*ADR enable*/
bool loraWanAdr = true;

/* Indicates if the node is sending confirmed or unconfirmed messages */
bool isTxConfirmed = true;

/* Application port */
uint8_t appPort = 20;

/*!
* Number of trials to transmit the frame, if the LoRaMAC layer did not
* receive an acknowledgment. The MAC performs a datarate adaptation,
* according to the LoRaWAN Specification V1.0.2, chapter 18.4, according
* to the following table:
*
* Transmission nb | Data Rate
* ----------------|-----------
* 1 (first)       | DR
* 2               | DR
* 3               | max(DR-1,0)
* 4               | max(DR-1,0)
* 5               | max(DR-2,0)
* 6               | max(DR-2,0)
* 7               | max(DR-3,0)
* 8               | max(DR-3,0)
*
* Note, that if NbTrials is set to 1 or 2, the MAC will not decrease
* the datarate, in case the LoRaMAC layer did not receive an acknowledgment
*/
uint8_t confirmedNbTrials = 800;

/*LoraWan debug level, select in arduino IDE tools.
* None : print basic info.
* Freq : print Tx and Rx freq, DR info.
* Freq && DIO : print Tx and Rx freq, DR, DIO0 interrupt and DIO1 interrupt info.
* Freq && DIO && PW: print Tx and Rx freq, DR, DIO0 interrupt, DIO1 interrupt and MCU deepsleep info.
*/
uint8_t debugLevel = LoRaWAN_DEBUG_LEVEL;

/*LoraWan region, select in arduino IDE tools*/
LoRaMacRegion_t loraWanRegion = ACTIVE_REGION;

// Pin donde se conecta el bus 1-Wire
const int pinDatosDQ = 21;
 
// Instancies a les clases OneWire y DallasTemperature
OneWire oneWireObjeto(pinDatosDQ);
DallasTemperature sensorDS18B20(&oneWireObjeto);
//accelerometre
Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified(21);

static void prepareTxFrame( uint8_t port )
{
  /*
  {
    ax: float,
    ay: float,
    az: float,
    temp: float
  }
  */

  int i;
  uint8_t fifo_buf_length;
  FIFO_regs_values_t sampleWindow[32];
  int32_t averages[3];
  fifo_buf_length = accel.readRegister(ADXL345_REG_FIFO_STATUS) & 0b00111111;
  if (fifo_buf_length >= 32) {
    i = 0;
    while (i < 32) {
      sampleWindow[i] = accel.FIFO_multiByteRead();
      delayMicroseconds(6);
      i++;
    }
    averages[0] = 0;
    averages[1] = 0;
    averages[2] = 0;
    i = 0;
    while (i < 32) {
      averages[0] += sampleWindow[i].x;
      averages[1] += sampleWindow[i].y;
      averages[2] += sampleWindow[i].z;
      i++;  
    }
  }
  
  sensorDS18B20.requestTemperatures();
  uint8_t strData[LORAWAN_APP_DATA_MAX_SIZE];
  //AppDataSize max value is 64

  
  
  sprintf((char *)strData, "%f,", (sqrt(pow(averages[0], 2) / 32)) * ADXL345_MG2G_MULTIPLIER);
  strcpy((char *)appData, (char *)strData);
  
  sprintf((char *)strData, "%f,", (sqrt(pow(averages[1], 2) / 32)) * ADXL345_MG2G_MULTIPLIER);
  strcat((char *)appData, (char *)strData);

  //strcat((char *)appData, "'az': ");
  sprintf((char *)strData, "%f,", (sqrt(pow(averages[2], 2) / 32)) * ADXL345_MG2G_MULTIPLIER);
  strcat((char *)appData, (char *)strData);
  
  //strcat((char *)appData, "'temp': ");
  sprintf((char *)strData, "%f,", sensorDS18B20.getTempCByIndex(0));
  strcat((char *)appData, (char *)strData);

  Serial.println((char *)appData);
  /*appData[0] = 0x00;
  appData[1] = 0x01;
  appData[2] = 0x02;
  appData[3] = 0x03;*/
  appDataSize = strlen((char *)appData);
}

// Add your initialization code here
void setup()
{
  Serial.begin(115200);
  
  while (!Serial);
  SPI.begin(SCK,MISO,MOSI,SS);
  Mcu.init(SS,RST_LoRa,DIO0,DIO1,license);
  deviceState = DEVICE_STATE_INIT;
  if(!accel.begin(ACCEL_I2C_ADDR)) {
    /* There was a problem detecting the ADXL345 ... check your connections */
    Serial.println("  -  Ooops, no ADXL345 detected ... Check your wiring!");
  }
  accel.setRange(ADXL345_RANGE_16_G);
  accel.setDataRate(ADXL345_DATARATE_100_HZ);
  accel.writeRegister(ADXL345_REG_FIFO_CTL, 0b10011111); //FIFO in Stream Mode
  sensorDS18B20.begin();
}

// The loop function is called in an endless loop
void loop()
{
  switch( deviceState )
  {
    case DEVICE_STATE_INIT:
    {
      LoRaWAN.init(loraWanClass,loraWanRegion);
      break;
    }
    case DEVICE_STATE_JOIN:
    {
      LoRaWAN.join();
      break;
    }
    case DEVICE_STATE_SEND:
    {
      
      prepareTxFrame( appPort );
      LoRaWAN.send(loraWanClass);
      deviceState = DEVICE_STATE_CYCLE;
      break;
    }
    case DEVICE_STATE_CYCLE:
    {
      // Schedule next packet transmission
      txDutyCycleTime = appTxDutyCycle + randr( -APP_TX_DUTYCYCLE_RND, APP_TX_DUTYCYCLE_RND );
      LoRaWAN.cycle(txDutyCycleTime);
      deviceState = DEVICE_STATE_SLEEP;
      break;
    }
    case DEVICE_STATE_SLEEP:
    {
      LoRaWAN.sleep(loraWanClass,debugLevel);
      break;
    }
    default:
    {
      deviceState = DEVICE_STATE_INIT;
      break;
    }
  }
}
