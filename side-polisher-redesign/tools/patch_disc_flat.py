p = r'F:/Research/ASPS/side-polisher-redesign/cad_pincer9.py'
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)
rep("# between the bottom plate and the top stopper. Bearing-sized (22 mm), symmetric (either way up), holes opposite the hex's flats.",
    "# between the bottom plate and the top stopper. Bearing-sized (22 mm), holes opposite the hex's flats. Plate at the bottom, spacer collar on\n"
    "# top only, so it prints flat with no supports (the first version had a collar on both faces and the plate overhung). Stack them plate down.")
rep("""    c = DISC_PITCH / 2
    sol = cz(0, 0, c - DISC_PLATE_T / 2, c + DISC_PLATE_T / 2, STOP_D).fuse(
          cq.Workplane('XY').polygon(6, BOT_BODY_AF / 0.8660254).extrude(DISC_PITCH).val()).clean()       # plate + hex spacer collar on both faces""",
    """    sol = cz(0, 0, 0, DISC_PLATE_T, STOP_D).fuse(
          cq.Workplane('XY').workplane(offset=DISC_PLATE_T - 0.1).polygon(6, BOT_BODY_AF / 0.8660254).extrude(DISC_PITCH - DISC_PLATE_T + 0.1).val()).clean()   # plate + hex spacer collar on top""")
rep("""                  cq.Solid.makeCone(YARN_HOLE_D / 2, YARN_HOLE_D / 2 + 0.6, 0.6, V(x, y, c + DISC_PLATE_T / 2 - 0.4), V(0, 0, 1)),   # softened edges
                  cq.Solid.makeCone(YARN_HOLE_D / 2, YARN_HOLE_D / 2 + 0.6, 0.6, V(x, y, c - DISC_PLATE_T / 2 + 0.4), V(0, 0, -1))]""",
    """                  cq.Solid.makeCone(YARN_HOLE_D / 2, YARN_HOLE_D / 2 + 0.6, 0.6, V(x, y, DISC_PLATE_T - 0.4), V(0, 0, 1)),   # softened edges
                  cq.Solid.makeCone(YARN_HOLE_D / 2, YARN_HOLE_D / 2 + 0.6, 0.6, V(x, y, 0.4), V(0, 0, -1))]""")
rep("    'tie-disc': to_bed(real(TIE_DISC)),                                          # flat; both faces are the same",
    "    'tie-disc': to_bed(real(TIE_DISC)),                                          # plate flat on the bed, collar up")
open(p, 'w', encoding='utf-8').write(s); print('ok')
