# Changelog

Every revision of the prototype gets a version number, an entry here, and a git tag (`vX.Y.Z`).

Versioning follows [Semantic Versioning](https://semver.org):

- **MAJOR**: a redesign that changes how the machine works or is built (new station layout, new controller). `1.0.0` is the prototype as defended.
- **MINOR**: a new part, feature or station (a new printed part, a new sensor, a new firmware command, a new paper chapter).
- **PATCH**: fixes and tweaks (clearances, pin fixes, wording, bug fixes) that don't add anything new.

## [Unreleased]

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
