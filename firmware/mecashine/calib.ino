// COPIED from firmware/mecashine_debug by sync_main.py. Do not edit here: edit it there and run sync_main.py.
// Calibration and closed-loop moves, using the distance sensors as feedback.
// The jaw servo is checked with the side sensor (it reads the gap to the reflector on the other jaw),
// and the lift servo with the top sensor (it reads the drop to the belt).

// ---------------------------------------------------------------- moving to a reading
float moveBoostMax = 150.0f;                           // homing sets it to 0: home is the end of travel, so no extra push against it
// Drives a servo until its sensor reads target mm (within 2 mm). Returns false on time-out or interrupt.
// risesWithPositive: the sign that makes the reading go up (jawOpenSign or liftUpSign).
bool moveToReading(uint8_t ch, bool side, int8_t risesWithPositive, float target, uint32_t timeoutMs) {
  if (!pcaFound) { Serial.println(F("  PCA9685 not found")); return false; }
  if (side ? !sideFound : !topFound) { Serial.println(F("  sensor not found")); return false; }
  const float tol = side ? 5.0f : 3.0f;               // the side sensor wobbles more than the top one
  uint32_t t0 = millis(), lastPrint = 0, stallT = millis();
  int stallR = -1000;
  uint32_t lostT = 0;                                  // when the readings went bad; 0 while they are good
  // Push harder when stuck (the user's idea): near the target the proportional push can fall inside the servo's still band
  // (the lift only moves down above ~1460 us with its stop at 1400), so every 100 ms without progress adds BOOST_STEP us,
  // up to BOOST_MAX. The boost is kept once it moves, so it does not sink back into the still band.
  const float BOOST_STEP = 5.0f, BOOST_MAX = moveBoostMax;
  float boost = 0, bestErr = 1e9;
  int lastSign = 0;
  uint32_t progressT = millis(), boostT = millis();
  while (millis() - t0 < timeoutMs) {
    int r = (int)roundf(tofAvg(side, 3));              // median of 3, so one wobbly reading does not stop or flip it
    // a few bad readings are normal at the far end of the side sensor's range: pause the servo and wait, give up after 600 ms
    if (r < 0) {
      servoStop(ch);
      if (!lostT) lostT = millis();
      if (millis() - lostT > 600) {
        servoOff(ch);
        Serial.printf("  sensor lost the target for 0.6 s (%s), stopped\n", tofStatusName(tofLastStatus[side]));
        return false;
      }
      if (stopRequested()) { stopAll(); aborted = true; Serial.println(F("  stopped by the user")); return false; }
      continue;
    }
    if (lostT) { stallT += millis() - lostT; progressT += millis() - lostT; lostT = 0; }   // the pause does not count as a stall
    float err = target - r;
    if (fabsf(err) <= tol) { servoOff(ch); Serial.printf("  reached %d mm (target %.0f)%s\n", r, target, boost > 0 ? String(" with +" + String((int)boost) + " us boost").c_str() : ""); return true; }
    int sign = err > 0 ? 1 : -1;                         // passed the target: drop the boost so it does not swing back hard
    if (lastSign && sign != lastSign) { boost = 0; bestErr = fabsf(err); progressT = millis(); }
    lastSign = sign;
    // progress = the distance to the target shrank by more than the sensor's wobble
    if (fabsf(err) < bestErr - tol) { bestErr = fabsf(err); progressT = millis(); }
    if (millis() - progressT > 100 && millis() - boostT >= 100 && boost < BOOST_MAX) { boost += BOOST_STEP; boostT = millis(); }
    // stall guard: no progress for 1.5 s even at full boost means it is against the end of its travel (or jammed)
    if (abs(r - stallR) > tol) { stallR = r; stallT = millis(); }
    else if (millis() - stallT > 1500 && boost >= BOOST_MAX) {   // with BOOST_MAX 0 (homing) this is the plain 1.5 s stall
      servoOff(ch);
      Serial.printf("  stopped: no movement for 1.5 s at %d mm, even pushing hard (end of travel, or jammed)\n", r);
      return false;
    }
    // proportional, with a floor so it still moves when close (360-degree servos have a still band round the stop pulse)
    float u = constrain(err * 4.0f, -(float)cal.moveUs, (float)cal.moveUs), floorUs = cal.moveUs / 2.0f;
    if (fabsf(u) < floorUs) u = u < 0 ? -floorUs : floorUs;
    u += u < 0 ? -boost : boost;
    servoOffset(ch, (int)(risesWithPositive * u));
    if (millis() - lastPrint > 300) { lastPrint = millis(); Serial.printf("    reading %d mm\n", r); }
    if (stopRequested()) { stopAll(); aborted = true; Serial.println(F("  stopped by the user")); return false; }
  }
  servoOff(ch);
  Serial.println(F("  time-out: the reading did not reach the target"));
  return false;
}
bool jawTo(float mm) { Serial.printf("Jaws to a side reading of %.0f mm\n", mm); return moveToReading(SV_JAW, true, cal.jawOpenSign, mm, 15000); }
bool liftTo(float mm) { Serial.printf("Carriage to a top reading of %.0f mm\n", mm); return moveToReading(SV_LIFT, false, cal.liftUpSign, mm, 15000); }

