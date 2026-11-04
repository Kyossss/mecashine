p = r'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/yarn_concept.py'
s = open(p, encoding='utf-8').read()
a = s.index('DISC_D = 33.0'); b = s.index('D = disc()')
s = s[:a] + '''DISC_D = 22.0                                             # as big as the 608ZZ bearing (and the two stoppers)
COLLAR_AF = HEX_AF + 0.4 + 2 * 1.2                        # spacer collar: a hex with 1.2 mm walls, so its flats stay clear of the tie holes
HOLE_D, HOLE_R, N_HOLE = 2.4, 8.9, 6                      # tie holes: a folded strand (two 1 mm cores, fur squashed) pulls through 2.4 mm
BRUSH_R = 26.0                                            # yarn tips when spinning: 52 mm brush, 4 mm inside the arm legs (30 mm from the axis)
YARN_CORE, YARN_FLUFF = 1.0, 9.0                          # the user's chenille: 1 mm core, about 9 mm across with the fur

HOLE_ANG0 = 30.0                                          # holes opposite the hex's flats (corners at 0, 60, ...), where there is the most plastic
def disc():
    # symmetric: plate in the middle, hex spacer collar on both faces
    c = PITCH / 2
    plate = cq.Solid.makeCylinder(DISC_D / 2, PLATE_T, V(0, 0, c - PLATE_T / 2), V(0, 0, 1))
    collar = cq.Workplane('XY').polygon(6, COLLAR_AF / 0.8660254).extrude(PITCH).val()
    sol = plate.fuse(collar).clean()
    hexhole = cq.Workplane('XY').workplane(offset=-1).polygon(6, (HEX_AF + 0.4) / 0.8660254).extrude(PITCH + 2).val()
    sol = sol.cut(hexhole)
    for k in range(N_HOLE):
        a = math.radians(HOLE_ANG0 + 360.0 / N_HOLE * k)
        x, y = HOLE_R * math.cos(a), HOLE_R * math.sin(a)
        sol = sol.cut(cq.Solid.makeCylinder(HOLE_D / 2, PITCH + 2, V(x, y, -1), V(0, 0, 1)))
        # 0.4 mm countersink on both faces, so the hole edges don't cut the yarn
        sol = sol.cut(cq.Solid.makeCone(HOLE_D / 2, HOLE_D / 2 + 0.6, 0.6, V(x, y, c + PLATE_T / 2 - 0.4), V(0, 0, 1)))
        sol = sol.cut(cq.Solid.makeCone(HOLE_D / 2, HOLE_D / 2 + 0.6, 0.6, V(x, y, c - PLATE_T / 2 + 0.4), V(0, 0, -1)))
    return sol.clean()
''' + s[b:]
s = s.replace("""print('disc valid', D.isValid(), 'vol cm3', round(D.Volume() / 1000, 2), 'web outside holes', round(DISC_D / 2 - HOLE_R - HOLE_D / 2, 2),
      'wall hole-to-hex corner', round(HOLE_R - HOLE_D / 2 - (HEX_AF + 0.4) / 2 / 0.8660254, 2))""",
"""print('disc valid', D.isValid(), 'solids', len(D.Solids()), 'vol cm3', round(D.Volume() / 1000, 2), ' rim outside holes', round(DISC_D / 2 - HOLE_R - HOLE_D / 2, 2),
      ' hole to hex flat', round(HOLE_R - HOLE_D / 2 - (HEX_AF + 0.4) / 2, 2), ' hole to collar flat', round(HOLE_R - HOLE_D / 2 - COLLAR_AF / 2, 2))""")
s = s.replace("'n_hole': N_HOLE, 'brush_r': BRUSH_R, 'yarn_d': 6.0,", "'n_hole': N_HOLE, 'brush_r': BRUSH_R, 'yarn_d': YARN_FLUFF, 'yarn_core': YARN_CORE, 'collar_af': round(COLLAR_AF, 1),")
s = s.replace("'disc_d': DISC_D, 'collar_d': COLLAR_D,", "'disc_d': DISC_D,")
s = s.replace("'strand_cut': round(2 * (BRUSH_R - HOLE_R) + 8, 0)", "'strand_cut': round(2 * (BRUSH_R - HOLE_R) + 6, 0)")
s = s.replace("stack = cq.Compound.makeCompound([(D if i % 2 == 0 else D.rotate(V(0, 0, PITCH / 2), V(1, 0, PITCH / 2), 180)).translate(V(0, AX_D, ZONE0 + i * PITCH)) for i in range(N_DISC)])",
              "stack = cq.Compound.makeCompound([D.translate(V(0, AX_D, ZONE0 + i * PITCH)) for i in range(N_DISC)])")
open(p, 'w', encoding='utf-8').write(s); print('ok')
