import re,sys
p=sys.argv[1]; s=open(p,encoding='utf-8').read()
a=s.index('# ---------------- guide block.'); b=s.index('# ---------------- guide rail')
new='''# ---------------- guide block. A cap that wraps the pillar's middle flange: top on the flange, a cheek down each side, a solid front, and a
# printed bottom plate under the flange that pulls up into the cheeks with one M3 x 16 screw each side, so the flange is clamped top and bottom.
# Your M4 flange bolt heads come up through two holes in the top. Nothing on the pillar changes.
# Block coordinates: X = Fusion x - 925, Y = across, 0 at the middle of the bay, Z above belt. Drawn for the upstream bay.
FL_TOP, BOLT_X, BOLT_Y, PILLAR_FACE = 97.0, -34.5, 5.85, -45.0
FL_BOT = 77.0                                          # underside of the flange (z 294 in Fusion)
FL_HALF = 17.5                                         # the flange is 35 mm wide (y 110..145)
HAUNCH_X = -23.5                                       # the pillar's 45 degree haunch starts here, above and below the flange
HEAD_HOLE_D = 11.0                                     # clears the M4 bolt heads on top and the nuts underneath
CAP_X1 = HAUNCH_X - 0.5
CHEEK_Y0, CHEEK_Y1 = FL_HALF + 0.3, FL_HALF + 9.3      # cheeks beside the flange, 0.3 mm clearance
CHEEK_X0 = PILLAR_FACE + 0.5                           # cheeks start just behind the flange face; the arm's rail boss passes in front
SKIRT_X0 = -68.5                                       # solid front, the same width as the body, down the flange's front face
BASE_Z = FL_BOT + 0.8                                  # cheeks and front stop 0.8 mm above the flange underside, so the plate clamps the flange
PLATE_T = 5.0
CLAMP_SCREW_X, CLAMP_SCREW_Y = -29.0, (CHEEK_Y0 + CHEEK_Y1) / 2
BLOCK_ROD_X = -56.0
def block():
    s = fuse([box(-68.5, -41, -13, 13, FL_TOP, 129),                        # body around the rail, in front of the pillar
              box(PILLAR_FACE, CAP_X1, -CHEEK_Y1, CHEEK_Y1, FL_TOP, FL_TOP + 8),   # cap on top of the flange
              wedge_xz([(-41, FL_TOP + 8), (-41, 125), (-26.5, FL_TOP + 8)], 11.5, 15.5),
              wedge_xz([(-41, FL_TOP + 8), (-41, 125), (-26.5, FL_TOP + 8)], -15.5, -11.5),
              box(SKIRT_X0, PILLAR_FACE - 0.3, -13, 13, BASE_Z, FL_TOP + 0.5),       # solid front down the flange's front face
              box(CHEEK_X0, CAP_X1, CHEEK_Y0, CHEEK_Y1, BASE_Z, FL_TOP + 0.5),
              box(CHEEK_X0, CAP_X1, -CHEEK_Y1, -CHEEK_Y0, BASE_Z, FL_TOP + 0.5)])
    gw, gh = RAIL_W / 2 + RAIL_FIT, RAIL_H / 2 + RAIL_FIT
    tools = [box(BLOCK_ROD_X - gw, BLOCK_ROD_X + gw, -14, 14, ROD_Z - gh, ROD_Z + gh)]       # the rail slides through this printed guide
    for sy in (-1, 1):       # small lead-in at each end of the guide
        tools.append(cq.Solid.makeLoft([cq.Wire.makePolygon([V(BLOCK_ROD_X - gw - 1, sy * 13.01, ROD_Z - gh - 1), V(BLOCK_ROD_X + gw + 1, sy * 13.01, ROD_Z - gh - 1), V(BLOCK_ROD_X + gw + 1, sy * 13.01, ROD_Z + gh + 1), V(BLOCK_ROD_X - gw - 1, sy * 13.01, ROD_Z + gh + 1)], close=True),
                                        cq.Wire.makePolygon([V(BLOCK_ROD_X - gw, sy * 12, ROD_Z - gh), V(BLOCK_ROD_X + gw, sy * 12, ROD_Z - gh), V(BLOCK_ROD_X + gw, sy * 12, ROD_Z + gh), V(BLOCK_ROD_X - gw, sy * 12, ROD_Z + gh)], close=True)], True))
    for sy in (-1, 1):
        tools.append(cz(BOLT_X, sy * BOLT_Y, FL_TOP - 1, FL_TOP + 9, HEAD_HOLE_D))                  # your flange bolts come up through these
        y = sy * CLAMP_SCREW_Y
        tools.append(cz(CLAMP_SCREW_X, y, BASE_Z - 1, BASE_Z + 13, M3))                             # plate screw, up into the cheek
        nz = BASE_Z + 4.0                                                                           # nut slot, open at the cheek's outer face
        y0, y1 = sorted((y - sy * (M3_NUT_AF / 2 + 0.2), sy * (CHEEK_Y1 + 1)))
        tools.append(box(CLAMP_SCREW_X - M3_NUT_AF / 2 - 0.1, CLAMP_SCREW_X + M3_NUT_AF / 2 + 0.1, y0, y1, nz, nz + 2.8))
    return cut(s, tools)

def flange_clamp():
    # flat plate under the flange; one M3 x 16 screw each side goes up through it into the nut in the cheek
    s = box(PILLAR_FACE - 0.5, CAP_X1, -CHEEK_Y1, CHEEK_Y1, FL_BOT - PLATE_T, FL_BOT)
    tools = [cz(CLAMP_SCREW_X, sy * CLAMP_SCREW_Y, FL_BOT - PLATE_T - 1, FL_BOT + 1, M3) for sy in (-1, 1)]
    tools += [cz(BOLT_X, sy * BOLT_Y, FL_BOT - PLATE_T - 1, FL_BOT + 1, HEAD_HOLE_D) for sy in (-1, 1)]   # room for the flange bolts' nuts
    return cut(s, tools)

'''
s=s[:a]+new+s[b:]
s=s.replace("'bushing-block': to_bed(BLOCK.rotate(V(0, 0, 0), V(1, 0, 0), 180)),          # upside down: the flat top on the bed",
            "'bushing-block': to_bed(BLOCK),                                               # as it sits: cheeks and front on the bed, cap bridges between")
s=s.replace("'flange-clamp': to_bed(CLAMP.rotate(V(0, 0, 0), V(1, 0, 0), 90)),             # lying on its end, the L shape flat on the bed",
            "'flange-clamp': to_bed(CLAMP),                                                # flat plate")
open(p,'w',encoding='utf-8').write(s)
print(s.count("to_bed(BLOCK)"), s.count("to_bed(CLAMP)"))
