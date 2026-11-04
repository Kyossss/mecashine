// The 3.5 inch display: a status dashboard, the test pattern, and questions during the guided test.
// Landscape, 480 x 320. The touch panel is not fitted, so questions are answered on the Serial Monitor or with START / STOP.


void screenBegin() {
  tft.begin(10000000);
  tft.setRotation(1);
  tft.fillScreen(C_BG);
  tftOk = true;            // there is no way to read back from this display: the test asks you what you see
}

void text(int16_t x, int16_t y, const String &s, uint16_t col, uint8_t size, uint16_t bg) {
  tft.setTextSize(size);
  if (bg == 0xFFFF) tft.setTextColor(col); else tft.setTextColor(col, bg);
  tft.setCursor(x, y);
  tft.print(s);
}

// Every 2 s, send the display its set-up again (see ILI9488::refresh): motor noise can reset it, and it would then stay white.
void screenKeepAlive() {
  static uint32_t last = 0;
  if (!tftOk || millis() - last < 2000) return;
  last = millis();
  tft.refresh();
}

void screenMessage(const String &s, uint16_t col) { screenMsg = s; screenMsgColor = col; }

void screenDashboard(bool full) {
  if (!tftOk || screenHold) return;
  if (full) {
    tft.fillScreen(C_BG);
    tft.fillRect(0, 0, 480, 34, C_PANEL);
    text(10, 9, "SHOE POLISHER  DEBUG", C_TEXT, 2);
    text(10, 46, "DEVICES", C_DIM, 1);
    text(10, 150, "DISTANCE", C_DIM, 1);
    text(10, 248, "BUTTONS", C_DIM, 1);
    text(250, 46, "TEST RESULTS", C_DIM, 1);
  }
  // uptime
  char buf[32];
  snprintf(buf, sizeof(buf), "%6lus", (unsigned long)(millis() / 1000));
  text(390, 9, buf, C_DIM, 2, C_PANEL);

  // devices
  struct { const char *n; bool ok; } dev[] = {
    {"PCF8575", pcfFound}, {"PCA9685", pcaFound}, {"ToF side", sideFound}, {"ToF top", topFound},
  };
  for (uint8_t i = 0; i < 4; i++) {
    int y = 60 + i * 20;
    tft.fillRect(10, y + 2, 10, 10, dev[i].ok ? C_OK : C_BAD);
    text(28, y, dev[i].n, C_TEXT, 2, C_BG);
    text(150, y, dev[i].ok ? "ok     " : "MISSING", dev[i].ok ? C_OK : C_BAD, 2, C_BG);
  }

  // distances
  int s = tofRead(true), t = tofRead(false);
  snprintf(buf, sizeof(buf), "side %4s mm ", s > 0 ? String(s).c_str() : "---");
  text(10, 166, buf, sideFound ? C_INFO : C_DIM, 2, C_BG);
  snprintf(buf, sizeof(buf), "top  %4s mm ", t > 0 ? String(t).c_str() : "---");
  text(10, 190, buf, topFound ? C_INFO : C_DIM, 2, C_BG);
  snprintf(buf, sizeof(buf), "home %u / %u", cal.jawHomeMm, cal.liftHomeMm);
  text(10, 218, buf, C_DIM, 1, C_BG);
  bool ir = irSeen();
  snprintf(buf, sizeof(buf), "spray IR  %s   spray %s ", ir ? "SHOE " : "clear", sprayAuto ? "AUTO" : "off ");
  text(10, 232, buf, ir ? C_WARN : C_DIM, 1, C_BG);

  // buttons (their raw level: they latch, so either level is normal)
  snprintf(buf, sizeof(buf), "START %s  STOP %s", digitalRead(PIN_START) ? "up  " : "down", digitalRead(PIN_STOP) ? "up  " : "down");
  text(10, 262, buf, C_TEXT, 2, C_BG);

  // results
  for (uint8_t i = 0; i < TEST_COUNT; i++) {
    int y = 58 + i * 15;   // 15 rows fit above the message bar
    const char *r = results[i] == R_PASS ? "PASS" : results[i] == R_FAIL ? "FAIL" : results[i] == R_SKIP ? "skip" : "--  ";
    uint16_t c = results[i] == R_PASS ? C_OK : results[i] == R_FAIL ? C_BAD : C_DIM;
    text(250, y, TEST_NAME[i], C_TEXT, 1, C_BG);
    text(400, y, r, c, 2, C_BG);
  }

  // message line
  tft.fillRect(0, 292, 480, 28, C_PANEL);
  text(10, 299, screenMsg.substring(0, 38), screenMsgColor ? screenMsgColor : C_TEXT, 2, C_PANEL);
}

