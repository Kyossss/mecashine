// COPIED from firmware/mecashine_debug by sync_main.py. Do not edit here: edit it there and run sync_main.py.
// ================================================================ stage 2: polishing pass with the side brushes, following the shoe live
// No measuring pass first. The side sensor sits on one jaw, 71 mm before the brushes, and reads the gap from the jaw to the
// side of the shoe. Each reading is turned into the shoe's half-width (jaw / 2 - reading) and stored by its place along the
// shoe; 71 mm of belt travel later that part of the shoe is at the brushes, and the jaws close to it.
// While the shoe is in the beam the jaw position comes from time and the measured jaw speeds (spd); it is re-checked by the
// sensor whenever the beam sees the reflector. An error in that estimate goes into the stored width and into the jaw's
// position alike, so it cancels: only how much it drifts in the 2 s between reading a part of the shoe and polishing it counts.
// The grip (gripMm) is the side reading, on a straight-sided box, with the yarn pressing the way you want: gripcal finds it.
constexpr float BRUSH_R_MM = 26.0f;       // side brush radius (52 mm chenille brush)
constexpr float JAW_MIN_MM = 108.0f;      // never aim the jaws closer than this side reading (fully closed reads ~104)
constexpr float JAW_DEAD_MM = 3.0f;       // stop the jaw within this of its target
constexpr float OPEN_EARLY_S = 0.4f;      // look this far ahead and open early for a wider part, so it never presses harder
constexpr float NO_TOE_MM = 700.0f;       // give up if the belt has run this far and the side sensor has not seen a shoe
const int8_t BRUSH_DIR[2] = {1, -1};
float liveHeelMm = -1;                    // the shoe's length once the heel has passed the sensor, -1 before
float jawOpenMm = 217;                    // side reading with the jaws at the end of their travel, measured at the start of each pass      // side brushes L and R turn opposite ways, so their sideways push on the shoe cancels

// half-width at a slot, filling small gaps between readings by straight lines; NAN outside the shoe or not read yet
float halfWAt(int i) {
  if (i < 0 || i >= PROF_N) return NAN;
  if (!isnan(shoe.halfW[i])) return shoe.halfW[i];
  int a = i, b = i;
  while (a > 0 && isnan(shoe.halfW[a])) a--;
  while (b < PROF_N - 1 && isnan(shoe.halfW[b])) b++;
  if (isnan(shoe.halfW[a]) || isnan(shoe.halfW[b]) || b - a > 10) return NAN;   // more than 20 mm missing: not inside the shoe
  return shoe.halfW[a] + (shoe.halfW[b] - shoe.halfW[a]) * (i - a) / (b - a);
}

// Side reading wanted with the brush axes at s mm from the toe. A round brush touches the widest part of the shoe within its
// own radius, not just the slice level with its axis; then the jaws close until the reading on that part would be the grip.
float liveTarget(float s) {
  float best = -1e9;
  int c = (int)roundf(s / PROF_STEP_MM);
  const int k0 = (int)(BRUSH_R_MM / PROF_STEP_MM);
  for (int k = -k0; k <= k0; k++) {
    float w = halfWAt(c + k);
    float u = k * PROF_STEP_MM;
    if (isnan(w) || fabsf(u) > BRUSH_R_MM) continue;
    best = max(best, w + sqrtf(BRUSH_R_MM * BRUSH_R_MM - u * u) - BRUSH_R_MM);   // how far the shoe reaches toward the brush line
  }
  if (best < -1e8) return (liveHeelMm >= 0 && s - BRUSH_R_MM > liveHeelMm) ? JAW_MIN_MM : jawOpenMm;   // behind the heel: close, to brush its back
  return constrain(2 * (best + gripMm), JAW_MIN_MM, jawOpenMm);
}

// ramps the two side brushes up over 0.6 s: a hard start draws a current surge that can reset the distance sensors
void brushesSoftStart(int pct) {
  for (int i = 1; i <= 12; i++) { for (uint8_t m = 0; m < 2; m++) motorRun(m, BRUSH_DIR[m] * pct * i / 12); delay(50); }
}

