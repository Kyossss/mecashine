// The front-panel menu: a potentiometer picks an item, START chooses it, STOP stops anything.
// The knob's turn is split into one zone per item. The two ends of the turn are left out (the ESP32's ADC is poor near
// 0 V and 3.3 V), and the choice only moves once the knob is clearly past a zone edge, so it does not flicker on a boundary.
// The knob is only read while the machine is idle: turning it during a cycle does nothing.

const char *const MENU_ITEM[] = {"Polish shoe", "Prime pump", "Self-test"};
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
  if (full) {
    tft.fillScreen(C_BG);
    tft.fillRect(0, 0, 480, 34, C_PANEL);
    text(10, 9, "SHOE POLISHER", C_TEXT, 2);
    tft.fillRect(0, 292, 480, 28, C_PANEL);
    text(10, 299, "Turn the knob, then press START", C_DIM, 2, C_PANEL);
    menuDrawn = -1;
  }
  if (menuDrawn == menuSel) return;
  for (uint8_t i = 0; i < MENU_COUNT; i++) {
    if (menuDrawn >= 0 && i != menuSel && i != menuDrawn) continue;   // only the two rows that changed
    int16_t y = 56 + i * 76;
    bool on = i == menuSel;
    tft.fillRect(20, y, 440, 60, on ? C_INFO : C_PANEL);
    text(44, y + 18, MENU_ITEM[i], on ? C_BG : C_TEXT, 3, on ? C_INFO : C_PANEL);
  }
  menuDrawn = menuSel;
}

void screenIdle(bool full) { if (menuOn) menuScreen(full); else screenDashboard(full); }

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
  tft.fillRect(0, 40, 480, 250, C_BG);
  text(24, 70, state, col, 4);
  text(24, 130, l1, C_TEXT, 2);
  text(24, 156, l2, C_TEXT, 2);
}

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

// START from the menu
void menuRun() {
  aborted = false;
  screenHold = false;
  Serial.printf("MENU: %s\n", MENU_ITEM[menuSel]);
  switch (menuSel) {
    case 0:
      if (!polishBoth() && !screenHold) {              // it could not start: the reason is on the Serial Monitor
        menuFrame("Turn the knob for the menu");
        menuState("NOT READY", C_BAD, "The machine is not set up.", "See the Serial Monitor.");
      }
      break;                                           // otherwise its result stays on the cycle screen
    case 1: primePump(); break;
    case 2:
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
  Serial.println(F("Knob reading (0..4095) and the menu item it picks. Any key ends."));
  int8_t lastSel = -1; uint32_t lastPrint = 0;
  while (!Serial.available()) {
    knobItem();
    if (menuSel != lastSel || millis() - lastPrint > 500) {
      lastSel = menuSel; lastPrint = millis();
      Serial.printf("  %4d   %s\n", (int)knobF, MENU_ITEM[menuSel]);
      menuScreen(false);
    }
    delay(20);
  }
  while (Serial.available()) Serial.read();
}
