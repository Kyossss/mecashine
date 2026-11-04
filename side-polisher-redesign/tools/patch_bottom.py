p = r'F:/Research/ASPS/side-polisher-redesign/cad_pincer9.py'
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)
rep("BOT_DISC_Z0, BOT_DISC_Z1, BOT_SOCK_Z0 = 21.0, 28.0, 22.0",
    "BOT_DISC_Z0, BOT_DISC_Z1, BOT_SOCK_Z0 = 24.6, 27.0, 21.0  # bottom plate (also the first row of yarn ties, knots underneath), bar socket floor\n"
    "BOT_BODY_AF = HEX_AF + 0.4 + 2 * 1.2                 # hex body under the plate holds the bar's socket; its flats stay clear of the tie holes\n"
    "TIE_HOLE_D, TIE_HOLE_R, TIE_N, TIE_ANG0 = 2.4, 8.9, 6, 30.0   # tie holes for the chenille yarn, opposite the hex's flats")
rep("""    bot = fuse([cz(0, AX_D, ax0, BR_Z1 + 0.7, STUB_D), cz(0, AX_D, BR_Z1 + 0.6, BOT_DISC_Z0 + 0.1, 16.0), cz(0, AX_D, BOT_DISC_Z0, BOT_DISC_Z1, STOP_D)])
    bot = bot.fillet(0.8, [e for e in bot.Edges() if abs(e.Center().z - ax0) < 0.01])                              # lead-in on the axle tip
    bot = cut(bot, [hexz(HEX_AF + 2 * FIT_BOT, 0, BOT_SOCK_Z0, BOT_DISC_Z1 + 1)])""",
"""    bot = fuse([cz(0, AX_D, ax0, BR_Z1 + 0.7, STUB_D), hexz(BOT_BODY_AF, 0, BR_Z1 + 0.6, BOT_DISC_Z0 + 0.1), cz(0, AX_D, BOT_DISC_Z0, BOT_DISC_Z1, STOP_D)])
    bot = bot.fillet(0.8, [e for e in bot.Edges() if abs(e.Center().z - ax0) < 0.01])                              # lead-in on the axle tip
    tools = [hexz(HEX_AF + 2 * FIT_BOT, 0, BOT_SOCK_Z0, BOT_DISC_Z1 + 1)]
    for k in range(TIE_N):
        a = math.radians(TIE_ANG0 + 360.0 / TIE_N * k); x, y = TIE_HOLE_R * math.cos(a), AX_D + TIE_HOLE_R * math.sin(a)
        tools += [cz(x, y, BOT_DISC_Z0 - 1, BOT_DISC_Z1 + 1, TIE_HOLE_D),
                  cq.Solid.makeCone(TIE_HOLE_D / 2, TIE_HOLE_D / 2 + 0.6, 0.6, V(x, y, BOT_DISC_Z1 - 0.4), V(0, 0, 1)),     # softened edges for the yarn
                  cq.Solid.makeCone(TIE_HOLE_D / 2, TIE_HOLE_D / 2 + 0.6, 0.6, V(x, y, BOT_DISC_Z0 + 0.4), V(0, 0, -1))]
    bot = cut(bot, tools)""")
rep("    'brush-core-bottom': to_bed(real(CORE_BOT).rotate(V(0, 0, 0), V(1, 0, 0), 180)),  # socket face on the bed, axle pointing up",
    "    'brush-core-bottom': to_bed(real(CORE_BOT).rotate(V(0, 0, 0), V(1, 0, 0), 180)),  # plate on the bed (socket opens there), axle pointing up")
rep("# held in the top by an M3x16 cross screw and nut; and a bottom with the second stopper, a hex socket, a shoulder and the 8 mm axle.",
    "# held in the top by an M3x16 cross screw and nut; and a bottom: a thin plate (stopper and first row of yarn ties) on a hex body with the\n"
    "# bar's socket, and the 8 mm axle. The thin bottom puts the lowest yarn about 23 mm above the belt, at the top edge of the shoe's sole.")
open(p, 'w', encoding='utf-8').write(s); print('ok')
