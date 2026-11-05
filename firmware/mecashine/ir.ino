// COPIED from firmware/mecashine_debug by sync_main.py. Do not edit here: edit it there and run sync_main.py.
// ================================================================ spray-station IR sensor (FC-51 on the far spray post)
// It sits before the side polisher and tells the pump when a shoe is passing the nozzles. Two debug tools:
//   ir       live state, for setting the module's sensitivity pot
//   ir belt  carries a shoe past it and the side sensor, and measures how far apart they are along the belt

void irWatch() {
  Serial.println(F("SPRAY IR, live (any key or STOP ends)"));
  Serial.println(F("  Turn the module's pot until it says SHOE with a shoe in front of the nozzles, and clear with nothing there."));
  Serial.println(F("  The module's own LED should agree. Try a dark shoe too: dark leather reflects the least."));
  while (Serial.available()) Serial.read();
  bool state = irSeen();
  uint32_t since = millis(), lastBeat = millis();
  uint16_t changes = 0, chatter = 0;
  bool lastRaw = irRaw();
  if (sonarOn) Serial.printf("  ULTRASONIC: a shoe is closer than %.0f mm (set sonarmm). The distance is shown every half second.\n", sonarMm);
  Serial.printf("  %s\n", state ? "SHOE" : "clear");
  while (true) {
    bool raw = irRaw();
    if (raw != lastRaw) { lastRaw = raw; chatter++; }
    bool s = irSeen();
    if (s != state) {
      Serial.printf("  %-6s (was %s for %.2f s)", s ? "SHOE" : "clear", state ? "SHOE" : "clear", (millis() - since) / 1000.0f);
      if (sonarOn) Serial.printf("  %.0f mm", usLastMm);
      Serial.println();
      state = s; since = millis(); changes++;
      screenDashboard(false);
    }
    if (sonarOn && millis() - lastBeat > 500) {
      lastBeat = millis();
      if (!usAlive()) Serial.println(F("    no echo pulses: check TRIG on GPIO 19, ECHO through the divider to GPIO 34, VCC 5 V, GND"));
      else if (usLastMm == 0) Serial.printf("    %s   nothing in range\n", state ? "SHOE" : "clear");
      else Serial.printf("    %s   %.0f mm\n", state ? "SHOE" : "clear", usLastMm);
      chatter = 0;
    } else if (!sonarOn && millis() - lastBeat > 2000) {
      lastBeat = millis();
      Serial.printf("    still %s   (raw flickers in the last 2 s: %u%s)\n", state ? "SHOE" : "clear", chatter,
                    chatter > 4 ? " - at the edge of its range: turn the pot a little" : "");
      chatter = 0;
    }
    if (Serial.available() || buttonPressed(btnStop)) break;
    delay(1);
  }
  while (Serial.available()) Serial.read();
  Serial.printf("  ended: %u changes\n", changes);
}

void irBelt() {
  if (!pcaFound || !sideFound) { Serial.println(F("Needs the PCA9685 and the side sensor")); return; }
  bool was = beltFastActive;
  beltUse(false);
  if (cal.beltMmPerS <= 0) { beltUse(was); Serial.println(F("Normal belt speed not calibrated: beltmode normal, belttape, save")); return; }
  const float v = cal.beltMmPerS;
  Serial.println(F("IR ON THE BELT: where the IR sees the shoe, compared with the side sensor"));
  if (!homeOne(true)) { beltUse(was); stopAll(); Serial.println(F("  could not open the jaws")); return; }
  float sideEmpty = tofAvg(true, 9);
  if (sideEmpty < 0) { beltUse(was); stopAll(); Serial.println(F("  the side sensor gives no reading")); return; }
  if (irSeen()) { Serial.println(F("  the IR already sees something with the belt empty: turn its pot down, or clear its view (ir)")); beltUse(was); stopAll(); return; }
  if (askYesNo("Put the shoe on the belt BEFORE the spray posts, toe first, in the middle. Ready?") != 1) { beltUse(was); stopAll(); return; }

  tofContinuous(true);
  beltDrive(1.0f);
  uint32_t t0 = millis();
  float irOn = -1, irOff = -1, sideOn = -1, sideLast = -1, sideOff = -1;
  uint16_t irDrops = 0;                                   // the IR lost the shoe for a moment while it was passing
  bool irState = false;
  while (true) {
    float pos = v * (millis() - t0) / 1000.0f;
    bool s = irSeen();
    if (s != irState) {
      irState = s;
      if (s && irOn < 0) { irOn = pos; Serial.printf("  IR: toe at %.0f mm of belt travel\n", pos); }
      else if (s && irOff >= 0) { irDrops++; irOff = -1; }   // it came back: the earlier "clear" was a drop-out, not the heel
      else if (!s && irOn >= 0) irOff = pos;
    }
    int r = tofPoll(true);
    if (r > 0) {
      bool seen = r < sideEmpty - SIDE_SEE_MM;
      if (seen) { if (sideOn < 0) { sideOn = pos; Serial.printf("  side sensor: toe at %.0f mm\n", pos); } sideLast = pos; }
      else if (sideOn >= 0 && sideOff < 0 && pos - sideLast > GAP_END_MM) { sideOff = sideLast; Serial.printf("  side sensor: heel at %.0f mm\n", sideOff); }
    }
    if (sideOff >= 0 && irOff >= 0 && pos - irOff > 30) break;
    if (pos > 1000) { Serial.println(F("  1 m of belt and not done: stopped")); break; }
    if (stopRequested()) { aborted = true; Serial.println(F("  stopped by the user")); break; }
    delay(1);
  }
  servoOff(SV_BELT);
  tofContinuous(false);
  stopAll();
  beltUse(was);
  Serial.println(F("  RESULT"));
  if (irOn < 0) { Serial.println(F("    the IR never saw the shoe: turn its pot up, or aim it at the middle of the shoe's height")); return; }
  if (irOff >= 0) Serial.printf("    IR saw the shoe for %.0f mm (%u drop-outs while it passed%s)\n", irOff - irOn, irDrops, irDrops ? ": dark leather or a curve; the firmware will bridge short ones" : "");
  if (sideOn >= 0) {
    Serial.printf("    IR to side sensor   %.0f mm along the belt (the firmware uses %.0f)\n", sideOn - irOn, IR_TO_SIDE_SENSOR_MM);
    if (sideOff >= 0 && irOff >= 0) Serial.printf("    shoe length         IR %.0f mm, side sensor %.0f mm (the IR's is longer if it sees the shoe from further away)\n", irOff - irOn, sideOff - sideOn);
  }
}

