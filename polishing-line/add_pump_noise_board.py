# Control board tab: the pump noise fixes, drawn on the wires. 2026-11-04 (v2).
# - PUMP plug − gets its own wire to the 12 V IN GND terminal (off the ground bus), at y 590 (free there).
# - Below the PUMP plug: its cable to the pump, twisted, with the 1N4007 and the 104 across the two wires at the pump end.
# - Below each sensor plug: its cable to the VL53L0X, with the 10 µF across VIN and GND at the sensor end.
# - The four-fix figure repeated under the board.
# Apply to the v0.3.2 page (before the first board version): python add_pump_noise_board.py <in> <out>
import math, re, sys

MONO = 'font-family="IBM Plex Mono, ui-monospace, Consolas, monospace"'
INK, SUB, RED, BLK = "#2a1d10", "#5a4630", "#d0281e", "#1b1b1b"

def txt(x, y, t, size=8, weight=500, fill=INK, anchor="start"):
    return f'<text x="{x}" y="{y}" {MONO} font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{t}</text>'

def line(d, col, w=1.8, extra=""):
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round"{extra}/>'

pump_net = ('<g class="net" data-name="Pump return, its own wire: Pump plug − · 12 V input GND">'
            '<title>Pump return, its own wire: Pump plug − · 12 V input GND (not on the ground bus)</title>'
            '<path class="hit" d="M992 608V590H1756V601H1729V610"/>'
            + line("M992 608V590H1756V601H1729V610", "#fff3dc", 6.5)
            + '<path class="mw" d="M992 608V590H1756V601H1729V610" fill="none" stroke="#1b1b1b" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/></g>')

def pump_cable():
    # the plug's two wires leave below its label, twist, and end on the pump; diode and 104 across them near the pump
    xp, xm, y0, y1 = 966, 1002, 722, 756          # + wire, − wire, top of cable, end of twist
    g = '<g aria-label="Pump cable with the diode and capacitor at the pump end">'
    p1, p2, y = [], [], y0
    while y <= y1:
        s = math.sin((y - y0) / 12 * 2 * math.pi) * 0.5 + 0.5   # 0..1, the two wires swap sides every 6 px
        p1.append(f"{xp + (xm - xp) * s:.1f} {y}"); p2.append(f"{xm - (xm - xp) * s:.1f} {y}"); y += 2
    g += line("M" + " L".join(p1), RED, 2.2) + line("M" + " L".join(p2), BLK, 2.2)
    g += line(f"M{xp} {y1}V818", RED, 2.2) + line(f"M{xm} {y1}V818", BLK, 2.2)
    # diode across at y 778: cathode (bar) on the + wire
    yd = 778
    g += line(f"M{xp} {yd}H{xp + 10}M{xp + 26} {yd}H{xm}", INK, 1.6)
    g += f'<path d="M{xp + 26} {yd - 7}L{xp + 26} {yd + 7}L{xp + 12} {yd}Z" fill="{INK}"/>' + line(f"M{xp + 11} {yd - 8}V{yd + 8}", INK, 2.4)
    # 104 across at y 800
    yc = 800
    g += line(f"M{xp} {yc}H{xp + 15}M{xp + 21} {yc}H{xm}M{xp + 15} {yc - 7}V{yc + 7}M{xp + 21} {yc - 7}V{yc + 7}", INK, 1.6)
    for yy in (yd, yc):
        g += f'<circle cx="{xp}" cy="{yy}" r="2.6" fill="{RED}"/><circle cx="{xm}" cy="{yy}" r="2.6" fill="{BLK}"/>'
    g += f'<rect x="946" y="818" width="76" height="26" rx="3" fill="#33363b" stroke="#111" stroke-width="1"/>'
    g += txt(984, 835, "PUMP", 9, 600, "#f3f3f3", "middle") + txt(xp, 814, "+", 8, 600, RED, "middle") + txt(xm, 814, "−", 8, 600, BLK, "middle")
    g += txt(1010, 775, "1N4007", 8.5, 600) + txt(1010, 785, "bar (stripe) on the + wire", 7.5, 500, SUB)
    g += txt(1010, 803, "104 (100 nF)", 8.5, 600) + txt(1010, 813, "across + and −", 7.5, 500, SUB)
    g += txt(1010, 738, "twisted pair", 8.5, 600) + txt(1010, 748, "5 cm+ from sensor cables", 7.5, 500, SUB)
    g += txt(1010, 726, "FIX 1 + 3 · at the pump end", 8, 600, "#b3261e")
    g += "</g>"
    return g

