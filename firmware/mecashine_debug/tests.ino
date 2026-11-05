// The tests. Each one sets results[i] to PASS, FAIL or SKIP with a short note.
// test       runs them all in order and prints a report at the end
// test <n>   runs just test n (1..15, as numbered in the report)

void setResult(uint8_t id, Result r, const String &note) {
  results[id] = r;
  resultNote[id] = note;
  const char *word = r == R_PASS ? "PASS" : r == R_FAIL ? "FAIL" : "SKIP";
  Serial.printf("  => %s: %s  %s\n", TEST_NAME[id], word, note.c_str());
  screenMessage(String(TEST_NAME[id]) + ": " + word, r == R_PASS ? C_OK : r == R_FAIL ? C_BAD : C_DIM);
}

void header(uint8_t id) {
  Serial.println();
  Serial.printf("---- Test %u of %u: %s ----\n", id + 1, TEST_COUNT, TEST_NAME[id]);
  screenMessage(String("Testing: ") + TEST_NAME[id], C_WARN);
  screenDashboard(false);
}

// ---------------------------------------------------------------- 1 I2C bus
void testI2C() {
  header(T_I2C);
  pcfFound = pcfFind() && pcfWrite(pcfState);
  pcaBegin();                                   // also wakes it, in case it was powered after the ESP32 booted
  sideFound = sideFound && i2cPresent(TOF_SIDE_ADDR);
  topFound = topFound && i2cPresent(TOF_TOP_ADDR);
  i2cScan(true);
  String miss;
  if (!pcfFound) miss += " PCF8575";
  if (!pcaFound) miss += " PCA9685";
  if (!sideFound) miss += " side-ToF";
  if (!topFound) miss += " top-ToF";
  if (miss.length()) setResult(T_I2C, R_FAIL, "missing:" + miss);
  else setResult(T_I2C, R_PASS, String("PCF8575 at 0x") + String(pcfAddr, HEX) + ", PCA9685, both sensors");
}

// ---------------------------------------------------------------- 2 PCF8575 pins
// Walks P00..P07 one at a time with the motor PWM held at 0, and reads each pin back.
void testPCF() {
  header(T_PCF);
  if (!pcfFound) { setResult(T_PCF, R_SKIP, "PCF8575 not found"); return; }
  for (uint8_t m = 0; m < MOTOR_COUNT; m++) pwmWrite(m, 0);
  static const char *const PIN_NAME[8] = {"P00 AIN1 #1", "P01 AIN2 #1", "P02 BIN1 #1", "P03 BIN2 #1", "P04 STBY #1", "P05 AIN1 #2", "P06 AIN2 #2", "P07 STBY #2"};
  uint8_t bad = 0;
  for (uint8_t bit = 0; bit < 8; bit++) {
    uint16_t out = 0xFF00 | (1u << bit), back = 0;
    bool ok = pcfWrite(out) && pcfRead(back);
    bool match = ok && ((back & 0xFF) == (out & 0xFF));
    if (!match) bad++;
    Serial.printf("  %-12s high: wrote 0x%02X read 0x%02X  %s\n", PIN_NAME[bit], out & 0xFF, back & 0xFF, !ok ? "NO ANSWER" : match ? "ok" : "MISMATCH");
    if (!waitOrAbort(150)) break;
  }
  pcfState = 0xFF00; pcfWrite(pcfState);
  if (aborted) { setResult(T_PCF, R_SKIP, "interrupted"); return; }
  if (bad) setResult(T_PCF, R_FAIL, String(bad) + " pin(s) did not read back: shorted or miswired");
  else setResult(T_PCF, R_PASS, "all 8 driver pins switch and read back");
}

