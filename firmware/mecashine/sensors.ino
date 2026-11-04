// COPIED from firmware/mecashine_debug by sync_main.py. Do not edit here: edit it there and run sync_main.py.
// The two VL53L0X distance sensors.
// Both ship at address 0x29. At boot the side sensor is held off with its XSHUT pin while the top
// sensor is moved to 0x30; then the side sensor is switched on and keeps 0x29.

void tofBegin() {
  pinMode(PIN_XSHUT_TOP, OUTPUT);
  pinMode(PIN_XSHUT_SIDE, OUTPUT);
  digitalWrite(PIN_XSHUT_TOP, LOW);
  digitalWrite(PIN_XSHUT_SIDE, LOW);
  delay(20);

  digitalWrite(PIN_XSHUT_TOP, HIGH);              // top sensor only
  delay(20);
  topFound = tofTop.begin(TOF_TOP_ADDR, false, &Wire, tofMode[0]);

  digitalWrite(PIN_XSHUT_SIDE, HIGH);             // now the side sensor
  delay(20);
  sideFound = tofSide.begin(TOF_SIDE_ADDR, false, &Wire, tofMode[1]);

  Serial.printf("Distance sensors: side %s (0x%02X, %s), top %s (0x%02X, %s)\n",
                sideFound ? "found" : "MISSING", TOF_SIDE_ADDR, tofModeName(tofMode[1]),
                topFound ? "found" : "MISSING", TOF_TOP_ADDR, tofModeName(tofMode[0]));
}

const char *tofModeName(Adafruit_VL53L0X::VL53L0X_Sense_config_t m) {
  switch (m) {
    case Adafruit_VL53L0X::VL53L0X_SENSE_LONG_RANGE: return "long range";
    case Adafruit_VL53L0X::VL53L0X_SENSE_HIGH_SPEED: return "fast";
    case Adafruit_VL53L0X::VL53L0X_SENSE_HIGH_ACCURACY: return "accurate";
    default: return "default";
  }
}
// Why a reading was rejected, from the sensor's range status.
const char *tofStatusName(uint8_t st) {
  switch (st) {
    case 0: return "ok";
    case 1: return "sigma fail (noisy: weak or angled target)";
    case 2: return "signal fail (too little light back)";
    case 3: return "min range fail (too close)";
    case 4: return "phase fail (out of range)";
    case 5: return "hardware fail";
    default: return "no update";
  }
}
// Switches one sensor's ranging mode without a restart.
bool tofSetMode(bool side, Adafruit_VL53L0X::VL53L0X_Sense_config_t m) {
  if (side ? !sideFound : !topFound) return false;
  tofMode[side] = m;
  return (side ? tofSide : tofTop).configSensor(m);
}
// Prints the raw reading and status of both sensors live, including the readings tofRead() rejects.
void tofRawWatch() {
  Serial.printf("Raw readings with the sensor's status (any key or STOP to end). Restarts after a dropout so far: %u\n", tofRestarts);
  while (!stopRequested()) {
    for (uint8_t i = 0; i < 2; i++) {
      bool side = i == 0;
      if (side ? !sideFound : !topFound) { Serial.printf("  %-4s missing      ", side ? "side" : "top"); continue; }
      Adafruit_VL53L0X &s = side ? tofSide : tofTop;
      uint16_t mm = s.readRange();
      Serial.printf("  %-4s %5u mm  %-42s", side ? "side" : "top", mm, tofStatusName(s.readRangeStatus()));
    }
    Serial.println();
    delay(150);
  }
}

// One reading in millimetres. Returns -1 for no valid reading (out of range, or the sensor is missing).
int tofRead(bool side) {
  Adafruit_VL53L0X &s = side ? tofSide : tofTop;
  if (side ? !sideFound : !topFound) return -1;
  uint16_t mm = s.readRange();
  uint8_t st = s.readRangeStatus();
  tofLastStatus[side] = st;
  if (tofDeadCheck(side, mm, st)) return -1;            // it had dropped out and was restarted: this reading is lost
  if (st != 0 || mm == 0 || mm > TOF_MAX_VALID_MM) return -1;
  return mm;
}

