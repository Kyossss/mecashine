# Adds the two-channel relay (channel 1 = pump, IN1 on ESP32 GPIO 4) and a pump plug to the Control board tab, 2026-10-27.
# Edits polishing-line.html and polishing-line.publish.html the same way. Run once.
MONO = 'font-family="IBM Plex Mono, ui-monospace, Consolas, monospace"'

def pin_sq(x, label):                      # module header pin on the top edge, label reading down into the board
    return (f'<rect x="{x-3}" y="611" width="6" height="6" fill="#e9edf0" stroke="#444" stroke-width="0.6"/>'
            f'<text x="{x+3}" y="621" {MONO} font-size="7.5" font-weight="500" fill="#fff" text-anchor="end" transform="rotate(-90 {x+3} 621)">{label}</text>')
def screw(x, label, y=618, ty=654):          # screw terminal, like the plugs
    return (f'<circle cx="{x}" cy="{y}" r="4.5" fill="#c9ced3" stroke="#555" stroke-width="1"/>'
            f'<text x="{x+3}" y="{ty}" {MONO} font-size="7.5" font-weight="500" fill="#f3f3f3" transform="rotate(-90 {x+3} {ty})">{label}</text>')

relay = ('<g>'
         '<rect x="760" y="608" width="176" height="100" fill="#1f4fa3" rx="3" stroke="#12306a" stroke-width="1"/>'
         + pin_sq(776, "IN1") + pin_sq(792, "IN2") + pin_sq(808, "VCC") + pin_sq(824, "GND") +
         '<rect x="852" y="610" width="70" height="16" fill="#1f6fd0" rx="1" stroke="#12306a" stroke-width="0.8"/>'
         + screw(872, "COM", 618, 640) + screw(888, "NO", 618, 640) + screw(904, "NC", 618, 640) +
         '<rect x="776" y="660" width="44" height="38" fill="#2b74d8" rx="2" stroke="#12306a" stroke-width="0.8"/>'
         '<rect x="848" y="660" width="44" height="38" fill="#2b74d8" rx="2" stroke="#12306a" stroke-width="0.8"/>'
         f'<text x="798" y="682" {MONO} font-size="7" font-weight="500" fill="#f3f3f3" text-anchor="middle">K1</text>'
         f'<text x="870" y="682" {MONO} font-size="7" font-weight="500" fill="#f3f3f3" text-anchor="middle">K2</text>'
         f'<text x="848" y="724" {MONO} font-size="9.5" font-weight="600" fill="#2a1d10" text-anchor="middle">RELAY ×2</text>'
         f'<text x="848" y="736" {MONO} font-size="8" font-weight="500" fill="#5a4630" text-anchor="middle">K1 pump · K2 spare</text>'
         '</g>\n'
         '<g><rect x="960" y="608" width="48" height="50" fill="#2f8a3a" rx="2" stroke="#1f6a2a" stroke-width="1"/>'
         + screw(976, "+") + screw(992, "−") +
         '<path d="M968 658 H1000 L984 684 Z" fill="#33363b" opacity=".55"/>'
         f'<text x="984" y="700" {MONO} font-size="9.5" font-weight="600" fill="#2a1d10" text-anchor="middle">PUMP</text>'
         f'<text x="984" y="712" {MONO} font-size="8" font-weight="500" fill="#5a4630" text-anchor="middle">12 V pump</text>'
         '</g>\n')

def net(name, d, colour, width, dots=()):
    c = "".join(f'<circle cx="{x}" cy="{y}" r="{4 if width == 3 else 3.2}" fill="{colour}"/>' for x, y in dots)
    return (f'<g class="net" data-name="{name}"><title>{name}</title><path class="hit" d="{d}"/>'
            f'<path class="mw" d="{d}" fill="none" stroke="{colour}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>{c}</g>\n')

new_nets = (net("Pump relay: ESP32 4 · Relay IN1", "M776 542H1152M1104 280H1152V542M776 608V542", "#0c8a8a", 1.8)
            + net("Pump switched 12 V: Relay NO · Pump plug +", "M888 590H976M888 626V590M976 608V590", "#d0281e", 3))

