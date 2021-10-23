#include <BH1750.h>

#include <avr/pgmspace.h>
#include <LCD5110_Graph.h>
#include <Wire.h>

LCD5110 lcd(8,9,10,12,11);
extern unsigned char SmallFont[];


BH1750 lightSensor;
String light;


void setup() {
  lightSensor.begin();
  lcd.InitLCD();
  lcd.setContrast(57);
  lcd.setFont(SmallFont);
  lcd.clrScr();
  lcd.print("Zing!", CENTER, 20);
  lcd.update();
  lcd.invert(true);
  delay(1000);
  lcd.invert(false);
  delay(3000);
  
  lcd.clrScr();
  lcd.print("LUX", CENTER, 10);
  lcd.drawRect(0,0,83,47);
  lcd.drawRect(1,1,82,46);
  
  for(int j = 24; j < 45; j++){
    lcd.drawLine(3,j,81,j);
  }
  
  lcd.update();
}

void loop() {
  lcd.clrScr();
  lcd.invertText(false);
  lcd.invert(true);
  lcd.print("LUX", CENTER, 10);
  lcd.drawRect(0,0,83,47);
  lcd.drawRect(1,1,82,46);
  lcd.update();
  
  for(int j = 24; j < 45; j++){
    lcd.drawLine(3,j,81,j);
  }

  int stringLength=0;
  uint16_t lux = lightSensor.readLightLevel();  // Read the sensor
  light = String(lux); //Convertion to String

  lcd.invertText(true);
  lcd.print(light, CENTER, 31);
  
  lcd.update();
  delay(1000);
}
