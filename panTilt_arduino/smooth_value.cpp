#include "smooth_value.h"

Smoothing::Smoothing() {
}

void Smoothing::setup(float in_acceleration, int in_maxUp, int in_maxDown) {
  acceleration = in_acceleration;
  maxUp = in_maxUp;
  maxDown = in_maxDown;
  increaseVelocity = acceleration * interval / 1000;
  stoppingDistance = calculateStopping(currentVelocity);
}

float Smoothing::speedUpdate(float targetVelocity, int stepperPosition) {
  stoppingDistance = calculateStopping(currentVelocity);
  if (stepperPosition + stoppingDistance >= maxUp) {
    if (targetVelocity > 0) targetVelocity = 0;
  }
  else if (stepperPosition + stoppingDistance <= maxDown) {
    if (targetVelocity < 0) targetVelocity = 0;
  }

  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    if (currentVelocity < targetVelocity) {
      currentVelocity += increaseVelocity;
      if (currentVelocity > targetVelocity) currentVelocity = targetVelocity;
    }

    else if (currentVelocity > targetVelocity) {
      currentVelocity -= increaseVelocity;
      if (currentVelocity < targetVelocity) currentVelocity = targetVelocity;
    }
    previousMillis = currentMillis;
  }
  return currentVelocity;
}

float Smoothing::positionUpdate(int targetValue, int stepperPosition) {
  if (targetValue > maxUp) targetValue = maxUp;
  else if (targetValue < maxDown) targetValue = maxDown;
  stoppingDistance = calculateStopping(currentVelocity);

  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    if (targetValue > stepperPosition) {
      if (stepperPosition + stoppingDistance > targetValue) {
        currentVelocity -= increaseVelocity;
      }
      else {
        currentVelocity += increaseVelocity;
      }
    }

    else if (targetValue < stepperPosition) {
      if (stepperPosition + stoppingDistance <  targetValue) {
        currentVelocity += increaseVelocity;
      }

      else {
        currentVelocity -= increaseVelocity;
      }
    }
    else if (targetValue == stepperPosition) {
      if (currentVelocity > increaseVelocity) {
        currentVelocity -= increaseVelocity;
      }
      else if (currentVelocity < -increaseVelocity) {
        currentVelocity += increaseVelocity;
      }
      else currentVelocity = 0;
    }
    previousMillis = currentMillis;
  }
  return currentVelocity;
}

void Smoothing::reset() {
  currentVelocity = 0;
}

float Smoothing::calculateStopping(float in_currentVelocity) {
  float Iterations = ceil(abs(in_currentVelocity / increaseVelocity)); //interasjoner igjen som trengs for å få inreaseValue til 0
  float Distance = ceil(abs((Iterations + 1) * (in_currentVelocity*interval/1000) / 2));
  if (in_currentVelocity < 0) Distance = -Distance;
  return Distance;
}
