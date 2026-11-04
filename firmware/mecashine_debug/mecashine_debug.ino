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

#include <Wire.h>
#include <SPI.h>
#include <Preferences.h>
#include <Adafruit_PWMServoDriver.h>
#include <Adafruit_VL53L0X.h>
#include "config.h"
#include "ili9488.h"

// functions with default arguments, declared once here
int askYesNo(const char *question, uint32_t timeoutMs = 60000);
void text(int16_t x, int16_t y, const String &s, uint16_t col, uint8_t size = 2, uint16_t bg = 0xFFFF);

// ---------------------------------------------------------------- devices
Adafruit_PWMServoDriver pca(PCA_ADDR);
Adafruit_VL53L0X tofSide, tofTop;
// ranging mode of each sensor, [0] top and [1] side. Measured 2026-10-22/23: the top reads the belt equally well in every
// mode (sd ~2.7 mm). The side needs long range: at full open, even with white paper on the reflector, default mode gets
// "signal fail" 50 of 50, while long range reads 50 of 50 with sd ~5.6 mm. Home values must be measured in this mode.
Adafruit_VL53L0X::VL53L0X_Sense_config_t tofMode[2] = { Adafruit_VL53L0X::VL53L0X_SENSE_LONG_RANGE, Adafruit_VL53L0X::VL53L0X_SENSE_LONG_RANGE };
uint8_t tofLastStatus[2] = { 0, 0 };  // range status of each sensor's last reading
ILI9488 tft(PIN_TFT_CS, PIN_TFT_DC, PIN_TFT_RST);
Preferences prefs;

// ---------------------------------------------------------------- state
uint8_t pcfAddr = 0x20;
bool pcfFound = false, pcaFound = false, sideFound = false, topFound = false, tftOk = false;
uint16_t pcfState = 0xFF00;  // P00-P07 low (drivers in standby), P10-P17 high (spare inputs)
Calib cal;
bool sprayAuto = false;  // debug: the pump follows the spray IR (spray on / spray off)
bool aborted = false;  // set when a key or STOP interrupts a running test
bool menuOn = true;    // the idle screen shows the knob menu (menu) or the debug dashboard (dash); see menu.ino

ToggleButton btnStart = { PIN_START, HIGH, HIGH, 0 };
ToggleButton btnStop = { PIN_STOP, HIGH, HIGH, 0 };

// results of the guided test, in order
const char *const TEST_NAME[] = {
  "I2C bus",
  "PCF8575 pins",
  "Buttons",
  "Side sensor",
  "Top sensor",
  "Side sees",
  "Top sees",
  "Display",
  "Side brush L",
  "Side brush R",
  "Top roller",
  "Jaw servo",
  "Lift servo",
  "Belt servo",
  "Pump relay",
};
constexpr uint8_t TEST_COUNT = sizeof(TEST_NAME) / sizeof(TEST_NAME[0]);
Result results[TEST_COUNT];
String resultNote[TEST_COUNT];

// display colours
const uint16_t C_BG = ILI9488::rgb(11, 15, 20), C_PANEL = ILI9488::rgb(24, 33, 43), C_TEXT = ILI9488::rgb(232, 238, 244),
               C_DIM = ILI9488::rgb(120, 136, 150), C_OK = ILI9488::rgb(61, 220, 132), C_BAD = ILI9488::rgb(240, 80, 70),
               C_WARN = ILI9488::rgb(255, 176, 32), C_INFO = ILI9488::rgb(56, 198, 244);
String screenMsg = "Type  help  in the Serial Monitor";
uint16_t screenMsgColor = 0;
bool screenHold = false;         // the cycle screen stays up after a run until the next command

// ---------------------------------------------------------------- stopping and waiting
void stopAll() {
  pumpSet(false);
  for (uint8_t m = 0; m < MOTOR_COUNT; m++) pwmWrite(m, 0);
  pcfState = 0xFF00;
  if (pcfFound) pcfWrite(pcfState);
  servosOff();
}

// True if the user asked to stop: any key in the Serial Monitor, or the STOP button.
bool stopRequested() {
  pumpTick();  // the pump's safety time-out runs wherever the firmware is waiting or moving
  if (Serial.available()) {
    while (Serial.available()) Serial.read();
    return true;
  }
  if (buttonPressed(btnStop)) return true;
  return false;
}

