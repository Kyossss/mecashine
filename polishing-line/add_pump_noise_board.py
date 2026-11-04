# Control board tab: the pump noise fixes. Pump plug − gets its own wire to the 12 V input's GND terminal (off the
# ground bus), callouts for the parts that go at the far ends of the cables, and the four-fix figure repeated under the
# board. 2026-11-04.
import re, sys

MONO = 'font-family="IBM Plex Mono, ui-monospace, Consolas, monospace"'

def callout(x, y, lines, tx, ty, col="#b3261e"):
    # leader from (x, y) on the board item to a note box at (tx, ty)
    w = max(len(l) for l in lines) * 5.6 + 16
    h = 14 * len(lines) + 8
    s = f'<path d="M{x} {y}V{ty}H{tx}" fill="none" stroke="{col}" stroke-width="1.4" stroke-dasharray="4 3"/>'
    s += f'<circle cx="{x}" cy="{y}" r="3.5" fill="{col}"/>'
    s += f'<rect x="{tx}" y="{ty - h / 2:.0f}" width="{w:.0f}" height="{h}" rx="3" fill="#fff8ec" stroke="{col}" stroke-width="1.2"/>'
    for i, l in enumerate(lines):
        s += f'<text x="{tx + 8}" y="{ty - h / 2 + 17 + 14 * i:.0f}" {MONO} font-size="9" font-weight="{600 if i == 0 else 500}" fill="{col if i == 0 else "#2a1d10"}">{l}</text>'
    return s

pump_net = ('<g class="net" data-name="Pump return, its own wire: Pump plug − · 12 V input GND">'
            '<title>Pump return, its own wire: Pump plug − · 12 V input GND (not on the ground bus)</title>'
            '<path class="hit" d="M992 608V598H1724V608"/>'
            '<path d="M992 608V598H1724V608" fill="none" stroke="#fff3dc" stroke-width="6.5" stroke-linejoin="round"/>'
            '<path class="mw" d="M992 608V598H1724V608" fill="none" stroke="#1b1b1b" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/></g>')

notes = ('<g aria-hidden="true">'
         + callout(992, 660, ["FIX 1 · at the pump end of this cable:", "1N4007 (stripe to +) and 104 on the pump's tabs"], 1010, 790)
         + callout(1360, 598, ["FIX 2 · pump − on its own wire", "to the 12 V IN GND terminal"], 1380, 560)
         + callout(380, 660, ["FIX 4 · at the sensor end of each cable:", "10 µF across VIN and GND, + to VIN"], 120, 790)
         + callout(970, 720, ["FIX 3 · pump cable twisted, run away", "from the sensor cables (5 cm or more)"], 560, 830)
         + '</g>')

def board_css(s):
    # the four-fix figure uses the wiring tab's classes; give the copy in the board tab the same look
    rules = [l for l in s.split("\n") if l.startswith("#tab-wiring .") and any(k in l for k in (".bx", " .t ", " .s ", " .p ", " .pm", " .tn", " .k", "circle.k", "circle.dot"))]
    out = "\n".join(l.replace("#tab-wiring ", "#tab-board .pnfig ") for l in rules)
    return out

def apply(path):
    s = open(path, encoding="utf-8").read()
    assert "Pump return, its own wire" not in s
    # 1. the ground bus no longer reaches the pump plug
    i = s.index('<g class="net" data-name="Ground: TB6612 #1 GND · TB6612 #2 GND · PCA9685 GND')
    j = s.index("</g>", i) + 4
    g = s[i:j]
    assert g.count("M992 438V608") == 2 and g.count(" · Pump plug −") == 2
    g = g.replace("M992 438V608", "").replace(" · Pump plug −", "")
    g = re.sub(r'<circle cx="992" cy="438" r="4" fill="#1b1b1b"/>', "", g)
    s = s[:i] + g + "\n" + pump_net + s[j:]
    # 2. callouts, drawn last so they sit on top
    k = s.index("</svg>", s.index('<svg id="mb"'))
    s = s[:k] + notes + s[k:]
    # 3. the four-fix figure, repeated under the board
    a = s.index('<svg id="pn"'); b = s.index("</svg>", a) + 6
    fig = s[a:b].replace('<svg id="pn"', '<svg id="pn2"').replace("#pn ", "#pn2 ")
    sec = f'''<section>
  <h2>Pump noise on the board</h2>
  <p>The pump's motor knocked out both distance sensors on the bench (2026-11-04). On the board above it changes one wire: the pump plug's − now has its own wire to the 12 V input's GND terminal instead of joining the ground bus, so the pump's current never flows in the sensors' ground. The other fixes go at the far ends of the cables, marked in red on the board. Test after each with <code>pump on</code> / <code>pump off</code> while watching the sensor readings.</p>
  <figure class="pnfig">
    <div class="sheet"><div style="min-width:820px">{fig}</div></div>
    <figcaption>The same four fixes as in the Wiring tab. Fix 1 matters most; fix 2 is the black wire from PUMP − to 12 V IN on the board.</figcaption>
  </figure>
</section>

'''
    anchor = "<section>\n  <h2>Why it is laid out this way</h2>"
    assert s.count(anchor) == 1
    s = s.replace(anchor, sec + anchor, 1)
    # 4. its CSS, and a line in "What changes"
    css = board_css(s)
    s = s.replace("@media (prefers-reduced-motion: reduce) { #tab-board .net", css + "\n@media (prefers-reduced-motion: reduce) { #tab-board .net", 1)
    li = '    <li><strong>Kept:</strong>'
    assert s.count(li) == 1
    s = s.replace(li, '    <li><strong>Changed (pump noise):</strong> the PUMP plug\'s − has its own wire to the 12 V IN GND terminal and is off the ground bus.</li>\n' + li, 1)
    open(path, "w", encoding="utf-8", newline="").write(s)

for p in sys.argv[1:]:
    apply(p); print("ok", p)