// Do the brush motors upset the distance sensors? 30 readings from each with the motors off, then with all three running.
NoiseCount noiseSample(bool side) {
  NoiseCount c = {0, 0, 0};
  for (uint8_t i = 0; i < 30; i++) {
    int r = tofRead(side);
    if (r > 0) c.ok++; else if (tofLastStatus[side] > 5) c.silent++; else c.bad++;
  }
  return c;
}
// Each motor on its own, then all three, so the one that upsets a sensor can be found.
void noiseRow(const char *name, const NoiseCount &s, const NoiseCount &t) {
  Serial.printf("  %-18s side %2u ok %2u bad %2u silent    top %2u ok %2u bad %2u silent\n", name, s.ok, s.bad, s.silent, t.ok, t.bad, t.silent);
}
void noiseTest(int pct) {
  if (!pcfFound) { Serial.println(F("PCF8575 not found, so the motors cannot run")); return; }
  Serial.printf("Noise test at %d %%: 30 readings from each sensor with the motors off, then with each motor on its own, then all three.\n", pct);
  Serial.println(F("  The brushes will spin: keep hands clear."));
  if (askYesNo("Clear to spin the brush motors?") != 1) return;
  const char *name[4] = {"side brush L only", "side brush R only", "top roller only", "all three"};
  NoiseCount s = noiseSample(true), t = noiseSample(false);
  Serial.println();
  noiseRow("motors off", s, t);
  bool anySilent = false;
  for (uint8_t k = 0; k < 4 && !aborted; k++) {
    for (int i = 1; i <= 12; i++) {                       // the same 0.6 s soft start as polishing
      for (uint8_t m = 0; m < MOTOR_COUNT; m++) if (k == 3 || k == m) motorRun(m, (m == 1 ? -1 : 1) * pct * i / 12);
      delay(50);
    }
    delay(300);
    s = noiseSample(true); t = noiseSample(false);
    for (uint8_t m = 0; m < MOTOR_COUNT; m++) motorRun(m, 0);
    noiseRow(name[k], s, t);
    if (s.silent || t.silent) { anySilent = true; delay(300); tofBegin(); }   // restart them before the next motor
    delay(500);
    if (stopRequested()) aborted = true;
  }
  stopAll();
  Serial.println();
  if (anySilent) {
    Serial.println(F("  RESULT: a sensor stops answering (it is being reset) when the motor(s) above run."));
    Serial.println(F("  Fixes, cheapest first:"));
    Serial.println(F("    1. 100 nF ceramic capacitor soldered across the two terminals of each motor"));
    Serial.println(F("    2. 470-1000 uF capacitor across each TB6612's VM and GND"));
    Serial.println(F("    3. 10 uF + 100 nF across the sensor board's VIN and GND, at the sensor"));
    Serial.println(F("    4. motor wires twisted in pairs, kept away from the sensor cable"));
    Serial.println(F("    5. motor ground back to the power supply on its own wire, not through the sensor's ground"));
  } else if (s.ok + 3 < 30 || t.ok + 3 < 30) Serial.println(F("  RESULT: fewer good readings with the motors on: some noise, or a spinning brush is in a beam."));
  else Serial.println(F("  RESULT: the motors do not upset the sensors."));
}

// ================================================================ stage 3: the top roller
// The top sensor rides on the carriage, 75 mm before the roller, and reads the drop to the shoe. Shoe height = carriage
// (its reading on the empty belt) - reading. Like the side, the height is stored by place along the shoe and used when that
// part reaches the roller, and a constant error in the carriage estimate cancels.
// The carriage waits at its home (lifthome, 150 mm above the belt since 2026-11-03, not fully up), follows the shoe live,
// and comes down early to meet the toe. If the shoe rises faster than the carriage can climb, the belt waits for it.
// At the shoe's opening (the height drops well below the highest point so far) the roller lifts away and the top pass
// ends there (the user's choice); it stays up until the heel has passed.
constexpr float ROLLER_R_MM = 26.0f;      // top roller radius (52 mm chenille, like the side brushes)
constexpr float TOP_SEE_MM2 = 15.0f;      // the top reads this much closer than the empty belt: shoe
constexpr float TOP_DEAD_MM = 3.0f;       // stop the carriage within this of its target
constexpr float TOP_WAIT_MM = 8.0f;       // the carriage is this much lower than it should be: the belt waits for it
constexpr float TOP_CLEAR_MM = 25.0f;     // the top reading on the shoe must not go below this: the sensor arm must clear it
// openDropMm (set opendrop, default 20): the height falls this far below the highest point so far: the shoe's opening
constexpr float TOP_END_EARLY_MM = 10.0f; // lift away when the roller axis is this far before the opening (or the heel)
constexpr float LIFT_MAX_MM = 240.0f;     // top reading near the top of the carriage's travel: never aim higher
float liftOpenMm = 150;                   // top reading with the carriage at home, measured at the start of each pass
float topEndMm = -1;                      // where the top pass ends (the opening or the heel), mm from the toe; -1 not yet known
float topHoldMm = 150;                    // carriage height before there are heights to follow (home)
float topMaxMm = 0;                       // the highest part of the shoe read so far
// Carriage target once lifted away at the opening: liftAwayMm (set liftaway) above where it pressed on the highest part of
// the shoe, so the roller clears the collar and heel. Never above LIFT_MAX_MM.
float liftAwayTarget() { return min(LIFT_MAX_MM, topMaxMm + gripTopMm + liftAwayMm); }

float heightAt(int i) {
  if (i < 0 || i >= PROF_N) return NAN;
  if (!isnan(shoe.height[i])) return shoe.height[i];
  int a = i, b = i;
  while (a > 0 && isnan(shoe.height[a])) a--;
  while (b < PROF_N - 1 && isnan(shoe.height[b])) b++;
  if (isnan(shoe.height[a]) || isnan(shoe.height[b]) || b - a > 10) return NAN;
  return shoe.height[a] + (shoe.height[b] - shoe.height[a]) * (i - a) / (b - a);
}
// Carriage height wanted with the roller axis at s mm from the toe: the roller must clear the highest part of the shoe under
// any part of it, then press by the grip.
float topTarget(float s) {
  if (topEndMm >= 0 && s >= topEndMm - TOP_END_EARLY_MM) return liftAwayTarget();  // the opening or the heel: lift away
  float best = -1e9;
  int c = (int)roundf(s / PROF_STEP_MM);
  const int k0 = (int)(ROLLER_R_MM / PROF_STEP_MM);
  for (int k = -k0; k <= k0; k++) {
    float h = heightAt(c + k);
    float u = k * PROF_STEP_MM;
    if (isnan(h) || fabsf(u) > ROLLER_R_MM) continue;
    best = max(best, h + sqrtf(ROLLER_R_MM * ROLLER_R_MM - u * u) - ROLLER_R_MM);
  }
  if (best < -1e8) return s + ROLLER_R_MM < 0 ? topHoldMm : max(topHoldMm, topMaxMm + gripTopMm);   // before the toe: hold; a gap inside the shoe: stay above it
  return constrain(best + gripTopMm, gripTopMm, LIFT_MAX_MM);
}