// Waits ms milliseconds. Returns false, with everything stopped, if the user interrupts.
bool waitOrAbort(uint32_t ms) {
  uint32_t t0 = millis();
  while (millis() - t0 < ms) {
    if (stopRequested()) {
      stopAll();
      aborted = true;
      Serial.println(F("  >> stopped by the user"));
      return false;
    }
    delay(2);
  }
  return true;
}

// Asks a yes / no question. Answer y or n in the Serial Monitor, or push START for yes and STOP for no.
// Returns 1 for yes, 0 for no, -1 if nobody answered in time.
int askYesNo(const char *question, uint32_t timeoutMs) {
  Serial.printf("  ? %s  [y/n, or START = yes, STOP = no]\n", question);
  screenAsk(question);
  while (Serial.available()) Serial.read();
  uint32_t t0 = millis();
  while (millis() - t0 < timeoutMs) {
    if (Serial.available()) {
      char c = tolower(Serial.read());
      if (c == 'y' || c == 'n') {
        // the rest of the typed line (the Enter) is still arriving: drop it, or the next step reads it as "a key was pressed, stop"
        delay(30);
        while (Serial.available()) Serial.read();
        screenAskDone();
        return c == 'y' ? 1 : 0;
      }
    }
    if (buttonPressed(btnStart)) {
      Serial.println(F("    (START: yes)"));
      screenAskDone();
      return 1;
    }
    if (buttonPressed(btnStop)) {
      Serial.println(F("    (STOP: no)"));
      screenAskDone();
      return 0;
    }
    delay(10);
  }
  Serial.println(F("    no answer"));
  screenAskDone();
  return -1;
}

// ---------------------------------------------------------------- calibration storage
// The belt has two settings: normal (polishing) and fast (measuring and backing up). The active one lives in cal.beltMoveUs,
// cal.beltRevUs and cal.beltMmPerS, so every belt command works on whichever is active; the other waits in beltOther.
// The fast one is saved under its own key, so adding it did not change the Calib layout or wipe the saved calibration.
BeltSet beltOther = {300, 300, 0};
SpeedSet spd = {0, 0, 0, 0};             // jaw and carriage speed each way (speed), saved under its own key
// squeezeMm and brushOffsetMm belonged to the measure-first polishing pass; they stay in the struct so the saved "pol" key
// still loads. Polishing now uses gripMm instead (see polish.ino).
PolishSet pol = {5.0f, 60.0f, 38.0f};   // only brushPct is used since polishing follows the shoe live (2026-11-03)
float gripMm = 40.0f;                   // side reading on a straight-sided box with the yarn pressing as wanted (gripcal)
SpraySet spr = {3, 300, 300, 1000};      // spray bursts (set spraycount / sprayon / spraygap / spraypause)
extern bool polishSpray;
extern uint16_t tofRestarts;      // sensors.ino: restarts after a dropout since power-up
float openDropMm = 20.0f;               // top: the height dips this far below the highest point: the opening, the roller goes up (set opendrop)
float gripTopMm = 30.0f;                // top reading on a flat box with the roller pressing as wanted (gripcal top)
float startGapMm = 30.0f;               // after measuring, the toe stops this far before the side sensor beam (set startgap)
bool beltFastActive = false;
void beltUse(bool fast) {
  if (fast == beltFastActive) return;
  BeltSet cur = {cal.beltMoveUs, cal.beltRevUs, cal.beltMmPerS};
  cal.beltMoveUs = beltOther.fwdUs; cal.beltRevUs = beltOther.revUs; cal.beltMmPerS = beltOther.mmPerS;
  beltOther = cur;
  beltFastActive = fast;
}
BeltSet beltFastSet() { return beltFastActive ? BeltSet{cal.beltMoveUs, cal.beltRevUs, cal.beltMmPerS} : beltOther; }