// ---------------------------------------------------------------- 3 buttons
bool waitButton(ToggleButton &b, const char *name, uint32_t ms) {
  Serial.printf("  push %s now (%lu s; type s to skip)\n", name, (unsigned long)(ms / 1000));
  screenMessage(String("Push ") + name, C_WARN); screenDashboard(false);
  uint32_t t0 = millis();
  while (millis() - t0 < ms) {
    if (buttonPressed(b)) { Serial.printf("    %s seen\n", name); return true; }
    if (Serial.available() && tolower(Serial.read()) == 's') return false;
    delay(5);
  }
  return false;
}
void testButtons() {
  header(T_BUTTONS);
  buttonPressed(btnStart); buttonPressed(btnStop);   // clear old changes
  bool a = waitButton(btnStart, "START", 15000);
  bool b = waitButton(btnStop, "STOP", 15000);
  if (a && b) setResult(T_BUTTONS, R_PASS, "both buttons seen");
  else setResult(T_BUTTONS, R_FAIL, String(a ? "" : "START not seen ") + (b ? "" : "STOP not seen") + " (check GPIO 32 / 33 and ground)");
}

// ---------------------------------------------------------------- 4, 5 distance sensors
void testTof(bool side) {
  uint8_t id = side ? T_SIDE : T_TOP;
  header(id);
  if (side ? !sideFound : !topFound) { setResult(id, R_FAIL, "sensor not found on I2C (check XSHUT GPIO 14 / 13)"); return; }
  Serial.println(side ? F("  the side sensor should be looking across at the reflector")
                      : F("  the top sensor should be looking down at the belt"));
  TofStats s = tofStats(side, 60);
  tofPrintStats(side ? "side" : "top", s);
  if (aborted) { setResult(id, R_SKIP, "interrupted"); return; }
  const char *why = tofMainFailure(s);
  if (s.good < 54) setResult(id, R_FAIL, String(s.good) + " of 60 readings valid, mostly " + (why ? why : "no reading") +
                                         (side ? ": the beam is probably wider than the reflector at this distance" : ""));
  // side: the small reflector at full open gives sd ~5.6..6.5 mm in long range (2026-10-23), fine once readings are medianed;
  // 10 mm still catches the bad case (18 mm without the white face). Top: the belt fills the beam, sd ~3 mm.
  else if (s.sd > (side ? 10 : 6)) setResult(id, R_FAIL, String("readings jump around (") + String(s.sd, 1) + " mm, " + String(s.mn, 0) + " to " + String(s.mx, 0) +
                                         "): the beam is catching more than the target");
  else setResult(id, R_PASS, String("steady at ") + String(s.mean, 0) + " mm (spread " + String(s.sd, 1) + " mm)");
}

// ---------------------------------------------------------------- 6, 7 does each sensor see an object?
// Takes the empty reading, asks you to hold something in front of the sensor and checks the reading drops,
// then asks you to take it away and checks the reading comes back.
constexpr int SEE_DROP_MM = 30;          // the object must read at least this much closer than the empty reading

// Waits until the reading has met the condition for 3 readings in a row.
// Returns that reading (0 means "nothing in range"), or -2 on time-out or skip.
int waitReading(bool side, bool wantObject, float base, uint32_t ms) {
  uint32_t t0 = millis(), lastPrint = 0;
  uint8_t inARow = 0;
  while (millis() - t0 < ms) {
    int r = tofRead(side);
    bool object = r > 0 && (base < 0 || r < base - SEE_DROP_MM);
    bool empty = base < 0 ? r < 0 : (r > 0 && fabsf(r - base) <= 15);
    if (wantObject ? object : empty) { if (++inARow >= 3) return r > 0 ? r : 0; }
    else inARow = 0;
    if (millis() - lastPrint > 400) {
      lastPrint = millis();
      if (r > 0) Serial.printf("    reading %d mm\n", r); else Serial.println(F("    reading: nothing in range"));
    }
    if (Serial.available() && tolower(Serial.read()) == 's') return -2;
    if (buttonPressed(btnStop)) return -2;
  }
  return -2;
}

