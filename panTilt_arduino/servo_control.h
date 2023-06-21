#ifndef SERVO_CONTROL_H
#define SERVO_CONTROL_H

void setupServos(int panServo_pin, int tiltServo_pin);
void joyMoveServos(float panAngleSpeed, float tiltAngleSpeed);
void movePanToPosition(float absolute_position);
void homeServos();
float getPosPan();
float getPosTilt();
float getPAN_OFFSET();
float getTILT_OFFSET();

#endif