// ---------------------------------------------------------------- home: the first step of the start-up calibration
// Home is the end of travel (jaws fully open, carriage fully up). The reading there drifts by 10-20 mm between sessions on the
// side sensor (long range mode, small reflector), so a move that stops at the end of its travel with the reading near the
// home value also counts as home, the way a limit switch would. A jam far from home still fails.
constexpr float HOME_NEAR_MM = 30.0f;
// Drives only TOWARD home (open / up) until the end of travel: no reading can make it go the other way. Before 2026-11-03
// homing aimed at the saved reading, so a sensor that sometimes read too high (top: 220 / 270) drove the carriage DOWN to
// "reach" home, a little lower each time. The end of travel is when the reading has not risen for 1 s, and no sooner than the
// full travel would take at the measured speed; the reading is only used to check that it really got near home.
bool homeOne(bool side) {
  if (!side) {
    // The carriage's home is not the end of travel any more (2026-11-03): it is lifthome (150 mm above the belt), found by the
    // top sensor on the empty belt now that the yarn is out of its beam. It always arrives from below, so gravity and the
    // gears' play leave it in the same place every time.
    Serial.printf("Carriage home (top reading %u mm, from below)\n", cal.liftHomeMm);
    float r = tofAvg(false, 5);
    if (r > cal.liftHomeMm + 5 && !liftTo(cal.liftHomeMm - 15)) return false;
    return liftTo(cal.liftHomeMm);
  }
  const uint8_t ch = side ? SV_JAW : SV_LIFT;
  const int8_t sign = side ? cal.jawOpenSign : cal.liftUpSign;
  const float home = side ? cal.jawHomeMm : cal.liftHomeMm, tol = side ? 5.0f : 3.0f;
  const float speed = side ? spd.jawOpen : spd.liftUp;
  if (!pcaFound) { Serial.println(F("  PCA9685 not found")); return false; }
  Serial.printf("%s home (to the end of travel)\n", side ? "Jaws" : "Carriage");
  float r0 = tofAvg(side, 3);
  uint32_t minMs = (speed > 0 && r0 > 0 && r0 < home) ? (uint32_t)((home - r0) / speed * 1000.0f) : 0;
  servoOffset(ch, sign * (int)cal.moveUs);
  uint32_t t0 = millis(), progressT = t0, lastPrint = 0;
  float best = r0 > 0 ? r0 : -1;
  while (true) {
    float r = tofAvg(side, 3);
    if (r > 0 && (best < 0 || r > best + tol)) { best = r; progressT = millis(); }
    if (millis() - lastPrint > 300 && r > 0) { lastPrint = millis(); Serial.printf("    reading %.0f mm\n", r); }
    if (millis() - t0 >= minMs && millis() - progressT > 1000) break;    // not rising any more: at the end of travel
    if (millis() - t0 > 8000) { servoOff(ch); Serial.println(F("  time-out: still not at the end of travel after 8 s")); return false; }
    if (stopRequested()) { servoOff(ch); aborted = true; Serial.println(F("  stopped by the user")); return false; }
  }
  servoOff(ch);
  float r = tofAvg(side, 9);
  if (r > 0 && r > home - HOME_NEAR_MM) {
    Serial.printf("  at the end of its travel, reading %.0f mm (saved home %.0f): home\n", r, home);
    return true;
  }
  Serial.printf("  stopped moving at a reading of %.0f mm, far from home (%.0f): jammed, or the sensor reads wrong\n", r, home);
  return false;
}
bool homeAll() {
  Serial.println(F("Homing: jaws fully open, carriage to its home."));
  machineHomed = false;
  bool a = homeOne(true);
  if (aborted) return false;
  bool b = homeOne(false);
  Serial.printf("  jaws %s, carriage %s\n", a ? "home" : "NOT home", b ? "home" : "NOT home");
  machineHomed = a && b;
  return a && b;
}