def edit(s):
    def sub(a, b, n=1):
        nonlocal s
        assert s.count(a) == n, (s.count(a), a[:100])
        s = s.replace(a, b)
    a0 = s.index('<svg id="mb"'); a1 = s.index('</svg>', a0)
    svg = s[a0:a1]
    def ssub(a, b):
        nonlocal svg
        assert svg.count(a) == 1, (svg.count(a), a[:100])
        svg = svg.replace(a, b)

    # 12 V: down to the relay's COM
    t_old = 'M56 430H1708M184 316V296H56V430M368 316V296H240V430M1224 328H1208V430M1504 328H1488V430M1420 638H1412V430M1708 608V430'
    assert svg.count(t_old) == 2                    # the hover path and the drawn wire
    svg = svg.replace(t_old, t_old + 'M872 430V614')
    ssub('<circle cx="1412" cy="430" r="4" fill="#d0281e"/></g>', '<circle cx="1412" cy="430" r="4" fill="#d0281e"/><circle cx="872" cy="430" r="4" fill="#d0281e"/></g>')
    svg = svg.replace("XL4016 IN+ · 12 V input +12", "XL4016 IN+ · 12 V input +12 · Relay COM")

    # ground: down to the relay's GND and the pump plug's −
    g_old = 'M1652 728H1668V438M1724 608V438'
    assert svg.count(g_old) == 2
    svg = svg.replace(g_old, g_old + 'M824 438V608M992 438V608')
    ssub('<circle cx="792" cy="438" r="4" fill="#1b1b1b"/>', '<circle cx="792" cy="438" r="4" fill="#1b1b1b"/><circle cx="824" cy="438" r="4" fill="#1b1b1b"/><circle cx="992" cy="438" r="4" fill="#1b1b1b"/>')
    svg = svg.replace("XL4016 OUT− · 12 V input GND", "XL4016 OUT− · 12 V input GND · Relay GND · Pump plug −")

    # 5 V from XL4015 #1: on down to the relay's VCC
    f_old = 'M808 470H1456M816 376H808V470M1440 328H1456V470'
    assert svg.count(f_old) == 2
    svg = svg.replace(f_old, f_old + 'M808 470V608')
    ssub('<path class="mw" d="' + f_old + 'M808 470V608" fill="none" stroke="#e06a00" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/></g>',
         '<path class="mw" d="' + f_old + 'M808 470V608" fill="none" stroke="#e06a00" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/><circle cx="808" cy="470" r="4" fill="#e06a00"/></g>')
    svg = svg.replace("5 V for the ESP32: ESP32 5V · XL4015 #1 OUT+", "5 V for the ESP32 and relay: ESP32 5V · XL4015 #1 OUT+ · Relay VCC")

    # the new wires go with the others, the relay and plug with the other bottom-row parts
    first_net = svg.index('<g class="net"')
    svg = svg[:first_net] + new_nets + svg[first_net:]
    svg = svg + relay
    svg = svg.replace("the XL4016 converter and the 12 volt input.", "the two-channel relay with the pump plug, the XL4016 converter and the 12 volt input.")
    s = s[:a0] + svg + s[a1:]

    # the text about the board
    sub('<li><strong>Left off:</strong> the two-channel relay. It is not part of this build, so its place on the board is free.</li>',
        '<li><strong>Back in:</strong> the two-channel relay, now on the bottom row next to the display plug. Channel 1 switches the 12 V pump from GPIO 4; channel 2 is spare.</li>')
    sub('<li><strong>Added:</strong> five screw-terminal plugs along the bottom (two sensors, buttons, display, 12 V in) and three small ones for the brush motors at the top.</li>',
        '<li><strong>Added:</strong> six screw-terminal plugs along the bottom (two sensors, buttons, display, pump, 12 V in) and three small ones for the brush motors at the top.</li>')
    sub("Brush motors and servos leave from the top; sensors, buttons, display and 12 V leave from the bottom.",
        "Brush motors and servos leave from the top; sensors, buttons, display, pump and 12 V leave from the bottom.")
    return s

for name in ("polishing-line.html", "polishing-line.publish.html"):
    p = "F:/Research/ASPS/polishing-line/" + name
    s = open(p, encoding="utf-8").read()
    if "Relay IN1" in s:
        print(name, "board already has the relay"); continue
    s = edit(s)
    open(p, "w", encoding="utf-8").write(s)
    print(name, "updated")
