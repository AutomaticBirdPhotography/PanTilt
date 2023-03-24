/*
V 1.0.0
*/

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
    
    unsigned long potVerdi = 0;
    AccelStepper vertikal;
    AccelStepper horisontal;
    int pot;
    int enablePin;
    const int maxUp = 650;
    const int maxDown = -350;  //hvor langt motoren kan gå før det er fare for at kameraet treffer rammen
    const int maxSpeed = 200;

    void setupSteppers(int horisontalDirPin, int horisontalStepPin, int vertikalDirPin, int vertikalStepPin, int in_enablePin, int in_pot);
    void homeSteppers();
    void steppersDriveToPoint(float float_hSteps, float float_vSteps);
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