void testTofSees(bool side) {
  uint8_t id = side ? T_SIDE_SEE : T_TOP_SEE;
  const char *name = side ? "side" : "top";
  header(id);
  if (side ? !sideFound : !topFound) { setResult(id, R_FAIL, "sensor not found on I2C"); return; }
  while (Serial.available()) Serial.read();
  float base = tofAvg(side, 8);
  if (base > 0) Serial.printf("  empty reading %.0f mm (%s)\n", base, side ? "the reflector across the jaws" : "the belt under the carriage");
  else Serial.println(F("  empty reading: nothing in range"));

  Serial.printf("  Hold your hand or a shoe about 10 cm in front of the %s sensor (15 s; type s or push STOP to skip).\n", name);
  screenMessage(String("Hand in front of ") + name + " sensor", C_WARN);
  screenDashboard(false);
  int seen = waitReading(side, true, base, 15000);
  if (seen == -2) { setResult(id, R_FAIL, "did not see the object: check the lens is clean and the sensor faces the gap"); return; }
  Serial.printf("  SEEN at %d mm\n", seen);

  Serial.println(F("  Now take it away (15 s)."));
  screenMessage(String("Take it away from ") + name + " sensor", C_WARN);
  screenDashboard(false);
  int back = waitReading(side, false, base, 15000);
  if (back == -2) { setResult(id, R_FAIL, String("saw it at ") + seen + " mm, but the reading did not return to the empty value"); return; }
  setResult(id, R_PASS, String("sees an object at ") + seen + " mm and clears again");
}

// ---------------------------------------------------------------- 8 display
void testDisplay() {
  header(T_DISPLAY);
  screenTestPattern();
  Serial.println(F("  The display shows 8 colour bars, a grey ramp and two lines of text."));
  delay(300);
  int a = askYesNo("Bars, grey ramp and text all look right?");
  screenDashboard(true);
  if (a == 1) setResult(T_DISPLAY, R_PASS, "pattern seen correctly");
  else if (a == 0) setResult(T_DISPLAY, R_FAIL, "blank: check VCC 5 V, LED 3.3 V, CS 5, DC 16, RST 17. Wrong colours: check MOSI 23, SCK 18");
  else setResult(T_DISPLAY, R_SKIP, "no answer");
}

// ---------------------------------------------------------------- 9, 10, 11 brush motors
void testMotor(uint8_t m) {
  uint8_t id = T_MOTOR_L + m;
  header(id);
  if (!pcfFound) { setResult(id, R_SKIP, "PCF8575 not found, so the driver cannot be enabled"); return; }
  Serial.printf("  %s will turn one way at 60 %%, stop, then turn the other way.\n", MOTOR[m].name);
  bool ok = motorSequence(m, 60);
  motorRun(m, 0);
  if (!ok) { setResult(id, R_SKIP, "interrupted"); return; }
  int a = askYesNo("Did it turn one way, stop, then the other way?");
  if (a == 1) setResult(id, R_PASS, "turns both ways");
  else if (a == 0) setResult(id, R_FAIL, "no turn: check 12 V to VM, the motor leads and STBY. One way only: check xIN1 / xIN2");
  else setResult(id, R_SKIP, "no answer");
}

