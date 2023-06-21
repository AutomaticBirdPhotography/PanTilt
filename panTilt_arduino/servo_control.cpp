  /*
   * (0,0)----(180,0)
   *  |
   *  |
   * (0,180)---(180,180)
   */
#include <Arduino.h>
#include <Servo.h>
#include "servo_control.h"

#define TIMEOUT_DURATION 3*1000 //3 sek | Hvor mye lengere enn estimert kjøretid den skal tillate å ha while-løkka
int INTERVAL = 50;
int TILT_UP_LIMIT = 60;
int TILT_DOWN_LIMIT = 85;
float STANDARD_ANGLESPEED = 30;
Servo panServo;
Servo tiltServo;

float PAN_OFFSET = 0;   //verdiene er etter de på kartet, negativ er venstre
float TILT_OFFSET = 0;  //negative verdier vil få den til å gå gå mot positive verdier

float initPanPos = 90 + PAN_OFFSET;
float panPos = initPanPos;
float initTiltPos = 90 + TILT_OFFSET;
float tiltPos = initTiltPos;

unsigned long previousMillis = 0;
unsigned long loopStartedTime;

struct ServoData {
  Servo servo;
  int targetPosition;
  float currentPosition;
  float angleSpeed;
};

void setupServos(int panServo_pin, int tiltServo_pin) {
  panServo.attach(panServo_pin);
  tiltServo.attach(tiltServo_pin);
  homeServos();
}

int calculateRunTime(float angleSpeed, float currentPosition, int targetPosition){
  angleSpeed = constrain(angleSpeed, 1, 180);
  targetPosition = constrain(targetPosition, 0, 180);
  currentPosition = constrain(currentPosition, 0, 180);
  
  int distanceToGo = abs(targetPosition - currentPosition);
  float estimated_runtime = 1000.0 * distanceToGo / angleSpeed;

  return estimated_runtime;
}

int calculateLongestRunTime(ServoData servoData[], int numServos){
  float longest_estimated_runtime = 0;

  for (int i = 0; i < numServos; i++){
    ServoData& data = servoData[i];
    float estimated_runtime = calculateRunTime(data.angleSpeed, data.currentPosition, data.targetPosition);
    longest_estimated_runtime = max(longest_estimated_runtime, estimated_runtime);
  }

  return longest_estimated_runtime;
}

float getIncreaseValue(float angleSpeed, int elapsedTime){
  float increaseValue = angleSpeed * (elapsedTime / 1000.0);
  return increaseValue;
}

void moveServo(Servo &servo, int targetPosition, float angleSpeed){
  // angleSpeed = antall grader per sekund

  // når man tar servo.write(90) kjører den til posisjon 90 grader, altså absolutt posisjon
  // servo.write(i) der i skal øke med angleSpeed per sekund
  targetPosition = constrain(targetPosition, 0, 180);
  angleSpeed = constrain(angleSpeed, 1, 180); // Farten må være mer enn 0, den klarer ikke kjøre fortere enn 180 grader på ett sekund

  unsigned long previousTime = millis();
  float currentPosition = servo.read();  //må være double eller float ettersom den øker med en increment som ikke er int

  float estimated_runtime = calculateRunTime(angleSpeed, currentPosition, targetPosition);

  loopStartedTime = previousTime;
  while (currentPosition != targetPosition){
    unsigned long currentTime = millis();
    int elapsedTime = currentTime - previousTime;
    if (elapsedTime >= INTERVAL) {
      float increment = angleSpeed * (elapsedTime / 1000.0);

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
      int writePosition = round(currentPosition);
      servo.write(writePosition);
      previousTime = currentTime;
    }

    if (currentTime - loopStartedTime >= estimated_runtime + TIMEOUT_DURATION){   // Denne fungerer ikke riktig! når den bryter ut, og moveServo er i loop begynner while løkka på nytt, og loopStartedTime blir oppdatert
      break;
    }
  }
}

void moveMultipleServos(ServoData servoData[], int numServos){
  unsigned long previousTime = millis();
  loopStartedTime = previousTime;

  bool servosRunning = true;

  float estimated_runtime = calculateLongestRunTime(servoData, numServos);

  while (servosRunning) {
    unsigned long currentTime = millis();
    int elapsedTime = currentTime - previousTime;
    if (elapsedTime >= INTERVAL) {
      servosRunning = false; // vi antar at ingen kjører, denne blir true senere hvis minst en av servoene ikke er ved targetPosition
      for (int i = 0; i < numServos; i++){
        ServoData& data = servoData[i];
        data.targetPosition = constrain(data.targetPosition, 0, 180);
        data.angleSpeed = constrain(data.angleSpeed, 1, 180);

        if (data.currentPosition != data.targetPosition){
          float increment = getIncreaseValue(data.angleSpeed, elapsedTime);
          if (data.currentPosition < data.targetPosition){
            data.currentPosition += increment;           // currentPosition blir nå verdien vi skal kjøre servoen til

            if (data.currentPosition > data.targetPosition){
              data.currentPosition = data.targetPosition;
            }
          } else {
            data.currentPosition -= increment;

            if (data.currentPosition < data.targetPosition){
              data.currentPosition = data.targetPosition;
            }
          }
          int writePosition = round(data.currentPosition);
          data.servo.write(writePosition);
          servosRunning = true; // en servo kjørte så da er servosRunning true
        }
      }

      previousTime = currentTime;
    }
    if (currentTime - loopStartedTime >= estimated_runtime + TIMEOUT_DURATION){
      break;
    }
  }
}

void joyMoveServos(float panAngleSpeed, float tiltAngleSpeed) {
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= INTERVAL) {
    float panIncreaseValue = getIncreaseValue(-panAngleSpeed, INTERVAL);
    panPos += panIncreaseValue;
    panPos = constrain(panPos, 0, 180);
    int writePanPos = int(round(panPos));
    panServo.write(writePanPos);

    float tiltIncreaseValue = getIncreaseValue(-tiltAngleSpeed, INTERVAL);
    tiltPos += tiltIncreaseValue;
    if (panPos < 75 || panPos > 115){
      tiltPos = constrain(tiltPos, TILT_UP_LIMIT, TILT_DOWN_LIMIT);  //når der er i ytterkantene i pan, kan den ikke tilte så mye ned
    }
    else{
      tiltPos = constrain(tiltPos, TILT_UP_LIMIT, 110);
    }
    int writeTiltPos = int(round(tiltPos));
    tiltServo.write(writeTiltPos);
    previousMillis = currentMillis;
  }
}

void movePanToPosition(float absolute_position){
  absolute_position = int(round(absolute_position));
  panServo.write(absolute_position);  //må bruke write da den ikke skal blokkere. Der den brukes økes absolute_position gradvis :=)
  panPos = panServo.read();
}

void homeServos(){
  ServoData servos[] = {
    { panServo, initPanPos, panServo.read(), STANDARD_ANGLESPEED },
    { tiltServo, initTiltPos, tiltServo.read(), STANDARD_ANGLESPEED },
  };

  int numServos = sizeof(servos) / sizeof(servos[0]); //størrelsen på hele arrayet delt på antall parametre i første objekt
  moveMultipleServos(servos, numServos);
}

float getPosPan(){return 180-panPos;}
float getPosTilt(){return tiltPos;}
float getPAN_OFFSET(){return PAN_OFFSET;}
float getTILT_OFFSET(){return TILT_OFFSET;}