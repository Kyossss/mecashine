// The user's screens: boot logo, the knob menu, Settings and the Self-test. Only in the user firmware.

// ---------------------------------------------------------------- boot screen
// The logo (logo.h, from make_logo.py) on black, the version, and a loading bar along the bottom that fills as start-up
// goes on. bootLogo(0, ..) draws it all; bootLogo(1..BOOT_STEPS, what) moves the bar on and says what is starting.
#include "logo.h"
constexpr uint8_t BOOT_STEPS = 4;
constexpr int16_t BAR_X = 40, BAR_Y = 292, BAR_W = 400, BAR_H = 8;
void bootLogo(uint8_t step, const char *what) {
  if (!tftOk) return;
  const uint16_t BLACK = 0, GOLD = C_WARN;
  static int16_t filled = 0;
  if (step == 0) {
    tft.fillScreen(BLACK);
    tft.drawRGB565((480 - LOGO_W) / 2, 100, LOGO_W, LOGO_H, LOGO);
    text(102, 206, "AUTOMATIC SHOE POLISHER", C_DIM, 2, BLACK);
    char v[24];
    snprintf(v, sizeof(v), "v%s", FW_VERSION);
    text(474 - 6 * strlen(v), 8, v, C_DIM, 1, BLACK);
    tft.fillRect(BAR_X, BAR_Y, BAR_W, BAR_H, C_PANEL);
    filled = 0;
  }
  tft.fillRect(BAR_X, BAR_Y - 20, BAR_W, 12, BLACK);
  text(BAR_X, BAR_Y - 20, what, C_DIM, 1, BLACK);
  // fill smoothly up to this step
  int16_t to = (int16_t)((int32_t)BAR_W * min<uint8_t>(step, BOOT_STEPS) / BOOT_STEPS);
  while (filled < to) {
    int16_t n = min<int16_t>(8, to - filled);
    tft.fillRect(BAR_X + filled, BAR_Y, n, BAR_H, GOLD);
    filled += n;
    delay(12);
  }
}

// ---------------------------------------------------------------- the knob
// The turn is split into one zone per row; the choice moves only once the reading is clearly in another zone and has
// stayed there for 150 ms (the 50k pot picks up noise). The two ends of the turn are left out.
constexpr int KNOB_LO = 200, KNOB_HI = 3900, KNOB_BAND = 200;
float knobF = -1;
int knobRaw() {
  uint32_t s = 0;
  for (uint8_t i = 0; i < 32; i++) s += analogRead(PIN_KNOB);
  return s / 32;
}
uint8_t knobPick(uint8_t count, uint8_t cur) {
  static int8_t cand = -1;
  static uint32_t candAt = 0;
  knobF = knobF < 0 ? knobRaw() : knobF + 0.15f * (knobRaw() - knobF);
  float zone = (KNOB_HI - KNOB_LO) / (float)count, lo = KNOB_LO + cur * zone;
  if (cur < count && knobF >= lo - KNOB_BAND && knobF <= lo + zone + KNOB_BAND) { cand = -1; return cur; }
  int8_t want = constrain((int)((knobF - KNOB_LO) / zone), 0, count - 1);
  if (want != cand) { cand = want; candAt = millis(); return cur < count ? cur : want; }
  if (millis() - candAt >= 150) { cand = -1; return want; }
  return cur < count ? cur : want;
}

// ---------------------------------------------------------------- menu pages (also used by the shared code)
void menuFrame(const char *footer) {
  if (!tftOk) return;
  scrKind = 2; msShown = false;
  if (footer != mfFooter) strlcpy(mfFooter, footer, sizeof(mfFooter));
  screenHold = true;
  tft.fillScreen(C_BG);
  tft.fillRect(0, 0, 480, 34, C_PANEL);
  text(10, 9, "MECASHINE", C_TEXT, 2, C_PANEL);
  tft.fillRect(0, 292, 480, 28, C_PANEL);
  text(10, 299, footer, C_DIM, 2, C_PANEL);
}
void menuState(const char *state, uint16_t col, const char *l1, const char *l2) {
  if (!tftOk) return;
  if (state != msState) strlcpy(msState, state, sizeof(msState));
  if (l1 != msL1) strlcpy(msL1, l1, sizeof(msL1));
  if (l2 != msL2) strlcpy(msL2, l2, sizeof(msL2));
  msCol = col; msShown = true;
  tft.fillRect(0, 40, 480, 250, C_BG);
  text(24, 70, state, col, 4);
  text(24, 130, l1, C_TEXT, 2);
  text(24, 156, l2, C_TEXT, 2);
}
void menuFooter(const char *s) {
  if (!tftOk) return;
  tft.fillRect(0, 292, 480, 28, C_PANEL);
  text(10, 299, s, C_DIM, 2, C_PANEL);
}

// ---------------------------------------------------------------- the main menu
const char *const UITEM[] = {"Polish shoe", "Home machine", "Prime pump", "Self-test", "Settings"};
enum : uint8_t { U_POLISH, U_HOME, U_PRIME, U_TEST, U_SETTINGS, U_COUNT };
uint8_t uSel = 0;
int8_t uDrawn = -1;
bool inSettings = false;