// question shown across the middle of the screen until it is answered
void screenAsk(const char *q) {
  if (!tftOk) return;
  tft.fillRect(20, 110, 440, 100, C_WARN);
  tft.drawRect(20, 110, 440, 100, C_TEXT);
  String s = q;
  text(34, 122, s.substring(0, 34), C_BG, 2);
  if (s.length() > 34) text(34, 144, s.substring(34, 68), C_BG, 2);
  text(34, 180, "START = yes    STOP = no", C_BG, 2);
}
void screenAskDone() { screenDashboard(true); }

// colour bars, a grid and text: if all of this looks right, the display and its wiring are good
void screenTestPattern() {
  if (!tftOk) return;
  const uint16_t bars[] = {ILI9488::rgb(255, 255, 255), ILI9488::rgb(255, 255, 0), ILI9488::rgb(0, 255, 255), ILI9488::rgb(0, 255, 0),
                           ILI9488::rgb(255, 0, 255), ILI9488::rgb(255, 0, 0), ILI9488::rgb(0, 0, 255), ILI9488::rgb(0, 0, 0)};
  for (uint8_t i = 0; i < 8; i++) tft.fillRect(i * 60, 0, 60, 200, bars[i]);
  for (int x = 0; x < 480; x++) {
    uint8_t v = x * 255 / 479;
    tft.drawFastVLine(x, 200, 30, ILI9488::rgb(v, v, v));
  }
  tft.fillRect(0, 230, 480, 90, C_BG);
  tft.drawRect(0, 0, 480, 320, C_WARN);
  text(12, 242, "Bars: white yellow cyan green", C_TEXT, 2);
  text(12, 264, "magenta red blue black", C_TEXT, 2);
  text(12, 292, "Grey ramp: smooth, dark to light", C_DIM, 2);
}

// ---------------------------------------------------------------- the cycle screen (laid out like the Polishing Line mock-up)
// Big state word and clock, a progress bar, the stored shape drawn as it is measured (height orange, width blue),
// a box for each station and the belt, and the START / STOP indicators. Only the parts that change are redrawn.
constexpr int16_t PLOT_X = 24, PLOT_W = 432, PLOT_Y0 = 210, PLOT_H = 66;   // plot area: x along the shoe, y up from the base line
constexpr float PLOT_MM = 400.0f, PLOT_VMAX = 150.0f;                      // 400 mm of shoe across, 0..150 mm up
const uint16_t C_HEIGHT = ILI9488::rgb(255, 176, 32), C_WIDTH = ILI9488::rgb(56, 198, 244);
int16_t plotLastX[2] = {-1, -1}, plotLastY[2];                              // [0] height, [1] width

void cycleScreen(const char *state, uint16_t col, const char *sub) {
  if (!tftOk) return;
  screenHold = true;
  tft.fillScreen(C_BG);
  tft.fillRect(0, 0, 480, 34, C_PANEL);
  text(10, 9, "SHOE POLISHER", C_TEXT, 2);
  tft.fillRect(14, 108, 452, 6, C_PANEL);                                   // progress track
  tft.drawRect(14, 124, 452, 92, C_PANEL);                                  // shape panel
  text(24, 130, "STORED SHAPE", C_DIM, 1);
  text(110, 130, "HEIGHT", C_HEIGHT, 1);
  text(160, 130, "WIDTH", C_WIDTH, 1);
  text(330, 130, "LENGTH --- mm", C_DIM, 1, C_BG);
  tft.drawFastHLine(PLOT_X, PLOT_Y0, PLOT_W, C_PANEL);
  plotLastX[0] = plotLastX[1] = -1;
  cycleState(state, col, sub);
}

