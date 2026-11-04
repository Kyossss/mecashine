/*
  MecaShine - automatic shoe polisher. User firmware.

  This is the firmware the machine ships with. Everything is done with the knob and the START / STOP buttons:
    Polish shoe    one START per shoe (greyed out until the machine has been homed)
    Home machine   needed after power-up and after a stop
    Prime pump     runs the pump until polish reaches the nozzle
    Self-test      shows which sensors and boards answer; nothing moves and nothing is changed
    Settings       spray amount, spray on / off, brush pressure, brush speed

  Calibration is done once, by the admin, with the debug firmware (firmware/mecashine_debug). This firmware only reads it:
  it never writes the calibration. The user settings are stored under their own keys and applied as offsets on the
  calibrated values, so changing them cannot spoil the calibration.

  The USB Serial port (115200) only logs what the machine does; it takes no commands. Any key typed there stops the machine,
  like STOP.

  The machine code is shared with the debug firmware: run firmware/sync_main.py to copy it in (see that file).
  Board: ESP32 Dev Module. Libraries: Adafruit PWM Servo Driver, Adafruit VL53L0X, Adafruit GFX.
*/

#include "state.h"
#include "version.h"

// ---------------------------------------------------------------- user settings
// 0 / 1 / 2 = less / normal / more. Stored under "u_*" keys; never the admin's keys.
uint8_t uSpray = 1, uPress = 1, uSpeed = 1;
bool uSprayOn = true;
// the admin's values as loaded, before the user's offsets
float baseGrip = 40, baseGripTop = 30, baseBrushPct = 60;
uint16_t baseOnMs = 300;
bool basePspray = true;

void userLoad() {
  prefs.begin("asps", true);
  uSpray = constrain(prefs.getUChar("u_spray", 1), 0, 2);
  uPress = constrain(prefs.getUChar("u_press", 1), 0, 2);
  uSpeed = constrain(prefs.getUChar("u_speed", 1), 0, 2);
  uSprayOn = prefs.getBool("u_sprayon", true);
  prefs.end();
}
void userSave() {
  prefs.begin("asps", false);
  prefs.putUChar("u_spray", uSpray);
  prefs.putUChar("u_press", uPress);
  prefs.putUChar("u_speed", uSpeed);
  prefs.putBool("u_sprayon", uSprayOn);
  prefs.end();
}
// The values the polishing pass uses = the admin's values with the user's offsets. Only in memory.
void userApply() {
  static const float sprayX[3] = {0.6f, 1.0f, 1.5f};      // burst length
  static const float pressMm[3] = {10.0f, 0.0f, -10.0f};  // grip reading: smaller presses harder (light / normal / firm)
  static const float speedX[3] = {0.75f, 1.0f, 1.25f};    // brush motor power
  spr.onMs = (uint16_t)constrain(baseOnMs * sprayX[uSpray], 20.0f, 5000.0f);
  gripMm = max(5.0f, baseGrip + pressMm[uPress]);
  gripTopMm = max(5.0f, baseGripTop + pressMm[uPress]);
  pol.brushPct = constrain(baseBrushPct * speedX[uSpeed], 20.0f, 100.0f);
  polishSpray = basePspray && uSprayOn;
}

// The machine has been set up by the admin: calibration saved, speeds measured, belt timed.
bool machineSetUp() {
  return calStored && spd.jawOpen > 0 && spd.jawClose > 0 && spd.liftUp > 0 && spd.liftDown > 0 && cal.beltMmPerS > 0;
}

// The shared calibration code (calib.ino) can run the debug firmware's tests; the user firmware has none and never calls it.
void runTest(uint8_t) {}

// ---------------------------------------------------------------- setup and loop
void setup() {
  pumpBegin();                                  // first of all, so the pump cannot run during start-up
  irBegin();
  analogSetPinAttenuation(PIN_KNOB, ADC_11db);
  Serial.begin(115200);
  pwmBegin();                                   // motor PWM at 0 before anything else
  buttonBegin(btnStart);
  buttonBegin(btnStop);
  SPI.begin(PIN_SCK, -1, PIN_MOSI);
  screenBegin();
  bootLogo(0, "Starting...");
  Wire.begin(PIN_SDA, PIN_SCL);
  Wire.setClock(100000);
  pcfFound = pcfFind() && pcfWrite(pcfState);   // both motor drivers to standby
  bootLogo(1, "Motor drivers");
  calLoad();
  baseGrip = gripMm; baseGripTop = gripTopMm; baseBrushPct = pol.brushPct; baseOnMs = spr.onMs; basePspray = polishSpray;
  userLoad();
  userApply();
  pcaBegin();
  bootLogo(2, "Distance sensors");
  tofBegin();
  bootLogo(3, "Settings");

  Serial.println();
  Serial.printf("MecaShine %s - user firmware. This port only logs; it takes no commands.\n", FW_VERSION);
  Serial.printf("  servo driver %s, motor expander %s, side sensor %s, top sensor %s\n", pcaFound ? "ok" : "MISSING",
                pcfFound ? "ok" : "MISSING", sideFound ? "ok" : "MISSING", topFound ? "ok" : "MISSING");
  if (!machineSetUp()) Serial.println(F("  NOT SET UP: calibrate it with the debug firmware first (calibrate, speed, belttape)."));
  Serial.println(F("  Not homed yet: choose Home machine."));
  bootLogo(4, machineSetUp() ? "Ready" : "Not set up: contact service");
  delay(900);                                   // let the logo be seen
  menuOn = true;
  screenIdle(true);
}

void loop() {
  pumpTick();
  if (buttonPressed(btnStop)) { stopAll(); Serial.println(F("STOP")); }
  if (buttonPressed(btnStart)) userRun();
  userTick();
  while (Serial.available()) Serial.read();     // log only: typed input is ignored here (and stops a running job)

  static uint32_t lastFull = 0;
  screenKeepAlive();
  if (millis() - lastFull > 30000) { lastFull = millis(); screenRecover(); }   // in case noise wiped the display
}
