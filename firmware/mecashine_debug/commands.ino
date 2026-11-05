// Serial Monitor commands.

// ---------------------------------------------------------------- help: a short menu, then one topic at a time
void hBar() { Serial.println(F("  ================================================")); }
void hTitle(const char *t) { Serial.println(); hBar(); Serial.printf("    %s\n", t); hBar(); }
void hHead(const char *t) { Serial.println(); Serial.printf("  %s\n", t); }
void hLine(const char *cmd, const char *what) { Serial.printf("    %-20s %s\n", cmd, what); }
void hEnd() { Serial.println(); Serial.println(F("  Stop anything: press any key, or the STOP button.")); Serial.println(); }

void help(const String &topic) {
  if (topic == "tests") {
    hTitle("TESTS");
    hLine("test", "run all 15 checks");
    hLine("test <n>", "run one check, e.g. test 4");
    hLine("report", "show the results again");
    hHead("THE 15 CHECKS");
    for (uint8_t i = 0; i < TEST_COUNT; i += 2) {
      if (i + 1 < TEST_COUNT) Serial.printf("    %2u  %-16s %2u  %s\n", i + 1, TEST_NAME[i], i + 2, TEST_NAME[i + 1]);
      else Serial.printf("    %2u  %s\n", i + 1, TEST_NAME[i]);
    }
  } else if (topic == "sensors") {
    hTitle("DISTANCE SENSORS");
    hLine("tofraw", "live readings, with the reason if bad");
    hLine("tof", "live readings, simple");
    hLine("tofstat", "100 readings: average and wobble");
    hLine("tofstat <n>", "the same with n readings");
    hLine("see side", "does the side sensor see your hand?");
    hLine("see top", "does the top sensor see your hand?");
    hHead("ADVANCED");
    hLine("tofmode side long", "ranging mode: long / default /");
    hLine("", "accurate / fast (both start long)");
    hLine("scan", "list everything on the I2C bus");
  } else if (topic == "move") {
    hTitle("MOVING THINGS");
    hHead("BY SENSOR (stops at the reading)");
    hLine("home", "jaws open, carriage up");
    hLine("jaw <mm>", "jaws to a side reading, e.g. jaw 150");
    hLine("lift <mm>", "carriage to a top reading, e.g. lift 180");
    hHead("BY HAND (any key stops)");
    char c[24], d[48];
    snprintf(c, sizeof(c), "servo 2 %u", cal.stopUs[SV_JAW] + cal.jawOpenSign * 150);  hLine(c, "open the jaws");
    snprintf(c, sizeof(c), "servo 2 %u", cal.stopUs[SV_JAW] - cal.jawOpenSign * 150);  hLine(c, "close the jaws");
    snprintf(c, sizeof(c), "servo 1 %u", cal.stopUs[SV_LIFT] + cal.liftUpSign * 150);  hLine(c, "raise the carriage");
    snprintf(c, sizeof(c), "servo 1 %u", cal.stopUs[SV_LIFT] - cal.liftUpSign * 150);  hLine(c, "lower the carriage");
    snprintf(d, sizeof(d), "hold still (jaw %u, lift %u)", cal.stopUs[SV_JAW], cal.stopUs[SV_LIFT]);
    hLine("servo <ch> <stop>", d);
    hLine("off", "no signal to any servo");
    hHead("CHANNELS");
    Serial.println(F("    0 belt    1 lift    2 jaw"));
    hHead("FAULT FINDING");
    hLine("sweep <ch>", "slow one way, then the other");
    hLine("direct <us>", "drive a servo from GPIO 4 directly");
  } else if (topic == "belt") {
    hTitle("BELT");
    Serial.printf("    active setting: %s, %.1f mm/s\n", beltFastActive ? "FAST" : "NORMAL", cal.beltMmPerS);
    hHead("RUN IT");
    hLine("beltmm <mm>", "move a distance, e.g. beltmm 200");
    hLine("beltmm -<mm>", "move back, e.g. beltmm -200");
    hLine("belt <pct> <ms>", "run for a time, e.g. belt 100 3000");
    hHead("WHICH SETTING");
    hLine("beltmode normal", "slow, for polishing");
    hLine("beltmode fast", "fast, for measuring");
    hHead("CALIBRATE THE ACTIVE SETTING");
    hLine("belttape", "empty belt: tape mark + ruler");
    hLine("beltmatch", "with an object: by the sensors");
    hLine("beltcheck", "check it: 3 trips, both speeds");
  } else if (topic == "motors") {
    hTitle("BRUSH MOTORS");
    hLine("motor <n>", "one way, stop, the other way");
    hLine("motor all", "the same, all three in turn");
    hLine("run <n> <pct>", "run, -100..100, e.g. run 1 60");
    hLine("run <n> 0", "stop it");
    hHead("NUMBERS");
    Serial.println(F("    1 side brush L    2 side brush R    3 top roller"));
    Serial.println(F("    (the pump, the spray IR and the spray pattern:  help spray)"));
  } else if (topic == "spray" || topic == "pump" || topic == "ir") {
    hTitle("SPRAY: PUMP, IR SENSOR AND BURST PATTERN");
    Serial.printf("    now: %u x %u ms on, %u ms apart, then %u ms pause; in polish %s\n", spr.count, spr.onMs, spr.gapMs, spr.pauseMs, polishSpray ? "yes" : "no");
    hHead("SPRAY IR SENSOR (GPIO 34)");
    hLine("ir", "live: shoe / clear, for setting its pot");
    hLine("ir belt", "run a shoe through: IR to side sensor mm");
    hLine("spray on", "bursts while the IR sees a shoe");
    hLine("spray off", "stop that (STOP does too)");
    hLine("spray test", "one group of bursts now, IR or not");
    hHead("SPRAY PATTERN  (set ..., then save)");
    hLine("spraycount <n>", "bursts in a group, e.g. 3");
    hLine("sprayon <ms>", "each burst, e.g. 300");
    hLine("spraygap <ms>", "between bursts, e.g. 300");
    hLine("spraypause <ms>", "after each group, e.g. 1000");
    hLine("polishspray 0/1", "spray during polish: 1 yes, 0 no");
    hHead("ULTRASONIC INSTEAD OF THE IR (HC-SR04, sees black shoes)");
    hLine("sonar 1 / sonar 0", "use the ultrasonic / the IR");
    hLine("sonarmm <mm>", "closer than this = shoe, e.g. 80");
    Serial.println(F("    ir  then shows the live distance: put a shoe in front, set sonarmm a bit above it"));
    Serial.println(F("    e.g.  set sprayon 250   then  spray test  to see it,  save  to keep"));
    hHead("PUMP (relay on GPIO 4)");
    hLine("pump <ms>", "run it for a time, e.g. pump 1500");
    hLine("pump on / pump off", "on stops itself after 10 s");
  } else if (topic == "cycle") {
    hTitle("POLISHING CYCLE");
    hLine("gripcal", "side: how hard the brushes press (once)");
    hLine("gripcal top", "top: how hard the roller presses (once)");
    hLine("polish", "side brushes and top roller, one pass");
    hLine("polish side", "side brushes only");
    hLine("polish top", "top roller only");
    hHead("TOOLS");
    hLine("measure", "measure a shoe and print its shape");
    hLine("", "(polishing does not need it)");
    hHead("COMING NEXT");
    Serial.println(F("    stage 3: add the top roller"));
  } else if (topic == "calibrate") {
    hTitle("CALIBRATION");
    hHead("IN THIS ORDER, FOR THE JAW (2) OR LIFT (1)");
    hLine("1. findstop <ch>", "find the stop pulse");
    hLine("2. test 12 / 13", "learn the direction");
    hLine("3. set jawhome / lifthome", "");
    hLine("4. save", "keep it");
    hHead("OTHER");
    hLine("findstop 0", "belt stop pulse, by eye");
    hLine("speed", "time the jaws and carriage");
    hLine("calibrate", "steps 1, 2 and speed in one go");
    hHead("SAVED SETTINGS");
    hLine("cal", "show them");
    hLine("save", "keep changes after power-off");
    hLine("load", "undo unsaved changes");
    hLine("defaults", "factory values (not saved until save)");
  } else if (topic == "set") {
    hTitle("CHANGE ONE SETTING:  set <name> <value>");
    hHead("HOME POSITIONS");
    hLine("jawhome", "side reading with the jaws fully open");
    hLine("lifthome", "top reading at the carriage home (150)");
    hHead("STOP PULSES");
    hLine("stop0 / stop1 / stop2", "belt / lift / jaw");
    hHead("DIRECTIONS (1 or -1)");
    hLine("jawsign / liftsign / beltsign", "");
    hHead("SPEEDS");
    hLine("move", "jaw and lift push, e.g. set move 100");
    hLine("beltmove / beltback", "belt push forward / back");
    hLine("beltspeed", "belt speed in mm/s");
    hHead("POLISHING");
    hLine("grip", "side reading on the shoe, mm (gripcal)");
    hLine("griptop", "top reading on the shoe, mm (gripcal top)");
    hLine("opendrop", "dip below the top that means the opening, mm");
    hLine("polishspray", "1 = spray during polish, 0 = no spray");
    hLine("exitmm", "belt travel after the shoe leaves, mm");
    hLine("liftaway", "top: rise at the opening, mm above pressing");
    hLine("liftlag", "top: lift when the roller is this far past the opening edge, mm (0; more = later)");
    hLine("", "smaller = presses harder");
    hLine("brushpct", "side brush motor power, %");
    hHead("MEASURING");
    hLine("startgap", "toe stop point before the side sensor, mm");
    Serial.println();
    Serial.println(F("    Then type  save  to keep it."));
  } else if (topic == "other") {
    hTitle("OTHER");
    hLine("pcf", "walk the PCF8575 pins");
    hLine("buttons", "START / STOP levels, live");
    hLine("knob", "menu knob reading, live");
    hLine("menu / dash", "idle screen: knob menu / dashboard");
    hLine("display", "colour test pattern");
    hLine("noisetest [pct]", "do the motors upset the sensors?");
    hLine("stop  or  x", "stop everything");
  } else {
    if (topic.length()) Serial.printf("\n  There is no help topic called %s.\n", topic.c_str());
    hTitle("SHOE POLISHER  -  COMMANDS");
    hHead("EVERYDAY");
    hLine("home", "open the jaws, raise the carriage");
    hLine("polish", "polish a shoe (side and top)");
    hLine("gripcal / gripcal top", "set how hard they press");
    hLine("test", "run all 15 checks");
    hLine("cal", "show the saved settings");
    hLine("save", "keep changes after power-off");
    hHead("MORE HELP  (type one of these)");
    hLine("help move", "jaw, lift and servos by hand");
    hLine("help belt", "belt: run, speed, calibrate");
    hLine("help sensors", "distance sensors");
    hLine("help tests", "the 15 checks");
    hLine("help motors", "brush motors");
    hLine("help spray", "pump, spray IR, burst pattern");
    hLine("help cycle", "the polishing cycle");
    hLine("help calibrate", "stop pulses, home, speeds");
    hLine("help set", "change one setting");
    hLine("help other", "everything else");
  }
  hEnd();
}
void help() { help(String("")); }

