// COPIED from firmware/mecashine_debug by sync_main.py. Do not edit here: edit it there and run sync_main.py.
// ================================================================ evaluation logs for the thesis (Testing Instruments)
// Sheet A   eval tof <side|top> <white|black> <actual mm>   10 readings at a distance measured with a ruler -> one row
// Sheet B1  every polishing pass is logged by itself, in both firmwares, with the shoe size set by  eval size <US>
// Sheet B2  every START that starts a pass and every STOP pressed during a pass is logged, with the time the machine took
// The logs are kept in flash (NVS "asps", keys ev_*): they survive power-off and switching between the two firmwares.
// The printing commands are in the debug firmware (commands.ino -> evalCommand).

struct EvalTof { uint8_t side, black; uint16_t actual; float mean, sd; uint8_t n, pad[3]; };
struct EvalCycle { uint8_t size2, done, failAt, reason, sprays, restarts; uint16_t ds; };   // ds = cycle time in 0.1 s
struct EvalPress { uint8_t isStop, responded; uint16_t ms; uint16_t cycle, pad; };
constexpr uint8_t EVAL_MAX_TOF = 40, EVAL_MAX_CYC = 60, EVAL_MAX_PRESS = 80;
EvalTof evTof[EVAL_MAX_TOF]; uint8_t evNTof = 0;
EvalCycle evCyc[EVAL_MAX_CYC]; uint8_t evNCyc = 0;
EvalPress evPress[EVAL_MAX_PRESS]; uint8_t evNPress = 0;
uint8_t evSize2 = 0;                       // shoe size x 2 (so 9.5 fits), 0 = not set
bool evLoaded = false;

enum : uint8_t { EF_NONE, EF_MIST, EF_SIDE, EF_TOP, EF_CONVEYOR, EF_USER };
enum : uint8_t { ER_NONE, ER_NOTOE, ER_TOPMISS, ER_TOOLONG, ER_TIMEOUT, ER_USER, ER_NOSPRAY, ER_NOTHOME, ER_KEY };
const char *const EF_NAME[] = {"-", "mist", "side", "top", "conveyor", "-"};
const char *const ER_NAME[] = {"", "the shoe never reached the side sensor", "the top sensor did not see the shoe",
                               "the shoe took too long to pass", "over 2 minutes", "stopped with STOP (a Sheet B2 trial)",
                               "the spray sensor never saw the shoe", "a station did not get back home",
                               "stopped from the Serial Monitor"};

void evalLoad() {
  if (evLoaded) return;
  evLoaded = true;
  prefs.begin("asps", true);
  evSize2 = prefs.getUChar("ev_size", 0);
  size_t n;
  n = prefs.getBytesLength("ev_tof");   if (n && n % sizeof(EvalTof) == 0 && n <= sizeof(evTof)) { prefs.getBytes("ev_tof", evTof, n); evNTof = n / sizeof(EvalTof); }
  n = prefs.getBytesLength("ev_cyc");   if (n && n % sizeof(EvalCycle) == 0 && n <= sizeof(evCyc)) { prefs.getBytes("ev_cyc", evCyc, n); evNCyc = n / sizeof(EvalCycle); }
  n = prefs.getBytesLength("ev_press"); if (n && n % sizeof(EvalPress) == 0 && n <= sizeof(evPress)) { prefs.getBytes("ev_press", evPress, n); evNPress = n / sizeof(EvalPress); }
  prefs.end();
}
void evalSave() {
  prefs.begin("asps", false);
  prefs.putUChar("ev_size", evSize2);
  if (evNTof) prefs.putBytes("ev_tof", evTof, evNTof * sizeof(EvalTof)); else prefs.remove("ev_tof");
  if (evNCyc) prefs.putBytes("ev_cyc", evCyc, evNCyc * sizeof(EvalCycle)); else prefs.remove("ev_cyc");
  if (evNPress) prefs.putBytes("ev_press", evPress, evNPress * sizeof(EvalPress)); else prefs.remove("ev_press");
  prefs.end();
}
void evalAddPress(bool isStop, bool responded, uint32_t ms) {
  evalLoad();
  if (evNPress >= EVAL_MAX_PRESS) { Serial.println(F("  eval: the button log is full (eval clear buttons)")); return; }
  evPress[evNPress++] = {(uint8_t)isStop, (uint8_t)responded, (uint16_t)min<uint32_t>(ms, 65535), (uint16_t)(evNCyc + 1), 0};
  evalSave();
}

