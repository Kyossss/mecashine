// Shoe polisher (ASPS) - debug and test firmware: pins, addresses and settings.
// Change the values here if your wiring differs. Everything else reads from this file.
#pragma once
#include <Arduino.h>

// ---------------------------------------------------------------- pins (same as the wiring tab)
constexpr uint8_t PIN_SDA = 21, PIN_SCL = 22;                  // I2C: PCF8575, PCA9685, both VL53L0X
constexpr uint8_t PIN_START = 32, PIN_STOP = 33;               // push-toggle buttons, other leg to GND
constexpr uint8_t PIN_XSHUT_TOP = 13, PIN_XSHUT_SIDE = 14;     // VL53L0X enable pins
constexpr uint8_t PIN_SCK = 18, PIN_MOSI = 23;                 // SPI: display only (its SDO is not connected, so no MISO; no touch panel)
constexpr uint8_t PIN_TFT_CS = 5, PIN_TFT_DC = 16, PIN_TFT_RST = 17;
constexpr uint8_t PWM_PIN[3] = {25, 26, 27};                   // TB6612 #1 PWMA, #1 PWMB, #2 PWMA
constexpr uint8_t PIN_PUMP = 4;                                // pump relay (was touch CS). Not a boot strapping pin, so it cannot upset start-up
constexpr bool PUMP_ACTIVE_LOW = true;
constexpr uint8_t PIN_IR = 34;                                  // spray-station IR module (FC-51) OUT: input-only pin, 10k pull-up on the board
constexpr bool IR_ACTIVE_LOW = true;                            // the module pulls OUT LOW when something is in front of it
constexpr float IR_TO_SIDE_SENSOR_MM = 164.0f;                  // along the belt, IR beam to side sensor beam (CAD x 665 -> 829); ir belt measures it                         // most relay modules switch on when IN goes LOW; false for an active-high one
constexpr uint8_t PIN_KNOB = 35;                                // menu potentiometer wiper (ends to 3.3 V and GND, 100 nF wiper to GND). Input-only ADC1 pin
constexpr uint32_t PUMP_MAX_MS = 10000;                        // the pump switches itself off after this, however it was switched on
constexpr uint8_t PIN_SERVO_DIRECT = 19;                       // spare pin (was touch MISO): drives one servo without the PCA9685, for fault finding

// ---------------------------------------------------------------- I2C addresses
constexpr uint8_t PCA_ADDR = 0x40;
constexpr uint8_t TOF_SIDE_ADDR = 0x29;                        // side sensor keeps the factory address
constexpr uint8_t TOF_TOP_ADDR = 0x30;                         // top sensor is moved here at boot
// the PCF8575 is found automatically anywhere in 0x20..0x27

// ---------------------------------------------------------------- motors (TB6612FNG through the PCF8575)
struct Motor {
  const char *name;
  uint8_t in1, in2, stby;                                      // PCF8575 bit numbers
};
constexpr uint8_t MOTOR_COUNT = 3;
const Motor MOTOR[MOTOR_COUNT] = {
  {"Side brush L (TB6612 #1 A)", 0, 1, 4},
  {"Side brush R (TB6612 #1 B)", 2, 3, 4},
  {"Top roller   (TB6612 #2 A)", 5, 6, 7},
};
constexpr uint32_t PWM_FREQ = 20000;                           // 20 kHz
constexpr uint8_t PWM_BITS = 10;                               // duty 0..1023
constexpr uint16_t PWM_MAX = (1u << PWM_BITS) - 1;

// ---------------------------------------------------------------- servos (PCA9685, all 360-degree)
enum ServoCh : uint8_t { SV_BELT = 0, SV_LIFT = 1, SV_JAW = 2 };
constexpr uint8_t SERVO_COUNT = 3;
const char *const SERVO_NAME[SERVO_COUNT] = {"belt (CH0)", "lift (CH1)", "jaw (CH2)"};

