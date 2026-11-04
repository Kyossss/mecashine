p = r'F:/Research/ASPS/side-polisher-redesign/cad_pincer9.py'
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)
rep("# ---------------- carriage (local)", '''# Yarn tie discs (2026-10-21): chenille yarn strands are lark's-head knotted through 6 tie holes per disc, and 15 discs stack on the hex bar
# between the bottom plate and the top stopper. Bearing-sized (22 mm), symmetric (either way up), holes opposite the hex's flats.
DISC_N, DISC_PITCH, DISC_PLATE_T = 15, 7.25, 2.4
def tie_disc():
    c = DISC_PITCH / 2
    sol = cz(0, 0, c - DISC_PLATE_T / 2, c + DISC_PLATE_T / 2, STOP_D).fuse(
          cq.Workplane('XY').polygon(6, BOT_BODY_AF / 0.8660254).extrude(DISC_PITCH).val()).clean()       # plate + hex spacer collar on both faces
    tools = [cq.Workplane('XY').workplane(offset=-1).polygon(6, (HEX_AF + 2 * FIT_BOT) / 0.8660254).extrude(DISC_PITCH + 2).val()]
    for k in range(YARN_N):
        a = math.radians(YARN_ANG0 + 360.0 / YARN_N * k); x, y = YARN_HOLE_R * math.cos(a), YARN_HOLE_R * math.sin(a)
        tools += [cz(x, y, -1, DISC_PITCH + 1, YARN_HOLE_D),
                  cq.Solid.makeCone(YARN_HOLE_D / 2, YARN_HOLE_D / 2 + 0.6, 0.6, V(x, y, c + DISC_PLATE_T / 2 - 0.4), V(0, 0, 1)),   # softened edges
                  cq.Solid.makeCone(YARN_HOLE_D / 2, YARN_HOLE_D / 2 + 0.6, 0.6, V(x, y, c - DISC_PLATE_T / 2 + 0.4), V(0, 0, -1))]
    return cut(sol, tools)

# ---------------- carriage (local)''')
rep("CORE = cq.Compound.makeCompound([CORE_TOP, CORE_BAR, CORE_BOT])     # the three as they sit together",
    "CORE = cq.Compound.makeCompound([CORE_TOP, CORE_BAR, CORE_BOT])     # the three as they sit together\n"
    "TIE_DISC = tie_disc()\n"
    "DISCS = cq.Compound.makeCompound([TIE_DISC.translate(V(0, AX_D, BOT_DISC_Z1 + i * DISC_PITCH)) for i in range(DISC_N)])   # the stack on the bar")
rep("        it['core_' + side] = place(CORE, p)", "        it['core_' + side] = place(CORE, p)\n        it['discs_' + side] = place(DISCS, p)")
rep("cut(cz(0, AX_D, 0, 200, HEX_AF / 0.8660254 + 0.4)), p)   # brush material between the stoppers",
    "cut(cz(0, AX_D, 0, 200, STOP_D + 0.4)), p)   # yarn between the stoppers, outside the tie discs")
rep("    'brush-core-bottom': to_bed(real(CORE_BOT).rotate(V(0, 0, 0), V(1, 0, 0), 180)),  # plate on the bed (socket opens there), axle pointing up",
    "    'brush-core-bottom': to_bed(real(CORE_BOT).rotate(V(0, 0, 0), V(1, 0, 0), 180)),  # plate on the bed (socket opens there), axle pointing up\n"
    "    'tie-disc': to_bed(real(TIE_DISC)),                                          # flat; both faces are the same")
rep("COL = {'rail': (0.84, 0.86, 0.89), 'core': (0.85, 0.55, 0.3),", "COL = {'discs': (0.31, 0.64, 0.66), 'rail': (0.84, 0.86, 0.89), 'core': (0.85, 0.55, 0.3),")
open(p, 'w', encoding='utf-8').write(s)

p = r'F:/Research/ASPS/side-polisher-redesign/export_fusion.py'
s = open(p, encoding='utf-8').read()
rep("'core': 'Brush core', ", "'core': 'Brush core', 'discs': 'Yarn tie discs', ")
rep("COL = {'arm': (0.72, 0.67, 0.86),", "COL = {'discs': (0.31, 0.64, 0.66), 'arm': (0.72, 0.67, 0.86),")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
