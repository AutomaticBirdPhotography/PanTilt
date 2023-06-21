#include "smooth_value.h"

Smoothing::Smoothing() {
}

void Smoothing::setup(float in_ACCELERATION, int in_MAX_UP, int in_MAX_DOWN) {
  ACCELERATION = in_ACCELERATION;
  MAX_UP = in_MAX_UP;
  MAX_DOWN = in_MAX_DOWN;
  INCREASE_VELOCITY = ACCELERATION * (INTERVAL / 1000.0);
  stoppingDistance = calculateStopping(currentVelocity);
}

float Smoothing::speedUpdate(float targetVelocity, int currentPosition) {
  stoppingDistance = calculateStopping(currentVelocity);
  remainingSteps = stoppingDistance;

  if (currentPosition + stoppingDistance >= MAX_UP) {
    if (targetVelocity > 0) {
      targetVelocity = 0;
    }
  } else if (currentPosition + stoppingDistance <= MAX_DOWN) {
    if (targetVelocity < 0) {
      targetVelocity = 0;
    }
  }

  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= INTERVAL) {
    if (currentVelocity < targetVelocity) {
      currentVelocity += INCREASE_VELOCITY;
      if (currentVelocity > targetVelocity) {
        currentVelocity = targetVelocity;
      }
    } else if (currentVelocity > targetVelocity) {
      currentVelocity -= INCREASE_VELOCITY;
      if (currentVelocity < targetVelocity) {
        currentVelocity = targetVelocity;
      }
    }
    previousMillis = currentMillis;
  }

  return currentVelocity;
}

float Smoothing::positionUpdate(int targetValue, int currentPosition) {
  targetValue = constrain(targetValue, MAX_DOWN, MAX_UP);
  stoppingDistance = calculateStopping(currentVelocity);
  remainingSteps = currentPosition-targetValue;

  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= INTERVAL) {
    if (targetValue > currentPosition) {
      if (currentPosition + stoppingDistance > targetValue) {
        currentVelocity -= INCREASE_VELOCITY;
      }
      else {
        currentVelocity += INCREASE_VELOCITY;
      }
    }

    else if (targetValue < currentPosition) {
      if (currentPosition + stoppingDistance <  targetValue) {
        currentVelocity += INCREASE_VELOCITY;
      }

      else {
        currentVelocity -= INCREASE_VELOCITY;
      }
    }
    else if (targetValue == currentPosition) {
      if (currentVelocity > INCREASE_VELOCITY) {
        currentVelocity -= INCREASE_VELOCITY;
      }
      else if (currentVelocity < -INCREASE_VELOCITY) {
        currentVelocity += INCREASE_VELOCITY;
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
  float Iterations = ceil(abs(in_currentVelocity / INCREASE_VELOCITY)); //interasjoner igjen som trengs for å få inreaseValue til 0
  float Distance = ceil(abs((Iterations + 1) * (in_currentVelocity * (INTERVAL / 1000.0)) / 2.0));
  if (in_currentVelocity < 0) Distance = -Distance;
  return Distance;
}

int Smoothing::getRemainingSteps(){return abs(remainingSteps);}