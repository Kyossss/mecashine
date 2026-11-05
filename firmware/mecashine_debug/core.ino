// Shared helpers: stopping, waiting, the yes/no question, and the saved settings (calibration). Both sketches use these;
// the single source is firmware/mecashine_debug (sync_main.py copies it).

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
  screenKeepAlive();  // and the display's set-up is re-sent every 2 s there too: homing, tests and moves block the main loop,
                      // and a servo stalling at the end of its travel can reset the display (it then stays white)
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

void beltUse(bool fast) {
  if (fast == beltFastActive) return;
  BeltSet cur = {cal.beltMoveUs, cal.beltRevUs, cal.beltMmPerS};
  cal.beltMoveUs = beltOther.fwdUs; cal.beltRevUs = beltOther.revUs; cal.beltMmPerS = beltOther.mmPerS;
  beltOther = cur;
  beltFastActive = fast;
}
BeltSet beltFastSet() { return beltFastActive ? BeltSet{cal.beltMoveUs, cal.beltRevUs, cal.beltMmPerS} : beltOther; }

void calLoad() {
  calStored = false;
  cal = calibDefaults();
  beltOther = {300, 300, 0};
  beltFastActive = false;
  prefs.begin("asps", true);
  if (prefs.getBytesLength("cal") == sizeof(Calib)) {
    Calib c;
    prefs.getBytes("cal", &c, sizeof(Calib));
    if (c.magic == CALIB_MAGIC) { cal = c; calStored = true; }
  }
  if (prefs.getBytesLength("bfast") == sizeof(BeltSet)) prefs.getBytes("bfast", &beltOther, sizeof(BeltSet));
  startGapMm = prefs.getFloat("gap", 30.0f);
  pol = {5.0f, 60.0f, 38.0f};
  if (prefs.getBytesLength("pol") == sizeof(PolishSet)) prefs.getBytes("pol", &pol, sizeof(PolishSet));
  gripMm = prefs.getFloat("grip", 40.0f);
  gripTopMm = prefs.getFloat("gript", 30.0f);
  openDropMm = prefs.getFloat("odrop", 20.0f);
  exitMm = prefs.getFloat("exitmm", 100.0f);
  liftAwayMm = prefs.getFloat("lifta", 40.0f);
  liftLagMm = prefs.getFloat("liftlag", 0.0f);
  polishSpray = prefs.getBool("pspray", true);
  sonarOn = prefs.getBool("sonar", false);
  sonarMm = prefs.getFloat("sonarmm", 80.0f);
  spr = {3, 300, 300, 1000};
  if (prefs.getBytesLength("spray") == sizeof(SpraySet)) prefs.getBytes("spray", &spr, sizeof(SpraySet));
  spd = {0, 0, 0, 0};
  if (prefs.getBytesLength("spd") == sizeof(SpeedSet)) prefs.getBytes("spd", &spd, sizeof(SpeedSet));
  prefs.end();
  irBegin();                              // the spray sensor type is known now
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
  prefs.putFloat("exitmm", exitMm);
  prefs.putFloat("lifta", liftAwayMm);
  prefs.putFloat("liftlag", liftLagMm);
  prefs.putBool("pspray", polishSpray);
  prefs.putBool("sonar", sonarOn);
  prefs.putFloat("sonarmm", sonarMm);
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
  Serial.printf("  top lift-away     %.0f mm above its pressing height on the highest part (set liftaway)\n", liftAwayMm);
  Serial.printf("  top lift point    roller axis %+.0f mm past the opening's edge (set liftlag; more = lifts later)\n", liftLagMm);
  Serial.printf("  exit travel       %.0f mm after the heel has passed the last station (set exitmm)\n", exitMm);
  Serial.printf("  spray in polish   %s (set polishspray 0/1)\n", polishSpray ? "yes, while the spray sensor sees the shoe" : "no");
  if (sonarOn) Serial.printf("  spray sensor      ultrasonic HC-SR04: a shoe is closer than %.0f mm (set sonarmm; set sonar 0 = IR)\n", sonarMm);
  else Serial.println(F("  spray sensor      IR FC-51 (set sonar 1 = ultrasonic HC-SR04)"));
  Serial.printf("  spray bursts      %u x %u ms on, %u ms apart, then %u ms pause\n", spr.count, spr.onMs, spr.gapMs, spr.pauseMs);
}

// ---------------------------------------------------------------- priming the pump (a menu item in both sketches)
// Pump on until START is pressed again (polish has reached the nozzle), STOP or a key cancels, 10 s at most.
void primePump() {
  Serial.println(F("PRIME PUMP: press START when mist comes out of the nozzle (STOP or any key cancels, 10 s limit)"));
  menuFrame("STOP cancels");
  menuState("PRIMING", C_INFO, "Watch the nozzle.", "Press START when you see mist.");
  pumpSet(true);
  uint32_t t0 = millis(), lastDraw = 0;
  uint8_t how = 0;                                     // 0 time-out, 1 START, 2 cancelled
  while (true) {
    uint32_t t = millis() - t0;
    if (t >= PUMP_MAX_MS) break;                       // before stopRequested, whose pumpTick would also switch it off
    if (buttonPressed(btnStart)) { how = 1; break; }
    if (stopRequested()) { how = 2; break; }
    if (tftOk && millis() - lastDraw > 100) {
      lastDraw = millis();
      char buf[12];
      snprintf(buf, sizeof(buf), "%4.1f s ", t / 1000.0f);
      text(24, 200, buf, C_INFO, 4, C_BG);
      tft.fillRect(24, 250, (int16_t)(432L * t / PUMP_MAX_MS), 8, C_INFO);
      screenKeepAlive();
    }
    delay(5);
  }
  pumpSet(false);
  float s = (millis() - t0) / 1000.0f;
  char l1[40];
  if (how == 1) {
    snprintf(l1, sizeof(l1), "The pump ran %.1f s.", s);
    menuState("PRIMED", C_OK, l1, "Ready to polish.");
    Serial.printf("  primed: the pump ran %.1f s\n", s);
  } else if (how == 0) {
    menuState("NO MIST?", C_WARN, "Stopped after 10 s. Is the tank", "empty, or a tube off? Try again.");
    Serial.println(F("  stopped after 10 s without START: tank empty, a tube off, or the nozzle blocked?"));
  } else {
    menuState("CANCELLED", C_DIM, "Pump stopped.", "");
    Serial.println(F("  cancelled"));
  }
  if (tftOk) {
    tft.fillRect(0, 292, 480, 28, C_PANEL);
    text(10, 299, "Turn the knob for the menu", C_DIM, 2, C_PANEL);
  }
}

