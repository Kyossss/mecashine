# Adds the spray-station IR shoe sensor (FC-51, OUT on ESP32 GPIO 34, powered from 3.3 V) to the
# Polishing Line wiring tab, control board and tables, and draws the pump's diode + 100 nF. 2026-11-03.
# Edits polishing-line.html and polishing-line.publish.html the same way. Run once.
import re
MONO = 'font-family="IBM Plex Mono, ui-monospace, Consolas, monospace"'

def edit(s):
    def sub(a, b, n=1):
        nonlocal s
        assert s.count(a) == n, (s.count(a), a[:100])
        s = s.replace(a, b)

    # ---------------- wiring tab ----------------
    w0 = s.index('<svg id="wd"'); w1 = s.index('</svg>', w0)
    w = s[w0:w1]
    def wsub(a, b, n=1):
        nonlocal w
        assert w.count(a) == n, (w.count(a), a[:100])
        w = w.replace(a, b)

    w = w.replace("and a relay module switching the 12 V pump.", "a relay module switching the 12 V pump, and the IR sensor at the spray station.")
    # 3.3 V rail and ground: drops to the IR module
    g3 = "M36 192H1200M584 140V192M1048 140V192M1176 140V192M96 422V192M448 422V192M720 422V192M976 422V192M1200 422V192"
    wsub(g3, g3 + "M648 140V192", 2)
    wsub('<circle class="k-3 dot" cx="976" cy="192" r="2.8"/></g>', '<circle class="k-3 dot" cx="976" cy="192" r="2.8"/><circle class="k-3 dot" cx="648" cy="192" r="2.8"/></g>')
    w = w.replace("TB6612 #1 VCC · TB6612 #2 VCC\">", "TB6612 #1 VCC · TB6612 #2 VCC · Spray IR VCC\">", 1)
    w = w.replace("TB6612 #1 VCC · TB6612 #2 VCC</title>", "TB6612 #1 VCC · TB6612 #2 VCC · Spray IR VCC</title>", 1)
    gg = "M1328 422V180M1328 180H1424V422"
    wsub(gg, gg + "M664 140V180", 2)
    wsub('<circle class="k-gnd dot" cx="1328" cy="180" r="2.8"/></g>', '<circle class="k-gnd dot" cx="1328" cy="180" r="2.8"/><circle class="k-gnd dot" cx="664" cy="180" r="2.8"/></g>')
    w = w.replace("Relay GND · Pump −", "Relay GND · Pump − · Spray IR GND")
    # IR OUT to GPIO 34 on the free track at y 252 (left part) and the free ESP32 pin slot at x 128
    net = ('<g class="net" data-name="Spray IR: IR module OUT · ESP32 34"><title>Spray IR: IR module OUT · ESP32 34 (LOW = shoe seen)</title>'
           '<path class="hit" d="M680 140V252H128V422"/><path class="k k-gpio" d="M680 140V252H128V422"/></g>\n')
    wsub('<rect class="bx" x="56" y="30" width="112" height="110"/>', net + '<rect class="bx" x="56" y="30" width="112" height="110"/>')
    wsub('<text class="p" text-anchor="end" transform="translate(115.5 428) rotate(-90)">23</text>',
         '<text class="p" text-anchor="end" transform="translate(115.5 428) rotate(-90)">23</text><text class="p" text-anchor="end" transform="translate(131.5 428) rotate(-90)">34</text>')
    parts = ('<rect class="bx" x="628" y="30" width="76" height="110"/><text class="t" x="636" y="52">Spray IR</text>'
             '<text class="s" x="636" y="68">FC-51</text><text class="s" x="636" y="82">3.3 V</text><text class="s" x="636" y="96">LOW = shoe</text>'
             '<text class="p" transform="translate(651.5 134) rotate(-90)">VCC</text>'
             '<text class="p" transform="translate(667.5 134) rotate(-90)">GND</text>'
             '<text class="p" transform="translate(683.5 134) rotate(-90)">OUT</text>'
             # 100 nF right at the module, across VCC and GND
             '<path class="k k-out" d="M648 148H654M654 144V152M658 144V152M658 148H664"/>'
             '<text class="pm" x="644" y="151" text-anchor="end">104</text>'
             # the pump's 1N4007 (stripe to +) and 100 nF across its terminals
             '<path class="k k-out" d="M1376 592H1340M1376 614H1340M1344 592V597M1338 597H1350M1344 609V614M1364 592V601M1358 601H1370M1358 605H1370M1364 605V614"/>'
             '<path d="M1338 609H1350L1344 598Z" fill="currentColor" opacity=".8"/>'
             '<text class="pm" x="1354" y="636" text-anchor="middle">1N4007 · 104</text>\n')
    wsub('<text class="pm" x="1292" y="42">WIRE KEY</text>', parts + '<text class="pm" x="1292" y="42">WIRE KEY</text>')
    s = s[:w0] + w + s[w1:]

    # ---------------- control board ----------------
    a0 = s.index('<svg id="mb"'); a1 = s.index('</svg>', a0)
    b = s[a0:a1]
    def bsub(a, c, n=1):
        nonlocal b
        assert b.count(a) == n, (b.count(a), a[:100])
        b = b.replace(a, c)
    c3 = re.search(r'data-name="3\.3 V logic[^"]*".*?<path class="mw" d="[^"]*" fill="none" stroke="(#[0-9a-fA-F]+)"', b, re.S).group(1)

    # GPIO 34 on the header now in use
    bsub('<rect x="819" y="149" width="6" height="6" fill="#9aa0a6" stroke="#444" stroke-width="0.6"/><text x="846" y="155" ' + MONO + ' font-size="8" font-weight="500" fill="#b8c6bd" text-anchor="start">34</text>',
         '<rect x="819" y="149" width="6" height="6" fill="#e9edf0" stroke="#444" stroke-width="0.6"/><text x="846" y="155" ' + MONO + ' font-size="8" font-weight="500" fill="#fff" text-anchor="start">34</text>')
    # 3.3 V: rail on to the plug and to the pull-up
    t3 = 'M64 446H736'
    bsub(t3, 'M64 446H1112M1064 446V608M1112 446V598', 2)
    bsub('Display plug LED">', 'Display plug LED · Spray IR plug 3V3 · IR pull-up 10k">')
    bsub('Display plug LED</title>', 'Display plug LED · Spray IR plug 3V3 · IR pull-up 10k</title>')
    # dot at the old rail end, where the 3V3 wire from the ESP32 joins
    m = re.search(r'(data-name="3\.3 V logic.*?)(</g>)', b, re.S)
    b = b[:m.start(2)] + f'<circle cx="736" cy="446" r="4" fill="{c3}"/><circle cx="1064" cy="446" r="4" fill="{c3}"/>' + b[m.start(2):]
    # ground: to the plug and to the 100 nF
    g_old = 'M824 438V608M992 438V608'
    bsub(g_old, g_old + 'M1080 438V608M1184 438V598', 2)
    bsub('<circle cx="992" cy="438" r="4" fill="#1b1b1b"/>', '<circle cx="992" cy="438" r="4" fill="#1b1b1b"/><circle cx="1080" cy="438" r="4" fill="#1b1b1b"/><circle cx="1184" cy="438" r="4" fill="#1b1b1b"/>')
    b = b.replace("Relay GND · Pump plug −", "Relay GND · Pump plug − · Spray IR plug GND · IR filter 100 nF")
    # GPIO 34 over the top of the ESP32 and down the free column at x 1200 to the plug's IN
    d = "M816 152H728V40H1200V598H1096V608"
    ir = (f'<g class="net" data-name="Spray IR: ESP32 34 · Spray IR plug IN"><title>Spray IR: ESP32 34 · Spray IR plug IN (LOW = shoe seen)</title><path class="hit" d="{d}"/>'
          f'<path class="mw" d="{d}" fill="none" stroke="#0c8a8a" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"/>'
          '<circle cx="1112" cy="598" r="3.2" fill="#0c8a8a"/><circle cx="1184" cy="598" r="3.2" fill="#0c8a8a"/></g>\n')
    first_net = b.index('<g class="net"')
    b = b[:first_net] + ir + b[first_net:]

    def screw(x, label):
        return (f'<circle cx="{x}" cy="618" r="4.5" fill="#c9ced3" stroke="#555" stroke-width="1"/>'
                f'<text x="{x+3}" y="654" {MONO} font-size="7.5" font-weight="500" fill="#f3f3f3" transform="rotate(-90 {x+3} 654)">{label}</text>')
    plug = ('<g><rect x="1048" y="608" width="64" height="50" fill="#2f8a3a" rx="2" stroke="#1f6a2a" stroke-width="1"/>'
            + screw(1064, "3V3") + screw(1080, "GND") + screw(1096, "IN") +
            '<path d="M1056 658 H1104 L1080 684 Z" fill="#33363b" opacity=".55"/>'
            f'<text x="1080" y="700" {MONO} font-size="9.5" font-weight="600" fill="#2a1d10" text-anchor="middle">SPRAY IR</text>'
            f'<text x="1080" y="712" {MONO} font-size="8" font-weight="500" fill="#5a4630" text-anchor="middle">FC-51 on spray post</text>'
            '</g>\n'
            # 10k pull-up (3V3 to IN) and 100 nF (IN to GND), on the board next to the plug
            '<g><rect x="1108.5" y="556" width="7" height="26" rx="2" fill="#e3d3a8" stroke="#6b5a3a" stroke-width="0.8"/>'
            '<path d="M1108.5 563H1115.5M1108.5 567H1115.5M1108.5 571H1115.5" stroke="#8a4b16" stroke-width="1.4"/>'
            f'<text x="1120" y="572" {MONO} font-size="8" font-weight="600" fill="#2a1d10">10k</text>'
            '<ellipse cx="1184" cy="568" rx="6.5" ry="5.5" fill="#d9a43a" stroke="#7a5a12" stroke-width="0.8"/>'
            f'<text x="1174" y="571" {MONO} font-size="8" font-weight="600" fill="#2a1d10" text-anchor="end">104</text>'
            '</g>\n')
    b = b + plug
    b = b.replace("the two-channel relay with the pump plug,", "the two-channel relay with the pump plug, the spray IR sensor plug,")
    s = s[:a0] + b + s[a1:]

    # board notes
    sub('six screw-terminal plugs along the bottom (two sensors, buttons, display, pump, 12 V in)',
        'seven screw-terminal plugs along the bottom (two sensors, buttons, display, pump, spray IR, 12 V in)')
    sub("sensors, buttons, display, pump and 12 V leave from the bottom.", "sensors, buttons, display, pump, spray IR and 12 V leave from the bottom.")

    # ---------------- tables and text ----------------
    sub('<tr><td class="pin">GPIO 4</td><td>Relay module IN</td><td class="note">pump on / off</td></tr>',
        '<tr><td class="pin">GPIO 4</td><td>Relay module IN</td><td class="note">pump on / off</td></tr>\n'
        '          <tr><td class="pin">GPIO 34</td><td>Spray IR sensor OUT, 10 kΩ pull-up to 3V3 on the board</td><td class="note">input only · LOW = shoe</td></tr>')
    sub('<td>Logic rail: PCA9685 VCC, PCF8575 VCC, both sensor VIN, both TB6612 VCC, display LED</td>',
        '<td>Logic rail: PCA9685 VCC, PCF8575 VCC, both sensor VIN, both TB6612 VCC, display LED, spray IR VCC</td>')
    sub("and input-only GPIO 34, 35, 36, 39.", "and input-only GPIO 35, 36, 39.")
    ir_tbl = ('    <div class="tbl">\n'
              '      <h3>Spray IR sensor</h3>\n'
              '      <div class="scroll"><table>\n'
              '        <thead><tr><th>Pin</th><th>Goes to</th><th>Note</th></tr></thead>\n'
              '        <tbody>\n'
              '          <tr><td class="pin">VCC</td><td>3.3 V (board plug 3V3)</td><td class="note">not 5 V: OUT is pulled up to VCC</td></tr>\n'
              '          <tr><td class="pin">GND</td><td>Common ground</td><td class="note"></td></tr>\n'
              '          <tr><td class="pin">OUT</td><td>GPIO 34 (board plug IN)</td><td class="note">LOW while the shoe is in front</td></tr>\n'
              '          <tr><td class="pin">At the module</td><td>100 nF across VCC and GND</td><td class="note">solder on the pins</td></tr>\n'
              '          <tr><td class="pin">On the board</td><td>10 kΩ from IN to 3V3, 100 nF from IN to GND</td><td class="note">reads "no shoe" if the cable comes off</td></tr>\n'
              '        </tbody>\n'
              '      </table></div>\n'
              '      <p class="small">An FC-51 / MH-B obstacle module on the far spray post. GPIO 34 is input-only and has no internal pull-up, so the 10 kΩ on the board holds it HIGH (no shoe, pump off) if the cable is unplugged or broken. Use three-core cable with OUT twisted against GND, run along the box edge away from the brush motor leads; cross motor leads at right angles. At 3.3 V the IR LED is dimmer than at 5 V, so set the sensitivity pot with a black shoe at the real distance from the post and check the red LED on the module. Keep the nozzles from spraying the lens, and shield it from sunlight.</p>\n'
              '    </div>\n\n')
    i = s.index('<h3>Pump relay</h3>')
    j = s.index('    </div>\n', i) + len('    </div>\n')
    s = s[:j] + '\n' + ir_tbl + s[j:].lstrip('\n')
    sub("Solder a 1N4007 diode (stripe to +) and a 100 nF capacitor across the pump's terminals:",
        "The relay's contacts (SRD-05VDC-SL-C, printed on the relay) are rated 10 A at 30 V DC, far more than a small 12 V pump draws. Solder a 1N4007 diode (stripe to +) and a 100 nF capacitor across the pump's terminals, as drawn next to the pump in the diagram:")
    sub("The firmware switches the pump off at power-up, on any stop, and after 10 s at most.</p>",
        "The firmware switches the pump off at power-up, on any stop, and after 10 s at most. On the polishing pass it bursts only while the spray IR sensor sees the shoe.</p>")
    sub('<li><b>Add 12 V to the motor drivers last.</b>',
        '<li><b>Add the spray IR sensor.</b> Power it from 3.3 V, put a shoe in front and check that GPIO 34 reads LOW and the module\'s LED lights; unplug it and check it reads HIGH.</li>\n'
        '    <li><b>Add 12 V to the motor drivers last.</b>')
    sub("<li><strong>Sensor wires:</strong> keep each sensor's four signal wires under about 50 cm,",
        "<li><strong>Spray IR cable:</strong> about 0.5–1 m from the box to the spray post. Three cores, OUT twisted with GND, kept apart from the brush motor leads. The 100 nF at each end filters what the motors induce.</li>\n"
        "    <li><strong>Sensor wires:</strong> keep each sensor's four signal wires under about 50 cm,")
    return s

for name in ("polishing-line.html", "polishing-line.publish.html"):
    p = "F:/Research/ASPS/polishing-line/" + name
    s = open(p, encoding="utf-8").read()
    if "Spray IR: ESP32 34" in s:
        print(name, "already has the IR sensor"); continue
    s = edit(s)
    open(p, "w", encoding="utf-8").write(s)
    print(name, "updated")
