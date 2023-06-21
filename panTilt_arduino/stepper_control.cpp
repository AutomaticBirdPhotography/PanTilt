#include <Arduino.h>
#include <AccelStepper.h>
#define motorInterfaceType 1
#include "smooth_value.h"
#include "stepper_control.h"

Stepper_control::Stepper_control() {
}

int getPotentiometerValue(int pin) {
  unsigned long potValue = 0;
  for (int i = 0; i < 500; i++){
    potValue += analogRead(pin);
  }
  return potValue / 500;
}

int getAbsolutePosition(int potPin){
  float potValue = getPotentiometerValue(potPin);
  int absolutePosition = map(potValue, 838, 596, -500, 500);  //verdier kalibrert ved "calibrate_homing_arduino.ino"
  return absolutePosition;
}

void Stepper_control::setupSteppers(int horisontalDirPin, int horisontalStepPin, int vertikalDirPin, int vertikalStepPin, int in_enablePin, int in_microsteps, int in_potPin) {
  potPin = in_potPin;
  enablePin = in_enablePin;
  microsteps = in_microsteps;

  //maxUp = (maxUp/16)*microsteps;      //verdiene er satt til 16 microsteps, derfor deles på 16 først
  //maxDown = (maxDown/16)*microsteps;  //hvor langt motoren kan gå før det er fare for at kameraet treffer rammen
  //maxSpeed = (maxSpeed/16)*microsteps;
  //vAcceleration = (vAcceleration/16)*microsteps;
  //hAcceleration = (hAcceleration/16)*microsteps;

  
  vSpeedSmoothing.setup(vAcceleration, maxUp, maxDown);
  hSpeedSmoothing.setup(hAcceleration, 360*microsteps, -360*microsteps);  //verdiene her ser hvor langt side til side den kan gå. 360 er en hel runde ettersom det en runde på nema 17 er 200, og vi har beltenedgiring på 1.8
  
  vertikal = AccelStepper(motorInterfaceType, vertikalStepPin, vertikalDirPin);
  horisontal = AccelStepper(motorInterfaceType, horisontalStepPin, horisontalDirPin);

  pinMode(potPin, INPUT);

  vertikal.setMaxSpeed(maxSpeed);
  vertikal.setCurrentPosition(0);
  vertikal.setAcceleration(500);  //verdiene her har ingen ting å si, de settes i vSpeedSmoothing
  vertikal.setEnablePin(enablePin);
  vertikal.setPinsInverted(false, false, true);  //enable når pinnen er LOW
  horisontal.setMaxSpeed(maxSpeed);
  horisontal.setAcceleration(500);
  horisontal.setCurrentPosition(0);
  horisontal.setEnablePin(enablePin);
  horisontal.setPinsInverted(false, false, true);
  vertikal.enableOutputs();  //vertikal og horisontal har samme enablepin; så ubetydelig hvem som er valgt
  homeSteppers();
  vertikal.disableOutputs();  //motorene skal ikke være på i starten
}
void Stepper_control::homeSteppers() {
  int currentAbsolutePosition = getAbsolutePosition(potPin);

  int vInitPos = vertikal.currentPosition();
  bool steppersStillRunning = true;

  unsigned long loopStartedTime = millis();
  while (steppersStillRunning) {
    hSpeedSmooth = hSpeedSmoothing.speedUpdate(0, horisontal.currentPosition());
    horisontal.setSpeed(hSpeedSmooth);
    horisontal.runSpeed();

    vSpeedSmooth = vSpeedSmoothing.positionUpdate(vInitPos+currentAbsolutePosition, vertikal.currentPosition());
    vertikal.setSpeed(vSpeedSmooth);
    vertikal.runSpeed();
    steppersStillRunning = steppersRunning();
    if (millis() - loopStartedTime > TIMEOUT_DURATION) {
      // Stop the motors
      disableSteppers();
      break; // exit the loop
    }
  }
  vertikal.setCurrentPosition(0);
  vSpeedSmoothing.reset();
}

