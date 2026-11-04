p = r'F:/Research/ASPS/side-polisher-redesign/cad_pincer9.py'
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)
a = s.index('def brush_core():'); b = s.index('# ---------------- carriage (local)')
s = s[:a] + '''# 3-part slim core (2026-10-20, the user's sketch): a top with your D-shaped motor shaft hole, a captive-nut M3x8 on the shaft's flat and the
# top stopper; a plain 12 mm hex bar whose top end narrows to an 8 mm hex tip (2 mm off-centre, so one flat is flush and the bar prints flat),
# held in the top by an M3x16 cross screw and nut; and a bottom with the second stopper, a hex socket, a shoulder and the 8 mm axle.
# The brush material slides onto the bar between the two stoppers. Both stoppers stick out 5 mm past the bar.
HEX_AF, TIP_AF, TIP_OFF = 12.0, 8.0, -2.0
STOP_D = HEX_AF + 10.0
CORE_HUB_D = 16.0                                       # slimmest hub that holds the shaft screw's captive nut
TOP_STOP_Z0, TOP_STOP_Z1 = 137.0, 140.0
TOP_SOCK_Z1 = CORE_Z1 - SHAFT_DEPTH - 1.0               # the tip's socket stops 1 mm under the shaft hole
BOT_DISC_Z0, BOT_DISC_Z1, BOT_SOCK_Z0 = 21.0, 28.0, 22.0
CORE_SCREW_Z = CORE_Z1 - GRUB_DOWN                      # shaft screw, level with the arm's hex key hole
CROSS_Z = TOP_STOP_Z0 + 5.5
FIT_TOP, FIT_BOT = 0.25, 0.4                            # hex clearance: snug in the top, loose in the bottom
NUT_U0, CROSS_HEAD_U = 3.2, 7.5
def core_parts():
    hexz = lambda af, d0, z0, z1: cq.Workplane('XY').polygon(6, af / 0.8660254).extrude(z1 - z0).val().translate(V(0, AX_D + d0, z0))   # flats face +-d
    cross_d = AX_D + TIP_OFF
    # top
    top = fuse([cz(0, AX_D, TOP_STOP_Z0, TOP_STOP_Z1, STOP_D), cz(0, AX_D, TOP_STOP_Z1 - 0.1, CORE_Z1, CORE_HUB_D)])
    dhole = cz(0, AX_D, CORE_Z1 - SHAFT_DEPTH, CORE_Z1 + 1, SHAFT_D).cut(box(SHAFT_FLAT, 5, AX_D - 5, AX_D + 5, CORE_Z1 - SHAFT_DEPTH - 1, CORE_Z1 + 2))   # your D hole, unchanged
    nut_u1 = -(TIP_AF / 2 / 0.8660254 + FIT_TOP) - 0.3
    tools = [dhole,
             hexz(TIP_AF + 2 * FIT_TOP, TIP_OFF, TOP_STOP_Z0 - 1, TOP_SOCK_Z1),                                   # socket for the bar's tip
             cx(AX_D, CORE_SCREW_Z, 0, CORE_HUB_D, M3),                                                           # shaft screw, square to the flat
             box(NUT_U0, NUT_U0 + 2.6, AX_D - 3.0, AX_D + 3.0, CORE_SCREW_Z - 3.4, CORE_Z1 + 1),                  # its nut, dropped in from the top face
             cx(cross_d, CROSS_Z, -CORE_HUB_D / 2 - 1, CORE_HUB_D / 2 + 1, M3),                                    # cross screw
             cx(cross_d, CROSS_Z, CROSS_HEAD_U, CORE_HUB_D / 2 + 2, M3_HEAD),                                     # its head seat
             cq.Workplane(cq.Plane(origin=(-CORE_HUB_D / 2 - 1, cross_d, CROSS_Z), xDir=(0, 0, 1), normal=(1, 0, 0)))
               .polygon(6, M3_NUT_AF / 0.8660254).extrude(CORE_HUB_D / 2 + 1 + nut_u1).val()]                      # its nut pocket, open at the surface
    top = cut(top, tools)
    # bar
    bar = cq.Workplane().add(hexz(HEX_AF, 0, BOT_SOCK_Z0 + 0.5, TOP_STOP_Z0)).edges('|Z').fillet(0.6).val()
    bar = bar.fuse(hexz(TIP_AF, TIP_OFF, TOP_STOP_Z0 - 0.1, TOP_SOCK_Z1 - 0.5)).clean()
    bar = cut(bar, [cx(cross_d, CROSS_Z, -10, 10, M3)])
    # bottom
    ax0 = BR_Z1 - BEARING_W + 0.5
    bot = fuse([cz(0, AX_D, ax0, BR_Z1 + 0.7, STUB_D), cz(0, AX_D, BR_Z1 + 0.6, BOT_DISC_Z0 + 0.1, 16.0), cz(0, AX_D, BOT_DISC_Z0, BOT_DISC_Z1, STOP_D)])
    bot = bot.fillet(0.8, [e for e in bot.Edges() if abs(e.Center().z - ax0) < 0.01])                              # lead-in on the axle tip
    bot = cut(bot, [hexz(HEX_AF + 2 * FIT_BOT, 0, BOT_SOCK_Z0, BOT_DISC_Z1 + 1)])
    return top, bar, bot

''' + s[b:]
rep("CORE = brush_core()", "CORE_TOP, CORE_BAR, CORE_BOT = core_parts()\nCORE = cq.Compound.makeCompound([CORE_TOP, CORE_BAR, CORE_BOT])     # the three as they sit together")
rep("CORE_D + 0.4)), p)", "HEX_AF / 0.8660254 + 0.4)), p)")
rep("    'brush-core': to_bed(real(CORE).rotate(V(0, 0, 0), V(1, 0, 0), 180)),        # upside down: socket on the bed, axle at the top                                                        # as it sits in the machine; turn it the way you printed the current rack",
    "    'brush-core-top': to_bed(real(CORE_TOP)),                                    # stopper face on the bed, shaft hole pointing up\n"
    "    'brush-core-bar': to_bed(real(CORE_BAR).rotate(V(0, 0, 0), V(1, 0, 0), -90)),  # lying on the flat that the tip is flush with\n"
    "    'brush-core-bottom': to_bed(real(CORE_BOT).rotate(V(0, 0, 0), V(1, 0, 0), 180)),  # socket face on the bed, axle pointing up")
open(p, 'w', encoding='utf-8').write(s); print('ok')
