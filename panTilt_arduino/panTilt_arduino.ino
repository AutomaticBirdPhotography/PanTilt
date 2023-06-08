/*
      Notes:
              0,100
               |
               |
      -100,0---0,0---100,0
               |
               |
              0,-100

      Python: pan_tilt_v4.py -på stativet
      Verdiene som skal komme ved joy er mellom -100 og 100
*/
#include "servo_control.h"
#include "stepper_control.h"
Stepper_control stepper;
int i = 1;
bool allowAlign = true;

const int vertikalDirPin = 7;
const int vertikalStepPin = 6;
const int enablePin = 2;

const int horisontalDirPin = 8;
const int horisontalStepPin = 9;

const int fokusEnablePin = 12;

const int panServoPin = 11;
const int tiltServoPin = 10;

const int potPin = A7;
int hSpeed = 0;
int vSpeed = 0;
float panSpeed = 0;
float tiltSpeed = 0;
int maxUp = stepper.getMaxUp();     //verdiene settes i stepper_control.cpp
int maxDown = stepper.getMaxDown();

String innkommende;
bool fokusEnable = false;
bool enable = false;

void setup() {
  digitalWrite(fokusEnablePin, HIGH);

  setupServos(panServoPin, tiltServoPin);
  stepper.setupSteppers(horisontalDirPin, horisontalStepPin, vertikalDirPin, vertikalStepPin, enablePin, potPin);

  Serial.begin(115200);
  Serial.setTimeout(15);

}

void loop() {
  if (Serial.available() > 0) {
    innkommende = Serial.readStringUntil('\n');
  }
  if (innkommende[0] == 's') stepper.disableSteppers();

  if (innkommende[0] != 'h' && innkommende[0] != 'a' && innkommende[0] != 'p' && innkommende[0] != 'e' && innkommende[0] != 'd') {  //må ikke være noen av disse verdiene
    float joy_verdier[4];                                                                                                           //må definere at det er 4 verdier (mellom kommaer) vi har
    decodeDataString(4, innkommende, joy_verdier);

    panSpeed = joy_verdier[2];
    tiltSpeed = joy_verdier[3];  //index 3, så 4. verdien

    //-----------------------------------
    vSpeed = joy_verdier[1] * -1;
    hSpeed = joy_verdier[0];
  }

  if (innkommende[0] == 'h' && enable) {  //skal ikke bli sann om motorene ikke er på
    if (i == 1) {
      stepper.homeSteppers();
      homeServos();
      i = 2;
      innkommende = "0,0,0,0";
      vSpeed = 0;
      hSpeed = 0;
    }
  } else if (innkommende[0] == 'a' && enable) {
    if (allowAlign) {
      //nema 17 : 200 steps pr rev. *16(microstepping) *1,8(36/20(tannhjul))=5760 -> 1deg = 16steps (5760/360)
      float horisontalAlignPos = stepper.getCurrentHsteps()+(getOldPosPan() - (90 + getPan_offset())) * 15;  //blir som move() isteden for moveTo() når det er med currentHsteps (15 fordi kjører litt for langt)
      float vertikalAlignPos = (getOldPosTilt() - (90 + getTilt_offset())) * 16;
      if (vertikalAlignPos > maxUp) {
        vertikalAlignPos = maxUp;
      } else if (vertikalAlignPos < maxDown) {
        vertikalAlignPos = maxDown;
      }
      
      int totalMove = round(horisontalAlignPos);
      float gjenMove = totalMove;
      bool steppersStillRunning = true;
      float initOldPosPan = getOldPosPan();
      int initHsteps = stepper.getCurrentHsteps();
      while (steppersStillRunning) {
        gjenMove = totalMove+stepper.getCurrentHsteps();
        float alignPanServo = map(gjenMove, 0, totalMove, 90 + getPan_offset(), 180-initOldPosPan);
        positionMovePanServo(alignPanServo);
        stepper.steppersDriveToPosition(horisontalAlignPos, vertikalAlignPos);
        steppersStillRunning = stepper.steppersRunning();
      }
      allowAlign = false;
      innkommende = "0,0,0,0";
      hSpeed = 0;
      vSpeed = 0;
    }
  } else if (innkommende[0] == 'e') {
    enable = true;
    stepper.enableSteppers();
    innkommende = "0,0,0,0";
  } else if (innkommende[0] == 'd') {
    enable = false;
    stepper.disableSteppers();
    innkommende = "0,0,0,0";
  } else if (innkommende[0] == 'p' && enable) {
    innkommende.remove(0, 1);  //fjerner første bokstav, som er p
    float toPoint_verdier[2];
    decodeDataString(2, innkommende, toPoint_verdier);
    float float_hSteps = toPoint_verdier[0];
    float float_vSteps = toPoint_verdier[1];

    stepper.steppersDriveToPoint(float_hSteps, float_vSteps); //blokkerer fram til den når posisjonen
    innkommende = "0,0,0,0";
  } else {
    joyMoveServos(panSpeed, tiltSpeed);
    if (enable) {
      stepper.steppersDriveSpeed(hSpeed, vSpeed);
      i = 1;
      allowAlign = true;
    }
  }
}

float decodeDataString(int number_of_values, String dataString, float* values) {
  int komma_pos = 0;
  int next_komma_pos = 0;
  for (int i = 0; i < number_of_values; i++) {
    if (i == 0) {
      komma_pos = dataString.indexOf(',');
      values[i] = dataString.substring(0, komma_pos).toFloat();
    } else {
      komma_pos = dataString.indexOf(',', next_komma_pos);
      if (i == number_of_values - 1) {  //hvis det er på siste verdi, leser den bare fra next_komma_pos som var ned neste kommaposisjonen ved forrige iterasjon, altså er dette kommaposisjonen rett før siste verdi
        values[i] = dataString.substring(next_komma_pos).toFloat();
      }
      values[i] = dataString.substring(next_komma_pos, komma_pos).toFloat();
    }
    next_komma_pos = komma_pos + 1;
    if (komma_pos == -1) {
      break;
    }
  }
}