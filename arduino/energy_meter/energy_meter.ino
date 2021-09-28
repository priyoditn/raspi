#include <LiquidCrystal.h>  

int Read_Voltage  = A1;
int Read_Current  = A0;
const int rs = 2, en = 4, d4 = 9, d5 = 10, d6 = 11, d7 = 12; 
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);
float Voltage = 0.0;
float Current = 0.0;
float Power = 0.0;

void setup() 
{
  lcd.begin(16, 2); 
  Serial.begin(9600);

  lcd.print("     Nimesh + Arun    "); 
  lcd.setCursor(0, 1);
  lcd.print("    = Winners!   "); 

  delay(2000);
  lcd.clear();

}

void loop() 
{
 
 Voltage = analogRead(Read_Voltage);
 Current = analogRead(Read_Current);

 Voltage = Voltage * (5.0/1023.0) * 6.46;
 Current = Current * (5.0/1023.0) * 0.239;

 Serial.println(Voltage);
 Serial.println(Current);

 Power = Voltage * Current;

 Serial.println(Power);


 lcd.setCursor(0, 0);
 lcd.print("V="); lcd.print(Voltage); 
 lcd.print(" "); 
 lcd.print("I=");lcd.print(Current); 
 lcd.setCursor(0, 1);
 lcd.print("P="); lcd.print(Power); 
 delay(1000);
}