void motorsSoftStart(bool side, bool top, int pct) {
  for (int i = 1; i <= 12; i++) {
    if (side) for (uint8_t m = 0; m < 2; m++) motorRun(m, BRUSH_DIR[m] * pct * i / 12);
    if (top) motorRun(2, pct * i / 12);
    delay(50);
  }
}

// ---------------------------------------------------------------- one polishing pass: side brushes, top roller, or both
bool polishPass(bool doSide, bool doTop) {
  const char *what = doSide && doTop ? "side brushes and top roller" : doSide ? "side brushes" : "top roller";
  if (doSide && (spd.jawClose <= 0 || spd.jawOpen <= 0)) { Serial.println(F("Jaw speeds not measured: run  speed  and save")); return false; }
  if (doTop && (spd.liftDown <= 0 || spd.liftUp <= 0)) { Serial.println(F("Carriage speeds not measured: run  speed  and save")); return false; }
  if (!pcaFound || !pcfFound || !sideFound || (doTop && !topFound)) { Serial.println(F("Needs the PCA9685, the PCF8575 and the distance sensors")); return false; }
  bool was = beltFastActive;
  beltUse(false);                                         // polishing runs at the normal belt speed
  if (cal.beltMmPerS <= 0) { beltUse(was); Serial.println(F("Normal belt speed not calibrated: beltmode normal, belttape, save")); return false; }
  const float v = cal.beltMmPerS, brushX = SIDE_SENSOR_TO_BRUSH_MM, rollX = TOP_SENSOR_TO_ROLLER_MM;
  Serial.printf("POLISHING PASS, %s, following the shoe live\n", what);
  Serial.printf("  belt %.1f mm/s, motors %.0f %%", v, pol.brushPct);
  if (doSide) Serial.printf(", side grip %.0f mm", gripMm);
  if (doTop) Serial.printf(", top grip %.0f mm", gripTopMm);
  Serial.println();

  uint32_t cycleT0 = millis();
  cycleScreen("POLISHING", C_WARN, what);
  cycleBoxes("checking", -1, "checking", -1, "stopped");
  cycleButtons(false);
  // No homing here: the last pass left both stations at home. A quick look with the sensors (nothing moves) confirms it;
  // anything else (power-up, a STOP, a fault, a hand move) needs  home  first.
  if (!machineHomed) {
    Serial.println(F("  Not homed since power-up or since the last stop: run  home  (menu: Home machine) first."));
    cycleState("HOME FIRST", C_BAD, "Choose Home machine"); beltUse(was); return false;
  }
  float jaw = tofAvg(true, 9);                            // where the jaws are now, in side-reading mm
  if (doSide && (jaw < 0 || jaw < cal.jawHomeMm - HOME_NEAR_MM)) {
    Serial.printf("  The jaws are not open: the side sensor reads %.0f mm, home is %u. Run  home  first.\n", jaw, cal.jawHomeMm);
    machineHomed = false; cycleState("HOME FIRST", C_BAD, "Jaws not open"); beltUse(was); return false;
  }
  if (jaw < 0) jaw = cal.jawHomeMm;
  jawOpenMm = min(jaw, (float)cal.jawHomeMm);             // they cannot open further than this: never drive into the end stop
  if (doSide) Serial.printf("  jaws fully open read %.0f mm, so the widest shoe they can grip at this grip is %.0f mm\n", jawOpenMm, jawOpenMm - 2 * gripMm);
  float lift = topFound ? tofAvg(false, 9) : -1;          // the carriage, in top-reading mm (the drop to the belt)
  if (lift < 0) lift = cal.liftHomeMm;
  liftOpenMm = lift;
  if (doTop) Serial.printf("  carriage at home reads %.0f mm to the belt\n", liftOpenMm);
  if (doTop && fabsf(liftOpenMm - cal.liftHomeMm) > 30) {   // not at home, or something is in the top sensor's beam
    Serial.printf("  The carriage is not at home: the top sensor reads %.0f mm, home is %u (or something is in its beam:\n", liftOpenMm, cal.liftHomeMm);
    Serial.println(F("  yarn, a cable). Run  home  first."));
    machineHomed = false; cycleState("HOME FIRST", C_BAD, "Carriage not home"); beltUse(was); stopAll(); return false;
  }
  // START has been pressed with the shoe on the belt (before the spray posts): go
  Serial.printf("  shoe on the belt %s, toe first: going\n", polishSpray ? "before the spray posts" : "before the side sensor");
  machineHomed = false;                                   // until both stations are back home at the end of this pass

  motorsSoftStart(doSide, doTop, (int)pol.brushPct);
  if (tofAvg(true, 5) < 0 && !(tofRecover() && tofAvg(true, 5) > 0)) {
    for (uint8_t m = 0; m < MOTOR_COUNT; m++) motorRun(m, 0);
    Serial.println(F("  the side sensor stops answering when the motors run: electrical noise (try  noisetest)"));
    cycleState("FAULT", C_BAD, "Sensor lost with motors on"); beltUse(was); return false;
  }

  static uint8_t nW[PROF_N], nH[PROF_N];                  // the live shape goes in shoe.halfW / shoe.height, as measure's does
  for (int i = 0; i < PROF_N; i++) { shoe.halfW[i] = shoe.height[i] = NAN; nW[i] = nH[i] = 0; }
  shoe.valid = shoe.placed = false;
  liveHeelMm = -1; topEndMm = -1; topHoldMm = liftOpenMm; topMaxMm = 0;

  tofContinuous(true);                                    // new readings every period, without waiting for them
  bool beltOn = true;
  beltDrive(1.0f);
  float pos = 0;                                          // belt travel, counted only while the belt runs

  // side station (the same as polish side before; it also runs, without moving the jaws, in a top-only pass so the top
  // knows when to expect the toe)
  uint8_t st = 0;                                         // 0 waiting for the toe, 1 shoe in the beam, 2 heel has passed
  float toe = 0, lastSeen = 0, len = 0;
  int sideR = -1, firstR = -1;
  int8_t dir = 0;                                         // jaw: +1 opening, -1 closing, 0 holding
  uint16_t good = 0, bad = 0, resyncs = 0, misses = 0;
  bool sideDone = !doSide;

  // top station: 0 waiting at home, 3 following, 4 lifted away (the opening or the heel), waiting for the heel to pass
  uint8_t tt = 0;
  float tToe = 0, tLast = 0, tMax = 0, tHeel = -1;
  int topR = -1, tSeenRun = 0, tDropRun = 0, tMisses = 0;
  int tBuf[3] = {0, 0, 0}; uint8_t tBufN = 0;              // the last 3 good readings, for a median: one wild reading does not move it
  int8_t lDir = 0;                                        // carriage: +1 up, -1 down, 0 holding
  uint16_t tGood = 0, tBad = 0, waits = 0;
  bool topDone = !doTop, waiting = false;

  uint32_t t0 = millis(), last = t0, lastDraw = 0;
  bool ok = false;
  if (polishSpray) Serial.printf("  spray: bursts while the IR sees the shoe (%u x %u ms, %u ms apart, %u ms pause)\n", spr.count, spr.onMs, spr.gapMs, spr.pauseMs);
  uint16_t sprays = 0; bool sprayWas = false;
  uint16_t restarts0 = tofRestarts;
  // the end: each station goes home as soon as the shoe has passed it, while the belt carries the shoe on exitMm
  // 0 not yet, 1 on its way, 2 home, 3 failed
  uint8_t sRet = doSide ? 0 : 2, tRet = doTop ? 0 : 2, tRetPhase = 0;
  uint32_t sRetT0 = 0, sRetProg = 0, sRetMin = 0, tRetT0 = 0;
  float sRetBest = -1, exitFrom = -1;
  bool exitDone = false;
  struct LogRow { int16_t pos, r, est, want; };
  static LogRow logS[90], logT[90];
  uint8_t nLogS = 0, nLogT = 0; float nextLogS = 0, nextLogT = 0;
  while (true) {
    uint32_t now = millis();
    float dt = (now - last) / 1000.0f; last = now;
    if (beltOn) pos += v * dt;
    jaw += dir > 0 ? spd.jawOpen * dt : dir < 0 ? -spd.jawClose * dt : 0;   // tracked by time
    jaw = constrain(jaw, JAW_MIN_MM - 4, jawOpenMm);         // it cannot be past either end of its travel
    if (st == 0 || !doSide) jaw = jawOpenMm;              // before the toe (or with the side off) the jaws sit fully open
    if (tt >= 3) {
      lift += lDir > 0 ? spd.liftUp * dt : lDir < 0 ? -spd.liftDown * dt : 0;
      lift = constrain(lift, 0.0f, LIFT_MAX_MM);
    }

    // ---------------- spray: bursts while the shoe is at the nozzles (not while the belt waits: it would soak one spot)
    bool sprayNow = polishSpray && beltOn && irSeen();
    if (sprayNow && !sprayWas) sprays++;
    sprayWas = sprayNow;
    sprayUpdate(sprayNow);

    // ---------------- side sensor
    int r = tofPoll(true);
    if (r != -2) {
      sideR = r;
      bool seen = r > 0 && r < jaw - SIDE_SEE_MM, clear = r > 0 && !seen;
      if (seen && st != 2) {                              // the shoe: store its half-width where the sensor is
        if (st == 0) { st = 1; toe = pos; firstR = r; good = bad = 0; }
        lastSeen = pos; good++; misses = 0;
        float hw = jaw / 2.0f - r;
        if (hw > 2) { profileAdd(shoe.halfW, nW, pos - toe, hw); cyclePlot(1, pos - toe, 2 * hw); }
      } else if (clear) {
        misses = 0;
        if (st == 1 && pos - lastSeen > GAP_END_MM) {
          if (good < BLIP_READINGS || lastSeen - toe < BLIP_MM) {
            Serial.printf("  side sensor: ignored a blip (%u readings, first %d mm)\n", good, firstR);
            st = 0;
            for (int i = 0; i < PROF_N; i++) { shoe.halfW[i] = NAN; nW[i] = 0; }
          } else {
            st = 2; len = lastSeen - toe; liveHeelMm = len;
            Serial.printf("  side sensor: heel passed, shoe %.0f mm long\n", len);
            cycleLength(len);
          }
        }
        if (doSide && st == 2 && pos - toe - brushX > len + BRUSH_R_MM && fabsf(r - jaw) < 15) { jaw = 0.5f * jaw + 0.5f * r; resyncs++; }
      } else {
        if (st == 1) bad++;
        if (tofLastStatus[1] > 5 && ++misses >= 5) { tofRecover(); misses = 0; }
      }
    }

    // ---------------- side jaws
    float s = st ? pos - toe - brushX : -1e6f;            // the part of the shoe level with the brush axes, mm from the toe
    float want = jawOpenMm;
    if (doSide && !sideDone) {
      if (st) {
        want = liveTarget(s);
        for (uint8_t k = 1; k <= 4; k++) want = max(want, liveTarget(s + v * OPEN_EARLY_S * k / 4));   // open early, close on time
        // the toe is coming: close in time to meet it, aiming at the widest half-width read so far (see the notes above)
        if (want >= jawOpenMm - 0.5f && (st == 1 || s < len)) {
          const float seenAhead = brushX - BRUSH_R_MM;
          for (float d = 2; d <= seenAhead; d += 2) {
            if (liveTarget(s + d) >= jawOpenMm - 0.5f) continue;
            float hw = 0;
            int iEnd = min((int)((pos - toe) / PROF_STEP_MM), PROF_N - 1);
            for (int i = 0; i <= iEnd; i++) if (!isnan(shoe.halfW[i])) hw = max(hw, shoe.halfW[i]);
            float w = max(liveTarget(s + d), constrain(2 * (hw + gripMm), JAW_MIN_MM, jawOpenMm));
            if (d <= v * (jawOpenMm - w) / spd.jawClose + 10) want = w;
            break;
          }
        }
      }
      float err = want - jaw;
      dir = err > JAW_DEAD_MM ? 1 : err < -JAW_DEAD_MM ? -1 : 0;
      if (dir) jawDrive(dir); else servoStop(SV_JAW);
      if (st && pos - toe >= nextLogS && nLogS < 90) { logS[nLogS++] = {(int16_t)(pos - toe), (int16_t)sideR, (int16_t)jaw, (int16_t)want}; nextLogS += 10; }
      if (st == 2 && s > len + BRUSH_R_MM + 15 && jaw < JAW_MIN_MM + JAW_DEAD_MM + 2) {   // closed behind the heel: done
        sideDone = true; dir = 0; servoStop(SV_JAW);
        for (uint8_t m = 0; m < 2; m++) motorRun(m, 0);
        Serial.println(F("  side brushes: done"));
      }
    }

    // ---------------- top sensor and carriage
    float ts = (tt >= 3) ? pos - tToe - rollX : -1e6f;     // the part of the shoe level with the roller axis, mm from the toe
    float lWant = liftOpenMm;
    if (doTop && !topDone) {
      int tr = topFound ? tofPoll(false) : -2;
      if (tr != -2) {
        topR = tr;
        if (tr > 0) { tBuf[tBufN % 3] = tr; tBufN++; tMisses = 0; }
        else if (tofLastStatus[0] > 5 && ++tMisses >= 5) { tofRecover(); tMisses = 0; }
        int med = tr;                                     // median of the last 3 good readings
        if (tr > 0 && tBufN >= 3) { int a = tBuf[0], b = tBuf[1], c = tBuf[2]; med = max(min(a, b), min(max(a, b), c)); }
        // the shoe reaches the top sensor only after the side sensor has seen it, and SENSOR_SPACING_MM later
        bool expected = st != 0 && pos - toe > SENSOR_SPACING_MM - 60;
        if (tt == 0) {
          bool seenT = tr > 0 && tr < liftOpenMm - TOP_SEE_MM2 && expected;
          if (seenT) {
            if (++tSeenRun == 1) tToe = pos;
            if (tSeenRun >= 3) { tt = 3; lift = liftOpenMm; Serial.printf("  top sensor: toe (side to top %.0f mm, should be %.0f)\n", tToe - toe, SENSOR_SPACING_MM); }
          } else if (tr > 0) tSeenRun = 0;
        } else {
          bool seenT = tr > 0 && tr < lift - TOP_SEE_MM2;
          float at = pos - tToe;
          // The dip into the shoe's opening: the height falls openDropMm below the highest point so far, 3 readings in a
          // row. Looking straight down the hole the sensor reads (nearly) the belt, or nothing valid at all (dark inside,
          // surfaces at angles): both count as a dip. Before 2026-11-05 the invalid ones were skipped, so a dark opening
          // was never noticed and the roller stayed down. Once the shoe's length is known (side sensor), not in its
          // first 30 %, so a bad patch on the toe cannot end the pass early.
          bool dipZone = tt == 3 && topEndMm < 0 && at > 40 && tMax > openDropMm && (st != 2 || at > 0.3f * len);
          if (dipZone) {
            float hd = (tr > 0 && seenT) ? lift - med : 0;
            if (hd < tMax - openDropMm) {
              if (++tDropRun >= 3) {
                topEndMm = at - 2 * PROF_STEP_MM;
                Serial.printf("  top: dip into the opening at %.0f mm from the toe (%s, highest %.0f): the roller goes up to %.0f\n",
                              topEndMm, tr > 0 ? (seenT ? "height dropped" : "reads the belt") : "no valid reading", tMax, liftAwayTarget());
              }
            } else tDropRun = 0;
          }
          if (seenT) {
            tLast = pos;
            float h = lift - med;
            if (tt == 3 && topEndMm < 0) {
              tGood++;
              if (h > 2 && tDropRun == 0) {
                profileAdd(shoe.height, nH, at, h); cyclePlot(0, at, h);
                tMax = max(tMax, h); topMaxMm = tMax;
              }
            } else if (topEndMm >= 0 && h > 2 && tHeel < 0) {
              // past the opening: keep drawing the shape (the opening and the heel) so the graph shows the whole shoe.
              // Not used for the carriage: it is lifted away from here on
              profileAdd(shoe.height, nH, at, h); cyclePlot(0, at, h);
            }
          } else if (tr > 0 && tHeel < 0 && pos - tLast > GAP_END_MM && at > BLIP_MM && (st != 2 || at > 0.7f * len)) {
            // the top sees the belt again. With the side sensor's length known, a "clear" well before the heel is the
            // sensor looking down into the opening, not the end of the shoe
            tHeel = tLast - tToe;                         // the heel has passed the sensor
            if (topEndMm < 0) topEndMm = tHeel;          // no opening found: the roller ends at the heel
            Serial.printf("  top: heel passed the sensor, %.0f mm from the toe\n", tHeel);
          } else if (tr <= 0 && tt == 3) tBad++;
        }
        // The heel from the side sensor: it measured the whole length, so the heel reaches the top sensor that far after the
        // toe did. This ends the pass even when the top cannot tell the heel from the belt (the carriage, lifted away, is
        // not where its time-count says, so the empty belt still looks like shoe)
        if (tt >= 3 && tHeel < 0 && st == 2 && pos - tToe > len + GAP_END_MM) {
          tHeel = len;
          if (topEndMm < 0) topEndMm = tHeel;
          Serial.printf("  top: heel passed the sensor, %.0f mm from the toe (from the side sensor's length)\n", tHeel);
        }
      }

      if (tt >= 3) {
        lWant = topTarget(ts);
        for (uint8_t k = 1; k <= 4; k++) lWant = max(lWant, topTarget(ts + v * OPEN_EARLY_S * k / 4));   // rise early
        // the toe is coming and there is nothing under the roller yet: move to meet it in time. The sensor is 75 mm ahead,
        // so the first 20 mm the roller will meet are already read: aim at the highest of them. Rising early is always
        // safe; coming down only just in time
        if (tt == 3 && topEndMm < 0 && fabsf(lWant - topHoldMm) < 0.5f) {
          const float seenAhead = rollX - ROLLER_R_MM;
          for (float d = 2; d <= seenAhead; d += 2) {
            if (fabsf(topTarget(ts + d) - topHoldMm) < 0.5f) continue;
            float w = topTarget(ts + d);
            for (float j = 2; j <= 20 && d + j <= seenAhead; j += 2) w = max(w, topTarget(ts + d + j));
            if (w > lift || d <= v * (lift - w) / spd.liftDown + 10) lWant = w;
            break;
          }
        }
        if (tt == 3 && topEndMm < 0) {                    // keep the sensor arm clear of the shoe passing under it now
          float hs = 0;
          int i1 = min((int)((pos - tToe) / PROF_STEP_MM), PROF_N - 1);
          for (int i = max(0, i1 - 5); i <= i1; i++) if (!isnan(shoe.height[i])) hs = max(hs, shoe.height[i]);
          lWant = max(lWant, min(hs + TOP_CLEAR_MM, LIFT_MAX_MM));
        }
        if (tt == 3 && topEndMm >= 0 && ts >= topEndMm - TOP_END_EARLY_MM) { tt = 4; Serial.println(F("  top: roller lifting away")); }
        float le = lWant - lift;
        lDir = le > TOP_DEAD_MM ? 1 : le < -TOP_DEAD_MM ? -1 : 0;
        if (lDir) liftDrive(lDir); else servoStop(SV_LIFT);
        // the carriage is too low for what is coming: the belt waits for it
        bool behind = le > TOP_WAIT_MM;
        if (behind && beltOn) { beltOn = false; servoOff(SV_BELT); waits++; waiting = true; }
        else if (!behind && waiting && le < TOP_DEAD_MM + 1) { beltOn = true; beltDrive(1.0f); waiting = false; }
        if (pos - tToe >= nextLogT && nLogT < 90) { logT[nLogT++] = {(int16_t)(pos - tToe), (int16_t)topR, (int16_t)lift, (int16_t)lWant}; nextLogT += 10; }
        // done once the roller is up and the heel has gone past it
        if (tt == 4 && lift >= liftAwayTarget() - TOP_DEAD_MM - 2 && tHeel >= 0 && ts > tHeel + ROLLER_R_MM + 10) {
          topDone = true; lDir = 0; servoStop(SV_LIFT); motorRun(2, 0);
          if (waiting) { beltOn = true; beltDrive(1.0f); waiting = false; }
          Serial.println(F("  top roller: done"));
        }
      }
    }

    // ---------------- side station home: open to the end of travel, judged by the side sensor (the shoe has gone)
    if (sideDone && sRet == 0) {
      sRet = 1; sRetT0 = sRetProg = now; sRetBest = -1;
      sRetMin = spd.jawOpen > 0 ? (uint32_t)(max(0.0f, cal.jawHomeMm - jaw) / spd.jawOpen * 1000.0f) : 0;
      jawDrive(1.0f);
      Serial.println(F("  side: jaws going home"));
    }
    if (sRet == 1) {
      if (r > 0 && (sRetBest < 0 || r > sRetBest + 5)) { sRetBest = r; sRetProg = now; }
      bool atHome = r > 0 && r >= cal.jawHomeMm - 6;                   // reads home: stop now, no stall at the end stop
      if (atHome || (now - sRetT0 >= sRetMin && now - sRetProg > 1000)) {   // or not opening any more: at the end of travel
        if (atHome) sRetBest = max(sRetBest, (float)r);
        servoOff(SV_JAW);
        sRet = sRetBest > cal.jawHomeMm - HOME_NEAR_MM ? 2 : 3;
        Serial.printf("  side: jaws %s (reading %.0f, home %u)\n", sRet == 2 ? "home" : "did NOT get home", sRetBest, cal.jawHomeMm);
      } else if (now - sRetT0 > 8000) { servoOff(SV_JAW); sRet = 3; Serial.println(F("  side: jaws not home after 8 s")); }
    }

    // ---------------- top station home: down below lifthome, then up to it, so it always arrives from below (as  home )
    if (topDone && tRet == 0) { tRet = 1; tRetPhase = 1; tRetT0 = now; tBufN = 0; liftDrive(-1.0f); Serial.println(F("  top: carriage going home")); }
    if (tRet == 1) {
      int tr = tofPoll(false);
      if (tr > 0) {
        tBuf[tBufN % 3] = tr; tBufN++;
        int a = tBuf[0], b = tBuf[1], c = tBuf[2], med = tBufN >= 3 ? max(min(a, b), min(max(a, b), c)) : -1;
        if (med > 0 && tRetPhase == 1 && med < (int)cal.liftHomeMm - 15) { tRetPhase = 2; tBufN = 0; liftDrive(1.0f); }
        else if (med > 0 && tRetPhase == 2 && med >= (int)cal.liftHomeMm) {
          servoStop(SV_LIFT); tRet = 2;
          Serial.printf("  top: carriage home (reading %d, home %u)\n", med, cal.liftHomeMm);
        }
      }
      if (tRet == 1 && now - tRetT0 > 12000) { servoStop(SV_LIFT); tRet = 3; Serial.println(F("  top: carriage not home after 12 s")); }
    }

    // ---------------- exit: once the heel has passed the last station, the belt carries the shoe on exitMm, then stops
    if (exitFrom < 0) {
      bool past = doTop ? (tHeel >= 0 && ts > tHeel + ROLLER_R_MM) : (st == 2 && s > len + BRUSH_R_MM);
      if (past) { exitFrom = pos; Serial.printf("  shoe has left the %s: belt on for %.0f mm\n", doTop ? "top roller" : "side brushes", exitMm); }
    } else if (!exitDone && pos - exitFrom >= exitMm) {
      exitDone = true; beltOn = false; waiting = false; servoOff(SV_BELT);
      Serial.println(F("  exit travel done: belt stopped"));
    }

    if (now - lastDraw > 500) {
      lastDraw = now;
      const char *sStep = !doSide ? "off" : sRet == 1 ? "homing" : sRet == 2 ? "home" : sRet == 3 ? "NOT home" : sideDone ? "done" : st == 0 ? "waiting" : s < -BRUSH_R_MM ? "closing" : (st == 2 && s > len) ? "release" : "polishing";
      const char *tStep = !doTop ? "off" : tRet == 1 ? "homing" : tRet == 2 ? "home" : tRet == 3 ? "NOT home" : topDone ? "done" : tt == 0 ? "waiting" : tt == 4 ? "lifted" : "polishing";
      cycleClock(now - cycleT0);
      cycleBoxes(sStep, sideR, tStep, topR, exitDone ? "stopped" : exitFrom >= 0 ? "exit" : beltOn ? "forward" : "waiting");
      if (doSide && st && s >= 0 && (st == 1 || s <= len)) cycleMark(s);
    }
    if (sideDone && topDone && exitDone && sRet >= 2 && tRet >= 2) { ok = true; break; }
    if (st == 0 && pos > NO_TOE_MM) { Serial.println(F("  no shoe reached the side sensor: is it on the belt, in the middle?")); break; }
    if (doTop && tt == 0 && st != 0 && pos - toe > SENSOR_SPACING_MM + 150) { Serial.println(F("  the top sensor did not see the shoe: is the carriage up and the shoe in the middle?")); break; }
    if (pos > NO_TOE_MM + SENSOR_SPACING_MM + PROF_N * PROF_STEP_MM) { Serial.println(F("  took too long: stopped")); break; }
    if (millis() - t0 > 120000) { Serial.println(F("  took over 2 minutes: stopped")); break; }
    if (stopRequested()) { aborted = true; Serial.println(F("  stopped by the user")); break; }
    delay(1);
  }
  sprayUpdate(false); pumpSet(false);
  servoOff(SV_BELT);
  for (uint8_t m = 0; m < MOTOR_COUNT; m++) motorRun(m, 0);
  servoStop(SV_JAW); servoStop(SV_LIFT);
  tofContinuous(false);                                   // back to single readings
  uint32_t ranMs = millis() - t0;
  stopAll();
  // the next shoe can go straight away if both stations are home: back home, or never moved (no shoe reached them)
  machineHomed = (sRet == 2 || st == 0) && (tRet == 2 || tt == 0);
  if (!machineHomed) Serial.println(F("  a station is not at home: run  home  (menu: Home machine) before the next shoe"));
  beltUse(was);
  if (st == 2) shoe.lenSide = len;
  screenRecover();                                        // noise may have reset the display during the pass: reset and redraw
  cycleClock(millis() - cycleT0);
  cycleBoxes(ok ? "done" : "--", -1, ok ? "done" : "--", -1, "stopped");
  if (tofRestarts != restarts0) Serial.printf("  SENSORS: dropped out and were restarted %u time(s) during the pass (each costs about 0.2 s of readings)\n", tofRestarts - restarts0);
  if (polishSpray) Serial.printf("  SPRAY: the IR saw the shoe %u time(s)%s\n", sprays, sprays == 0 ? ": never: check its pot (ir) and that the shoe started before the spray posts" : "");
  if (doSide) {
    Serial.printf("  SIDE: readings on the shoe %u good, %u bad; jaw position re-checked %u times\n", good, bad, resyncs);
    float widest = 0;
    for (int i = 0; i < PROF_N; i++) if (!isnan(shoe.halfW[i])) widest = max(widest, 2 * shoe.halfW[i]);
    Serial.printf("  widest part of the shoe %.0f mm%s\n", widest, widest > jawOpenMm - 2 * gripMm ? "  (wider than the jaws can open for this grip: it is pressed harder there)" : "");
    Serial.println(F("  sensor at    reading   jaw (estimate)   jaw wanted     (mm; the brushes are 71 mm behind the sensor)"));
    for (uint8_t i = 0; i < nLogS; i++) Serial.printf("  %5d       %5d      %5d            %5d\n", logS[i].pos, logS[i].r, logS[i].est, logS[i].want);
  }
  if (doTop) {
    Serial.printf("  TOP: readings on the shoe %u good, %u bad; highest %.0f mm; the belt waited for the carriage %u times\n", tGood, tBad, tMax, waits);
    if (topEndMm >= 0) Serial.printf("  the roller polished up to %.0f mm from the toe\n", topEndMm);
    Serial.println(F("  sensor at    reading   carriage (estimate)   carriage wanted     (mm; the roller is 60 mm behind the sensor)"));
    for (uint8_t i = 0; i < nLogT; i++) Serial.printf("  %5d       %5d      %5d                 %5d\n", logT[i].pos, logT[i].r, logT[i].est, logT[i].want);
  }
  if (ok) {
    char sub[40];
    snprintf(sub, sizeof(sub), "%.1f s", ranMs / 1000.0f);
    cycleState("POLISHED", machineHomed ? C_OK : C_WARN, machineHomed ? sub : "Done, but Home machine next");
    cycleProgress(1, C_OK);
    Serial.printf("  done in %.1f s\n", ranMs / 1000.0f);
  } else cycleState(aborted ? "STOPPED" : "FAULT", C_BAD, aborted ? "Stopped by the user" : "See the Serial Monitor");
  return ok;
}
bool polishSide() { return polishPass(true, false); }
bool polishTop() { return polishPass(false, true); }
bool polishBoth() { return polishPass(true, true); }