// ---------------------------------------------------------------- stop pulse
// The stop pulse of a 360-degree servo drifts from 1500 us. For the jaw and lift servos the sensor can find it:
// try pulses across a range, measure how fast the reading changes at each, and take the middle of the
// band where it does not move at all.
// us = 0 measures with no pulse at all, which gives the sensor's own noise as a "speed".
// Medians of 7 readings at each end, so the side sensor's wobble (several mm) does not look like movement.
float speedAt(uint8_t ch, bool side, uint16_t us, uint16_t ms) {
  float d0 = tofAvg(side, 7);
  if (us) servoPulse(ch, us); else servoOff(ch);
  if (!waitOrAbort(ms)) return NAN;
  servoOff(ch); delay(120);
  float d1 = tofAvg(side, 7);
  if (d0 < 0 || d1 < 0) return NAN;
  return (d1 - d0) * 1000.0f / ms;
}
bool findStopWithSensor(uint8_t ch, bool side) {
  Serial.printf("Finding the stop pulse of the %s servo with the %s sensor\n", SERVO_NAME[ch], side ? "side" : "top");
  Serial.println(F("  Put it near the middle of its travel first (by hand, power off, or with  servo ). Any key stops."));
  const uint16_t MS = 600;
  // 1. the sensor's noise with the servo standing still sets what counts as "not moving"
  float noise = 0;
  for (uint8_t i = 0; i < 4; i++) {
    float v = speedAt(ch, side, 0, MS);
    if (isnan(v)) { if (!aborted) Serial.println(F("  no steady reading at rest: move it nearer the middle, or check  tofraw")); return false; }
    noise = max(noise, fabsf(v));
  }
  const float still = max(3.0f, 1.5f * noise);
  Serial.printf("  sensor noise at rest up to %.1f mm/s, so below %.1f mm/s counts as still\n", noise, still);
  // 2. pulses in pairs, one above and one below 1500 us, from far out to close in, so the movement of
  // each pair mostly cancels and the servo stays near where it started instead of running into an end
  const int centre = 1500, span = 150, step = 10, N = 2 * span / step + 1;
  float v[N];
  for (int i = 0; i < N; i++) v[i] = NAN;
  for (int k = span; k >= 0; k -= step) {
    for (int s = 1; s >= -1; s -= 2) {
      if (k == 0 && s < 0) break;
      int us = centre + s * k, i = (us - (centre - span)) / step;
      v[i] = speedAt(ch, side, us, MS);
      if (isnan(v[i])) { if (aborted) return false; Serial.printf("  %4d us: no reading\n", us); continue; }
      Serial.printf("  %4d us: %+6.1f mm/s\n", us, v[i]);
    }
  }
  servoOff(ch);
  // 3. the still band is the unbroken run of still pulses around the slowest one, so one noisy pulse far out does not widen it
  int best = -1;
  for (int i = 0; i < N; i++) if (!isnan(v[i]) && (best < 0 || fabsf(v[i]) < fabsf(v[best]))) best = i;
  if (best < 0) { Serial.println(F("  no readings at all")); return false; }
  int lo = best, hi = best;
  bool found = fabsf(v[best]) < still;
  if (found) {
    while (lo > 0 && (isnan(v[lo - 1]) || fabsf(v[lo - 1]) < still)) lo--;
    while (hi < N - 1 && (isnan(v[hi + 1]) || fabsf(v[hi + 1]) < still)) hi++;
  }
  int loUs = centre - span + lo * step, hiUs = centre - span + hi * step;
  uint16_t stop = (loUs + hiUs) / 2;
  if (found) Serial.printf("  still from %d to %d us; stop pulse set to %u us (was %u). Type  save  to keep it.\n", loUs, hiUs, stop, cal.stopUs[ch]);
  else Serial.printf("  never fully still; using the slowest pulse, %u us (was %u). Check it with  servo  before saving.\n", stop, cal.stopUs[ch]);
  if (found && (loUs == centre - span || hiUs == centre + span))
    Serial.println(F("  the still band reaches the end of the range: it may have been jammed at the end of its travel. Re-run from mid-travel."));
  cal.stopUs[ch] = stop;
  return found;
}
// The belt has no sensor watching it all the time: step slowly through pulses and mark both edges of the still range by eye.
// The stop pulse is the middle of that range, not its first edge, so it stays still even if the servo warms up or drifts.
void findStopByEye(uint8_t ch) {
  Serial.printf("Finding the stop pulse of the %s servo by eye.\n", SERVO_NAME[ch]);
  Serial.println(F("  The pulse steps up 4 us every 1.5 s, from 1400 to 1600. It runs one way, slows, stands still, then runs the other way."));
  Serial.println(F("  Push START (or type y) when it STANDS STILL, then again when it STARTS MOVING the other way."));
  Serial.println(F("  If it is already still at the start, push START straight away. Any other key cancels."));
  buttonPressed(btnStart);
  int lo = -1, hi = -1;
  for (int us = 1400; us <= 1600 && hi < 0; us += 4) {
    servoPulse(ch, us);
    Serial.printf("  %d us\n", us);
    uint32_t t0 = millis();
    while (millis() - t0 < 1500) {
      if (buttonPressed(btnStart) || (Serial.available() && tolower(Serial.peek()) == 'y')) {
        while (Serial.available()) Serial.read();
        if (lo < 0) { lo = us; Serial.printf("  still from %d us. Push again when it starts moving.\n", us); }
        else { hi = us - 4; break; }               // it moved at this pulse, so the last still pulse was the one before
      }
      else if (Serial.available() || buttonPressed(btnStop)) { while (Serial.available()) Serial.read(); servoOff(ch); Serial.println(F("  cancelled")); return; }
      delay(5);
    }
  }
  servoOff(ch);
  if (lo < 0) { Serial.println(F("  reached the end without an answer")); return; }
  if (hi < lo) hi = lo;                            // second push not given: use the first edge only
  cal.stopUs[ch] = (lo + hi) / 2;
  Serial.printf("  still from %d to %d us; stop pulse set to %u us. Type  save  to keep it.\n", lo, hi, cal.stopUs[ch]);
}
void findStop(uint8_t ch) {
  if (!pcaFound) { Serial.println(F("PCA9685 not found")); return; }
  if (ch == SV_JAW && sideFound) findStopWithSensor(ch, true);
  else if (ch == SV_LIFT && topFound) findStopWithSensor(ch, false);
  else findStopByEye(ch);
  stopAll();
}