// ---------------------------------------------------------------- dropout watchdog
// A spike from the pump or a motor can reset a sensor, or both. The top one then comes back at the factory address 0x29,
// the same as the side one, and neither answers (65535, "no update") until they are restarted. The firmware cannot stop
// the spike (that is the diode and the wiring), but it restarts them on its own as soon as it notices:
//   single readings:  3 dead readings in a row from either sensor
//   continuous mode:  no new reading from a sensor for 250 ms (it normally gives one every 35 ms)
// A restart takes about 0.2 s. At most one every 0.5 s, so a sensor that is really gone does not lock the loop up.
uint16_t tofRestarts = 0;          // since power-up, shown by  tofraw  and at the end of a pass
bool tofContOn = false;            // continuous mode is on (tofContinuous)
uint32_t tofNewAt[2] = {0, 0};     // when each sensor last gave a new reading in continuous mode
uint8_t tofDeadRun[2] = {0, 0};

// The I2C bus itself can be left stuck by a spike: a sensor holding SDA low half-way through a byte. Clocking SCL up to
// 9 times lets it finish and release the line; then the ESP32's I2C driver is started again.
void i2cBusClear() {
  Wire.end();
  pinMode(PIN_SDA, INPUT_PULLUP);
  pinMode(PIN_SCL, OUTPUT_OPEN_DRAIN);
  for (uint8_t i = 0; i < 9 && digitalRead(PIN_SDA) == LOW; i++) {
    digitalWrite(PIN_SCL, LOW); delayMicroseconds(6);
    digitalWrite(PIN_SCL, HIGH); delayMicroseconds(6);
  }
  Wire.begin(PIN_SDA, PIN_SCL);
  Wire.setClock(100000);
}

// Restarts both sensors (XSHUT off and on, addresses set again), and continuous mode if it was on.
bool tofRecover() {
  static uint32_t lastAt = 0;
  if (lastAt && millis() - lastAt < 500) return sideFound && topFound;
  lastAt = millis();
  tofRestarts++;
  Serial.printf("  distance sensors dropped out (pump or motor noise?): restarting them (%u so far)\n", tofRestarts);
  bool cont = tofContOn;
  i2cBusClear();
  tofBegin();
  if (cont) tofContinuous(true);
  tofDeadRun[0] = tofDeadRun[1] = 0;
  tofNewAt[0] = tofNewAt[1] = millis();
  return sideFound && topFound;
}

// true if the reading shows the sensor has dropped out and it was restarted
bool tofDeadCheck(bool side, uint16_t mm, uint8_t st) {
  bool dead = mm == 65535 || st > 5;
  if (!dead) { tofDeadRun[side] = 0; return false; }
  if (++tofDeadRun[side] < 3) return false;
  tofRecover();
  return true;
}

// Continuous mode, for the measuring pass: both sensors range at the same time, back to back, and tofPoll() collects each
// result when it is ready instead of waiting for one sensor and then the other. About 3x the readings of tofRead().
// tofRead() must not be used while it is on; tofContinuous(false) puts both back to single readings.
constexpr uint16_t TOF_PERIOD_MS = 35;    // just over the 33 ms timing budget
void tofContinuous(bool on) {
  tofContOn = on;
  tofNewAt[0] = tofNewAt[1] = millis();
  if (on) {
    if (sideFound) tofSide.startRangeContinuous(TOF_PERIOD_MS);
    if (topFound) tofTop.startRangeContinuous(TOF_PERIOD_MS);
  } else {
    if (sideFound) tofSide.stopRangeContinuous();
    if (topFound) tofTop.stopRangeContinuous();
  }
}
// -2: no new reading yet; -1: a new reading that is not valid; otherwise the new reading in mm
int tofPoll(bool side) {
  Adafruit_VL53L0X &s = side ? tofSide : tofTop;
  if (side ? !sideFound : !topFound) return -1;
  if (!s.isRangeComplete()) {
    if (tofContOn && millis() - tofNewAt[side] > 250) { tofRecover(); return -1; }   // gone quiet: it dropped out
    return -2;
  }
  tofNewAt[side] = millis();
  uint16_t mm = s.readRangeResult();
  uint8_t st = s.readRangeStatus();
  tofLastStatus[side] = st;
  if (tofDeadCheck(side, mm, st)) return -1;
  if (st != 0 || mm == 0 || mm > TOF_MAX_VALID_MM) return -1;
  return mm;
}