// why a row cannot be chosen now, or nullptr if it can
const char *uBlocked(uint8_t i) {
  if ((i == U_POLISH || i == U_HOME) && !machineSetUp()) return "service";
  if (i == U_POLISH && !machineHomed) return "home first";
  return nullptr;
}

void drawRows(const char *const *names, const char *const *values, uint8_t count, uint8_t sel, int8_t drawn, bool all) {
  for (uint8_t i = 0; i < count; i++) {
    if (!all && i != sel && i != drawn) continue;          // only the two rows that changed
    int16_t y = 42 + i * 49;
    const char *why = values ? nullptr : uBlocked(i);
    bool on = i == sel, ok = why == nullptr;
    uint16_t bg = on ? (ok ? C_INFO : C_DIM) : C_PANEL;
    tft.fillRect(20, y, 440, 43, bg);
    text(40, y + 10, names[i], on ? C_BG : (ok ? C_TEXT : C_DIM), 3, bg);
    const char *right = values ? values[i] : why;
    if (right && right[0]) text(456 - 12 * strlen(right), y + 15, right, on ? C_BG : (values ? C_WARN : C_DIM), 2, bg);
  }
}

void menuScreen(bool full) {
  if (!tftOk || screenHold) return;
  scrKind = 0;
  if (inSettings) { settingsScreen(full); return; }
  static bool homedDrawn = false;
  if (homedDrawn != machineHomed) { homedDrawn = machineHomed; full = true; }
  if (full) {
    tft.fillScreen(C_BG);
    tft.fillRect(0, 0, 480, 34, C_PANEL);
    text(10, 9, "MECASHINE", C_TEXT, 2, C_PANEL);
    text(330, 9, machineHomed ? "  ready" : "not homed", machineHomed ? C_OK : C_WARN, 2, C_PANEL);
    menuFooter("Turn the knob, then press START");
    uDrawn = -1;
  }
  if (uDrawn == uSel) return;
  drawRows(UITEM, nullptr, U_COUNT, uSel, uDrawn, uDrawn < 0);
  uDrawn = uSel;
}
void screenIdle(bool full) { if (full) scrKind = 0; menuScreen(full); }

// ---------------------------------------------------------------- settings
const char *const SITEM[] = {"Spray amount", "Spray", "Brush pressure", "Brush speed", "Back"};
enum : uint8_t { S_AMOUNT, S_SPRAY, S_PRESS, S_SPEED, S_BACK, S_COUNT };
uint8_t sSel = 0;
int8_t sDrawn = -1;

void settingsValues(const char **v) {
  static const char *const amount[3] = {"Less", "Normal", "More"}, *const press[3] = {"Light", "Normal", "Firm"},
                           *const speed[3] = {"Slow", "Normal", "Fast"};
  v[S_AMOUNT] = amount[uSpray]; v[S_SPRAY] = uSprayOn ? "On" : "Off"; v[S_PRESS] = press[uPress]; v[S_SPEED] = speed[uSpeed];
  v[S_BACK] = "";
}
void settingsScreen(bool full) {
  if (full) {
    tft.fillScreen(C_BG);
    tft.fillRect(0, 0, 480, 34, C_PANEL);
    text(10, 9, "SETTINGS", C_TEXT, 2, C_PANEL);
    menuFooter("START changes it, STOP goes back");
    sDrawn = -1;
  }
  if (sDrawn == sSel) return;
  const char *v[S_COUNT];
  settingsValues(v);
  drawRows(SITEM, v, S_COUNT, sSel, sDrawn, sDrawn < 0);
  sDrawn = sSel;
}
void settingsChange() {
  switch (sSel) {
    case S_AMOUNT: uSpray = (uSpray + 1) % 3; break;
    case S_SPRAY: uSprayOn = !uSprayOn; break;
    case S_PRESS: uPress = (uPress + 1) % 3; break;
    case S_SPEED: uSpeed = (uSpeed + 1) % 3; break;
    case S_BACK: inSettings = false; menuScreen(true); return;
  }
  userSave();
  userApply();
  const char *v[S_COUNT];
  settingsValues(v);
  Serial.printf("SETTINGS: %s = %s (burst %u ms, grip %.0f / %.0f mm, brushes %.0f %%, spray %s)\n", SITEM[sSel], v[sSel],
                spr.onMs, gripMm, gripTopMm, pol.brushPct, polishSpray ? "on" : "off");
  sDrawn = -1;                                             // redraw the row with its new value
  settingsScreen(false);
}