// ---------------------------------------------------------------- grip calibrations
// Jog the jaws (side) or the carriage (top) with c / C (closer to the shoe) and o (away) until it looks right; s saves:
// returns the reading then, or -1 if cancelled.
float jogTo(bool side) {
  Serial.println(F("    c = closer a little    C = closer more    o = away a little    s = save    x = cancel"));
  const uint8_t ch = side ? SV_JAW : SV_LIFT;
  while (true) {
    int r = (int)tofAvg(side, 7);
    if (r > 0) Serial.printf("  reading %d mm   [c / C / o / s / x]\n", r); else Serial.println(F("  no reading   [c / C / o / s / x]"));
    char k = 0;
    while (!k) {
      if (buttonPressed(btnStop)) { k = 'x'; break; }
      while (Serial.available()) { char ch2 = Serial.read(); if (ch2 != '\r' && ch2 != '\n' && ch2 != ' ') { k = ch2; break; } }
      delay(5);
    }
    while (Serial.available()) Serial.read();
    if (k == 'c' || k == 'C') { if (side) jawDrive(-1); else liftDrive(-1); delay(k == 'C' ? 200 : 40); servoStop(ch); delay(150); }
    else if (k == 'o' || k == 'O') { if (side) jawDrive(1); else liftDrive(1); delay(40); servoStop(ch); delay(150); }
    else if (k == 's' || k == 'S') {
      float g = tofAvg(side, 9);
      if (g <= 0) { Serial.println(F("  no good reading here: move a little and try again")); continue; }
      servoStop(ch);
      return g;
    }
    else if (k == 'x' || k == 'X') { servoStop(ch); return -1; }
  }
}

