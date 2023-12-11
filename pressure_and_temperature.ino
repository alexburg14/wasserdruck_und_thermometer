const float  OffSet = 0.5 ;
float V, P;

#include <Adafruit_MAX31865.h>

// Use software SPI: CS, DI, DO, CLK
Adafruit_MAX31865 thermo = Adafruit_MAX31865(10, 11, 12, 13);
// use hardware SPI, just pass in the CS pin
//Adafruit_MAX31865 thermo = Adafruit_MAX31865(10);

// The value of the Rref resistor. Use 430.0 for PT100 and 4300.0 for PT1000
#define RREF      430.0
// The 'nominal' 0-degrees-C resistance of the sensor
// 100.0 for PT100, 1000.0 for PT1000
#define RNOMINAL  100.0

void setup()
{
  Serial.begin(9600); 
  thermo.begin(MAX31865_3WIRE);       
}
void loop()
{
  //Connect sensor to Analog 0
  V = analogRead(0) * 5.00 / 1024;     //Sensor output voltage
  P = (V - 0.86) * 250; 
  Serial.print("Water pressure = ");
Serial.print(P)      ;; 



uint16_t rtd = thermo.readRTD();
  //Serial.print("RTD value: "); Serial.println(rtd);
  float ratio = rtd;
  ratio /= 32768;
  //Serial.print("Ratio = "); Serial.println(ratio,8);
  //Serial.print("Resistance = "); Serial.println(RREF*ratio,8);
Serial.print("Temperature = ");
Serial.println(thermo.temperature(RNOMINAL, RREF));

  // Check and print any faults
  uint8_t fault = thermo.readFault();
  if (fault) {
    Serial.print("Fault 0x"); Serial.println(fault, HEX);
    if (fault & MAX31865_FAULT_HIGHTHRESH) {
      Serial.println("RTD High Threshold"); 
    }
    if (fault & MAX31865_FAULT_LOWTHRESH) {
      Serial.println("RTD Low Threshold"); 
    }
    if (fault & MAX31865_FAULT_REFINLOW) {
      Serial.println("REFIN- > 0.85 x Bias"); 
    }
    if (fault & MAX31865_FAULT_REFINHIGH) {
      Serial.println("REFIN- < 0.85 x Bias - FORCE- open"); 
    }
    if (fault & MAX31865_FAULT_RTDINLOW) {
      Serial.println("RTDIN- < 0.85 x Bias - FORCE- open"); 
    }
    if (fault & MAX31865_FAULT_OVUV) {
      Serial.println("Under/Over voltage"); 
    }
    thermo.clearFault();
  }
;
}