// ---------------------------------------------------------------- speeds
// Times the jaws and the carriage at the move pulse, in the units the polishing pass uses: mm of sensor reading per second.
// Each direction separately (the carriage drops faster than it climbs), 3 short runs each way from mid-travel so neither
// end of travel cuts a run short, keeping the middle result of the three.
constexpr uint16_t SPEED_RUN_MS = 800;
float median3(float a, float b, float c) { return max(min(a, b), min(max(a, b), c)); }
// one servo: runs (toward the lower reading, toward the higher) 3 times; returns false if a reading failed
bool timeBothWays(uint8_t ch, bool side, int8_t risesWithPositive, float &down, float &up) {
  float d[3], u[3];
  for (uint8_t i = 0; i < 3; i++) {
    d[i] = speedAt(ch, side, cal.stopUs[ch] - risesWithPositive * cal.moveUs, SPEED_RUN_MS);
    u[i] = speedAt(ch, side, cal.stopUs[ch] + risesWithPositive * cal.moveUs, SPEED_RUN_MS);
    if (isnan(d[i]) || isnan(u[i])) return false;
    Serial.printf("    run %u:  %+6.1f mm/s   %+6.1f mm/s\n", i + 1, d[i], u[i]);
  }
  down = fabsf(median3(d[0], d[1], d[2]));
  up = fabsf(median3(u[0], u[1], u[2]));
  return true;
}
void measureSpeeds() {
  Serial.println(F("Measuring jaw and carriage speeds at the move pulse (about 30 s)."));
  if (!homeAll()) { Serial.println(F("  could not home, so the speeds were not measured")); return; }
  bool ok = true;
  Serial.println(F("  jaws: to mid-travel, then close / open 3 times"));
  jawTo(cal.jawHomeMm - 60);
  float jc = 0, jo = 0, ld = 0, lu = 0;
  if (aborted || !timeBothWays(SV_JAW, true, cal.jawOpenSign, jc, jo)) ok = false;
  if (ok) {
    Serial.println(F("  carriage: to mid-travel, then lower / raise 3 times"));
    liftTo(cal.liftHomeMm - 50);
    if (aborted || !timeBothWays(SV_LIFT, false, cal.liftUpSign, ld, lu)) ok = false;
  }
  stopAll();
  if (!ok) { Serial.println(aborted ? F("  stopped") : F("  a sensor lost its reading during a run; try again (tofraw)")); homeAll(); return; }
  spd = {jc, jo, ld, lu};
  cal.jawMmPerS = (jc + jo) / 2;
  cal.liftMmPerS = (ld + lu) / 2;
  Serial.println(F("  RESULT (mm of sensor reading per second)"));
  Serial.printf("    jaws      closing %5.1f   opening %5.1f\n", jc, jo);
  Serial.printf("    carriage  lowering %5.1f  raising %5.1f\n", ld, lu);
  if (jc > 0 && jo > 0 && max(jc, jo) / min(jc, jo) > 1.5f) Serial.println(F("    the jaws are much faster one way: their stop pulse may be off (findstop 2)"));
  Serial.println(F("  Type  save  to keep them."));
  homeAll();
}

