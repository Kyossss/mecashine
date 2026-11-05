// COPIED from firmware/mecashine_debug by sync_main.py. Do not edit here: edit it there and run sync_main.py.
// Buttons, I2C helpers, PCF8575, brush motors and servos.

// ---------------------------------------------------------------- buttons
// The buttons latch (push-toggle). Every change of state counts as one press, so they behave like push buttons.
constexpr uint32_t DEBOUNCE_MS = 30;
void buttonBegin(ToggleButton &b) {
  pinMode(b.pin, INPUT_PULLUP);
  b.stable = b.lastRead = digitalRead(b.pin);
  b.changedAt = millis();
}
bool buttonPressed(ToggleButton &b) {
  bool now = digitalRead(b.pin);
  if (now != b.lastRead) { b.lastRead = now; b.changedAt = millis(); }
  if (now != b.stable && millis() - b.changedAt >= DEBOUNCE_MS) { b.stable = now; return true; }
  return false;
}

// ---------------------------------------------------------------- I2C
bool i2cPresent(uint8_t addr) {
  Wire.beginTransmission(addr);
  return Wire.endTransmission() == 0;
}
bool pcfFind() {
  for (uint8_t a = 0x20; a <= 0x27; a++) if (i2cPresent(a)) { pcfAddr = a; return true; }
  return false;
}
uint8_t i2cScan(bool print) {
  uint8_t found = 0;
  if (print) Serial.println(F("I2C scan:"));
  for (uint8_t a = 1; a < 127; a++) {
    if (!i2cPresent(a)) continue;
    found++;
    if (!print) continue;
    Serial.printf("  0x%02X", a);
    if (a >= 0x20 && a <= 0x27) Serial.printf("  PCF8575 (A2 A1 A0 = %u%u%u)", (a >> 2) & 1, (a >> 1) & 1, a & 1);
    if (a == PCA_ADDR) Serial.print(F("  PCA9685 servo driver"));
    if (a == 0x70) Serial.print(F("  PCA9685 all-call address (normal)"));
    if (a == TOF_SIDE_ADDR) Serial.print(F("  VL53L0X side sensor"));
    if (a == TOF_TOP_ADDR) Serial.print(F("  VL53L0X top sensor"));
    Serial.println();
  }
  if (print && !found) Serial.println(F("  nothing answered: check SDA (21), SCL (22), 3.3 V and ground"));
  return found;
}

// ---------------------------------------------------------------- PCF8575
bool pcfWrite(uint16_t v) {
  Wire.beginTransmission(pcfAddr);
  Wire.write((uint8_t)(v & 0xFF));
  Wire.write((uint8_t)(v >> 8));
  return Wire.endTransmission() == 0;
}
bool pcfRead(uint16_t &v) {
  if (Wire.requestFrom((int)pcfAddr, 2) != 2) return false;
  uint8_t lo = Wire.read(), hi = Wire.read();
  v = ((uint16_t)hi << 8) | lo;
  return true;
}
bool pcfSet(uint8_t bit, bool level) {
  if (level) pcfState |= (1u << bit); else pcfState &= ~(1u << bit);
  return pcfWrite(pcfState);
}

// ---------------------------------------------------------------- motor PWM (LEDC changed in esp32 core 3)
void pwmBegin() {
  for (uint8_t i = 0; i < MOTOR_COUNT; i++) {
#if defined(ESP_ARDUINO_VERSION_MAJOR) && ESP_ARDUINO_VERSION_MAJOR >= 3
    ledcAttach(PWM_PIN[i], PWM_FREQ, PWM_BITS);
    ledcWrite(PWM_PIN[i], 0);
#else
    ledcSetup(i, PWM_FREQ, PWM_BITS);
    ledcAttachPin(PWM_PIN[i], i);
    ledcWrite(i, 0);
#endif
  }
}
void pwmWrite(uint8_t m, uint16_t duty) {
  if (duty > PWM_MAX) duty = PWM_MAX;
#if defined(ESP_ARDUINO_VERSION_MAJOR) && ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcWrite(PWM_PIN[m], duty);
#else
  ledcWrite(m, duty);
#endif
}