// ---------------------------------------------------------------- hooks called by the polishing pass
// The belt has just started: if START was pressed in the last 5 s, that press is logged with the time until the belt moved.
void evalPassStarted() {
  uint32_t ago = millis() - btnStart.changedAt;
  if (btnStart.changedAt && ago < 5000) {
    evalAddPress(false, true, ago);
    Serial.printf("  eval: START logged, belt moving %.2f s after the press\n", ago / 1000.0f);
  }
}
// The pass has ended (motors already off). stopMs: STOP press to motors off, 0 if not stopped with the button.
void evalPassEnded(bool ok, uint8_t failAt, uint8_t reason, uint16_t sprays, uint16_t restarts, uint32_t ms, uint32_t stopMs) {
  evalLoad();
  if (stopMs) { evalAddPress(true, true, stopMs); Serial.printf("  eval: STOP logged, motors off %.3f s after the press\n", stopMs / 1000.0f); }
  if (evNCyc >= EVAL_MAX_CYC) { Serial.println(F("  eval: the cycle log is full (eval clear cycles)")); return; }
  evCyc[evNCyc++] = {evSize2, (uint8_t)ok, failAt, reason, (uint8_t)min<uint16_t>(sprays, 255), (uint8_t)min<uint16_t>(restarts, 255),
                     (uint16_t)min<uint32_t>(ms / 100, 65535)};
  evalSave();
  Serial.printf("  eval: cycle %u logged (%s%s%s)\n", evNCyc, ok ? "completed" : failAt == EF_USER ? "stopped by the user" : "failed at ",
                ok || failAt == EF_USER ? "" : EF_NAME[failAt], evSize2 ? "" : "; shoe size not set: eval size <US>");
}

// ---------------------------------------------------------------- Sheet A: one row from 10 readings
void evalTofRow(bool side, bool black, uint16_t actual) {
  evalLoad();
  if (side ? !sideFound : !topFound) { Serial.println(F("  that sensor is not found")); return; }
  tofContinuous(false);
  int v[10]; uint8_t n = 0;
  for (uint8_t i = 0; i < 40 && n < 10; i++) { int r = tofRead(side); if (r > 0) v[n++] = r; delay(40); }
  if (n < 10) { Serial.printf("  only %u good readings out of 40 tries: hold the %s steady, square to the sensor\n", n, black ? "leather" : "card"); if (n == 0) return; }
  float sum = 0, sum2 = 0;
  for (uint8_t i = 0; i < n; i++) { sum += v[i]; sum2 += (float)v[i] * v[i]; }
  float mean = sum / n, sd = n > 1 ? sqrtf(max(0.0f, (sum2 - sum * sum / n) / (n - 1))) : 0;
  Serial.print(F("  readings:")); for (uint8_t i = 0; i < n; i++) Serial.printf(" %d", v[i]); Serial.println();
  float err = mean - actual;
  Serial.printf("  %s | %s | %u | %.1f | %+.1f | %.1f %%   (SD %.1f mm, %u readings)\n", side ? "Side" : "Top", black ? "Black leather" : "White card",
                actual, mean, err, fabsf(err) / actual * 100, sd, n);
  uint8_t k = 0;
  while (k < evNTof && !(evTof[k].side == side && evTof[k].black == black && evTof[k].actual == actual)) k++;
  if (k == evNTof) { if (evNTof >= EVAL_MAX_TOF) { Serial.println(F("  the Sheet A log is full")); return; } evNTof++; }
  else Serial.println(F("  (replaces the earlier row for this sensor, surface and distance)"));
  evTof[k] = {(uint8_t)side, (uint8_t)black, actual, mean, sd, n, {0, 0, 0}};
  evalSave();
}