// ---------------------------------------------------------------- belt speed
// Put a shoe (or a box) on the belt before the side sensor. The belt runs forward; the time between the
// side sensor and the top sensor seeing it gives the speed.
void measureBeltSpeed() {
  if (!pcaFound || !sideFound || !topFound) { Serial.println(F("Needs the PCA9685 and both sensors")); return; }
  Serial.println(F("Belt speed: put a shoe on the belt before the side sensor, jaws open, carriage up."));
  if (askYesNo("Shoe on the belt, jaws open, carriage up?") != 1) return;
  float sideBase = tofAvg(true, 5), topBase = tofAvg(false, 5);
  Serial.printf("  empty readings: side %.0f mm, top %.0f mm\n", sideBase, topBase);
  beltDrive(1.0f);
  uint32_t t0 = millis(), tSide = 0, tTop = 0;
  while (millis() - t0 < 25000 && !tTop) {
    int s = tofRead(true), t = tofRead(false);
    if (!tSide && s > 0 && s < sideBase - 25) { tSide = millis(); Serial.printf("  side sensor sees it at %.2f s\n", (tSide - t0) / 1000.0); }
    if (tSide && !tTop && t > 0 && t < topBase - 25) { tTop = millis(); Serial.printf("  top sensor sees it at %.2f s\n", (tTop - t0) / 1000.0); }
    if (stopRequested()) { aborted = true; break; }
  }
  servoOff(SV_BELT);
  if (!tSide || !tTop) { Serial.println(F("  did not see the shoe pass both sensors")); return; }
  cal.beltMmPerS = SENSOR_SPACING_MM * 1000.0f / (tTop - tSide);
  Serial.printf("  belt speed %.1f mm/s over %.0f mm. Type  save  to keep it.\n", cal.beltMmPerS, SENSOR_SPACING_MM);
}

// ---------------------------------------------------------------- matching the belt's backward speed to its forward speed
// A 360-degree servo rarely runs at the same speed both ways for the same offset, so forward keeps its offset (beltmove)
// and the backward offset is tuned. Each pass times the shoe's toe crossing both sensor beams, 240 mm apart:
// forward, the toe enters the side beam then the top beam; backward, the toe leaves the top beam then the side beam.
constexpr int BELT_DEAD_US = 90;        // about half the belt servo's still range (1310..1500 us), for the first correction

