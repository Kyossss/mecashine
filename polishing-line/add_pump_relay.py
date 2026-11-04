# Adds the pump relay (ESP32 GPIO 4) and the 12 V pump to the Polishing Line wiring tab, 2026-10-27.
# Edits polishing-line.html and polishing-line.publish.html the same way. Run once.
import sys

def edit(s):
    def sub(a, b):
        nonlocal s
        assert s.count(a) == 1, (s.count(a), a[:90])
        s = s.replace(a, b, 1)

    # dot colour for the 5 V rail (used by the new junction)
    sub("#tab-wiring circle.k-12 { fill: var(--w12); }", "#tab-wiring circle.k-12 { fill: var(--w12); } #tab-wiring circle.k-5 { fill: var(--w5); }")

    # describe the new parts to screen readers
    sub("PCF8575 I/O expander, and two motor drivers with three motors. Every connection is also listed in the tables below.",
        "PCF8575 I/O expander, two motor drivers with three motors, and a relay module switching the 12 V pump. Every connection is also listed in the tables below.")

    # 12 V rail: on to the relay's COM
    old12 = "M36 168H1184M72 140V168M216 140V168M344 140V168M920 140V168M960 422V168M1184 422V168"
    s = s.replace(old12, old12 + "M1184 168H1440V422")
    assert s.count(old12 + "M1184 168H1440V422") == 2
    sub('<circle class="k-12 dot" cx="960" cy="168" r="2.8"/></g>', '<circle class="k-12 dot" cx="960" cy="168" r="2.8"/><circle class="k-12 dot" cx="1184" cy="168" r="2.8"/></g>')
    s = s.replace("12 V: PSU V+ · XL4015 #1 IN+ · XL4015 #2 IN+ · XL4016 IN+ · TB6612 #1 VM · TB6612 #2 VM",
                  "12 V: PSU V+ · XL4015 #1 IN+ · XL4015 #2 IN+ · XL4016 IN+ · TB6612 #1 VM · TB6612 #2 VM · Relay COM")

    # ground rail: on to the relay's GND
    oldg = "M1312 422V180M1328 422V180"
    s = s.replace(oldg, oldg + "M1328 180H1424V422")
    assert s.count(oldg + "M1328 180H1424V422") == 2
    sub('<circle class="k-gnd dot" cx="1312" cy="180" r="2.8"/></g>', '<circle class="k-gnd dot" cx="1312" cy="180" r="2.8"/><circle class="k-gnd dot" cx="1328" cy="180" r="2.8"/></g>')
    s = s.replace("TB6612 #2 BIN1 · TB6612 #2 BIN2 · TB6612 #2 PWMB", "TB6612 #2 BIN1 · TB6612 #2 BIN2 · TB6612 #2 PWMB · Relay GND · Pump −")

    # 5 V from XL4015 #1: also to the relay's VCC, along a track just under the top row
    old5 = "M64 228H264M264 140V228M64 422V228"
    s = s.replace(old5, old5 + "M264 156H1408V422")
    assert s.count(old5 + "M264 156H1408V422") == 2
    s = s.replace("5 V for ESP32: XL4015 #1 OUT+ · ESP32 5V", "5 V for ESP32 and relay: XL4015 #1 OUT+ · ESP32 5V · Relay VCC")
    sub('<path class="k k-5" d="' + old5 + 'M264 156H1408V422"/></g>',
        '<path class="k k-5" d="' + old5 + 'M264 156H1408V422"/><circle class="k-5 dot" cx="264" cy="156" r="2.8"/></g>')

    # GPIO 4 to the relay's IN, on the free track at y 408
    net = ('<g class="net" data-name="Pump relay: ESP32 4 · Relay IN"><title>Pump relay: ESP32 4 · Relay IN</title>'
           '<path class="hit" d="M208 422V408H1392V422"/><path class="k k-gpio" d="M208 422V408H1392V422"/></g>\n')
    sub('<rect class="bx" x="56" y="30" width="112" height="110"/>', net + '<rect class="bx" x="56" y="30" width="112" height="110"/>')

    # the ESP32 gets a GPIO 4 pin label
    sub('<text class="p" text-anchor="end" transform="translate(195.5 428) rotate(-90)">17</text>',
        '<text class="p" text-anchor="end" transform="translate(195.5 428) rotate(-90)">17</text><text class="p" text-anchor="end" transform="translate(211.5 428) rotate(-90)">4</text>')

    # the relay module and the pump
    parts = ('<rect class="bx" x="1376" y="422" width="96" height="124"/><text class="t" x="1384" y="488">Relay</text>'
             '<text class="s" x="1384" y="504">pump · 1 channel</text><text class="s" x="1384" y="518">IN LOW = on</text>'
             '<text class="p" text-anchor="end" transform="translate(1395.5 428) rotate(-90)">IN</text>'
             '<text class="p" text-anchor="end" transform="translate(1411.5 428) rotate(-90)">VCC</text>'
             '<text class="p" text-anchor="end" transform="translate(1427.5 428) rotate(-90)">GND</text>'
             '<text class="p" text-anchor="end" transform="translate(1443.5 428) rotate(-90)">COM</text>'
             '<path class="k k-out" d="M1408 546V580"/><text class="p" transform="translate(1411.5 540) rotate(-90)">NO</text>'
             '<rect class="bx" x="1376" y="580" width="92" height="44"/><text class="tn" x="1422" y="598" text-anchor="middle">Pump</text>'
             '<text class="s" x="1422" y="613" text-anchor="middle">12 V · + from NO</text>'
             '<path class="k k-gnd" d="M1446 624V634M1438 634H1454M1441 638H1451M1444 642H1448"/>'
             '<text class="pm" x="1434" y="633" text-anchor="end">−</text>\n')
    sub('<text class="pm" x="1292" y="42">WIRE KEY</text>', parts + '<text class="pm" x="1292" y="42">WIRE KEY</text>')

    # ESP32 table
    sub('<tr><td class="pin">GPIO 33</td><td>Stop button, other leg to GND</td><td class="note">INPUT_PULLUP</td></tr>',
        '<tr><td class="pin">GPIO 33</td><td>Stop button, other leg to GND</td><td class="note">INPUT_PULLUP</td></tr>\n'
        '          <tr><td class="pin">GPIO 4</td><td>Relay module IN</td><td class="note">pump on / off</td></tr>')
    sub('<tr><td class="pin">5V / VIN</td><td>XL4015 #1 OUT+</td><td class="note">power in</td></tr>',
        '<tr><td class="pin">5V / VIN</td><td>XL4015 #1 OUT+, which also feeds the relay module VCC</td><td class="note">power in</td></tr>')
    sub('<p class="small">Still free: GPIO 4 and 19, and input-only GPIO 34, 35, 36, 39.',
        '<p class="small">Still free: GPIO 19 (the firmware\'s <code>direct</code> fault-finding command uses it), and input-only GPIO 34, 35, 36, 39.')

    # a table for the relay and pump, after the motor drivers
    relay = ('    <div class="tbl">\n'
             '      <h3>Pump relay</h3>\n'
             '      <div class="scroll"><table>\n'
             '        <thead><tr><th>Pin</th><th>Goes to</th><th>Note</th></tr></thead>\n'
             '        <tbody>\n'
             '          <tr><td class="pin">IN</td><td>GPIO 4</td><td class="note">LOW switches the pump on</td></tr>\n'
             '          <tr><td class="pin">VCC</td><td>XL4015 #1 OUT+ (5 V)</td><td class="note">relay coil</td></tr>\n'
             '          <tr><td class="pin">GND</td><td>Common ground</td><td class="note"></td></tr>\n'
             '          <tr><td class="pin">COM</td><td>12 V</td><td class="note"></td></tr>\n'
             '          <tr><td class="pin">NO</td><td>Pump +</td><td class="note">open, so pump off, while the relay is unpowered</td></tr>\n'
             '          <tr><td class="pin">NC</td><td>Leave unconnected</td><td class="note"></td></tr>\n'
             '          <tr><td class="pin">Pump −</td><td>Common ground</td><td class="note"></td></tr>\n'
             '        </tbody>\n'
             '      </table></div>\n'
             '      <p class="small">Use a relay module with an optocoupler input, which switches reliably from the ESP32\'s 3.3 V. If yours switches on when IN is HIGH, set <code>PUMP_ACTIVE_LOW</code> to false in the firmware\'s config.h. Solder a 1N4007 diode (stripe to +) and a 100 nF capacitor across the pump\'s terminals: without them the pump\'s motor can reset the distance sensors and wear the relay contacts. The firmware switches the pump off at power-up, on any stop, and after 10 s at most.</p>\n'
             '    </div>\n\n')
    i = s.index('<h3>Motor drivers</h3>')
    j = s.index('    </div>\n', i) + len('    </div>\n')
    s = s[:j] + '\n' + relay + s[j:].lstrip('\n')

    # assembly order and cables
    sub('<li><b>Add 12 V to the motor drivers last.</b>',
        '<li><b>Add the pump relay.</b> With the pump not yet connected, run <code>test 15</code> and listen for the click. Then connect the pump to COM and NO.</li>\n'
        '    <li><b>Add 12 V to the motor drivers last.</b>')
    sub("<li><strong>Motor leads:</strong> twist each motor's pair, and solder a 100 nF ceramic capacitor across each motor's terminals if you have them.</li>",
        "<li><strong>Motor and pump leads:</strong> twist each motor's pair, and solder a 100 nF ceramic capacitor across each motor's terminals. The bench test showed the side sensor resetting as soon as the brush motors start, so these capacitors are needed, not optional. The pump gets one too, plus its diode.</li>")
    return s

for name in ("polishing-line.html", "polishing-line.publish.html"):
    p = "F:/Research/ASPS/polishing-line/" + name
    s = open(p, encoding="utf-8").read()
    if "Pump relay: ESP32 4" in s:
        print(name, "already has the relay"); continue
    s = edit(s)
    open(p, "w", encoding="utf-8").write(s)
    print(name, "updated")
