// The front-panel menu: a potentiometer picks an item, START chooses it, STOP stops anything.
// The knob's turn is split into one zone per item. The two ends of the turn are left out (the ESP32's ADC is poor near
// 0 V and 3.3 V), and the choice only moves once the knob is clearly past a zone edge, so it does not flicker on a boundary.
// The knob is only read while the machine is idle: turning it during a cycle does nothing.

const char *const MENU_ITEM[] = {"Polish shoe", "Home machine", "Prime pump", "Self-test"};
enum MenuItem : uint8_t { MI_POLISH, MI_HOME, MI_PRIME, MI_TEST };
// Polish shoe is greyed out until the machine is homed (Home machine, or  home ): at power-up, and after a STOP or fault
bool menuItemOk(uint8_t i) { return i != MI_POLISH || machineHomed; }
constexpr uint8_t MENU_COUNT = sizeof(MENU_ITEM) / sizeof(MENU_ITEM[0]);
constexpr int KNOB_LO = 200, KNOB_HI = 3900, KNOB_BAND = 200;  // usable ADC range, and the dead band past each zone edge
constexpr uint32_t KNOB_SETTLE_MS = 150;                       // a new item must hold this long before the choice moves
uint8_t menuSel = 0;
int8_t menuDrawn = -1;   // the item drawn highlighted, -1 to redraw them all
float knobF = -1;        // filtered reading

int knobRaw() {
  uint32_t s = 0;
  for (uint8_t i = 0; i < 32; i++) s += analogRead(PIN_KNOB);
  return s / 32;
}

// which item the knob points at; it stays on the current one until the knob is clearly in another zone, and has stayed
// there for KNOB_SETTLE_MS (a 50k pot picks up noise: one wild reading must not move the choice)
uint8_t knobItem() {
  static int8_t cand = -1;
  static uint32_t candAt = 0;
  int r = knobRaw();
  knobF = knobF < 0 ? r : knobF + 0.15f * (r - knobF);  // average 32, then smooth
  float zone = (KNOB_HI - KNOB_LO) / (float)MENU_COUNT, lo = KNOB_LO + menuSel * zone;
  if (knobF >= lo - KNOB_BAND && knobF <= lo + zone + KNOB_BAND) { cand = -1; return menuSel; }
  int8_t want = constrain((int)((knobF - KNOB_LO) / zone), 0, MENU_COUNT - 1);
  if (want != cand) { cand = want; candAt = millis(); }
  else if (millis() - candAt >= KNOB_SETTLE_MS) { menuSel = want; cand = -1; }
  return menuSel;
}

void menuScreen(bool full) {
  if (!tftOk || screenHold) return;
  scrKind = 0;
  if (full) {
    tft.fillScreen(C_BG);
    tft.fillRect(0, 0, 480, 34, C_PANEL);
    text(10, 9, "SHOE POLISHER", C_TEXT, 2);
    tft.fillRect(0, 292, 480, 28, C_PANEL);
    text(10, 299, "Turn the knob, then press START", C_DIM, 2, C_PANEL);
    menuDrawn = -1;
  }
  static bool homedDrawn = false;
  if (homedDrawn != machineHomed) { homedDrawn = machineHomed; menuDrawn = -1; }   // Polish shoe greys out or lights up
  if (menuDrawn == menuSel) return;
  for (uint8_t i = 0; i < MENU_COUNT; i++) {
    if (menuDrawn >= 0 && i != menuSel && i != menuDrawn) continue;   // only the two rows that changed
    int16_t y = 44 + i * 61;
    bool on = i == menuSel, okI = menuItemOk(i);
    uint16_t bg = on ? (okI ? C_INFO : C_DIM) : C_PANEL;
    tft.fillRect(20, y, 440, 52, bg);
    text(44, y + 14, MENU_ITEM[i], on ? C_BG : (okI ? C_TEXT : C_DIM), 3, bg);
    if (!okI) text(300, y + 20, "home first", on ? C_BG : C_DIM, 2, bg);
  }
  menuDrawn = menuSel;
}