// The next backward offset to try, from this pass (rev, vR) and the one before (prevRev, prevV; prevV < 0 if none).
int nextBeltRev(int rev, int prevRev, float vF, float vR, float prevV) {
  int next;
  if (prevV > 0 && fabsf(vR - prevV) > 0.5f) next = rev + (int)roundf((vF - vR) * (rev - prevRev) / (vR - prevV));  // from the last two passes
  else next = BELT_DEAD_US + (int)roundf((rev - BELT_DEAD_US) * vF / vR);   // first guess: speed grows with the pulse past the still range
  next = constrain(next, rev - 60, rev + 60);       // no wild jumps
  return constrain(next, 40, 600);
}

// Waits until a sensor sees the shoe (wantSee) or stops seeing it, two readings in a row. Returns millis(), or 0 on time-out or a key.
uint32_t waitBeltEdge(bool side, bool wantSee, float base, uint32_t ms) {
  uint32_t t0 = millis(); uint8_t n = 0;
  while (millis() - t0 < ms) {
    int r = tofRead(side);
    bool see = r > 0 && r < base - 40, clear = r < 0 || r > base - 15;
    if (wantSee ? see : clear) { if (++n >= 2) return millis(); } else n = 0;
    if (stopRequested()) { aborted = true; return 0; }
  }
  return 0;
}

// One timed pass. Returns the speed in mm/s, or -1 if the shoe was not seen at both sensors.
float beltPass(bool forward, float sideBase, float topBase) {
  uint32_t t1 = 0, t2 = 0;
  beltDrive(forward ? 1.0f : -1.0f);
  if (forward) {
    t1 = waitBeltEdge(true, true, sideBase, 15000);
    if (t1) t2 = waitBeltEdge(false, true, topBase, 15000);
    if (t2) waitOrAbort(500);                       // a little further, so the backward pass starts at full speed
  } else {
    if (waitBeltEdge(false, true, topBase, 15000)) t1 = waitBeltEdge(false, false, topBase, 15000);
    if (t1 && waitBeltEdge(true, true, sideBase, 15000)) t2 = waitBeltEdge(true, false, sideBase, 15000);
    if (t2) waitOrAbort(1000);                      // back past the side sensor, ready for the next forward pass
  }
  servoOff(SV_BELT);
  delay(300);
  if (!t1 || !t2 || t2 <= t1) return -1;
  return SENSOR_SPACING_MM * 1000.0f / (t2 - t1);
}

void beltMatch() {
  if (!pcaFound || !sideFound || !topFound) { Serial.println(F("Needs the PCA9685 and both sensors")); return; }
  Serial.println(F("Belt speed matching: the shoe runs forward past both sensors and back, and the backward pulse is adjusted"));
  Serial.println(F("until both directions run at the same speed. Forward speed is set by  set beltmove ; it is not changed here."));
  Serial.println(F("Put a shoe on the belt a little before the side sensor, out of both beams. Jaws open, carriage up."));
  if (askYesNo("Shoe in place, jaws open, carriage up?") != 1) return;
  float sideBase = tofAvg(true, 9), topBase = tofAvg(false, 9);
  Serial.printf("  empty readings: side %.0f mm, top %.0f mm\n", sideBase, topBase);
  if (sideBase < 0 || topBase < 0) { Serial.println(F("  a sensor has no steady empty reading; fix that first (tofraw)")); return; }
  int rev = cal.beltRevUs, prevRev = -1; float prevV = -1, vF = -1, vR = -1;
  bool matched = false;
  int bestRev = rev; float bestDiff = 1e9;
  for (uint8_t it = 1; it <= 6 && !matched; it++) {
    vF = beltPass(true, sideBase, topBase);
    if (vF <= 0) { Serial.println(aborted ? F("  stopped") : F("  forward: the shoe was not seen at both sensors")); return; }
    vR = beltPass(false, sideBase, topBase);
    if (vR <= 0) { Serial.println(aborted ? F("  stopped") : F("  backward: the shoe was not seen at both sensors")); return; }
    float diff = (vR - vF) / vF * 100.0f;
    Serial.printf("  pass %u: forward %.1f mm/s (+%u us)   backward %.1f mm/s (-%d us)   difference %+.1f %%\n",
                  it, vF, cal.beltMoveUs, vR, rev, diff);
    if (fabsf(diff) < bestDiff) { bestDiff = fabsf(diff); bestRev = rev; }
    if (fabsf(diff) <= 3.0f) { matched = true; break; }
    int next = nextBeltRev(rev, prevRev, vF, vR, prevV);
    prevRev = rev; prevV = vR; rev = next;
    cal.beltRevUs = rev;
  }
  cal.beltRevUs = bestRev;                         // the closest pass, not an untried guess
  cal.beltMmPerS = (vF + vR) / 2;
  Serial.printf("  %s: forward +%u us, backward -%u us, belt speed %.1f mm/s\n",
                matched ? "MATCHED within 3 %" : "not matched after 6 passes (closest so far kept)", cal.beltMoveUs, cal.beltRevUs, cal.beltMmPerS);
  if (askYesNo("Save this?") == 1) calSave();
}

