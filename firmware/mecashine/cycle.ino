// COPIED from firmware/mecashine_debug by sync_main.py. Do not edit here: edit it there and run sync_main.py.
// The polishing cycle, built in stages (the demo page's plan):
//   1. measuring pass: brushes off, jaws open, carriage up; the belt carries the shoe past both sensors and its shape is stored,
//      then the belt backs it up to where it started             <- this file, command  measure
//   2. polishing pass with the side brushes                      (next)
//   3. polishing pass with the top roller as well                (after that)
// Distances along the belt are belt speed x running time (cal.beltMmPerS); the belt has no position sensor.

constexpr float PROF_STEP_MM = 2.0f;      // the stored shape has one value every 2 mm along the shoe
constexpr int PROF_N = 250;               // up to 500 mm of shoe
constexpr int SIDE_SEE_MM = 25;           // the side sensor reads this much closer than empty: the shoe is in its beam
constexpr int TOP_SEE_MM = 15;            // the same for the top sensor
constexpr int BLIP_READINGS = 5;          // fewer good readings than this, or shorter than BLIP_MM, is a blip, not a shoe
constexpr float BLIP_MM = 20.0f;
constexpr float GAP_END_MM = 15.0f;       // not seen for this much belt travel: the heel has passed
constexpr float MEASURE_MAX_MM = 900.0f;  // give up if the belt has run this far without the shoe passing both sensors
constexpr float SHOE_GUESS_MM = 330.0f;   // for the progress bar until the real length is known

// The stored shape, measured from the toe. Side: half-width, from the side sensor's distance to the shoe, assuming the shoe
// runs down the middle of the belt. Top: height above the belt.
struct ShoeProfile {
  bool valid;
  float lenSide, lenTop;                  // toe to heel, as each sensor saw it
  float maxWidth, maxHeight;
  float sideEmpty;                        // the side reading with nothing in the beam, when this shoe was measured
  bool placed;                            // backed up to startGapMm before the side sensor, ready to polish
  float halfW[PROF_N], height[PROF_N];    // NAN where there was no reading
};
ShoeProfile shoe;

// adds one reading to its 2 mm slot; several readings in one slot are averaged
void profileAdd(float *arr, uint8_t *count, float fromToe, float value) {
  int i = (int)(fromToe / PROF_STEP_MM);
  if (i < 0 || i >= PROF_N) return;
  arr[i] = count[i] ? (arr[i] * count[i] + value) / (count[i] + 1) : value;
  if (count[i] < 255) count[i]++;
}

// Measuring and backing up use whichever belt setting  beltmode  has made active (normal after power-up).
bool measurePass() {
  Serial.printf("Belt: %s setting, %.1f mm/s%s\n", beltFastActive ? "FAST" : "NORMAL", cal.beltMmPerS,
                beltFastActive ? "" : "   (beltmode fast  to measure faster)");
  return measurePassRun();
}

