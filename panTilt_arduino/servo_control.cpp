  /*
   * (0,0)----(180,0)
   *  |
   *  |
   * (0,180)---(180,180)
   */
#include <Arduino.h>
#include <Servo.h>
#include "servo_control.h"
#define TIMEOUT_DURATION 30*1000 // 30 sec
Servo panServo;
Servo tiltServo;
int interval = 15;
float pan_offset = 0;   //verdiene er etter de på kartet, negativ er venstre
float tilt_offset = 0;  //negative verdier vil få den til å gå gå mot positive verdier
float OldTiltPos = 90 + tilt_offset;
float OldPanPos = 90 + pan_offset;
int tiltUpLimit = 60;
int tiltDownLimit = 85;
unsigned long previousMillis = 0;
unsigned long loopStartedTime;

void setupServos(int panServo_pin, int tiltServo_pin) {
  panServo.attach(panServo_pin);
  tiltServo.attach(tiltServo_pin);
  homeServos();
  delay(100);
}

void moveServo(Servo &servo, int currentPosition, int targetPosition){
  if (currentPosition < targetPosition) {
    for (int i = currentPosition; i <= targetPosition; i++) {
      servo.write(i);
      delay(50);
    }
  } else if (currentPosition > targetPosition) {
    for (int i = currentPosition; i >= targetPosition; i--) {
      servo.write(i);
      delay(50);
    }
  }
}

void moveServo2(Servo &servo, int targetPosition, int angleSpeed){
  // angleSpeed = antall grader per sekund

  // når man tar servo.write(90) kjører den til posisjon 90 grader, altså absolutt posisjon
  // servo.write(i) der i skal øke med angleSpeed per sekund
  targetPosition = constrain(targetPosition, 0, 180);
  angleSpeed = constrain(angleSpeed, 1, 180); // Farten må være mer enn 0, den klarer ikke kjøre fortere enn 180 grader på ett sekund

  unsigned long previousTime = millis();
  int currentPosition = servo.read();

  loopStartedTime = previousTime;
  while (currentPosition != targetPosition){
    unsigned long currentTime = millis();
    unsigned long elapsedTime = currentTime - previousTime;

    if (elapsedTime >= interval) {
      int increment = angleSpeed * (elapsedTime / 1000);

      if (currentPosition < targetPosition){
        currentPosition += increment;           // currentPosition blir nå verdien vi skal kjøre servoen til
        if (currentPosition > targetPosition){
          currentPosition = targetPosition;
        }
      } else {
        currentPosition -= increment;
        if (currentPosition < targetPosition){
          currentPosition = targetPosition;
        }
      }

      servo.write(currentPosition);
      previousTime = currentTime;
    }

    // Break out of the loop if elapsed time exceeds a threshold (e.g., 10 seconds)
    if (currentTime - loopStartedTime >= TIMEOUT_DURATION){
      break;
    }
  }
}

void joyMoveServos(float in_panSpeed, float in_tiltSpeed) {
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    float panIncreaseValue = -in_panSpeed * (interval / 1000);
    float newPanPos = OldPanPos + panIncreaseValue;
    newPanPos = constrain(newPanPos, 0, 180);
    panServo.write(newPanPos);
    OldPanPos = newPanPos;

    float tiltIncreaseValue = -in_tiltSpeed * (interval / 1000);
    float newTiltPos = OldTiltPos + tiltIncreaseValue;
    if (newPanPos < 75 || newPanPos > 115){
      newTiltPos = constrain(newTiltPos, tiltUpLimit, tiltDownLimit);  //når der er i ytterkantene i pan, kan den ikke tilte så mye ned
    }
    else{
      newTiltPos = constrain(newTiltPos, tiltUpLimit, 110);
    }
    tiltServo.write(newTiltPos);
    OldTiltPos = newTiltPos;
    previousMillis = currentMillis;
  }
}
void positionMovePanServo(float posPan){  // burde endre navn til moveToPosition() eller noe
  panServo.write(posPan);
  OldPanPos = panServo.read();  //litt usikker på om denne leser verdien før den har rukket å komme til posisjonen. Kanskje må ha OldPanPos = posPan

}

void homeServos() {
  int currentPosition = panServo.read();
  int targetPosition = 90 + pan_offset;
  moveServo(panServo, currentPosition, targetPosition);
  OldPanPos = targetPosition;

  //------tilt--
  currentPosition = tiltServo.read();
  targetPosition = 90 + tilt_offset;
  moveServo(tiltServo, currentPosition, targetPosition);
  OldTiltPos = targetPosition;
}

float getOldPosPan(){return 180-OldPanPos;}
float getOldPosTilt(){return OldTiltPos;}
float getPan_offset(){return pan_offset;}
float getTilt_offset(){return tilt_offset;}