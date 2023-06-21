/*
      TODO: gjør slik at vi har konstanten MICROSTEPS, og at stativet skal kjøre identisk hva enn denne er
      Gjør slik at hver stepper og hver servo har sin instans av en klasse og at man kjører panServo.home()
      så har en loop so for hvert intervall oppdaterer med panServo.runIncrement() eller noe.
      
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
#define TIMEOUT_DURATION 60*1000 // 60 sec

Stepper_control stepper;
bool allowHoming = true;
bool allowAlign = true;

const int VERTICAL_DIR_PIN = 7;
const int VERTICAL_STEP_PIN = 6;

const int HORIZONTAL_DIR_PIN = 8;
const int HORIZONTAL_STEP_PIN = 9;

const int ENABLE_PIN = 2;
const int MICROSTEPS = 16;

const int panServoPin = 11;
const int tiltServoPin = 10;

const int POT_PIN = A7;
int hSpeed = 0;
int vSpeed = 0;
float panSpeed = 0;
float tiltSpeed = 0;
int maxUp = stepper.getMaxUp();     //verdiene settes i stepper_control.cpp
int maxDown = stepper.getMaxDown();

String INIT_INCOMING = "000,000,000,000";
String incoming = INIT_INCOMING;
bool enable = false;

void setup() {
  setupServos(panServoPin, tiltServoPin);
  stepper.setupSteppers(HORIZONTAL_DIR_PIN, HORIZONTAL_STEP_PIN, VERTICAL_DIR_PIN, VERTICAL_STEP_PIN, ENABLE_PIN, MICROSTEPS, POT_PIN);

  Serial.begin(115200);
  Serial.setTimeout(15);

}

void loop() {
  if (Serial.available() > 0) {
    incoming = Serial.readStringUntil('\n');
  }
  if (incoming[0] == 's') stepper.disableSteppers();

  if (incoming[0] != 'h' && incoming[0] != 'a' && incoming[0] != 'p' && incoming[0] != 'e' && incoming[0] != 'd') {  //må ikke være noen av disse verdiene
    float joy_verdier[4];                                                                                                           //må definere at det er 4 verdier (mellom kommaer) vi har
    decodeDataString(4, incoming, joy_verdier);

    panSpeed = joy_verdier[2];
    tiltSpeed = joy_verdier[3];  //index 3, så 4. verdien

    //-----------------------------------
    vSpeed = joy_verdier[1] * -1;
    hSpeed = joy_verdier[0];
  }

  if (incoming[0] == 'h' && enable) {  //skal ikke bli sann om motorene ikke er på
    if (allowHoming) {
      stepper.homeSteppers();
      homeServos();
      allowHoming = false;
      incoming = INIT_INCOMING;
      vSpeed = 0;
      hSpeed = 0;
    }
  } else if (incoming[0] == 'a' && enable) {
    if (allowAlign) {
      //nema 17 : 200 steps pr rev. * (MICROSTEPS) *1,8(36/20(tannhjul))= 360 * MICROSTEPS  -> 1deg = (360*MICROSTEPS/360) => 1deg = MICROSTEPS
      float horisontalAlignPos = stepper.getCurrentHsteps()+(getPosPan() - (90 + getPAN_OFFSET())) * MICROSTEPS;  //blir som move() isteden for moveTo() når det er med currentHsteps (15 fordi kjører litt for langt)
      float vertikalAlignPos = (getPosTilt() - (90 + getTILT_OFFSET())) * MICROSTEPS;
      if (vertikalAlignPos > maxUp) {
        vertikalAlignPos = maxUp;
      } else if (vertikalAlignPos < maxDown) {
        vertikalAlignPos = maxDown;
      }
      
      int totalMove = round(horisontalAlignPos);
      float gjenMove = totalMove;
      bool steppersStillRunning = true;
      float initOldPosPan = getPosPan();
      int initHsteps = stepper.getCurrentHsteps();
      unsigned long loopStartedTime = millis();
      while (steppersStillRunning) {
        gjenMove = totalMove+stepper.getCurrentHsteps();
        float alignPanServo = map(gjenMove, 0, totalMove, 90 + getPAN_OFFSET(), 180-initOldPosPan);
        movePanToPosition(alignPanServo);
        stepper.steppersDriveToPosition(horisontalAlignPos, vertikalAlignPos);
        steppersStillRunning = stepper.steppersRunning();
        if (millis() - loopStartedTime >= TIMEOUT_DURATION){
          stepper.disableSteppers();
          break;
        }
      }
      allowAlign = false;
      incoming = INIT_INCOMING;
      hSpeed = 0;
      vSpeed = 0;
    }
  } else if (incoming[0] == 'e') {
    enable = true;
    stepper.enableSteppers();
    incoming = INIT_INCOMING;
  } else if (incoming[0] == 'd') {
    enable = false;
    stepper.disableSteppers();
    incoming = INIT_INCOMING;
  } else if (incoming[0] == 'p' && enable) {
    incoming.remove(0, 1);  //fjerner første bokstav, som er p
    float toPoint_verdier[2];
    decodeDataString(2, incoming, toPoint_verdier);
    float float_hAngle = toPoint_verdier[0];
    float float_vAngle = toPoint_verdier[1];

    stepper.steppersDriveToPoint(float_hAngle, float_vAngle); //blokkerer fram til den når posisjonen
    incoming = INIT_INCOMING;
  } else {
    joyMoveServos(panSpeed, tiltSpeed);
    if (enable) {
      stepper.steppersDriveSpeed(hSpeed, vSpeed);
      allowHoming = true;
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