bool measurePassRun() {
  if (!pcaFound || !sideFound || !topFound) { Serial.println(F("Needs the PCA9685 and both sensors")); return false; }
  if (cal.beltMmPerS <= 0) { Serial.println(F("Belt speed not measured yet: run  belttape  and save")); return false; }
  Serial.println(F("MEASURING PASS: brushes off, jaws open, carriage up. The shoe runs past both sensors, then backs up."));
  stopAll();
  uint32_t cycleT0 = millis();
  cycleScreen("HOMING", C_INFO, "Jaws open, carriage up");
  cycleBoxes("homing", -1, "homing", -1, "stopped");
  cycleButtons(false);
  Serial.println(F("  homing..."));
  if (!homeAll()) {
    Serial.println(F("  could not home: check  jaw  and  lift  first"));
    cycleState("FAULT", C_BAD, "Could not home");
    return false;
  }
  Serial.println(F("  belt must be EMPTY for the next 2 s (empty readings)"));
  float sideEmpty = tofAvg(true, 15), topEmpty = tofAvg(false, 15);
  if (sideEmpty < 0 || topEmpty < 0) {
    Serial.println(F("  a sensor has no steady empty reading (tofraw)"));
    cycleState("FAULT", C_BAD, "No steady empty reading");
    return false;
  }
  Serial.printf("  empty readings: side %.0f mm, top %.0f mm\n", sideEmpty, topEmpty);
  cycleState("READY", C_OK, "Shoe on the belt, then START");
  cycleBoxes("open", (int)sideEmpty, "up", (int)topEmpty, "stopped");
  cycleButtons(true);
  int answer = askYesNo("Put the shoe on the belt before the side sensor, toe first, in the middle. Ready?");
  cycleScreen("READY", C_OK, "Shoe on the belt, then START");   // the question covered part of the screen
  if (answer != 1) { cycleState("CANCELLED", C_DIM, ""); return false; }

  static uint8_t nW[PROF_N], nH[PROF_N];
  for (int i = 0; i < PROF_N; i++) { shoe.halfW[i] = shoe.height[i] = NAN; nW[i] = nH[i] = 0; }
  shoe.valid = false;
  shoe.placed = false;
  shoe.sideEmpty = sideEmpty;
  const float v = cal.beltMmPerS;
  uint8_t sideState = 0, topState = 0;    // 0 waiting for the toe, 1 shoe in the beam, 2 heel has passed
  float sideToe = 0, sideLast = 0, topToe = 0, topLast = 0;
  int sideR = -1, topR = -1, sideFirstR = -1, topFirstR = -1;   // first reading of each, printed if it turns out to be a blip
  uint16_t sideN = 0, topN = 0, sideBad = 0, topBad = 0;   // good readings on the shoe, and bad ones while it was in the beam           // readings taken on the shoe, to show how dense the measurement was
  const char *stepName[3] = {"waiting", "measuring", "done"};

  cycleState("MEASURING", C_WARN, "Pass 1: brushes off");
  cycleButtons(false);
  tofContinuous(true);                                    // both sensors range at once while measuring
  beltDrive(1.0f);
  uint32_t t0 = millis(), lastDraw = 0;
  bool ok = false;
  while (true) {
    float pos = v * (millis() - t0) / 1000.0f;           // how far the belt has carried the shoe so far
    int r = tofPoll(true);
    if (r != -2) {                                        // a new side reading
      sideR = r;
      // seen: a valid reading closer than empty. Only a valid reading of the empty reflector counts toward "the heel has
      // passed"; a bad reading proves nothing either way (dark or angled leather gives some), so it is only counted.
      bool seen = sideR > 0 && sideR < sideEmpty - SIDE_SEE_MM, clear = sideR > 0 && !seen;
      if (seen) {
        if (sideState == 0) { sideState = 1; sideToe = pos; sideFirstR = sideR; sideN = sideBad = 0; }
        if (sideState == 1) {
          sideLast = pos; sideN++;
          float hw = sideEmpty / 2.0f - sideR;              // half-width; at the very tip the beam half-sees the shoe and this goes negative
          if (hw > 2) { profileAdd(shoe.halfW, nW, pos - sideToe, hw); cyclePlot(1, pos - sideToe, 2 * hw); }
        }
      } else if (!clear) { if (sideState == 1) sideBad++; }
      else if (sideState == 1 && pos - sideLast > GAP_END_MM) {
        if (sideN < BLIP_READINGS || sideLast - sideToe < BLIP_MM) {
          Serial.printf("  side sensor: ignored a blip at %.0f mm (%u readings, first %d mm, empty %.0f mm)\n", sideToe, sideN, sideFirstR, sideEmpty);
          sideState = 0;
          for (int i = 0; i < PROF_N; i++) { shoe.halfW[i] = NAN; nW[i] = 0; }
        } else {
          sideState = 2; shoe.lenSide = sideLast - sideToe;
          Serial.printf("  side sensor: toe at %.0f mm of belt travel, heel passed, length %.0f mm\n", sideToe, shoe.lenSide);
          cycleLength(shoe.lenSide);
        }
      }
    }

    r = tofPoll(false);
    if (r != -2) {                                        // a new top reading
      topR = r;
      // the top sensor is downstream of the side one: anything it sees before the side sensor has found the toe is not the shoe
      bool seen = topR > 0 && topR < topEmpty - TOP_SEE_MM && sideState != 0, clear = topR > 0 && !seen;
      if (seen) {
        if (topState == 0) { topState = 1; topToe = pos; topFirstR = topR; topN = topBad = 0; }
        if (topState == 1) {
          topLast = pos; topN++;
          profileAdd(shoe.height, nH, pos - topToe, topEmpty - topR);
          cyclePlot(0, pos - topToe, topEmpty - topR);
        }
      } else if (!clear) { if (topState == 1) topBad++; }
      else if (topState == 1 && pos - topLast > GAP_END_MM) {
        if (topN < BLIP_READINGS || topLast - topToe < BLIP_MM) {
          Serial.printf("  top sensor: ignored a blip at %.0f mm (%u readings, first %d mm, empty %.0f mm)\n", topToe, topN, topFirstR, topEmpty);
          topState = 0;
          for (int i = 0; i < PROF_N; i++) { shoe.height[i] = NAN; nH[i] = 0; }
        } else {
          topState = 2; shoe.lenTop = topLast - topToe;
          Serial.printf("  top sensor: toe at %.0f mm of belt travel, heel passed, length %.0f mm\n", topToe, shoe.lenTop);
        }
      }
    }

    if (millis() - lastDraw > 1000) {                     // status boxes, clock and progress once a second: redraws cost readings
      lastDraw = millis();
      float len = sideState == 2 ? shoe.lenSide : SHOE_GUESS_MM;
      float total = (sideState ? sideToe : pos + SHOE_GUESS_MM) + SENSOR_SPACING_MM + len + GAP_END_MM;
      cycleBoxes(stepName[sideState], sideR, stepName[topState], topR, "forward");
      cycleClock(millis() - cycleT0);
      cycleProgress(pos / total, C_WARN);
    }

    if (sideState == 2 && topState == 2) { ok = true; break; }
    if (stopRequested()) { aborted = true; Serial.println(F("  stopped by the user")); break; }
    if (pos > MEASURE_MAX_MM) { Serial.println(F("  the shoe did not pass both sensors: is it in both beams? (carriage up, shoe in the middle)")); break; }
    delay(1);
  }
  servoOff(SV_BELT);
  tofContinuous(false);                                   // back to single readings for everything else
  uint32_t ranMs = millis() - t0;

  if (ok) {
    shoe.maxWidth = shoe.maxHeight = 0;
    for (int i = 0; i < PROF_N; i++) {
      if (!isnan(shoe.halfW[i])) shoe.maxWidth = max(shoe.maxWidth, 2 * shoe.halfW[i]);
      if (!isnan(shoe.height[i])) shoe.maxHeight = max(shoe.maxHeight, shoe.height[i]);
    }
    shoe.valid = true;
    // the 240 mm between the sensors checks the belt speed for free: the toe should reach the top sensor 240 mm after the side one
    Serial.println(F("  RESULT"));
    Serial.printf("    length      side %.0f mm   top %.0f mm\n", shoe.lenSide, shoe.lenTop);
    Serial.printf("    widest      %.0f mm (if the shoe ran down the middle)\n", shoe.maxWidth);
    Serial.printf("    highest     %.0f mm above the belt\n", shoe.maxHeight);
    Serial.printf("    toe to toe  %.0f mm between the sensors (should be %.0f: checks the belt speed)\n", topToe - sideToe, SENSOR_SPACING_MM);
    Serial.printf("    readings    side %u good, %u bad (one every %.1f mm)   top %u good, %u bad (one every %.1f mm)\n",
                  sideN, sideBad, sideN ? shoe.lenSide / sideN : 0.0f, topN, topBad, topN ? shoe.lenTop / topN : 0.0f);
    Serial.println(F("    from toe   width   height"));
    for (int i = 0; i < PROF_N; i += 5) {
      if (isnan(shoe.halfW[i]) && isnan(shoe.height[i])) continue;
      Serial.printf("    %4.0f mm   %5s   %5s\n", i * PROF_STEP_MM,
                    isnan(shoe.halfW[i]) ? "-" : String(2 * shoe.halfW[i], 0).c_str(), isnan(shoe.height[i]) ? "-" : String(shoe.height[i], 0).c_str());
    }
  }

  // back up by the same running time, which returns the shoe to where it started (the two directions run at matched speeds)
  if (!aborted) {
    Serial.printf("  backing the shoe up (%.1f s)\n", ranMs / 1000.0f);
    cycleState("REVERSING", C_INFO, "Back to the start");
    beltDrive(-1.0f);
    uint32_t r0 = millis(), lastR = 0;
    // With a measured shoe, the side sensor ends the back-up: reverse until the toe has left its beam, then startGapMm more,
    // so the shoe always stops in the same place however the two directions' speeds differ under its weight.
    // Without one (measuring failed), fall back to the same running time as forward.
    uint8_t back = 0;                                     // 0 shoe not yet back in the side beam, 1 in it, 2 toe has left it
    float lastSeen = 0;
    const uint32_t limitMs = ranMs + ranMs / 2 + 2000;    // safety: never reverse much longer than it went forward
    bool placed = false;
    while (true) {
      uint32_t el = millis() - r0;
      if (!ok && el >= ranMs) break;
      if (ok && el >= limitMs) { Serial.println(F("  the side sensor did not see the toe go back past it; stopped on time")); break; }
      if (ok) {
        float pr = v * el / 1000.0f;                      // how far it has reversed
        int r = tofRead(true);
        bool seen = r > 0 && r < sideEmpty - SIDE_SEE_MM;
        if (seen) { back = back ? back : 1; lastSeen = pr; if (back == 2) back = 1; }
        else if (back == 1 && pr - lastSeen > GAP_END_MM) back = 2;
        if (back == 2 && pr >= lastSeen + startGapMm) { placed = true; break; }
      }
      if (stopRequested()) { aborted = true; Serial.println(F("  stopped by the user")); break; }
      if (millis() - lastR > 500) {
        lastR = millis();
        cycleBoxes(ok ? "done" : "--", -1, ok ? "done" : "--", -1, "reverse");
        cycleClock(millis() - cycleT0);
        cycleProgress((float)el / ranMs, C_INFO);
      }
      if (!ok) delay(5);
    }
    servoOff(SV_BELT);
    shoe.placed = ok && placed;
    if (placed) Serial.printf("  shoe placed: toe %.0f mm before the side sensor\n", startGapMm);
  }
  stopAll();
  cycleBoxes(ok ? "done" : "--", -1, ok ? "done" : "--", -1, "stopped");
  cycleClock(millis() - cycleT0);
  if (ok) {
    char sub[40];
    snprintf(sub, sizeof(sub), "%.0f mm long, %.0f high", shoe.lenSide, shoe.maxHeight);
    cycleState("MEASURED", C_OK, sub);
    cycleProgress(1, C_OK);
  } else cycleState(aborted ? "STOPPED" : "FAILED", C_BAD, aborted ? "Stopped by the user" : "Shoe not seen at both sensors");
  Serial.println(ok ? F("  done: the shoe is back just before the side sensor") : F("  measuring failed"));
  return ok;
}
