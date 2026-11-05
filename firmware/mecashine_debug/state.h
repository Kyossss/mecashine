// Machine state shared by both sketches: mecashine_debug (admin) and mecashine (users).
// The single source is firmware/mecashine_debug; sync_main.py copies it into firmware/mecashine. Edit it here.
// Each sketch's main .ino includes this once (the Arduino IDE joins all .ino files into one file, so the definitions
// below exist once).
#pragma once
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
bool sonarOn = false;      // spray sensor: false = FC-51 IR, true = HC-SR04 ultrasonic (set sonar 0/1); black shoes do not reflect IR
float sonarMm = 80.0f;     // ultrasonic: an echo closer than this is a shoe (set sonarmm)
bool polishSpray = true;   // spray during the polishing pass (polish ... nospray, or set polishspray 0)
bool calStored = false;         // a saved calibration was found in flash (calLoad); the user firmware will not run without one
bool machineHomed = false;      // false at power-up: polishing needs  home  (or Home machine) first; a pass leaves it homed
// what is on the screen now, so screenRecover() in screen.ino can draw it again: 0 idle (menu or dashboard), 1 cycle screen, 2 menu page
uint8_t scrKind = 0;
char cyState[24] = "", cySub[48] = "";
uint16_t cyCol = 0;
float cyLen = -1, cyProg = -1; uint16_t cyProgCol = 0;
char mfFooter[48] = "", msState[24] = "", msL1[48] = "", msL2[48] = "";
uint16_t msCol = 0;
bool msShown = false;
float liftLagMm = 0.0f;        // top: lift away when the roller axis is this far PAST the opening's edge (set liftlag; minus = before it)
float liftAwayMm = 40.0f;       // top: at the opening the carriage rises this far above its pressing height on the shoe (set liftaway)
float exitMm = 100.0f;          // after the heel has passed the last station the belt carries the shoe on this far (set exitmm)
extern uint16_t tofRestarts;      // sensors.ino: restarts after a dropout since power-up
float openDropMm = 20.0f;               // top: the height dips this far below the highest point: the opening, the roller goes up (set opendrop)
float gripTopMm = 30.0f;                // top reading on a flat box with the roller pressing as wanted (gripcal top)
float startGapMm = 30.0f;               // after measuring, the toe stops this far before the side sensor beam (set startgap)
bool beltFastActive = false;
