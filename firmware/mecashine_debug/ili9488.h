// Minimal ILI9488 driver for the 3.5 inch SPI display, built on Adafruit_GFX.
// It is in the sketch so it can use this machine's pins without changing the TFT_eSPI settings
// that your other project relies on. The ILI9488 takes 18-bit colour over SPI: 3 bytes a pixel.
#pragma once
#include <Adafruit_GFX.h>
#include <SPI.h>

class ILI9488 : public Adafruit_GFX {
 public:
  ILI9488(int8_t cs, int8_t dc, int8_t rst) : Adafruit_GFX(320, 480), _cs(cs), _dc(dc), _rst(rst) {}

  // 10 MHz, not 27: with the motors running, noise on the long jumper wires corrupted the display at 27 MHz (2026-11-03)
  void begin(uint32_t freq = 10000000) {
    _set = SPISettings(freq, MSBFIRST, SPI_MODE0);
    pinMode(_cs, OUTPUT); digitalWrite(_cs, HIGH);
    pinMode(_dc, OUTPUT); digitalWrite(_dc, HIGH);
    if (_rst >= 0) {
      pinMode(_rst, OUTPUT);
      digitalWrite(_rst, HIGH); delay(5);
      digitalWrite(_rst, LOW); delay(20);
      digitalWrite(_rst, HIGH); delay(150);
    }
    sendInit(120);
  }

  // Sends the set-up again without a hardware reset or clearing the screen (a few ms). If motor noise has reset the
  // controller or scrambled its settings (the screen goes white or garbled), this brings it back; what was on the screen
  // is lost, so it has to be drawn again.
  void refresh() { sendInit(5); setRotation(rotation); }
  // A hard reset through the RST pin and the full set-up (about 0.3 s). Brings it back even when refresh() cannot; the
  // screen is blank afterwards and must be drawn again.
  void hardReset() {
    if (_rst >= 0) { digitalWrite(_rst, LOW); delay(20); digitalWrite(_rst, HIGH); delay(150); }
    sendInit(120); setRotation(rotation);
  }

  void sendInit(uint16_t wakeMs) {
    static const uint8_t init[] = {
      // cmd, n, data...
      0xE0, 15, 0x00, 0x03, 0x09, 0x08, 0x16, 0x0A, 0x3F, 0x78, 0x4C, 0x09, 0x0A, 0x08, 0x16, 0x1A, 0x0F,   // positive gamma
      0xE1, 15, 0x00, 0x16, 0x19, 0x03, 0x0F, 0x05, 0x32, 0x45, 0x46, 0x04, 0x0E, 0x0D, 0x35, 0x37, 0x0F,   // negative gamma
      0xC0, 2, 0x17, 0x15,         // power control 1
      0xC1, 1, 0x41,               // power control 2
      0xC5, 3, 0x00, 0x12, 0x80,   // VCOM
      0x36, 1, 0x48,               // memory access: portrait, BGR
      0x3A, 1, 0x66,               // 18-bit pixels (the only depth the ILI9488 accepts over SPI)
      0xB0, 1, 0x00,               // interface mode
      0xB1, 1, 0xA0,               // frame rate
      0xB4, 1, 0x02,               // inversion control
      0xB6, 3, 0x02, 0x02, 0x3B,   // display function
      0xE9, 1, 0x00,               // set image function
      0xF7, 4, 0xA9, 0x51, 0x2C, 0x82,
    };
    start();
    for (size_t i = 0; i < sizeof(init);) {
      uint8_t c = init[i++], n = init[i++];
      cmd(c);
      for (uint8_t k = 0; k < n; k++) SPI.write(init[i++]);
    }
    cmd(0x11); end(); delay(wakeMs);     // sleep out
    start(); cmd(0x29); end(); delay(20); // display on
  }

  void setRotation(uint8_t r) override {
    static const uint8_t madctl[4] = {0x48, 0x28, 0x88, 0xE8};
    rotation = r & 3;
    _width = (rotation & 1) ? 480 : 320;
    _height = (rotation & 1) ? 320 : 480;
    start(); cmd(0x36); SPI.write(madctl[rotation]); end();
  }

  // ---- Adafruit_GFX hooks
  void startWrite() override { start(); }
  void endWrite() override { end(); }
  void drawPixel(int16_t x, int16_t y, uint16_t c) override { start(); writePixel(x, y, c); end(); }
  void writePixel(int16_t x, int16_t y, uint16_t c) override {
    if (x < 0 || y < 0 || x >= _width || y >= _height) return;
    window(x, y, 1, 1); push(c, 1);
  }
  void writeFillRect(int16_t x, int16_t y, int16_t w, int16_t h, uint16_t c) override {
    if (w < 0) { x += w + 1; w = -w; }
    if (h < 0) { y += h + 1; h = -h; }
    if (x < 0) { w += x; x = 0; }
    if (y < 0) { h += y; y = 0; }
    if (x + w > _width) w = _width - x;
    if (y + h > _height) h = _height - y;
    if (w <= 0 || h <= 0) return;
    window(x, y, w, h); push(c, (uint32_t)w * h);
  }
  void writeFastHLine(int16_t x, int16_t y, int16_t w, uint16_t c) override { writeFillRect(x, y, w, 1, c); }
  void writeFastVLine(int16_t x, int16_t y, int16_t h, uint16_t c) override { writeFillRect(x, y, 1, h, c); }
  void fillRect(int16_t x, int16_t y, int16_t w, int16_t h, uint16_t c) override { start(); writeFillRect(x, y, w, h, c); end(); }
  void drawFastHLine(int16_t x, int16_t y, int16_t w, uint16_t c) override { fillRect(x, y, w, 1, c); }
  void drawFastVLine(int16_t x, int16_t y, int16_t h, uint16_t c) override { fillRect(x, y, 1, h, c); }
  void fillScreen(uint16_t c) override { fillRect(0, 0, _width, _height, c); }

  static uint16_t rgb(uint8_t r, uint8_t g, uint8_t b) { return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3); }

 private:
  int8_t _cs, _dc, _rst;
  uint8_t _depth = 0;
  SPISettings _set;

  // transactions can nest (GFX calls drawPixel from inside its own startWrite)
  void start() { if (_depth++ == 0) { SPI.beginTransaction(_set); digitalWrite(_cs, LOW); } }
  void end() { if (_depth && --_depth == 0) { digitalWrite(_cs, HIGH); SPI.endTransaction(); } }
  void cmd(uint8_t c) { digitalWrite(_dc, LOW); SPI.write(c); digitalWrite(_dc, HIGH); }
  void window(int16_t x, int16_t y, int16_t w, int16_t h) {
    uint16_t x1 = x + w - 1, y1 = y + h - 1;
    cmd(0x2A); SPI.write(x >> 8); SPI.write(x); SPI.write(x1 >> 8); SPI.write(x1);
    cmd(0x2B); SPI.write(y >> 8); SPI.write(y); SPI.write(y1 >> 8); SPI.write(y1);
    cmd(0x2C);
  }
  void push(uint16_t c, uint32_t n) {
    uint8_t px[3] = {(uint8_t)((c >> 8) & 0xF8), (uint8_t)((c >> 3) & 0xFC), (uint8_t)((c << 3) & 0xF8)};
    while (n) { uint32_t k = n > 20000 ? 20000 : n; SPI.writePattern(px, 3, k); n -= k; }
  }
};