// side: with a straight-sided box between the brushes, close the jaws until the yarn presses the way you want
// top: with a flat box under the roller and the top sensor, lower the carriage until the yarn presses the way you want
void gripCal(bool side) {
  if (!pcaFound || !(side ? sideFound : topFound)) { Serial.println(F("Needs the PCA9685 and the sensor")); return; }
  Serial.printf("GRIP CALIBRATION (%s): how hard the %s presses on the shoe\n", side ? "side" : "top", side ? "side brushes" : "top roller");
  if (!homeOne(side)) { Serial.println(F("  could not get home")); stopAll(); return; }
  if (side) {
    if (askYesNo("Put a box with straight sides (a shoebox or a book, 150 mm long or more) between the brushes, in the middle of the belt, so it reaches from the side sensor to past the brushes. Ready?") != 1) { stopAll(); return; }
    Serial.println(F("  Close the jaws until the yarn presses on the box the way you want it to press on a shoe."));
  } else {
    if (askYesNo("Put a box with a flat top (100 mm long or more) on the belt under the roller, so it reaches from under the top sensor to past the roller. Ready?") != 1) { stopAll(); return; }
    Serial.println(F("  Lower the carriage until the yarn presses on the box the way you want it to press on a shoe."));
  }
  float g = jogTo(side);
  if (g > 0) { if (side) gripMm = g; else gripTopMm = g; }
  askYesNo("Take the box out. Done?");
  homeOne(side);
  stopAll();
  if (g > 0) Serial.printf("  %s grip = %.0f mm. Type  save  to keep it.\n", side ? "side" : "top", g);
  else Serial.println(F("  cancelled, grip unchanged"));
}