// ---------------------------------------------------------------- printing (debug firmware)
void evalPrintTof() {
  evalLoad();
  Serial.println(F("\nSHEET A - ToF distance accuracy (mean of 10 readings)"));
  Serial.println(F("Sensor | Surface | Actual (mm) | Mean reading (mm) | Error (mm) | Error (%)"));
  for (uint8_t s = 2; s-- > 0;) for (uint8_t b = 0; b < 2; b++) {
    float se = 0, sp = 0; uint8_t cnt = 0;
    for (uint16_t d = 1; d <= 2000; d++) for (uint8_t k = 0; k < evNTof; k++) {
      const EvalTof &r = evTof[k];
      if (r.side != s || r.black != b || r.actual != d) continue;
      float e = r.mean - r.actual;
      Serial.printf("%s | %s | %u | %.1f | %+.1f | %.1f\n", s ? "Side" : "Top", b ? "Black leather" : "White card", r.actual, r.mean, e, fabsf(e) / r.actual * 100);
      se += fabsf(e); sp += fabsf(e) / r.actual * 100; cnt++;
    }
    if (cnt) Serial.printf("   -> %s, %s: mean absolute error %.1f mm, mean error %.1f %% (%u distances)\n", s ? "Side" : "Top", b ? "black leather" : "white card", se / cnt, sp / cnt, cnt);
  }
  if (!evNTof) Serial.println(F("  (no rows yet: eval tof side white 50)"));
}

void evalPrintCycles() {
  evalLoad();
  Serial.println(F("\nSHEET B1 - Cycle completion"));
  Serial.println(F("Cycle | Shoe size (US) | Completed (Y/N) | Failed at | Cause and notes"));
  uint16_t done = 0, counted = 0;
  for (uint8_t i = 0; i < evNCyc; i++) {
    const EvalCycle &c = evCyc[i];
    char size[8]; if (c.size2) snprintf(size, sizeof(size), c.size2 % 2 ? "%.1f" : "%.0f", c.size2 / 2.0f); else strcpy(size, "?");
    bool user = c.failAt == EF_USER;
    if (!user) { counted++; if (c.done) done++; }
    char notes[120];
    snprintf(notes, sizeof(notes), "%s%s%.1f s; spray bursts %u; sensor restarts %u", ER_NAME[c.reason], c.reason ? "; " : "", c.ds / 10.0f, c.sprays, c.restarts);
    Serial.printf("%u | %s | %s | %s | %s\n", i + 1, size, user ? "-" : c.done ? "Y" : "N", c.done ? "-" : EF_NAME[c.failAt], notes);
  }
  if (!evNCyc) { Serial.println(F("  (no cycles yet: they are logged by themselves when you polish)")); return; }
  Serial.printf("Completion rate = %u / %u = %.1f %%", done, counted, counted ? 100.0f * done / counted : 0.0f);
  if (counted != evNCyc) Serial.printf("   (%u cycles stopped with STOP are left out: they are Sheet B2 trials)", evNCyc - counted);
  Serial.println();
  // per shoe size, as the analysis table asks
  for (uint8_t sz = 1; sz < 255; sz++) {
    uint16_t n = 0, d = 0;
    for (uint8_t i = 0; i < evNCyc; i++) if (evCyc[i].size2 == sz && evCyc[i].failAt != EF_USER) { n++; if (evCyc[i].done) d++; }
    if (n) Serial.printf("   size %s: %u / %u = %.1f %%\n", String(sz / 2.0f, sz % 2 ? 1 : 0).c_str(), d, n, 100.0f * d / n);
  }
}

void evalPrintButtons() {
  evalLoad();
  Serial.println(F("\nSHEET B2 - Start/stop response"));
  Serial.println(F("Trial | Button (Start / Stop) | Responded (Y/N) | Time to full stop (s), Stop only | Notes"));
  uint16_t nS = 0, rS = 0, nT = 0, rT = 0; float sumT = 0; uint16_t cntT = 0;
  for (uint8_t i = 0; i < evNPress; i++) {
    const EvalPress &p = evPress[i];
    char t[12] = "-", notes[90];
    if (p.isStop) {
      nT++; if (p.responded) { rT++; snprintf(t, sizeof(t), "%.2f", p.ms / 1000.0f); sumT += p.ms; cntT++; }
      snprintf(notes, sizeof(notes), p.responded ? "during cycle %u; all motors switched off" : "nothing happened (logged by hand)", p.cycle);
    } else {
      nS++; if (p.responded) rS++;
      if (p.responded) snprintf(notes, sizeof(notes), "cycle %u; belt moving %.2f s after the press", p.cycle, p.ms / 1000.0f);
      else strcpy(notes, "nothing happened (logged by hand)");
    }
    Serial.printf("%u | %s | %s | %s | %s\n", i + 1, p.isStop ? "Stop" : "Start", p.responded ? "Y" : "N", t, notes);
  }
  if (!evNPress) { Serial.println(F("  (no presses yet: START a polish, and press STOP during some)")); return; }
  Serial.printf("Start: %u / %u responded = %.1f %%.  Stop: %u / %u = %.1f %%.  Response rate overall %.1f %%\n", rS, nS, nS ? 100.0f * rS / nS : 0.0f,
                rT, nT, nT ? 100.0f * rT / nT : 0.0f, (nS + nT) ? 100.0f * (rS + rT) / (nS + nT) : 0.0f);
  if (cntT) Serial.printf("Mean time from STOP to all motors off: %.3f s (the brushes coast a little after that: watch them)\n", sumT / cntT / 1000.0f);
}