void calLoad() {
  cal = calibDefaults();
  beltOther = {300, 300, 0};
  beltFastActive = false;
  prefs.begin("asps", true);
  if (prefs.getBytesLength("cal") == sizeof(Calib)) {
    Calib c;
    prefs.getBytes("cal", &c, sizeof(Calib));
    if (c.magic == CALIB_MAGIC) cal = c;
  }
  if (prefs.getBytesLength("bfast") == sizeof(BeltSet)) prefs.getBytes("bfast", &beltOther, sizeof(BeltSet));
  startGapMm = prefs.getFloat("gap", 30.0f);
  pol = {5.0f, 60.0f, 38.0f};
  if (prefs.getBytesLength("pol") == sizeof(PolishSet)) prefs.getBytes("pol", &pol, sizeof(PolishSet));
  gripMm = prefs.getFloat("grip", 40.0f);
  gripTopMm = prefs.getFloat("gript", 30.0f);
  openDropMm = prefs.getFloat("odrop", 20.0f);
  polishSpray = prefs.getBool("pspray", true);
  spr = {3, 300, 300, 1000};
  if (prefs.getBytesLength("spray") == sizeof(SpraySet)) prefs.getBytes("spray", &spr, sizeof(SpraySet));
  spd = {0, 0, 0, 0};
  if (prefs.getBytesLength("spd") == sizeof(SpeedSet)) prefs.getBytes("spd", &spd, sizeof(SpeedSet));
  prefs.end();
}
void calSave() {
  bool was = beltFastActive;
  beltUse(false);                         // the normal belt setting goes in cal, the fast one under its own key
  cal.magic = CALIB_MAGIC;
  prefs.begin("asps", false);
  prefs.putBytes("cal", &cal, sizeof(Calib));
  prefs.putBytes("bfast", &beltOther, sizeof(BeltSet));
  prefs.putFloat("gap", startGapMm);
  prefs.putBytes("spd", &spd, sizeof(SpeedSet));
  prefs.putBytes("pol", &pol, sizeof(PolishSet));
  prefs.putFloat("grip", gripMm);
  prefs.putFloat("gript", gripTopMm);
  prefs.putFloat("odrop", openDropMm);
  prefs.putBool("pspray", polishSpray);
  prefs.putBytes("spray", &spr, sizeof(SpraySet));
  prefs.end();
  beltUse(was);
  Serial.println(F("  calibration saved to flash"));
}
void calShow() {
  Serial.println(F("Calibration:"));
  for (uint8_t i = 0; i < SERVO_COUNT; i++) Serial.printf("  stop pulse %-11s %u us\n", SERVO_NAME[i], cal.stopUs[i]);
  Serial.printf("  directions        jaw open %+d   lift up %+d   belt forward %+d   (+1: pulse above stop)\n", cal.jawOpenSign, cal.liftUpSign, cal.beltFwdSign);
  Serial.printf("  move pulse        stop +/- %u us (jaw, lift)\n", cal.moveUs);
  BeltSet n = beltFastActive ? beltOther : BeltSet{cal.beltMoveUs, cal.beltRevUs, cal.beltMmPerS}, f = beltFastSet();
  Serial.printf("  belt normal       +%u us forward, -%u us back, %.1f mm/s%s\n", n.fwdUs, n.revUs, n.mmPerS, beltFastActive ? "" : "   <- active");
  Serial.printf("  belt fast         +%u us forward, -%u us back, %.1f mm/s%s\n", f.fwdUs, f.revUs, f.mmPerS, beltFastActive ? "   <- active" : "");
  Serial.printf("  start gap         %.0f mm  (after measuring, the toe stops this far before the side sensor)\n", startGapMm);
  Serial.printf("  jaw home reading  %u mm  (side sensor, jaws fully open, sees the reflector)\n", cal.jawHomeMm);
  Serial.printf("  lift home reading %u mm  (top sensor, carriage at home, sees the belt)\n", cal.liftHomeMm);
  Serial.printf("  jaw speed         closing %.1f, opening %.1f mm/s   (0 = not measured yet: speed)\n", spd.jawClose, spd.jawOpen);
  Serial.printf("  lift speed        lowering %.1f, raising %.1f mm/s\n", spd.liftDown, spd.liftUp);
  Serial.printf("  polishing         grip %.0f mm (side reading on the shoe while polishing: gripcal), brushes %.0f %%\n", gripMm, pol.brushPct);
  Serial.printf("  top grip          %.0f mm (top reading on the shoe while polishing: gripcal top)\n", gripTopMm);
  Serial.printf("  top opening dip   %.0f mm below the highest point: the roller goes up (set opendrop)\n", openDropMm);
  Serial.printf("  spray in polish   %s (set polishspray 0/1)\n", polishSpray ? "yes, while the IR sees the shoe" : "no");
  Serial.printf("  spray bursts      %u x %u ms on, %u ms apart, then %u ms pause\n", spr.count, spr.onMs, spr.gapMs, spr.pauseMs);
}

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
  if (millis() - lastFull > 30000) { lastFull = millis(); screenIdle(true); }   // redraw it all now and then, in case noise wiped it
  else if (millis() - lastDraw > 400) {
    lastDraw = millis();
    if (!menuOn) screenDashboard(false);       // the menu redraws itself when the knob moves (menuTick)
  }
}
