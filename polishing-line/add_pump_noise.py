# Adds "Pump noise: the four fixes" to the Wiring tab (after "Cables that move"), and changes the pump's minus wire in the
# pump relay table to go straight to the PSU. 2026-11-04, after the pump was found to knock out both VL53L0X sensors.
import math, sys

def twisted(x0, x1, yc, a, period):
    p1, p2 = [], []
    x = x0
    while x <= x1:
        s = math.sin((x - x0) / period * 2 * math.pi)
        p1.append(f"{x:.0f} {yc + a * s:.1f}"); p2.append(f"{x:.0f} {yc - a * s:.1f}")
        x += 2
    return "M" + " L".join(p1), "M" + " L".join(p2)

tw1, tw2 = twisted(530, 740, 236, 6, 22)

svg = f'''<svg id="pn" viewBox="0 0 1000 366" role="img" aria-label="Four pump noise fixes. One: a 1N4007 diode with its stripe to the pump's plus terminal, and a 100 nF capacitor, both soldered across the pump's two terminals. Two: the pump's minus wire runs on its own straight to the 12 V power supply's minus terminal, not through the control board's ground. Three: the pump's two wires twisted together and kept at least 5 cm from the sensors' SDA and SCL wires. Four: a 10 microfarad capacitor across each distance sensor's VIN and GND pins, plus to VIN.">
<style>
#pn .ok {{ fill: var(--good); font: 600 12px var(--body); }} #pn .no {{ fill: var(--crit); font: 600 12px var(--body); }}
#pn .sym {{ fill: none; stroke: var(--fg); stroke-width: 2; }} #pn .solid {{ fill: var(--fg); }}
#pn .num {{ fill: var(--accent); font: 600 22px var(--display); }}
#pn .sep {{ stroke: var(--line); stroke-width: 1; }}
#pn .bad {{ fill: none; stroke: var(--crit); stroke-width: 1.7; stroke-dasharray: 5 4; }}
#pn .dim {{ fill: none; stroke: var(--muted); stroke-width: 1; }}
</style>
<line class="sep" x1="250" y1="14" x2="250" y2="346"/><line class="sep" x1="500" y1="14" x2="500" y2="346"/><line class="sep" x1="750" y1="14" x2="750" y2="346"/>

<!-- 1: diode and capacitor across the pump -->
<text class="num" x="14" y="34">1</text><text class="t" x="34" y="32">Diode + capacitor</text><text class="s" x="34" y="48">soldered on the pump's own tabs</text>
<path class="k k-12" d="M95 66V226"/><path class="k k-gnd" d="M175 66V226"/>
<text class="pm" x="91" y="78" text-anchor="end">from</text><text class="pm" x="91" y="90" text-anchor="end">relay NO</text>
<text class="pm" x="179" y="78">to PSU</text><text class="pm" x="179" y="90">V− (fix 2)</text>
<path class="sym" d="M95 120H122M142 120H175"/><path class="solid" d="M142 108L142 132L122 120Z"/><path class="sym" d="M122 107V133"/>
<circle class="k-12 dot" cx="95" cy="120" r="3" style="fill:var(--w12)"/><circle cx="175" cy="120" r="3" class="solid"/>
<text class="p" x="135" y="150" text-anchor="middle">1N4007</text><text class="s" x="135" y="164" text-anchor="middle">stripe (bar) to +</text>
<path class="sym" d="M95 190H131M139 190H175M131 178V202M139 178V202"/>
<circle cx="95" cy="190" r="3" style="fill:var(--w12)"/><circle cx="175" cy="190" r="3" class="solid"/>
<text class="p" x="135" y="216" text-anchor="middle">100 nF "104"</text>
<rect class="bx" x="70" y="226" width="130" height="62"/><text class="t" x="135" y="262" text-anchor="middle">Pump</text>
<text class="p" x="95" y="244" text-anchor="middle">+</text><text class="p" x="175" y="244" text-anchor="middle">−</text>
<text class="s" x="20" y="314">The diode swallows the spike the motor makes</text><text class="s" x="20" y="328">when it switches off; the capacitor its brush</text><text class="s" x="20" y="342">noise. Wrong way round, the diode shorts 12 V.</text>

<!-- 2: separate ground -->
<text class="num" x="264" y="34">2</text><text class="t" x="284" y="32">Pump − straight to the PSU</text><text class="s" x="284" y="48">its own wire, not via the board</text>
<rect class="bx" x="270" y="232" width="96" height="56"/><text class="t" x="280" y="256">12 V PSU</text>
<text class="p" x="292" y="276" text-anchor="middle">V+</text><text class="p" x="346" y="276" text-anchor="middle">V−</text>
<rect class="bx" x="270" y="70" width="96" height="50"/><text class="t" x="280" y="90">Relay</text>
<text class="p" x="296" y="114" text-anchor="middle">COM</text><text class="p" x="344" y="114" text-anchor="middle">NO</text>
<rect class="bx" x="400" y="140" width="84" height="50"/><text class="t" x="442" y="170" text-anchor="middle">Pump</text>
<text class="p" x="416" y="156" text-anchor="middle">+</text><text class="p" x="468" y="156" text-anchor="middle">−</text>
<path class="k k-12" d="M292 232V120"/><path class="k k-12" d="M344 120V132H416V140"/>
<path class="k k-gnd" style="stroke-width:3" d="M460 190V306H346V288"/>
<text class="ok" x="378" y="322">✓ own wire to V−</text>
<path class="bad" d="M476 190V222H430"/>
<rect x="388" y="206" width="42" height="32" fill="none" stroke="var(--crit)" stroke-width="1.2" stroke-dasharray="3 3"/><text class="pm" x="409" y="219" text-anchor="middle">board</text><text class="pm" x="409" y="231" text-anchor="middle">GND</text>
<text class="no" x="436" y="250">✗ not here</text>
<text class="s" x="264" y="342">Pump current stays out of the</text><text class="s" x="264" y="356">sensors' ground.</text>

<!-- 3: twist and separate -->
<text class="num" x="514" y="34">3</text><text class="t" x="534" y="32">Twist, and keep apart</text><text class="s" x="534" y="48">from the sensors' I²C wires</text>
<path class="k k-sda" d="M530 92H740"/><path class="k k-scl" d="M530 102H740"/>
<text class="p" x="530" y="82">SDA / SCL to the sensors</text>
<path class="k k-12" d="{tw1}"/><path class="k k-gnd" d="{tw2}"/>
<text class="p" x="530" y="268">pump + / − twisted together</text><text class="s" x="530" y="282">about one twist every 2 cm</text>
<path class="dim" d="M640 110V226M634 116L640 110L646 116M634 220L640 226L646 220"/>
<text class="t" x="650" y="166">at least 5 cm</text>
<text class="s" x="514" y="314">If they must cross, cross at right angles.</text><text class="s" x="514" y="328">The same goes for the brush motor and</text><text class="s" x="514" y="342">servo leads.</text>

<!-- 4: capacitor at each sensor -->
<text class="num" x="764" y="34">4</text><text class="t" x="784" y="32">10 µF at each sensor</text><text class="s" x="784" y="48">top and side VL53L0X</text>
<rect class="bx" x="790" y="68" width="180" height="60"/><text class="t" x="880" y="92" text-anchor="middle">VL53L0X</text>
<text class="p" x="815" y="122" text-anchor="middle">VIN</text><text class="p" x="850" y="122" text-anchor="middle">GND</text><text class="pm" x="882" y="122" text-anchor="middle">SCL</text><text class="pm" x="912" y="122" text-anchor="middle">SDA</text><text class="pm" x="946" y="122" text-anchor="middle">XSH</text>
<path class="k k-3" d="M815 128V262"/><path class="k k-gnd" d="M850 128V262"/>
<path class="dim" d="M882 128V146M912 128V146M946 128V146"/>
<path class="sym" d="M815 196H827M838 196H850M827 184V208"/><path class="sym" d="M838 184Q832 196 838 208"/>
<circle cx="815" cy="196" r="3" style="fill:var(--w3)"/><circle cx="850" cy="196" r="3" class="solid"/>
<text class="p" x="822" y="180" text-anchor="middle">+</text>
<text class="p" x="864" y="192">10 µF, 10 V+</text><text class="s" x="864" y="206">+ (long leg) to VIN</text>
<text class="pm" x="815" y="276" text-anchor="middle">3V3</text><text class="pm" x="850" y="276" text-anchor="middle">GND</text>
<text class="s" x="764" y="314">Solder it on the sensor's pins. It carries</text><text class="s" x="764" y="328">the sensor through a short dip, so it does</text><text class="s" x="764" y="342">not reset to its default address.</text>
</svg>'''

