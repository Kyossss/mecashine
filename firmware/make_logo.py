"""Turns the MecaShine logo PNG into firmware/mecashine/logo.h: an RGB565 bitmap for the boot screen.

    python F:/Research/ASPS/firmware/make_logo.py ["F:/Research/ASPS/Chrome and Gold MecaShine Logo.png"] [width]

The black margin around the logo is cropped off, then it is scaled to `width` pixels (default 460, the screen is 480 wide).
The boot screen's background is black, the same as the logo's.
"""
import pathlib, sys
from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "Chrome and Gold MecaShine Logo.png"
width = int(sys.argv[2]) if len(sys.argv) > 2 else 460

im = Image.open(src).convert("RGB")
# crop to what is not (nearly) black, plus a small margin
mask = im.convert("L").point(lambda v: 255 if v > 24 else 0)
l, t, r, b = mask.getbbox()
m = 12
im = im.crop((max(0, l - m), max(0, t - m), min(im.width, r + m), min(im.height, b + m)))
h = round(im.height * width / im.width)
im = im.resize((width, h), Image.LANCZOS)

px = []
for y in range(h):
    for x in range(width):
        R, G, B = im.getpixel((x, y))
        px.append(((R & 0xF8) << 8) | ((G & 0xFC) << 3) | (B >> 3))

out = HERE / "mecashine" / "logo.h"
lines = [f"0x{v:04X}" for v in px]
body = ",\n".join(", ".join(lines[i:i + 16]) for i in range(0, len(lines), 16))
out.write_text(
    "#pragma once\n// The MecaShine logo for the boot screen, RGB565, made by firmware/make_logo.py from\n"
    f"// {src.name}. Do not edit: run make_logo.py again.\n"
    f"constexpr int16_t LOGO_W = {width}, LOGO_H = {h};\n"
    f"const uint16_t LOGO[{width * h}] = {{\n{body}\n}};\n", encoding="utf-8")
im.save(HERE / "mecashine" / "logo_preview.png")
print(f"{out}: {width} x {h} px, {width * h * 2 // 1024} KB")
