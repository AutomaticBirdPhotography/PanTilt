#include <Arduino.h>
#include <AccelStepper.h>
#define motorInterfaceType 1
#include "smooth_value.h"
#include "stepper_control.h"

Stepper_control::Stepper_control() {
}

void Stepper_control::setupSteppers(int horisontalDirPin, int horisontalStepPin, int vertikalDirPin, int vertikalStepPin, int in_enablePin, int in_pot) {
  vSpeedSmoothing.setup(50, maxUp, maxDown);
  hSpeedSmoothing.setup(25, 5760, -5760);  //verdiene her ser hvor langt side til side den kan gå. 5760 er en hel runde
  pot = in_pot;
  enablePin = in_enablePin;
  vertikal = AccelStepper(motorInterfaceType, vertikalStepPin, vertikalDirPin);
  horisontal = AccelStepper(motorInterfaceType, horisontalStepPin, horisontalDirPin);

  pinMode(pot, INPUT);

  vertikal.setMaxSpeed(maxSpeed);
  vertikal.setCurrentPosition(0);
  vertikal.setAcceleration(50);
  vertikal.setEnablePin(enablePin);
  vertikal.setPinsInverted(false, false, true);  //enable når pinnen er LOW
  horisontal.setMaxSpeed(maxSpeed);
  horisontal.setAcceleration(50);
  horisontal.setCurrentPosition(0);
  horisontal.setEnablePin(enablePin);
  horisontal.setPinsInverted(false, false, true);
  vertikal.enableOutputs();  //vertikal og horisontal har samme enablepin; så ubetydelig hvem som er valgt
  homeSteppers();
  vertikal.disableOutputs();  //motorene skal ikke være på i starten
}
void Stepper_control::homeSteppers() {
  for (int i = 0; i < 100; i++) {
    potVerdi += analogRead(pot);
  }
  int homing = map((potVerdi / 100), 838, 596, 500, -500);  //verdier kalibrert tidligere
  potVerdi = 0;
  int vInitPos = vertikal.currentPosition();
  bool steppersStillRunning = true;

  while (steppersStillRunning) {
    Serial.println(vSpeedSmoothing.getRemainingSteps());
    hSpeedSmooth = hSpeedSmoothing.speedUpdate(0, horisontal.currentPosition());
    horisontal.setSpeed(hSpeedSmooth);
    horisontal.runSpeed();

    vSpeedSmooth = vSpeedSmoothing.positionUpdate(vInitPos+homing, vertikal.currentPosition());
    vertikal.setSpeed(vSpeedSmooth);
    vertikal.runSpeed();
    steppersStillRunning = steppersRunning();
  }
  vertikal.setCurrentPosition(0);
  vSpeedSmoothing.reset();
}

void Stepper_control::steppersDriveToPoint(float float_hSteps, float float_vSteps) {
  float fvSteps = float_vSteps * -16;
  int vSteps = round(fvSteps);
  float fhSteps = float_hSteps * 16;
  int hSteps = round(fhSteps);
  vSteps = vertikal.currentPosition() + vSteps;
  hSteps = horisontal.currentPosition() + hSteps;
  bool steppersStillRunning = true;
  
  while (steppersStillRunning) {
    vSpeedSmooth = vSpeedSmoothing.positionUpdate(vSteps, vertikal.currentPosition());
    hSpeedSmooth = hSpeedSmoothing.positionUpdate(hSteps, horisontal.currentPosition());
    vertikal.setSpeed(vSpeedSmooth);
    horisontal.setSpeed(hSpeedSmooth);
    vertikal.runSpeed();
    horisontal.runSpeed();
    steppersStillRunning = steppersRunning();
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
}

void Stepper_control::enableSteppers() {
  for (int i = 0; i < 500; i++) {
    potVerdi += analogRead(pot);
  }
  int absolutePosition = map((potVerdi / 500), 838, 596, -500, 500);  //verdier kalibrert tidligere
  potVerdi = 0;
  vertikal.setCurrentPosition(absolutePosition);
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