def sensor_cable(cx, name):
    # five wires fanned out below the plug: VIN, GND, SCL, SDA, XSHUT; 10 µF across VIN and GND near the sensor
    xs = [cx - 44 + 22 * i for i in range(5)]
    cols = ["#1f9a55", BLK, "#1492c8", "#2460c4", "#0c8a8a"]
    g = f'<g aria-label="{name} cable with the 10 µF capacitor at the sensor end">'
    for i, x in enumerate(xs):
        x0 = cx - 32 + 16 * i          # under the plug's terminals
        g += line(f"M{x0} 722L{x} 742V818", cols[i], 2 if i < 2 else 1.4)
    yv, xv, xg = 790, xs[0], xs[1]
    # electrolytic across VIN and GND: straight plate on the + (VIN) side, curved on the − side
    g += line(f"M{xv} {yv}H{xv + 8}M{xv + 14} {yv}H{xg}M{xv + 8} {yv - 7}V{yv + 7}", INK, 1.6)
    g += line(f"M{xv + 15} {yv - 7}Q{xv + 11} {yv} {xv + 15} {yv + 7}", INK, 1.6)
    g += txt(xv + 5, yv - 9, "+", 8, 600, "#1f9a55", "middle")
    g += f'<circle cx="{xv}" cy="{yv}" r="2.6" fill="#1f9a55"/><circle cx="{xg}" cy="{yv}" r="2.6" fill="{BLK}"/>'
    g += f'<rect x="{cx - 54}" y="818" width="108" height="26" rx="3" fill="#2a2d33" stroke="#111" stroke-width="1"/>'
    g += txt(cx, 835, name, 8.5, 600, "#f3f3f3", "middle")
    for i, t in enumerate(["VIN", "GND", "SCL", "SDA", "XSH"]):
        g += txt(xs[i], 763, t, 6.5, 500, SUB, "middle")
    g += "</g>"
    return g

fix_notes = ('<g>' + pump_cable() + sensor_cable(324, "TOP VL53L0X") + sensor_cable(436, "SIDE VL53L0X")
             + txt(244, 735, "FIX 4 · 10 µF at the sensor end:", 8, 600, "#b3261e", "end")
             + txt(244, 746, "+ (long leg) on VIN, − on GND", 7.5, 500, SUB, "end")
             + txt(1440, 582, "FIX 2 · pump − on its own wire to the 12 V IN GND terminal", 8, 600, "#b3261e")
             + '</g>')

def board_css(s):
    rules = [l for l in s.split("\n") if l.startswith("#tab-wiring .") and any(k in l for k in (".bx", " .t ", " .s ", " .p ", " .pm", " .tn", " .k", "circle.k", "circle.dot"))]
    return "\n".join(l.replace("#tab-wiring ", "#tab-board .pnfig ") for l in rules)

def apply(src, dst):
    s = open(src, encoding="utf-8").read()
    assert "Pump return, its own wire" not in s
    i = s.index('<g class="net" data-name="Ground: TB6612 #1 GND · TB6612 #2 GND · PCA9685 GND')
    j = s.index("</g>", i) + 4
    g = s[i:j]
    assert g.count("M992 438V608") == 2 and g.count(" · Pump plug −") == 2
    g = g.replace("M992 438V608", "").replace(" · Pump plug −", "")
    g = re.sub(r'<circle cx="992" cy="438" r="4" fill="#1b1b1b"/>', "", g)
    s = s[:i] + g + "\n" + pump_net + s[j:]
    k = s.index("</svg>", s.index('<svg id="mb"'))
    s = s[:k] + fix_notes + s[k:]
    a = s.index('<svg id="pn"'); b = s.index("</svg>", a) + 6
    fig = s[a:b].replace('<svg id="pn"', '<svg id="pn2"').replace("#pn ", "#pn2 ")
    sec = f'''<section>
  <h2>Pump noise on the board</h2>
  <p>The pump's motor knocked out both distance sensors on the bench (2026-11-04). The board drawing above now shows where each part goes. On the board itself one wire changes: the PUMP plug's − has its own wire to the 12 V IN GND terminal instead of joining the ground bus. Below the plugs, the drawing continues along the cables: the diode and the 104 go across the pump's two wires at the pump end, and a 10 µF goes across VIN and GND at the end of each sensor cable. Test after each with <code>pump on</code> / <code>pump off</code> while watching the sensor readings.</p>
  <figure class="pnfig">
    <div class="sheet"><div style="min-width:820px">{fig}</div></div>
    <figcaption>The same four fixes as in the Wiring tab. Fix 1 matters most.</figcaption>
  </figure>
</section>

'''
    anchor = "<section>\n  <h2>Why it is laid out this way</h2>"
    assert s.count(anchor) == 1
    s = s.replace(anchor, sec + anchor, 1)
    s = s.replace("@media (prefers-reduced-motion: reduce) { #tab-board .net", board_css(s) + "\n@media (prefers-reduced-motion: reduce) { #tab-board .net", 1)
    li = '    <li><strong>Kept:</strong>'
    assert s.count(li) == 1
    s = s.replace(li, '    <li><strong>Changed (pump noise):</strong> the PUMP plug\'s − has its own wire to the 12 V IN GND terminal and is off the ground bus. The diode, the 104 and the two 10 µF capacitors are drawn on the cables below the plugs, at the far ends where they are soldered.</li>\n' + li, 1)
    open(dst, "w", encoding="utf-8", newline="").write(s)

if __name__ == "__main__":
    apply(sys.argv[1], sys.argv[2]); print("ok", sys.argv[2])