// Runs something until the time-out, a key, or STOP; then stops everything.
void holdWithTimeout(uint32_t ms) {
  Serial.printf("  running; any key or STOP ends it (time-out %lu s)\n", (unsigned long)(ms / 1000));
  waitOrAbort(ms);
  stopAll();
  Serial.println(F("  stopped"));
}

void sweep(uint8_t ch) {
  if (!pcaFound) { Serial.println(F("PCA9685 not found")); return; }
  Serial.printf("Sweep %s\n", ch < SERVO_COUNT ? SERVO_NAME[ch] : "channel");
  uint16_t stop = ch < SERVO_COUNT ? cal.stopUs[ch] : 1500;
  Serial.println(F("  stop pulse (should stand still)")); servoPulse(ch, stop); if (!waitOrAbort(1500)) return;
  Serial.println(F("  slow one way")); servoPulse(ch, stop + 60); if (!waitOrAbort(1200)) return;
  servoPulse(ch, stop); if (!waitOrAbort(800)) return;
  Serial.println(F("  slow the other way")); servoPulse(ch, stop - 60); if (!waitOrAbort(1200)) return;
  servoOff(ch);
  Serial.println(F("  done. If it crept at the stop pulse, run  findstop"));
}

void buttonsLive() {
  Serial.println(F("Button levels (HIGH = open contact, LOW = closed). Type any key to end."));
  Serial.println(F("  The buttons latch, so each push flips the level; the program counts each flip as one press."));
  int last = -1;
  while (!Serial.available()) {
    int now = (digitalRead(PIN_START) << 1) | digitalRead(PIN_STOP);
    if (now != last) { last = now; Serial.printf("  START %s   STOP %s\n", (now & 2) ? "HIGH" : "LOW ", (now & 1) ? "HIGH" : "LOW "); }
    delay(10);
  }
  while (Serial.available()) Serial.read();
}