// Checks the saved belt settings without changing them: 3 round trips, then each direction's mean speed and how much it varies.
void beltCheck() {
  if (!pcaFound || !sideFound || !topFound) { Serial.println(F("Needs the PCA9685 and both sensors")); return; }
  Serial.println(F("Belt check: 3 round trips with the saved settings, nothing is changed."));
  Serial.println(F("Put a shoe on the belt a little before the side sensor, out of both beams. Jaws open, carriage up."));
  if (askYesNo("Shoe in place, jaws open, carriage up?") != 1) return;
  float sideBase = tofAvg(true, 9), topBase = tofAvg(false, 9);
  Serial.printf("  empty readings: side %.0f mm, top %.0f mm\n", sideBase, topBase);
  if (sideBase < 0 || topBase < 0) { Serial.println(F("  a sensor has no steady empty reading; fix that first (tofraw)")); return; }
  const uint8_t N = 3;
  float f[N], r[N];
  for (uint8_t i = 0; i < N; i++) {
    f[i] = beltPass(true, sideBase, topBase);
    if (f[i] <= 0) { Serial.println(aborted ? F("  stopped") : F("  forward: the shoe was not seen at both sensors")); return; }
    r[i] = beltPass(false, sideBase, topBase);
    if (r[i] <= 0) { Serial.println(aborted ? F("  stopped") : F("  backward: the shoe was not seen at both sensors")); return; }
    Serial.printf("  trip %u: forward %.1f mm/s   backward %.1f mm/s\n", i + 1, f[i], r[i]);
  }
  float fm = 0, rm = 0, fmin = 1e9, fmax = 0, rmin = 1e9, rmax = 0;
  for (uint8_t i = 0; i < N; i++) { fm += f[i] / N; rm += r[i] / N; fmin = min(fmin, f[i]); fmax = max(fmax, f[i]); rmin = min(rmin, r[i]); rmax = max(rmax, r[i]); }
  float diff = (rm - fm) / fm * 100.0f, fvar = (fmax - fmin) / fm * 100.0f, rvar = (rmax - rmin) / rm * 100.0f;
  Serial.printf("  forward  %.1f mm/s (varies %.1f %%)\n", fm, fvar);
  Serial.printf("  backward %.1f mm/s (varies %.1f %%)\n", rm, rvar);
  Serial.printf("  backward vs forward %+.1f %%   saved belt speed %.1f mm/s\n", diff, cal.beltMmPerS);
  if (fabsf(diff) <= 3 && fvar <= 5 && rvar <= 5) Serial.println(F("  PASS: both directions match and repeat"));
  else if (fvar > 5 || rvar > 5) Serial.println(F("  the speed changes from trip to trip: check belt tension, slipping, and that the servo supply holds 6 V"));
  else Serial.println(F("  the directions differ: run  beltmatch  again"));
}

// ---------------------------------------------------------------- the same with an empty belt: a tape mark and a ruler
// The sensors cannot see an empty belt move, so the user measures how far a tape mark travels in a fixed time each way.
constexpr uint32_t BELT_TAPE_MS = 5000;