// ---------------------------------------------------------------- motors
// percent -100..100, negative is reverse, 0 stops (coast)
void motorRun(uint8_t m, int percent) {
  if (m >= MOTOR_COUNT || !pcfFound) return;
  percent = constrain(percent, -100, 100);
  if (percent == 0) { pwmWrite(m, 0); pcfSet(MOTOR[m].in1, false); pcfSet(MOTOR[m].in2, false); return; }
  pcfSet(MOTOR[m].in1, percent > 0);
  pcfSet(MOTOR[m].in2, percent < 0);
  pcfSet(MOTOR[m].stby, true);
  pwmWrite(m, (uint32_t)abs(percent) * PWM_MAX / 100);
}
bool motorRamp(uint8_t m, int from, int to, uint32_t ms) {
  const int steps = 25;
  for (int i = 1; i <= steps; i++) { motorRun(m, from + (to - from) * i / steps); if (!waitOrAbort(ms / steps)) return false; }
  return true;
}
// forward, stop, reverse, stop; returns false if interrupted
bool motorSequence(uint8_t m, int top) {
  Serial.printf("  %s: forward\n", MOTOR[m].name);
  if (!motorRamp(m, 0, top, 1200) || !waitOrAbort(1500)) return false;
  motorRun(m, 0); Serial.println(F("  stop"));
  if (!waitOrAbort(800)) return false;
  Serial.println(F("  reverse"));
  if (!motorRamp(m, 0, -top, 1200) || !waitOrAbort(1500)) return false;
  motorRun(m, 0); Serial.println(F("  stop"));
  return waitOrAbort(300);
}

// ---------------------------------------------------------------- servos
// ---------------------------------------------------------------- pump relay (ESP32 GPIO, not the expander)
uint32_t pumpOnAt = 0;            // 0 while off
void pumpSet(bool on) {
  digitalWrite(PIN_PUMP, on != PUMP_ACTIVE_LOW ? HIGH : LOW);
  pumpOnAt = on ? max<uint32_t>(millis(), 1) : 0;
}
void pumpBegin() { pumpSet(false); pinMode(PIN_PUMP, OUTPUT); pumpSet(false); }   // level set before the pin drives
// ---------------------------------------------------------------- spray sensor: FC-51 IR, or HC-SR04 ultrasonic
// The IR only sees what reflects IR, so it misses matte black shoes. The HC-SR04 hears any shoe: TRIG on PIN_US_TRIG,
// ECHO into PIN_IR through a 1k / 2k divider. A shoe = an echo closer than sonarMm. Everything else asks irSeen() and
// does not care which one is fitted.
volatile uint32_t usRise = 0, usWidth = 0;
volatile bool usNew = false;
void IRAM_ATTR usIsr() {
  uint32_t t = micros();
  if (digitalRead(PIN_IR)) usRise = t;
  else if (usRise) { usWidth = t - usRise; usNew = true; }
}
float usLastMm = -1;            // last distance: -1 no reading yet, 0 no echo (nothing within about 4 m)
uint32_t usPingAt = 0, usGotAt = 0;
bool usAttached = false;
void irBegin() {                                            // GPIO 34 has no internal pull-up: the board's 10k does it
  pinMode(PIN_IR, INPUT);
  if (sonarOn) {
    pinMode(PIN_US_TRIG, OUTPUT); digitalWrite(PIN_US_TRIG, LOW);
    if (!usAttached) { attachInterrupt(digitalPinToInterrupt(PIN_IR), usIsr, CHANGE); usAttached = true; }
  } else if (usAttached) { detachInterrupt(digitalPinToInterrupt(PIN_IR)); usAttached = false; }
}
// A ping every 30 ms (the echoes need about 25 ms to die away); the echo pulse is timed by the interrupt, so nothing waits.
void usPoll() {
  if (usNew) {
    noInterrupts(); uint32_t w = usWidth; usNew = false; interrupts();
    usLastMm = w < 23000 ? w * 0.1715f : 0;                 // 0.343 mm/us there and back; the module's ~38 ms pulse = no echo
    usGotAt = millis();
  }
  uint32_t now = millis();
  if (now - usPingAt >= 30 && !digitalRead(PIN_IR)) {       // not while the last echo pulse is still running
    usPingAt = now; usRise = 0;
    digitalWrite(PIN_US_TRIG, HIGH); delayMicroseconds(10); digitalWrite(PIN_US_TRIG, LOW);
  }
}
bool usAlive() { return usLastMm >= 0 && millis() - usGotAt < 300; }
bool irRaw() {
  if (sonarOn) { usPoll(); return usAlive() && usLastMm > 0 && usLastMm < sonarMm; }
  return digitalRead(PIN_IR) == (IR_ACTIVE_LOW ? LOW : HIGH);
}
// The IR can chatter at the edge of its range: a change only counts once it has held for 15 ms. For the ultrasonic, 50 ms:
// two readings in a row must agree, so one stray echo does not start the pump.
uint32_t irEdgeAt = 0;     // millis() when the sensor's output last changed
bool irSeen() {
  static bool state = false, last = false;
  static uint32_t since = 0;
  bool r = irRaw();
  if (r != last) { last = r; since = millis(); irEdgeAt = since; }
  else if (r != state && millis() - since >= (sonarOn ? 50u : 15u)) state = r;
  return state;
}

