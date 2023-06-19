#ifndef STEPPER_CONTROL_H
#define STEPPER_CONTROL_H
#include <AccelStepper.h>
#include"smooth_value.h"

class Stepper_control {
  public:
    Stepper_control();
    Smoothing hSpeedSmoothing;
    float hSpeedSmooth;
    Smoothing vSpeedSmoothing;
    float vSpeedSmooth;
    
    const int TIMEOUT_DURATION = 1000*60*2; // 2min, en while løkke brytes dersom den har kjørt i mer enn denne verdien

    AccelStepper vertikal;
    AccelStepper horisontal;
    int potPin;
    int enablePin;
    int microsteps;

    int maxUp = 650;
    int maxDown = -350;  //hvor langt motoren kan gå før det er fare for at kameraet treffer rammen
    int maxSpeed = 200;   // steg/sekund
    int vAcceleration = 25; // steg/sekund^2
    int hAcceleration = 50;

    void setupSteppers(int horisontalDirPin, int horisontalStepPin, int vertikalDirPin, int vertikalStepPin, int in_enablePin, int in_microsteps, int in_potPin);
    void homeSteppers();
    void steppersDriveToPoint(float float_hAngle, float float_vAngle);
    void steppersDriveSpeed(float horisontalSpeed, float vertikalSpeed);
    void steppersDriveToPosition(float horisontalAlignPos, float vertikalAlignPos);
    void disableSteppers();
    void enableSteppers();
    bool steppersRunning();
    int getRemainingHsteps();
    int getCurrentHsteps();
    int getMaxUp();
    int getMaxDown();
};

#endif