void screenIdle(bool full) { if (full) scrKind = 0; if (menuOn) menuScreen(full); else screenDashboard(full); }

// from the main loop while idle; a result screen stays up until the knob is turned
void menuTick() {
  static uint32_t last = 0;
  if (!menuOn || millis() - last < 20) return;
  last = millis();
  uint8_t was = menuSel;
  knobItem();
  if (screenHold) {
    if (menuSel != was) { screenHold = false; menuScreen(true); }
    return;
  }
  menuScreen(false);
}

// header and footer of a menu page
void menuFrame(const char *footer) {
  if (!tftOk) return;
  scrKind = 2; msShown = false;
  if (footer != mfFooter) strlcpy(mfFooter, footer, sizeof(mfFooter));
  screenHold = true;
  tft.fillScreen(C_BG);
  tft.fillRect(0, 0, 480, 34, C_PANEL);
  text(10, 9, "SHOE POLISHER", C_TEXT, 2);
  tft.fillRect(0, 292, 480, 28, C_PANEL);
  text(10, 299, footer, C_DIM, 2, C_PANEL);
}

// big state word and a line or two under it
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

// START from the menu
void menuRun() {
  aborted = false;
  screenHold = false;
  Serial.printf("MENU: %s\n", MENU_ITEM[menuSel]);
  switch (menuSel) {
    case MI_POLISH:
      if (!machineHomed) {                             // greyed out: say why, and point at Home machine
        menuFrame("Turn the knob to Home machine");
        menuState("HOME FIRST", C_WARN, "The machine must be homed", "before polishing: Home machine.");
        Serial.println(F("  Polish shoe is greyed out until the machine is homed: choose Home machine"));
        break;
      }
      if (!polishBoth() && !screenHold) {              // it could not start: the reason is on the Serial Monitor
        menuFrame("Turn the knob for the menu");
        menuState("NOT READY", C_BAD, "The machine is not set up.", "See the Serial Monitor.");
      }
      break;                                           // otherwise its result stays on the cycle screen; START polishes the next
    case MI_HOME: {
      menuFrame("STOP cancels");
      menuState("HOMING", C_INFO, "Clear the belt.", "Jaws open, carriage to home.");
      bool h = homeAll();
      stopAll();
      menuState(h ? "HOMED" : "NOT HOMED", h ? C_OK : C_BAD, h ? "Ready to polish." : "See the Serial Monitor.",
                h ? "Turn the knob to Polish shoe." : "");
      if (tftOk) { tft.fillRect(0, 292, 480, 28, C_PANEL); text(10, 299, "Turn the knob for the menu", C_DIM, 2, C_PANEL); }
      break;
    }
    case MI_PRIME: primePump(); break;
    case MI_TEST:
      runAllTests();
      screenMessage("Self-test done: turn the knob", C_OK);
      screenDashboard(true);                           // the results stay up until the knob is turned
      screenHold = true;
      break;
  }
  stopAll();
  if (!screenHold) menuScreen(true);
}

// knob: the live reading and the item it picks, to check the wiring and the turning direction
void knobLive() {
  Serial.println(F("Knob: raw reading (0..4095, one sample of 32), smoothed reading, and the menu item. Any key ends."));
  Serial.println(F("Turn it SLOWLY from one end to the other: raw should climb evenly over the whole turn."));
  Serial.println(F("    raw   smooth   volts   item"));
  int8_t lastSel = -1; uint32_t lastPrint = 0; int lastRaw = -1000;
  while (!Serial.available()) {
    knobItem();
    int raw = analogRead(PIN_KNOB);
    // print on every real change (more than noise), and twice a second anyway
    if (menuSel != lastSel || abs(raw - lastRaw) > 40 || millis() - lastPrint > 500) {
      lastSel = menuSel; lastPrint = millis(); lastRaw = raw;
      Serial.printf("  %5d   %5d   %4.2f   %s\n", raw, (int)knobF, analogReadMilliVolts(PIN_KNOB) / 1000.0f, MENU_ITEM[menuSel]);
      menuScreen(false);
    }
    delay(20);
  }
  while (Serial.available()) Serial.read();
}