// the safety time-out, checked from the main loop and while waiting
void pumpTick() {
  if (pumpOnAt && millis() - pumpOnAt > PUMP_MAX_MS) { pumpSet(false); Serial.println(F("  pump: switched off after the 10 s safety limit")); }
}

// Drives a servo straight from PIN_SERVO_DIRECT at 50 Hz, bypassing the PCA9685, to tell a servo fault from a driver fault.
void directServo(uint16_t us) {
  static bool attached = false;
  if (!attached) attached = ledcAttach(PIN_SERVO_DIRECT, 50, 16);
  ledcWrite(PIN_SERVO_DIRECT, (uint32_t)constrain(us, 500, 2500) * 65535 / 20000);
}
void directServoOff() { ledcWrite(PIN_SERVO_DIRECT, 0); }

// Wakes the PCA9685 and sets 50 Hz. It powers up asleep with no pulses, so this must run whenever it is (re)found.
bool pcaBegin() {
  pcaFound = i2cPresent(PCA_ADDR);
  if (pcaFound) { pca.begin(); pca.setOscillatorFrequency(27000000); pca.setPWMFreq(50); servosOff(); }
  return pcaFound;
}
void servosOff() {
  if (!pcaFound) return;
  for (uint8_t ch = 0; ch < 16; ch++) pca.setPWM(ch, 0, 4096);   // no pulse at all
}
// ch 0..2 = the machine servos (belt, lift, jaw), sent to the PCA9685 outputs in SERVO_PCA_CH; 3..15 = that output as is
uint8_t servoPcaCh(uint8_t ch) { return ch < SERVO_COUNT ? SERVO_PCA_CH[ch] : ch; }
void servoOff(uint8_t ch) { if (pcaFound && ch < 16) pca.setPWM(servoPcaCh(ch), 0, 4096); }
void servoPulse(uint8_t ch, uint16_t us) {
  if (!pcaFound || ch >= 16) return;
  pca.writeMicroseconds(servoPcaCh(ch), constrain(us, 500, 2500));
}
// offset in microseconds from the stop pulse, for the three machine servos
void servoOffset(uint8_t ch, int us) { servoPulse(ch, cal.stopUs[ch] + us); }
void servoStop(uint8_t ch) { servoOffset(ch, 0); }

// direction helpers: speed is a fraction of the move pulse, -1..1
void jawDrive(float openSpeed) { servoOffset(SV_JAW, (int)(cal.jawOpenSign * openSpeed * cal.moveUs)); }
void liftDrive(float upSpeed) { servoOffset(SV_LIFT, (int)(cal.liftUpSign * upSpeed * cal.moveUs)); }
void beltDrive(float fwdSpeed) { servoOffset(SV_BELT, (int)(cal.beltFwdSign * fwdSpeed * (fwdSpeed >= 0 ? cal.beltMoveUs : cal.beltRevUs))); }
