"""Copies the shared machine code from mecashine_debug (admin / debug firmware, the single source) into mecashine (the
user firmware), and writes mecashine/version.h from the repo's VERSION file.

Run it after changing anything in the shared files, then build and upload mecashine:
    python F:/Research/ASPS/firmware/sync_main.py

Shared: everything that runs the machine. Not shared: each sketch's main .ino and its menu / commands / tests.
"""
import pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
SRC, DST = HERE / "mecashine_debug", HERE / "mecashine"
SHARED = ["config.h", "ili9488.h", "state.h", "core.ino", "hw.ino", "sensors.ino", "screen.ino", "ir.ino",
          "polish.ino", "calib.ino", "cycle.ino"]
NOTE = "// COPIED from firmware/mecashine_debug by sync_main.py. Do not edit here: edit it there and run sync_main.py.\n"

def main():
    DST.mkdir(exist_ok=True)
    for name in SHARED:
        text = (SRC / name).read_text(encoding="utf-8")
        (DST / name).write_text(NOTE + text, encoding="utf-8")
    version = (HERE.parent / "VERSION").read_text(encoding="utf-8").strip()
    (DST / "version.h").write_text(f'#pragma once\n// written by sync_main.py from the repo\'s VERSION file\n#define FW_VERSION "{version}"\n', encoding="utf-8")
    print(f"copied {len(SHARED)} files into {DST}, version {version}")

if __name__ == "__main__":
    sys.exit(main())