void Stepper_control::steppersDriveToPoint(float float_hAngle, float float_vAngle) {
  //nema 17 : 200 steps pr rev. * (microsteps) *1,8(36/20(tannhjul))= 360 * microsteps  -> 1deg = (360*microsteps/360) => 1deg = microsteps
  float float_vSteps = float_vAngle * -microsteps;
  int vSteps = round(float_vSteps);
  float float_hSteps = float_hAngle * microsteps;
  int hSteps = round(float_hSteps);
  vSteps = vertikal.currentPosition() + vSteps;
  hSteps = horisontal.currentPosition() + hSteps;
  bool steppersStillRunning = true;
  
  unsigned long loopStartedTime = millis();
  while (steppersStillRunning) {
    vSpeedSmooth = vSpeedSmoothing.positionUpdate(vSteps, vertikal.currentPosition());
    hSpeedSmooth = hSpeedSmoothing.positionUpdate(hSteps, horisontal.currentPosition());
    vertikal.setSpeed(vSpeedSmooth);
    horisontal.setSpeed(hSpeedSmooth);
    vertikal.runSpeed();
    horisontal.runSpeed();
    steppersStillRunning = steppersRunning();
    if (millis() - loopStartedTime > TIMEOUT_DURATION) {
      // Stop the motors
      disableSteppers();
      break; // exit the loop
    }
  }
}

void Stepper_control::steppersDriveSpeed(float horisontalSpeed, float vertikalSpeed) {
  vSpeedSmooth = vSpeedSmoothing.speedUpdate(vertikalSpeed, vertikal.currentPosition());
  vertikal.setSpeed(vSpeedSmooth);
  vertikal.runSpeed();
  //------------------------------

  hSpeedSmooth = hSpeedSmoothing.speedUpdate(horisontalSpeed, horisontal.currentPosition());
  horisontal.setSpeed(hSpeedSmooth);
  horisontal.runSpeed();
}

void Stepper_control::steppersDriveToPosition(float in_horisontalAlignPos, float in_vertikalAlignPos) {
  hSpeedSmooth = hSpeedSmoothing.positionUpdate(in_horisontalAlignPos, horisontal.currentPosition());
  horisontal.setSpeed(hSpeedSmooth);
  horisontal.runSpeed();
  vSpeedSmooth = vSpeedSmoothing.positionUpdate(in_vertikalAlignPos, vertikal.currentPosition());
  vertikal.setSpeed(vSpeedSmooth);
  vertikal.runSpeed();
}

void Stepper_control::disableSteppers() {
  vertikal.disableOutputs();
  vSpeedSmoothing.reset();
  hSpeedSmoothing.reset();
  vertikal.setSpeed(0);
  horisontal.setSpeed(0);
  vertikal.runSpeed();
  horisontal.runSpeed();
}

void Stepper_control::enableSteppers() {
  int currentAbsolutePosition = getAbsolutePosition(potPin);

  vertikal.setCurrentPosition(currentAbsolutePosition);
  vertikal.enableOutputs();
}

bool Stepper_control::steppersRunning() {
  if ((hSpeedSmoothing.getRemainingSteps() == 0 && vSpeedSmoothing.getRemainingSteps() == 0) || ((hSpeedSmooth == 0 && hSpeedSmoothing.getRemainingSteps() < 10) && (vSpeedSmooth == 0 && vSpeedSmoothing.getRemainingSteps() < 10))) return false;
  else return true;
}

int Stepper_control::getRemainingHsteps() {
  return horisontal.distanceToGo();
}

int Stepper_control::getCurrentHsteps() {
  return horisontal.currentPosition();
}

int Stepper_control::getMaxUp() {
  return maxUp;
}

int Stepper_control::getMaxDown() {
  return maxDown;
}