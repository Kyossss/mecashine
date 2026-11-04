# MecaShine: Automated Shoe Polishing Station (ASPS)

Thesis prototype: a conveyor-fed shoe polisher with side brushes, a top roller and a spray station, run by an ESP32.

Current version: see [`VERSION`](VERSION). History: [`CHANGELOG.md`](CHANGELOG.md).

## Folders

| Folder | What's in it |
|---|---|
| `firmware/mecashine_debug/` | ESP32 Arduino sketch (pins and settings in `config.h`) |
| `side-polisher-redesign/` | CadQuery model of the side polisher (`cad_pincer9.py`), STEP files, print STLs in `print/`, assembly guide |
| `spray station/`, `top polish/`, `shoe plate pins/` | Other stations' Fusion files and prints |
| `*-proposal/` | Earlier design proposals |
| `polishing-line/` | Polishing Line page (logic, wiring, control board) and the motor-noise guide |
| `papers/` | Thesis draft, templates, figures, user manual |

## Hardware summary

- ESP32, PCF8575 expander, PCA9685 servo driver, 2× TB6612FNG motor drivers
- 2× VL53L0X ToF sensors (homing and measuring, no limit switches), FC-51 IR at the spray station
- 3.5″ ILI9488 SPI display (no touch), latching Start and Stop buttons
- 12 V 20 A supply, bucks for 6 V servos, 5 V ESP32 and 5 V display; 12 V diaphragm pump on a relay

## Releasing a revision

1. Make the change.
2. Add an entry under `[Unreleased]` in `CHANGELOG.md`, then rename it to the new version and date.
3. Bump `VERSION` (MAJOR.MINOR.PATCH, see the changelog header).
4. Commit, tag and push:
   ```
   git commit -am "v0.2.0: short summary"
   git tag -a v0.2.0 -m "v0.2.0: short summary"
   git push --follow-tags
   ```