// A steady reading from n good ones: up to 3n tries, so a few dropouts do not fail it, and the median rather than
// the mean, so a reading that jumps between two surfaces gives the more common one, not a distance in between.
// -1 if fewer than half of n came back good.
float tofAvg(bool side, uint8_t n) {
  int v[30]; uint8_t good = 0;
  n = constrain(n, 1, 30);
  for (uint8_t i = 0; i < 3 * n && good < n; i++) { int r = tofRead(side); if (r > 0) v[good++] = r; }
  if (good * 2 < n) return -1;
  for (uint8_t i = 1; i < good; i++) for (uint8_t j = i; j > 0 && v[j - 1] > v[j]; j--) { int t = v[j]; v[j] = v[j - 1]; v[j - 1] = t; }
  return good % 2 ? v[good / 2] : (v[good / 2 - 1] + v[good / 2]) / 2.0f;
}

TofStats tofStats(bool side, uint16_t n) {
  TofStats s = {n, 0, 0, 0, 1e9, -1e9};
  float sum = 0, sum2 = 0;
  for (uint16_t i = 0; i < n; i++) {
    int r = tofRead(side);
    uint8_t st = min<uint8_t>(tofLastStatus[side], 5);
    s.why[r > 0 ? 0 : st ? st : 6]++;                  // status 0 but rejected means it read past TOF_MAX_VALID_MM
    if (r > 0) { s.good++; sum += r; sum2 += (float)r * r; s.mn = min(s.mn, (float)r); s.mx = max(s.mx, (float)r); }
    if (stopRequested()) { aborted = true; break; }
  }
  if (s.good) { s.mean = sum / s.good; s.sd = sqrtf(max(0.0f, sum2 / s.good - s.mean * s.mean)); }
  return s;
}
// The most common reason readings were rejected, or nullptr if none were.
const char *tofMainFailure(const TofStats &s) {
  uint8_t worst = 0;
  for (uint8_t i = 1; i < 7; i++) if (s.why[i] > (worst ? s.why[worst] : 0)) worst = i;
  return worst == 0 ? nullptr : worst == 6 ? "farther than the valid limit" : tofStatusName(worst);
}
void tofPrintStats(const char *name, const TofStats &s) {
  if (s.good < s.n) {
    Serial.printf("  %-5s rejected %u of %u:", name, s.n - s.good, s.n);
    for (uint8_t i = 1; i < 7; i++) if (s.why[i]) Serial.printf("  %u %s;", s.why[i], i == 6 ? "too far" : tofStatusName(i));
    Serial.println();
  }
  if (!s.good) { Serial.printf("  %-5s no valid readings out of %u\n", name, s.n); return; }
  Serial.printf("  %-5s mean %.1f mm   spread %.1f mm (sd)   min %.0f   max %.0f   valid %u of %u\n",
                name, s.mean, s.sd, s.mn, s.mx, s.good, s.n);
}

// Prints both sensors live until a key is pressed.
void tofWatch() {
  Serial.println(F("Live distances (any key or STOP to end). Wave a hand under each sensor."));
  while (!stopRequested()) {
    int a = tofRead(true), b = tofRead(false);
    Serial.printf("  side %5s mm   top %5s mm\n", a > 0 ? String(a).c_str() : "---", b > 0 ? String(b).c_str() : "---");
    screenDashboard(false);
    delay(150);
  }
}