bool setValue(const char *name, float v) {
  String n = name; n.toLowerCase();
  if (n == "jawhome") cal.jawHomeMm = v;
  else if (n == "lifthome") cal.liftHomeMm = v;
  else if (n == "move") cal.moveUs = constrain((int)v, 20, 400);
  else if (n == "beltmove") cal.beltMoveUs = constrain((int)v, 20, 600);   // up to 600: the belt servo keeps speeding up to ~1900 / ~1000 us
  else if (n == "beltback") cal.beltRevUs = constrain((int)v, 20, 600);
  else if (n == "brushpct") pol.brushPct = constrain(v, 0.0f, 100.0f);         // side brush motor power
  else if (n == "grip") gripMm = constrain(v, 5.0f, 150.0f);
  else if (n == "spraycount") spr.count = constrain((int)v, 1, 20);          // bursts in a group
  else if (n == "sprayon") spr.onMs = constrain((int)v, 20, 5000);         // ms each burst
  else if (n == "spraygap") spr.gapMs = constrain((int)v, 20, 5000);       // ms between bursts in a group
  else if (n == "spraypause") spr.pauseMs = constrain((int)v, 0, 30000);   // ms after each group
  else if (n == "liftlag") liftLagMm = constrain(v, -60.0f, 120.0f);     // top: lift this far past the opening's edge
  else if (n == "liftaway") liftAwayMm = constrain(v, 5.0f, 200.0f);     // top: rise above the pressing height at the opening
  else if (n == "exitmm") exitMm = constrain(v, 20.0f, 1000.0f);         // belt travel after the heel has left the last station
  else if (n == "polishspray") polishSpray = v != 0;
  else if (n == "sonar") { sonarOn = v != 0; irBegin(); }            // spray sensor: 1 ultrasonic HC-SR04, 0 IR FC-51
  else if (n == "sonarmm") sonarMm = constrain(v, 25.0f, 2000.0f);  // ultrasonic: closer than this is a shoe               // spray during the polishing pass
  else if (n == "opendrop") openDropMm = constrain(v, 5.0f, 100.0f);   // the top dips this much: the opening
  else if (n == "griptop") gripTopMm = constrain(v, 5.0f, 150.0f);   // top reading on the shoe while polishing                  // side reading on the shoe while polishing
  else if (n == "startgap") startGapMm = constrain(v, 0.0f, 200.0f);   // toe stop point after measuring, mm before the side sensor
  else if (n == "beltspeed") cal.beltMmPerS = constrain(v, 0.0f, 500.0f);   // the active belt setting's speed, e.g. to restore a known value
  else if (n == "stop0") cal.stopUs[0] = v;
  else if (n == "stop1") cal.stopUs[1] = v;
  else if (n == "stop2") cal.stopUs[2] = v;
  else if (n == "jawsign") cal.jawOpenSign = v < 0 ? -1 : 1;
  else if (n == "liftsign") cal.liftUpSign = v < 0 ? -1 : 1;
  else if (n == "beltsign") cal.beltFwdSign = v < 0 ? -1 : 1;
  else return false;
  return true;
}