// ---------------------------------------------------------------- 12, 13 jaw and lift servos (checked with their sensors)
// Moves a little each way and watches the sensor. It also learns which pulse direction opens or raises.
Result servoSensorTest(uint8_t ch, bool side, int8_t &sign, const char *upWord, String &note) {
  if (!pcaFound) { note = "PCA9685 not found"; return R_SKIP; }
  if (side ? !sideFound : !topFound) { note = "its sensor is missing, so movement cannot be checked"; return R_SKIP; }
  float d = tofAvg(side, 7);
  if (d < 0) {
    note = String("did not move: its sensor has no steady reading (") + tofStatusName(tofLastStatus[side]) + ")" +
           (side ? ". Close the jaws a little from fully retracted and run it again" : "");
    return R_FAIL;
  }
  // Four short pushes: above stop, below, below, above. If it starts against one end of its travel,
  // the later pushes bring it back, so both directions are always seen.
  const int8_t dir[4] = {1, -1, -1, 1};
  float plusMax = 0, minusMax = 0, plusSum = 0, minusSum = 0;
  Serial.printf("  start %.0f mm\n", d);
  for (uint8_t i = 0; i < 4; i++) {
    servoPulse(ch, cal.stopUs[ch] + dir[i] * cal.moveUs);
    if (!waitOrAbort(450)) return R_SKIP;
    servoOff(ch); delay(200);
    float e = tofAvg(side, 7);
    if (e < 0) { note = String("sensor lost its target during the test (") + tofStatusName(tofLastStatus[side]) + ")"; return R_FAIL; }
    float ch_mm = e - d; d = e;
    Serial.printf("  push %s stop: %+.0f mm  (now %.0f mm)\n", dir[i] > 0 ? "above" : "below", ch_mm, e);
    if (dir[i] > 0) { plusSum += ch_mm; plusMax = max(plusMax, fabsf(ch_mm)); }
    else { minusSum += ch_mm; minusMax = max(minusMax, fabsf(ch_mm)); }
  }
  // a real push moves it 15..25 mm; the sensors wobble 3..6 mm on their own, so anything under 8 mm is not counted as a move
  const float MOVED_MM = 8;
  bool plusMoves = plusMax >= MOVED_MM, minusMoves = minusMax >= MOVED_MM;
  if (!plusMoves && !minusMoves) { note = "no movement seen: check the servo plug, the 6 V supply and the stop pulse"; return R_FAIL; }
  if (!plusMoves || !minusMoves) {
    note = String("only a pulse ") + (plusMoves ? "above" : "below") + " stop moves it: the stop pulse is off, run  findstop " + String(ch);
    return R_FAIL;
  }
  if ((plusSum > 0) == (minusSum > 0)) { note = "both pulses move it the same way: the stop pulse is far off, run  findstop " + String(ch); return R_FAIL; }
  sign = plusSum > 0 ? 1 : -1;
  note = String("moves both ways; a pulse ") + (sign > 0 ? "above" : "below") + " stop " + upWord + " (sign " + (sign > 0 ? "+1" : "-1") + ", type  save  to keep it)";
  return R_PASS;
}
void testJaw() {
  header(T_JAW);
  String note;
  Result r = servoSensorTest(SV_JAW, true, cal.jawOpenSign, "opens the jaws", note);
  setResult(T_JAW, r, note);
}
void testLift() {
  header(T_LIFT);
  String note;
  Result r = servoSensorTest(SV_LIFT, false, cal.liftUpSign, "raises the carriage", note);
  setResult(T_LIFT, r, note);
}

// ---------------------------------------------------------------- 15 pump relay (checked by ear and eye)
void testPump() {
  header(T_PUMP);
  Serial.println(F("  The pump relay switches on for 2 s. Listen for the relay click and watch the pump."));
  if (askYesNo("Pump outlet pointing somewhere safe?") != 1) { setResult(T_PUMP, R_SKIP, "not run"); return; }
  pumpSet(true);
  bool ok = waitOrAbort(2000);
  pumpSet(false);
  if (!ok) { setResult(T_PUMP, R_SKIP, "interrupted"); return; }
  int a = askYesNo("Did the relay click and the pump run?");
  if (a == 1) setResult(T_PUMP, R_PASS, "relay and pump work");
  else if (a == 0) setResult(T_PUMP, R_FAIL, "no click: check GPIO 4, the relay's VCC/GND and PUMP_ACTIVE_LOW. Click but no pump: check the pump's supply and COM/NO");
  else setResult(T_PUMP, R_SKIP, "no answer");
}