// ---------------------------------------------------------------- machine geometry used by the tests
constexpr float SENSOR_SPACING_MM = 225.0f;   // along the belt, side sensor beam to top sensor beam: 240, minus the 15 mm the top bracket moved forward (2026-11-03); check with measure ("toe to toe")
constexpr float SIDE_SENSOR_TO_BRUSH_MM = 71.0f;  // along the belt, side sensor beam to the side brush axes (Fusion model; check on the machine)
constexpr float TOP_SENSOR_TO_ROLLER_MM = 75.0f;  // along the belt, top sensor beam to the top roller axis: 60 measured with a caliper, then the bracket moved 15 mm forward (2026-11-03) so the yarn is out of the beam
constexpr uint16_t TOF_MAX_VALID_MM = 1200;   // anything above this is treated as "nothing seen"

// ---------------------------------------------------------------- calibration, kept in flash between power cycles
struct Calib {
  uint16_t stopUs[SERVO_COUNT];   // pulse at which each 360-degree servo stands still
  int8_t jawOpenSign;             // +1: a pulse above the stop pulse opens the jaws
  int8_t liftUpSign;              // +1: a pulse above the stop pulse raises the carriage
  int8_t beltFwdSign;             // +1: a pulse above the stop pulse moves the belt toward the brushes
  uint16_t moveUs;                // how far from the stop pulse the jaw and lift moves and timings run
  uint16_t beltMoveUs;            // belt forward: pulse offset from stop. Its servo has a wide still range (about 1310..1500 us), so it needs more
  uint16_t beltRevUs;             // belt backward offset, tuned by  beltmatch  so both directions run at the same speed
  uint16_t jawHomeMm;             // side sensor reading with the jaws fully open (it sees the reflector)
  uint16_t liftHomeMm;            // top sensor reading with the carriage at home (it sees the belt)
  float jawMmPerS;                // measured speeds at moveUs
  float liftMmPerS;
  float beltMmPerS;
  uint32_t magic;
};
constexpr uint32_t CALIB_MAGIC = 0xA5B50005;   // changed when Calib changes, so an old saved layout is not misread
inline Calib calibDefaults() {
  Calib c;
  for (uint8_t i = 0; i < SERVO_COUNT; i++) c.stopUs[i] = 1500;
  c.stopUs[SV_BELT] = 1400;   // measured: still from about 1310 to 1500 us
  c.jawOpenSign = 1; c.liftUpSign = 1; c.beltFwdSign = 1;
  c.moveUs = 100;
  c.beltMoveUs = 150;
  c.beltRevUs = 150;
  c.jawHomeMm = 175;     // with the redesigned arms; it was 196 with the original arms
  c.liftHomeMm = 226;
  c.jawMmPerS = 0; c.liftMmPerS = 0; c.beltMmPerS = 0;
  c.magic = CALIB_MAGIC;
  return c;
}

// ---------------------------------------------------------------- shared types
struct ToggleButton { uint8_t pin; bool stable; bool lastRead; uint32_t changedAt; };
struct BeltSet { uint16_t fwdUs, revUs; float mmPerS; };   // one belt setting: offsets from the stop pulse and the matched speed
struct SpeedSet { float jawClose, jawOpen, liftDown, liftUp; };   // mm of sensor reading per second, at the move pulse
// polishing settings: how hard the brushes press, how fast they spin, and how the side reading maps to the gap between them
struct PolishSet { float squeezeMm, brushPct, brushOffsetMm; };
// spray pattern while the IR sees a shoe: <count> bursts of <onMs>, <gapMs> apart, then <pauseMs>, and again:  '''_'''_'''
struct SpraySet { uint16_t count, onMs, gapMs, pauseMs; };
struct NoiseCount { uint8_t ok, bad, silent; };   // noisetest: valid, rejected by the sensor, sensor not answering
struct TofStats { uint16_t n, good; float mean, sd, mn, mx; uint16_t why[7]; };   // why[]: count of each range status 0..5, [6] too far

// ---------------------------------------------------------------- test results
enum Result : uint8_t { R_NOT_RUN, R_PASS, R_FAIL, R_SKIP };
enum TestId : uint8_t { T_I2C, T_PCF, T_BUTTONS, T_SIDE, T_TOP, T_SIDE_SEE, T_TOP_SEE, T_DISPLAY, T_MOTOR_L, T_MOTOR_R, T_MOTOR_TOP, T_JAW, T_LIFT, T_BELT, T_PUMP };
