# Changelog

Every revision of the prototype gets a version number, an entry here, and a git tag (`vX.Y.Z`).

Versioning follows [Semantic Versioning](https://semver.org):

- **MAJOR**: a redesign that changes how the machine works or is built (new station layout, new controller). `1.0.0` is the prototype as defended.
- **MINOR**: a new part, feature or station (a new printed part, a new sensor, a new firmware command, a new paper chapter).
- **PATCH**: fixes and tweaks (clearances, pin fixes, wording, bug fixes) that don't add anything new.

## [Unreleased]

## [0.3.2] - 2026-11-04

### Electronics (Polishing Line page, version 20)
- New "Pump noise: the four fixes" figure in the Wiring tab: 1N4007 + 100 nF on the pump, pump − on its own wire to the PSU V−, twisted pump leads kept 5 cm from I²C, 10 µF at each VL53L0X. The bench test showed the pump (not the relay) knocking out both distance sensors.
- Pump relay table: Pump − now goes to the PSU V− directly, not the common ground.

## [0.3.1] - 2026-11-04

### Firmware
- `help spray` (also `help pump`, `help ir`): the pump, spray IR and burst-pattern commands on their own help page, with the current pattern; they were hidden under `help motors`.

## [0.3.0] - 2026-11-04

### Firmware
- The polishing pass now sprays: bursts (the `spr` pattern) while the spray IR sees the shoe and the belt is moving, none while the belt waits for the carriage. `polish ... nospray` leaves the pump off for one pass; `set polishspray 0/1` (saved) sets the default. The pass reports how many times the IR saw the shoe.
- Spray timing report: when the spray starts it prints how many ms after the IR module's output changed the relay came on, and the main loop's slowest pass, to trace the reported 1 s delay.
- `knob` prints the raw reading and the voltage as well as the smoothed one, on every change, to diagnose the pot jumping from about 50 to 4000.

## [0.2.1] - 2026-11-04

### Firmware
- Menu knob calmer for the B50K pot: dead band 60 -> 200 counts, 32 readings averaged (was 8), slower smoothing, and a new item must hold 150 ms before the highlight moves.

## [0.2.0] - 2026-11-04

### Firmware
- Front-panel menu: a potentiometer on GPIO 35 picks the item, START chooses it, STOP still stops everything. Items: Polish shoe, Prime pump, Self-test (`menu.ino`).
- Prime pump: the pump runs until START is pressed again when mist appears, with a 10 s cut-off; the screen shows the run time, or "NO MIST?" after 10 s.
- The knob is only read while idle, splits its turn into zones with dead bands, and ignores the ends of the ADC range.
- New commands: `knob` (live reading), `menu` / `dash` (idle screen: menu or debug dashboard).

## [0.1.0] - 2026-11-04

First tracked baseline of the whole project.

### Firmware
- `mecashine_debug` sketch: Serial Monitor commands, 15 self-tests, ToF homing, belt calibration, measure and side-polish stages.
- Pump relay on GPIO 4 (active low, 10 s safety cut-off) and spray IR sensor on GPIO 34.

### CAD
- Side polisher redesign (`cad_pincer9.py`): arm frames, carriages, racks, foot brackets, solid brush cores, guide rails, bolt-free guide blocks and flange clamps, sensor bracket and reflector.
- All parts use the M3 button-head kit sizes (8/12/16/20 mm) and nuts only.
- Guide block hole clearance 0.5 mm (`RAIL_FIT`).
- Print-ready STLs in `side-polisher-redesign/print/`.
- Spray station, top polish and shoe plate pin parts.

### Electronics
- Polishing Line page: logic and model, wiring and assembly, control board. TFT touch removed, pump relay and spray IR sensor added.
- Motor-noise fix guide.

### Paper
- Thesis draft, manuscript template, figures, user manual and calibration notes.
