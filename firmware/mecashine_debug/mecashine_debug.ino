/*
  Shoe polisher (ASPS) - full debug and test firmware for the ESP32.

  What it tests: the I2C bus, the PCF8575, both TB6612 drivers and all three brush motors,
  the three 360-degree servos (belt, lift, jaw), both VL53L0X distance sensors, the 3.5 inch display
  and the START / STOP buttons. It also calibrates the servos using the distance sensors and saves
  the results in flash. The display's touch panel is not connected, so it is not used.

  How to use it:
    1. Open the Serial Monitor at 115200 baud with line ending "Newline".
    2. At power-up it runs a quick check of everything it can test on its own and prints a report.
    3. Type  test  to walk through every test in order. Where it needs your eyes (did the motor turn?)
       it asks: answer y or n in the Serial Monitor, or push START for yes and STOP for no.
    4. Type  help  for every command.

  Safety: any key typed in the Serial Monitor, or the STOP button, stops every motor and servo at once.
  Test the servos with the jaws, carriage and belt free to move: a 360-degree servo keeps turning for
  as long as it gets a pulse away from its stop pulse. Every move has a time limit.

  Libraries: Adafruit PWM Servo Driver, Adafruit VL53L0X, Adafruit GFX.
  The display driver is in ili9488.h in this folder, so TFT_eSPI's settings are not used or changed.
  Board: ESP32 Dev Module (esp32 core 2.x or 3.x).
*/

#include "state.h"

// ---------------------------------------------------------------- setup and loop
void setup() {
  pumpBegin();  // first of all, so the pump cannot run during start-up
  irBegin();
  analogSetPinAttenuation(PIN_KNOB, ADC_11db);  // the knob swings the full 0..3.3 V
  Serial.begin(115200);
  delay(400);
  pwmBegin();  // motor PWM at 0 before anything else
  buttonBegin(btnStart);
  buttonBegin(btnStop);
  Wire.begin(PIN_SDA, PIN_SCL);
  Wire.setClock(100000);
  pcfFound = pcfFind() && pcfWrite(pcfState);  // the PCF8575 powers up with every pin high: put both drivers in standby now
  calLoad();

  Serial.println();
  Serial.println(F("=============================================="));
  Serial.println(F(" Shoe polisher - debug and test firmware"));
  Serial.println(F("=============================================="));

  pcaBegin();
  if (!pcaFound) Serial.println(F("PCA9685 servo driver NOT found at 0x40: the servos cannot move. Check its VCC, GND, SDA, SCL, then type  test 1"));
  tofBegin();
  SPI.begin(PIN_SCK, -1, PIN_MOSI);
  screenBegin();

  for (uint8_t i = 0; i < TEST_COUNT; i++) results[i] = R_NOT_RUN;
  bootCheck();
  help();
  screenIdle(true);
}

void loop() {
  pumpTick();
  sprayTick();
  static char line[64];
  static uint8_t len = 0;

  if (buttonPressed(btnStop)) {
    sprayAuto = false;
    stopAll();
    Serial.println(F("STOP button: everything stopped"));
  }
  if (buttonPressed(btnStart)) {
    if (menuOn) menuRun();
    else Serial.println(F("START button pressed (type  menu  to choose with the knob, or  test  to run the full test)"));
  }
  menuTick();

  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\r') continue;
    if (c == '\n') {
      line[len] = '\0';
      if (len > 0) {
        aborted = false;
        screenHold = false;
        handle(line);
        screenIdle(true);
      }
      len = 0;
    } else if (len < sizeof(line) - 1) line[len++] = c;
  }

  static uint32_t lastDraw = 0, lastFull = 0;
  screenKeepAlive();
  if (millis() - lastFull > 30000) { lastFull = millis(); screenRecover(); }   // reset and redraw it all now and then, in case noise wiped it
  else if (millis() - lastDraw > 400) {
    lastDraw = millis();
    if (!menuOn) screenDashboard(false);       // the menu redraws itself when the knob moves (menuTick)
  }
}