// ---------------------------------------------------------------- spray on / off: bursts while the IR sees a shoe (debug)
// The pattern (spr): count bursts of onMs, gapMs apart, then pauseMs, repeated while the IR sees the shoe:  '''_'''_'''
// It starts at the first burst each time a shoe arrives and stops at once when the IR is clear. Runs from the main loop
// (not during a test or a pass).
// Where in the pattern we are at time t (ms since the pattern started): true while a burst is on.
bool sprayPatternOn(uint32_t t) {
  uint32_t group = (uint32_t)spr.count * spr.onMs + (uint32_t)(spr.count - 1) * spr.gapMs;
  uint32_t period = group + spr.pauseMs;
  uint32_t u = period ? t % period : 0;
  if (u >= group) return false;                               // the long pause
  return u % ((uint32_t)spr.onMs + spr.gapMs) < spr.onMs;     // a burst, or the short gap after it
}

// Runs the burst pattern while want is true: starts at the first burst when want turns on, pump off at once when it turns off.
// Also reports how long after the IR module's output changed the pump came on, and the main loop's slowest pass, so a
// delay can be traced to the firmware (a slow loop) or to the hardware (the module or the relay).
void sprayUpdate(bool want) {
  static bool on = false, active = false;
  static uint32_t t0 = 0, lastCall = 0, slowest = 0, slowAt = 0;
  uint32_t now = millis();
  if (lastCall && now - lastCall > slowest) slowest = now - lastCall;
  if (now - slowAt > 5000) { slowAt = now; slowest = lastCall ? now - lastCall : 0; }
  lastCall = now;
  if (!want) {
    if (active) { active = false; if (on) { pumpSet(false); on = false; } Serial.println(F("  spray: IR clear, stopped")); }
    return;
  }
  bool first = !active;
  if (!active) { active = true; t0 = now; }
  bool burst = sprayPatternOn(now - t0);
  if (on && !pumpOnAt) on = false;                            // something else (STOP, a command) switched the pump off
  if (burst != on) { pumpSet(burst); on = burst; }
  if (first) Serial.printf("  spray: IR sees a shoe, bursting (relay on %lu ms after the IR output changed; slowest loop pass lately %lu ms)\n",
                           (unsigned long)(millis() - irEdgeAt), (unsigned long)slowest);
}
void sprayTick() { sprayUpdate(sprayAuto && irSeen()); }

// one group of bursts straight away, IR or not, to see the pattern (hose in a cup)
void sprayTest() {
  Serial.printf("  spray test: %u x %u ms, %u ms apart (any key or STOP stops)\n", spr.count, spr.onMs, spr.gapMs);
  for (uint16_t k = 0; k < spr.count; k++) {
    pumpSet(true);
    if (!waitOrAbort(spr.onMs)) break;
    pumpSet(false);
    if (k + 1 < spr.count && !waitOrAbort(spr.gapMs)) break;
  }
  pumpSet(false);
  Serial.println(F("  done"));
}