void handle(char *line) {
  char w0[16] = "", w1[16] = "", w2[16] = "";
  float a = NAN, b = NAN;
  int n = sscanf(line, "%15s %15s %f", w0, w1, &b);
  sscanf(line, "%*s %*s %15s", w2);                     // third word as text, for commands like tofmode
  String cmd = w0; cmd.toLowerCase();
  if (n >= 2) { char *end; a = strtof(w1, &end); if (end == w1) a = NAN; }
  bool hasA = !isnan(a), hasB = n >= 3;

  if (cmd == "help" || cmd == "h" || cmd == "?") { String t = String(w1); t.toLowerCase(); help(t); }
  else if (cmd == "test" || cmd == "t") {
    if (hasA) { int i = (int)a - 1; if (i >= 0 && i < TEST_COUNT) runTest(i); else Serial.printf("test number 1..%u\n", TEST_COUNT); }
    else runAllTests();
  }
  else if (cmd == "report") printReport();
  else if (cmd == "scan" || cmd == "s") i2cScan(true);
  else if (cmd == "pcf" || cmd == "p") runTest(T_PCF);
  else if (cmd == "buttons") buttonsLive();
  else if (cmd == "knob") knobLive();
  else if (cmd == "menu") { menuOn = true; Serial.println(F("  idle screen: the knob menu (turn the knob, START chooses)")); }
  else if (cmd == "dash") { menuOn = false; Serial.println(F("  idle screen: the debug dashboard (menu  brings the knob menu back)")); }
  else if (cmd == "tof") tofWatch();
  else if (cmd == "tofstat") {
    uint16_t k = hasA ? constrain((int)a, 5, 1000) : 100;
    tofPrintStats("side", tofStats(true, k));
    tofPrintStats("top", tofStats(false, k));
  }
  else if (cmd == "tofraw") tofRawWatch();
  else if (cmd == "tofmode") {
    String who = String(w1), m = String(w2);
    Adafruit_VL53L0X::VL53L0X_Sense_config_t mode = m == "long" ? Adafruit_VL53L0X::VL53L0X_SENSE_LONG_RANGE : m == "accurate" ? Adafruit_VL53L0X::VL53L0X_SENSE_HIGH_ACCURACY
                                : m == "fast" ? Adafruit_VL53L0X::VL53L0X_SENSE_HIGH_SPEED : Adafruit_VL53L0X::VL53L0X_SENSE_DEFAULT;
    if ((who != "side" && who != "top") || (m != "long" && m != "default" && m != "accurate" && m != "fast")) {
      Serial.println(F("tofmode side|top long|default|accurate|fast")); return;
    }
    bool ok = tofSetMode(who == "side", mode);
    Serial.printf("%s sensor: %s %s\n", who.c_str(), tofModeName(mode), ok ? "set" : "FAILED (sensor missing?)");
  }
  else if (cmd == "see") {
    if (String(w1) == "side") runTest(T_SIDE_SEE);
    else if (String(w1) == "top") runTest(T_TOP_SEE);
    else Serial.println(F("see side  or  see top"));
  }
  else if (cmd == "display") { screenTestPattern(); Serial.println(F("pattern on screen; any key returns to the dashboard")); while (!Serial.available()) delay(20); while (Serial.available()) Serial.read(); }
  else if (cmd == "motor" || cmd == "m") {
    if (!pcfFound) { Serial.println(F("PCF8575 not found, so the drivers cannot be enabled")); return; }
    if (String(w1) == "all" || (hasA && (int)a == 0)) { for (uint8_t m = 0; m < MOTOR_COUNT; m++) if (!motorSequence(m, 60)) break; }
    else if (hasA && a >= 1 && a <= MOTOR_COUNT) motorSequence((int)a - 1, 60);
    else Serial.println(F("motor 1, 2, 3 or all"));
    stopAll();
  }
  else if (cmd == "run" || cmd == "r") {
    if (!hasA || !hasB || a < 1 || a > MOTOR_COUNT) { Serial.println(F("run <1-3> <-100..100>")); return; }
    motorRun((int)a - 1, (int)b);
    if ((int)b != 0) holdWithTimeout(30000);
  }
  else if (cmd == "servo" || cmd == "v") {
    if (!hasA || !hasB) { Serial.println(F("servo <channel> <microseconds>")); return; }
    if (!pcaFound) { Serial.println(F("PCA9685 not found")); return; }
    servoPulse((int)a, (int)b);
    Serial.printf("  channel %d = %d us\n", (int)a, (int)b);
    holdWithTimeout(30000);
  }
  else if (cmd == "direct") {
    if (!hasA) { Serial.println(F("direct <microseconds>: servo signal on GPIO 19, no PCA9685")); return; }
    if (sonarOn) { Serial.println(F("  GPIO 19 is the ultrasonic's TRIG now (sonar 1): set sonar 0 first")); return; }
    directServo((int)a);
    Serial.printf("  GPIO %u = %d us (servo signal wire on GPIO %u, servo + and - on the servo supply, grounds joined)\n", PIN_SERVO_DIRECT, (int)a, PIN_SERVO_DIRECT);
    holdWithTimeout(30000);
    directServoOff();
  }
  else if (cmd == "sweep" || cmd == "w") { if (hasA) sweep((int)a); else Serial.println(F("sweep <0|1|2>")); stopAll(); }
  else if (cmd == "off" || cmd == "o") { servosOff(); Serial.println(F("servo outputs off")); }
  else if (cmd == "belt") {
    if (!hasA) { Serial.println(F("belt <pct> <ms>, e.g. belt 100 2000 (percent of beltmove / beltback)")); return; }
    if (fabsf(a) > 100) Serial.println(F("  capped at 100 %: the percentage is of beltmove (forward) or beltback (backward). For more speed:  set beltmove <us>"));
    float f = constrain(a, -100, 100) / 100.0f;
    int off = (int)(f * (f >= 0 ? cal.beltMoveUs : cal.beltRevUs));
    Serial.printf("  belt pulse %d us (stop %u %+d)\n", cal.stopUs[SV_BELT] + cal.beltFwdSign * off, cal.stopUs[SV_BELT], cal.beltFwdSign * off);
    if (off != 0 && abs(off) < 100) Serial.println(F("  note: this is inside or near the belt servo's still range (about 1310..1500 us); it may not move"));
    beltDrive(f);
    waitOrAbort(hasB ? constrain((int)b, 100, 30000) : 2000);
    stopAll();
  }
  else if (cmd == "beltmm") {
    // moves the belt a distance by time alone, from the saved belt speed: no sensors. The main program positions the shoe this way.
    if (!hasA || a == 0) { Serial.println(F("beltmm <mm>, + toward the brushes, - back, e.g. beltmm 200 then beltmm -200")); return; }
    if (cal.beltMmPerS <= 0) { Serial.println(F("  belt speed not measured yet: run  belttape  or  beltmatch  and save")); return; }
    uint32_t ms = (uint32_t)(fabsf(a) / cal.beltMmPerS * 1000.0f);
    Serial.printf("  %s %.0f mm at %.1f mm/s = %.2f s\n", a > 0 ? "forward" : "back", fabsf(a), cal.beltMmPerS, ms / 1000.0f);
    if (ms > 30000) { Serial.println(F("  more than 30 s: use a shorter distance")); return; }
    beltDrive(a > 0 ? 1.0f : -1.0f);
    waitOrAbort(ms);
    stopAll();
    Serial.println(F("  done: measure where the tape mark is now"));
  }
  else if (cmd == "jaw") { if (hasA) jawTo(a); else Serial.println(F("jaw <mm of side reading>")); stopAll(); }
  else if (cmd == "lift") { if (hasA) liftTo(a); else Serial.println(F("lift <mm of top reading>")); stopAll(); }
  else if (cmd == "home") { homeAll(); stopAll(); }
  else if (cmd == "findstop") { if (hasA && a >= 0 && a < SERVO_COUNT) findStop((int)a); else Serial.println(F("findstop <0 belt | 1 lift | 2 jaw>")); }
  else if (cmd == "speed") measureSpeeds();
  else if (cmd == "beltspeed") measureBeltSpeed();
  else if (cmd == "beltmatch") beltMatch();
  else if (cmd == "beltcheck") beltCheck();
  else if (cmd == "belttape") beltTape();
  else if (cmd == "measure") measurePass();
  else if (cmd == "gripcal") gripCal(String(w1) != "top");
  else if (cmd == "spray") {
    String w = String(w1);
    if (w == "test") { sprayTest(); return; }
    if (w == "on") sprayAuto = true; else if (w == "off") sprayAuto = false;
    else if (w.length()) { Serial.println(F("spray on  or  spray off")); return; }
    Serial.printf("  spray %s%s\n", sprayAuto ? "ON: bursts while the IR sees a shoe" : "off",
                  sprayAuto ? " (spray off or STOP ends it)" : "");
    Serial.printf("  pattern: %u x %u ms, %u ms apart, then %u ms pause  (help motors)\n", spr.count, spr.onMs, spr.gapMs, spr.pauseMs);
  }
  else if (cmd == "ir") { if (String(w1) == "belt") irBelt(); else irWatch(); }
  else if (cmd == "pump") {
    String w = String(w1);
    if (w == "on") { pumpSet(true); Serial.println(F("  pump ON (switches itself off after 10 s; any key or STOP stops it)")); holdWithTimeout(PUMP_MAX_MS); }
    else if (w == "off") { pumpSet(false); Serial.println(F("  pump off")); }
    else if (hasA && a > 0) { uint32_t ms = constrain((uint32_t)a, (uint32_t)50, PUMP_MAX_MS); Serial.printf("  pump on for %lu ms\n", (unsigned long)ms); pumpSet(true); waitOrAbort(ms); pumpSet(false); Serial.println(F("  pump off")); }
    else Serial.println(F("pump on, pump off, or pump <ms>  e.g. pump 1500"));
  }
  else if (cmd == "noisetest") noiseTest(hasA ? constrain((int)a, 10, 100) : (int)pol.brushPct);
  else if (cmd == "polish") {
    String w = String(w1); w.toLowerCase(); String all = String(line); all.toLowerCase();
    bool was = polishSpray;
    if (all.indexOf("nospray") >= 0) polishSpray = false;   // this pass only
    if (w == "nospray") w = "";
    if (w == "side") polishSide(); else if (w == "top") polishTop(); else if (w == "" || w == "both") polishBoth();
    else Serial.println(F("polish  (both),  polish side,  or  polish top;  add  nospray  to leave the pump off"));
    polishSpray = was;
  }
  else if (cmd == "beltmode") {
    String m = String(w1);
    if (m == "fast") beltUse(true); else if (m == "normal") beltUse(false);
    else { Serial.println(F("beltmode fast  or  beltmode normal")); return; }
    Serial.printf("  belt %s is active: +%u us forward, -%u us back, %.1f mm/s. belt, beltmm, belttape and set beltmove/beltback now use it.\n",
                  beltFastActive ? "FAST" : "NORMAL", cal.beltMoveUs, cal.beltRevUs, cal.beltMmPerS);
  }
  else if (cmd == "calibrate") calibrateAll();
  else if (cmd == "cal") calShow();
  else if (cmd == "set") {
    if (n < 3 || !setValue(w1, b)) { Serial.println(F("set <jawhome|lifthome|move|beltmove|beltback|beltspeed|startgap|grip|griptop|opendrop|polishspray|sonar|sonarmm|exitmm|liftaway|liftlag|brushpct|stop0|stop1|stop2|jawsign|liftsign|beltsign> <value>")); return; }
    Serial.printf("  %s = %g  (type  save  to keep it)\n", w1, b);
  }
  else if (cmd == "save") calSave();
  else if (cmd == "load") { calLoad(); calShow(); }
  else if (cmd == "defaults") { cal = calibDefaults(); beltOther = {300, 300, 0}; startGapMm = 30.0f; spd = {0, 0, 0, 0}; pol = {5.0f, 60.0f, 38.0f}; gripMm = 40.0f; gripTopMm = 30.0f; openDropMm = 20.0f; polishSpray = true; exitMm = 100.0f; liftAwayMm = 40.0f; liftLagMm = 0.0f; spr = {3, 300, 300, 1000}; beltFastActive = false; Serial.println(F("  defaults loaded (not saved yet)")); calShow(); }
  else if (cmd == "stop" || cmd == "x") { sprayAuto = false; stopAll(); Serial.println(F("everything stopped")); }
  else Serial.printf("\n  Unknown command: %s   (type  help  for the list)\n\n", w0);
  stopAll();
}