// ---------------------------------------------------------------- self-test: what answers, nothing moves, nothing saved
void selfTest() {
  Serial.println(F("SELF-TEST (nothing moves, nothing is changed)"));
  menuFrame("START or STOP: back to the menu");
  text(24, 44, "SELF-TEST", C_INFO, 3);
  text(220, 52, "nothing moves", C_DIM, 2);
  const char *names[] = {"Servo driver", "Motor driver", "Side sensor", "Top sensor", "Spray sensor", "Knob", "Machine set up"};
  const uint8_t N = sizeof(names) / sizeof(names[0]);
  uint32_t t0 = millis(), lastDraw = 0;
  bool logged = false;
  while (millis() - t0 < 120000) {
    if (buttonPressed(btnStart) || stopRequested()) break;
    if (millis() - lastDraw < 400) { delay(5); continue; }
    lastDraw = millis();
    int side = tofRead(true), top = tofRead(false);
    char val[N][32]; bool ok[N];
    ok[0] = pcaFound; strlcpy(val[0], pcaFound ? "OK" : "NOT FOUND", 32);
    ok[1] = pcfFound; strlcpy(val[1], pcfFound ? "OK" : "NOT FOUND", 32);
    ok[2] = side > 0; if (side > 0) snprintf(val[2], 32, "OK  %d mm", side); else strlcpy(val[2], sideFound ? "NO READING" : "NOT FOUND", 32);
    ok[3] = top > 0;  if (top > 0) snprintf(val[3], 32, "OK  %d mm", top); else strlcpy(val[3], topFound ? "NO READING" : "NOT FOUND", 32);
    if (sonarOn) {
      bool s = irSeen();
      ok[4] = usAlive();
      if (!ok[4]) strlcpy(val[4], "NO ECHO", 32);
      else if (usLastMm == 0) strlcpy(val[4], "OK  clear", 32);
      else snprintf(val[4], 32, "OK  %s %.0f mm", s ? "shoe" : "clear", usLastMm);
    } else { ok[4] = true; strlcpy(val[4], irSeen() ? "OK  sees something" : "OK  clear", 32); }
    int k = knobRaw(); ok[5] = true; snprintf(val[5], 32, "OK  %d", k);
    ok[6] = machineSetUp(); strlcpy(val[6], ok[6] ? "OK" : "NEEDS SERVICE", 32);
    for (uint8_t i = 0; i < N; i++) {
      int16_t y = 84 + i * 29;
      tft.fillRect(20, y, 440, 26, C_PANEL);
      text(32, y + 6, names[i], C_TEXT, 2, C_PANEL);
      text(240, y + 6, val[i], ok[i] ? C_OK : C_BAD, 2, C_PANEL);
    }
    if (!logged) {
      logged = true;
      for (uint8_t i = 0; i < N; i++) Serial.printf("  %-15s %s\n", names[i], val[i]);
    }
    screenKeepAlive();
  }
  aborted = false;
  screenHold = false;
  menuScreen(true);
}

// ---------------------------------------------------------------- START and the knob
void userRun() {
  aborted = false;
  screenHold = false;
  if (inSettings) { settingsChange(); return; }
  const char *why = uBlocked(uSel);
  Serial.printf("MENU: %s\n", UITEM[uSel]);
  if (why) {
    menuFrame("Turn the knob for the menu");
    if (!machineSetUp()) menuState("NEEDS SERVICE", C_BAD, "This machine has not been set up.", "Contact service.");
    else menuState("HOME FIRST", C_WARN, "Home the machine before polishing:", "turn the knob to Home machine.");
    return;
  }
  switch (uSel) {
    case U_POLISH:
      if (!polishBoth() && !screenHold) {
        menuFrame("Turn the knob for the menu");
        menuState("NOT READY", C_BAD, "The machine could not start.", "Try Home machine, then again.");
      }
      break;                                               // otherwise the result stays up; START polishes the next shoe
    case U_HOME: {
      menuFrame("STOP cancels");
      menuState("HOMING", C_INFO, "Keep hands clear of the belt.", "Jaws open, roller to home.");
      bool h = homeAll();
      stopAll();
      menuState(h ? "READY" : "NOT HOMED", h ? C_OK : C_BAD, h ? "Put a shoe on the belt, toe first," : "Clear the belt and try again.",
                h ? "turn the knob to Polish shoe." : "If it fails again, contact service.");
      menuFooter("Turn the knob for the menu");
      break;
    }
    case U_PRIME: primePump(); menuFooter("Turn the knob for the menu"); break;
    case U_TEST: selfTest(); break;
    case U_SETTINGS: inSettings = true; sSel = 0; menuScreen(true); break;
  }
  stopAll();
  if (!screenHold) menuScreen(true);
}

void userTick() {
  static uint32_t last = 0;
  if (millis() - last < 20) return;
  last = millis();
  if (inSettings) {
    if (buttonPressed(btnStop)) { inSettings = false; screenHold = false; menuScreen(true); return; }
    uint8_t was = sSel;
    sSel = knobPick(S_COUNT, sSel);
    if (sSel != was) settingsScreen(false);
    return;
  }
  uint8_t was = uSel;
  uSel = knobPick(U_COUNT, uSel);
  if (screenHold) {                                        // a result page stays up until the knob is turned
    if (uSel != was) { screenHold = false; menuScreen(true); }
    return;
  }
  menuScreen(false);
}
