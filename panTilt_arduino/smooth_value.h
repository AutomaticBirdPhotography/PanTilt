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
    int getRemainingSteps();
    int MAX_UP;
    int MAX_DOWN;
    float ACCELERATION;
  private:
    float currentValue = 0;
    float currentVelocity = 0;
    unsigned long previousMillis = 0;
    const float INTERVAL = 60;
    float INCREASE_VELOCITY;
    float stoppingDistance;
    int remainingSteps;
};

#endif