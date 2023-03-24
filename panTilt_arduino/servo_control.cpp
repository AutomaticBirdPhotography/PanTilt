/*
V 1.0.1
*/

  /*
   * (0,0)----(180,0)
   *  |
   *  |
   * (0,180)---(180,180)
   */
#include <Arduino.h>
#include <Servo.h>
#include "servo_control.h"
Servo panServo;
Servo tiltServo;
int interval = 15;
float pan_offset = 0;   //verdiene er etter de på kartet, negativ er venstre
float tilt_offset = 0;  //negative verdier vil få den til å gå gå mot positive verdier
float OldTiltPos = 90 + tilt_offset;
float OldPanPos = 90 + pan_offset;
int tilyUpLimit = 60;
int tiltDownLimit = 85;
unsigned long previousMillis = 0;
void setupServos(int panServo_pin, int tiltServo_pin) {
  panServo.attach(panServo_pin);
  tiltServo.attach(tiltServo_pin);
  homeServos();
  delay(100);
}

void joyMoveServos(float in_panSpeed, float in_tiltSpeed) {

  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    float panIncreaseValue = -in_panSpeed * interval/1000;
    float tiltIncreaseValue = -in_tiltSpeed * interval/1000;
    
    float newPanPos = OldPanPos + panIncreaseValue;
    newPanPos = constrain(newPanPos, 0, 180);
    panServo.write(newPanPos);
    OldPanPos = newPanPos;

    float newTiltPos = OldTiltPos + tiltIncreaseValue;
    if (newPanPos < 75 || newPanPos > 115){
      newTiltPos = constrain(newTiltPos, tilyUpLimit, tiltDownLimit);  //når der er i ytterkantene i pan, kan den ikke tilte så mye ned
    }
    else{
      newTiltPos = constrain(newTiltPos, tilyUpLimit, 110);
    }
    tiltServo.write(newTiltPos);
    OldTiltPos = newTiltPos;
    previousMillis = currentMillis;
  }
}
void positionMovePanServo(float posPan){
  panServo.write(posPan);
  OldPanPos = panServo.read();  //litt usikker på om denne leser verdien før den har rukket å komme til posisjonen. Kanskje må ha OldPanPos += posPan

}

void homeServos() {
  int x = panServo.read();
  if (x < 90 + pan_offset) {
    for (int i = x; i <= 90 + pan_offset; i++) {
      panServo.write(i);
      delay(50);
    }
  } else if (x > 90 + pan_offset) {
    for (int i = x; i >= 90 + pan_offset; i--) {
      panServo.write(i);
      delay(50);
    }
  }

  //------tilt--
  x = tiltServo.read();
  if (x < 90 + tilt_offset) {
    for (int i = x; i <= 90 + tilt_offset; i++) {
      tiltServo.write(i);
      delay(50);
    }
  } else if (x > 90 + tilt_offset) {
    for (int i = x; i >= 90 + tilt_offset; i--) {
      tiltServo.write(i);
      delay(50);
    }
  }
  OldPanPos = 90 + pan_offset;
  OldTiltPos = 90 + tilt_offset;
}

float getOldPosPan(){return 180-OldPanPos;}
float getOldPosTilt(){return OldTiltPos;}
float getPan_offset(){return pan_offset;}
float getTilt_offset(){return tilt_offset;}