// Reads a number typed in the Serial Monitor. NAN if a STOP, an empty line or a time-out.
float readNumber(const char *prompt, uint32_t timeoutMs) {
  Serial.printf("  ? %s  (type the number, Enter; STOP cancels)\n", prompt);
  while (Serial.available()) Serial.read();
  char buf[16]; uint8_t len = 0; uint32_t t0 = millis();
  while (millis() - t0 < timeoutMs) {
    if (buttonPressed(btnStop)) return NAN;
    while (Serial.available()) {
      char c = Serial.read();
      if (c == '\r') continue;
      if (c == '\n') { buf[len] = 0; if (!len) return NAN; char *end; float v = strtof(buf, &end); return end == buf ? NAN : v; }
      if (len < sizeof(buf) - 1) buf[len++] = c;
    }
    delay(5);
  }
  return NAN;
}

// Runs the belt BELT_TAPE_MS one way and asks how far the tape mark moved. Speed in mm/s, or -1 if cancelled.
float beltTapeRun(bool forward) {
  Serial.printf("  running %s for %.0f s...\n", forward ? "FORWARD (toward the brushes)" : "BACKWARD", BELT_TAPE_MS / 1000.0f);
  beltDrive(forward ? 1.0f : -1.0f);
  bool ok = waitOrAbort(BELT_TAPE_MS);
  servoOff(SV_BELT);
  if (!ok) return -1;
  float mm = readNumber("How many mm did the tape mark move?", 120000);
  if (isnan(mm) || mm <= 0) return -1;
  return mm * 1000.0f / BELT_TAPE_MS;
}

void beltTape() {
  if (!pcaFound) { Serial.println(F("PCA9685 not found")); return; }
  Serial.println(F("Belt speed with an EMPTY belt. Put a piece of tape across the belt and a ruler or tape measure beside it."));
  Serial.println(F("The belt runs 5 s forward, you type how far the mark moved; then 5 s back, the same. The backward"));
  Serial.println(F("pulse is adjusted until both match. Measure to the same edge of the tape each time."));
  if (askYesNo("Tape on the belt, ruler ready, belt empty?") != 1) return;
  int rev = cal.beltRevUs, prevRev = -1, bestRev = rev; float prevV = -1, vF = -1, vR = -1, bestDiff = 1e9;
  bool matched = false;
  for (uint8_t it = 1; it <= 6 && !matched; it++) {
    vF = beltTapeRun(true);
    if (vF <= 0) { Serial.println(F("  cancelled")); return; }
    vR = beltTapeRun(false);
    if (vR <= 0) { Serial.println(F("  cancelled")); return; }
    float diff = (vR - vF) / vF * 100.0f;
    Serial.printf("  round %u: forward %.1f mm/s (+%u us)   backward %.1f mm/s (-%d us)   difference %+.1f %%\n",
                  it, vF, cal.beltMoveUs, vR, rev, diff);
    if (fabsf(diff) < bestDiff) { bestDiff = fabsf(diff); bestRev = rev; }
    if (fabsf(diff) <= 3.0f) { matched = true; break; }
    int next = nextBeltRev(rev, prevRev, vF, vR, prevV);
    prevRev = rev; prevV = vR; rev = next;
    cal.beltRevUs = rev;
    Serial.printf("  backward pulse changed to -%d us; next round\n", rev);
  }
  cal.beltRevUs = bestRev;
  cal.beltMmPerS = (vF + vR) / 2;
  Serial.printf("  %s: forward +%u us, backward -%u us, belt speed %.1f mm/s\n",
                matched ? "MATCHED within 3 %" : "not matched after 6 rounds (closest kept)", cal.beltMoveUs, cal.beltRevUs, cal.beltMmPerS);
  if (askYesNo("Save this?") == 1) calSave();
}

// ---------------------------------------------------------------- the whole calibration, as the main program will do it at start-up
void calibrateAll() {
  Serial.println(F("FULL CALIBRATION: stop pulses, directions, home, speeds."));
  if (askYesNo("Belt empty, jaws and carriage clear to move?") != 1) return;
  if (sideFound) { findStop(SV_JAW); if (aborted) return; }
  if (topFound) { findStop(SV_LIFT); if (aborted) return; }
  runTest(T_JAW); if (aborted) return;
  runTest(T_LIFT); if (aborted) return;
  measureSpeeds(); if (aborted) return;
  calShow();
  if (askYesNo("Save this calibration?") == 1) calSave();
}