// ---------------------------------------------------------------- 14 belt servo (checked by eye)
void testBelt() {
  header(T_BELT);
  if (!pcaFound) { setResult(T_BELT, R_SKIP, "PCA9685 not found"); return; }
  Serial.println(F("  The belt will run one way for 2 s, stop, then the other way for 2 s."));
  servoPulse(SV_BELT, cal.stopUs[SV_BELT] + (cal.beltFwdSign > 0 ? cal.beltMoveUs : cal.beltRevUs));
  if (!waitOrAbort(2000)) { setResult(T_BELT, R_SKIP, "interrupted"); return; }
  servoOff(SV_BELT);
  if (!waitOrAbort(700)) { setResult(T_BELT, R_SKIP, "interrupted"); return; }
  servoPulse(SV_BELT, cal.stopUs[SV_BELT] - (cal.beltFwdSign > 0 ? cal.beltRevUs : cal.beltMoveUs));
  if (!waitOrAbort(2000)) { setResult(T_BELT, R_SKIP, "interrupted"); return; }
  servoOff(SV_BELT);
  int moved = askYesNo("Did the belt move, stop, then move the other way?");
  if (moved != 1) { setResult(T_BELT, moved == 0 ? R_FAIL : R_SKIP, moved == 0 ? "no movement: check the CH13 plug and the 6 V supply" : "no answer"); return; }
  int fwd = askYesNo("The FIRST run: did it carry things toward the brushes?");
  if (fwd >= 0) cal.beltFwdSign = fwd == 1 ? 1 : -1;
  setResult(T_BELT, R_PASS, String("runs both ways; forward is a pulse ") + (cal.beltFwdSign > 0 ? "above" : "below") + " stop (saved with  save)");
}

// ---------------------------------------------------------------- running them
void runTest(uint8_t id) {
  aborted = false;
  switch (id) {
    case T_I2C: testI2C(); break;
    case T_PCF: testPCF(); break;
    case T_BUTTONS: testButtons(); break;
    case T_SIDE: testTof(true); break;
    case T_TOP: testTof(false); break;
    case T_SIDE_SEE: testTofSees(true); break;
    case T_TOP_SEE: testTofSees(false); break;
    case T_DISPLAY: testDisplay(); break;
    case T_MOTOR_L: case T_MOTOR_R: case T_MOTOR_TOP: testMotor(id - T_MOTOR_L); break;
    case T_JAW: testJaw(); break;
    case T_LIFT: testLift(); break;
    case T_BELT: testBelt(); break;
    case T_PUMP: testPump(); break;
  }
  stopAll();
}

void runAllTests() {
  Serial.println();
  Serial.println(F("FULL TEST. Any key stops a test that is moving something; questions take y / n or START / STOP."));
  int ok = askYesNo("Brushes, jaws, carriage and belt clear to move?");
  if (ok != 1) { Serial.println(F("  Cancelled. Clear the machine and type  test  again.")); return; }
  calSave();                                         // keep a copy of the settings before the tests change any
  for (uint8_t i = 0; i < TEST_COUNT; i++) runTest(i);
  printReport();
  if (askYesNo("Save the directions the tests learned?") == 1) calSave();
}

void printReport() {
  uint8_t pass = 0, fail = 0, skip = 0;
  Serial.println();
  Serial.println(F("================ TEST REPORT ================"));
  for (uint8_t i = 0; i < TEST_COUNT; i++) {
    const char *r = results[i] == R_PASS ? "PASS" : results[i] == R_FAIL ? "FAIL" : results[i] == R_SKIP ? "skip" : "--";
    Serial.printf(" %2u  %-14s %-5s %s\n", i + 1, TEST_NAME[i], r, resultNote[i].c_str());
    if (results[i] == R_PASS) pass++; else if (results[i] == R_FAIL) fail++; else if (results[i] == R_SKIP) skip++;
  }
  Serial.printf(" %u passed, %u failed, %u skipped, %u not run\n", pass, fail, skip, TEST_COUNT - pass - fail - skip);
  Serial.println(F("============================================="));
  screenMessage(String(pass) + " pass  " + fail + " fail  " + skip + " skip", fail ? C_BAD : C_OK);
}

// Quick check at power-up: only the things that need no moving parts and no questions.
void bootCheck() {
  Serial.println(F("Power-up check:"));
  testI2C();
  testPCF();
  if (sideFound) testTof(true);
  if (topFound) testTof(false);
  calShow();
}