section = f'''
<section>
  <h2>Pump noise: the four fixes</h2>
  <p>The bench test on 2026-11-04 showed both distance sensors dropping out (reading 65535, "no update") the moment the pump switched, while the relay alone did not do it. It is the pump's motor. A short spike resets the sensors to the shared default address, so they clash and stay silent until the ESP32 restarts them. Do these four in order, testing after each.</p>
  <figure>
    <div class="sheet"><div style="min-width:820px">{svg}</div></div>
    <figcaption>Fix 1 is the important one and is the "diode and 104" already drawn next to the pump in the wiring diagram. Fix 2 changes one wire: the pump relay table below now sends Pump − to the PSU's V− terminal.</figcaption>
  </figure>
  <ol class="steps" style="max-width:72ch">
    <li><b>Diode and capacitor on the pump.</b> 1N4007, stripe to the pump's +; a 100 nF ceramic ("104") across the same two tabs. Keep the legs short. <span>Check the stripe twice: backwards, it shorts the 12 V the moment the relay closes.</span></li>
    <li><b>Pump − on its own wire to the PSU's V− terminal.</b> Take it off the board's ground and the breadboard rail.</li>
    <li><b>Twist the pump's two wires together</b> and route them at least 5 cm from the SDA/SCL wires to the sensors.</li>
    <li><b>10 µF across VIN and GND on each sensor,</b> + leg to VIN.</li>
    <li><b>Test after each one.</b> Watch the sensor readings on the dashboard and type <code>pump on</code>, then <code>pump off</code>, five times. Done when neither reading drops to 65535. If one still drops, the next fix in the list is the one to do.</li>
  </ol>
</section>
'''

def apply(path):
    s = open(path, encoding="utf-8").read()
    anchor = "<section>\n  <h2>Pin by pin</h2>"
    assert s.count(anchor) == 1 and "Pump noise: the four fixes" not in s
    s = s.replace(anchor, section.lstrip("\n") + "\n" + anchor, 1)
    old = '<tr><td class="pin">Pump −</td><td>Common ground</td><td class="note"></td></tr>'
    assert s.count(old) == 1
    s = s.replace(old, '<tr><td class="pin">Pump −</td><td>12 V PSU V−, on its own wire</td><td class="note">not the board ground: see "Pump noise"</td></tr>', 1)
    open(path, "w", encoding="utf-8", newline="").write(s)

for p in sys.argv[1:]:
    apply(p); print("ok", p)