void cycleState(const char *state, uint16_t col, const char *sub) {
  if (!tftOk) return;
  tft.fillRect(0, 40, 480, 64, C_BG);
  text(14, 46, state, col, 4);
  text(14, 84, sub, C_DIM, 2);
}

void cycleClock(uint32_t ms) {
  if (!tftOk) return;
  screenKeepAlive();
  char buf[12];
  snprintf(buf, sizeof(buf), "%6.1f s", ms / 1000.0f);
  text(370, 9, buf, C_DIM, 2, C_PANEL);
}

void cycleProgress(float frac, uint16_t col) {
  if (!tftOk) return;
  int16_t w = (int16_t)(constrain(frac, 0.0f, 1.0f) * 452);
  tft.fillRect(14, 108, w, 6, col);
  tft.fillRect(14 + w, 108, 452 - w, 6, C_PANEL);
}

// one measured point: which = 0 height, 1 width; joined to the previous point of the same line
void cyclePlot(uint8_t which, float fromToe, float mm) {
  if (!tftOk || isnan(mm)) return;
  int16_t x = PLOT_X + (int16_t)(constrain(fromToe / PLOT_MM, 0.0f, 1.0f) * (PLOT_W - 1));
  int16_t y = PLOT_Y0 - (int16_t)(constrain(mm / PLOT_VMAX, 0.0f, 1.0f) * PLOT_H);
  uint16_t c = which ? C_WIDTH : C_HEIGHT;
  if (plotLastX[which] >= 0 && x - plotLastX[which] < 20) {   // join across a few missed readings
    tft.drawLine(plotLastX[which], plotLastY[which], x, y, c);
    tft.drawLine(plotLastX[which], plotLastY[which] - 1, x, y - 1, c);       // 2 px thick
  } else tft.fillRect(x, y - 1, 2, 2, c);
  plotLastX[which] = x; plotLastY[which] = y;
}

// a small tick under the plot: where the brushes are along the shoe
void cycleMark(float fromToe) {
  if (!tftOk) return;
  tft.fillRect(PLOT_X + (int16_t)(constrain(fromToe / PLOT_MM, 0.0f, 1.0f) * (PLOT_W - 1)), PLOT_Y0 + 2, 2, 4, C_TEXT);
}

void cycleLength(float mm) {
  if (!tftOk) return;
  char buf[24];
  snprintf(buf, sizeof(buf), "LENGTH %3.0f mm", mm);
  text(330, 130, buf, C_TEXT, 1, C_BG);
}

// the three status boxes: each station's step and sensor reading, and the belt
void cycleBoxes(const char *sideStep, int sideMm, const char *topStep, int topMm, const char *belt) {
  if (!tftOk) return;
  const char *step[3] = {sideStep, topStep, belt};
  const char *name[3] = {"SIDE", "TOP", "BELT"};
  int mm[3] = {sideMm, topMm, -2};
  char buf[16];
  for (uint8_t i = 0; i < 3; i++) {
    int16_t x = 14 + i * 152;
    tft.fillRect(x, 224, 146, 52, C_PANEL);
    text(x + 6, 228, name[i], C_DIM, 1, C_PANEL);
    text(x + 6, 240, step[i], C_TEXT, 2, C_PANEL);
    if (mm[i] != -2) {
      if (mm[i] > 0) snprintf(buf, sizeof(buf), "%d mm", mm[i]); else snprintf(buf, sizeof(buf), "--- mm");
      text(x + 6, 262, buf, C_INFO, 1, C_PANEL);
    }
  }
}

// START / STOP indicators: START green when the machine is waiting for it
void cycleButtons(bool startReady) {
  if (!tftOk) return;
  tft.fillRect(14, 284, 220, 30, startReady ? C_OK : C_PANEL);
  text(94, 292, "START", startReady ? C_BG : C_DIM, 2, startReady ? C_OK : C_PANEL);
  tft.fillRect(246, 284, 220, 30, C_BAD);
  text(332, 292, "STOP", C_TEXT, 2, C_BAD);
}