// ---------------------------------------------------------------- the eval command (debug firmware)
void evalHelp() {
  Serial.println(F("EVAL - data for the thesis sheets (kept in flash; survives power-off and the user firmware)"));
  Serial.println(F("  eval size <US>                       shoe size for the next cycles, e.g. eval size 9.5"));
  Serial.println(F("  eval tof <side|top> <white|black> <mm>  Sheet A: hold the card / leather at <mm> (ruler, from the"));
  Serial.println(F("                                       sensor's front face), square to it: 10 readings -> one row"));
  Serial.println(F("  eval tof                             Sheet A table + mean error per sensor and surface"));
  Serial.println(F("  eval cycles                          Sheet B1 (every polish is logged by itself)"));
  Serial.println(F("  eval buttons                         Sheet B2 (START that starts a polish, STOP during one)"));
  Serial.println(F("  eval miss <start|stop>               log a press that did nothing (the firmware cannot see those)"));
  Serial.println(F("  eval all                             all three"));
  Serial.println(F("  eval clear <tof|cycles|buttons|all>  start a sheet again"));
}
void evalCommand(const char *line) {
  evalLoad();
  char w[5][16] = {"", "", "", "", ""};
  int n = sscanf(line, "%15s %15s %15s %15s %15s", w[0], w[1], w[2], w[3], w[4]);
  String a = w[1]; a.toLowerCase();
  if (n < 2) { evalHelp(); return; }
  if (a == "size") {
    float s = atof(w[2]);
    evSize2 = (uint8_t)constrain(lroundf(s * 2), 0, 254); evalSave();
    if (evSize2) Serial.printf("  shoe size %s for the next cycles\n", w[2]); else Serial.println(F("  shoe size cleared"));
  } else if (a == "tof") {
    if (n < 5) { evalPrintTof(); return; }
    String s = w[2], f = w[3]; s.toLowerCase(); f.toLowerCase();
    int mm = atoi(w[4]);
    if ((s != "side" && s != "top") || (f != "white" && f != "black") || mm < 10 || mm > 2000) { Serial.println(F("  eval tof <side|top> <white|black> <mm>, e.g. eval tof side white 50")); return; }
    evalTofRow(s == "side", f == "black", mm);
  } else if (a == "cycles") evalPrintCycles();
  else if (a == "buttons") evalPrintButtons();
  else if (a == "all") { evalPrintTof(); evalPrintCycles(); evalPrintButtons(); }
  else if (a == "miss") {
    String b = w[2]; b.toLowerCase();
    if (b != "start" && b != "stop") { Serial.println(F("  eval miss start  or  eval miss stop")); return; }
    evalAddPress(b == "stop", false, 0); Serial.printf("  logged: a %s press that did nothing\n", b.c_str());
  } else if (a == "clear") {
    String b = w[2]; b.toLowerCase();
    if (b == "tof" || b == "all") evNTof = 0;
    if (b == "cycles" || b == "all") evNCyc = 0;
    if (b == "buttons" || b == "all") evNPress = 0;
    if (b != "tof" && b != "cycles" && b != "buttons" && b != "all") { Serial.println(F("  eval clear <tof|cycles|buttons|all>")); return; }
    evalSave(); Serial.printf("  cleared: %s\n", b.c_str());
  } else evalHelp();
}
