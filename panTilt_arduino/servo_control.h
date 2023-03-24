/*
V 1.0.1
*/

#ifndef SERVO_CONTROL_H
#define SERVO_CONTROL_H

void setupServos(int panServo_pin, int tiltServo_pin);
void joyMoveServos(float in_panSpeed, float in_tiltSpeed);
void positionMovePanServo(float posPan);
void homeServos();
float getOldPosPan();
float getOldPosTilt();
float getPan_offset();
float getTilt_offset();

#endif