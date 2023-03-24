/*
V 1.0.0
*/

#ifndef SMOOTH_VALUE_H
#define SMOOTH_VALUE_H

#include <Arduino.h>

class Smoothing {
  public:
    Smoothing();
    void setup(float in_acceleration, int in_maxUp, int in_maxDown);
    void reset();
    float speedUpdate(float targetVelocity, int stepperPosition);
    float positionUpdate(int targetValue, int stepperPosition);
    float calculateStopping(float in_currentVelocity);
    int maxUp;
    int maxDown;
    float acceleration;
  private:
    float currentValue = 0;
    float currentVelocity = 0;
    unsigned long previousMillis = 0;
    const float interval = 60;
    const int microStepping = 16;
    float increaseVelocity;
    float stoppingDistance;  
};

#endif
