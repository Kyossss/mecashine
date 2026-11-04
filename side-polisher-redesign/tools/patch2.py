import sys
p=sys.argv[1]; s=open(p,encoding='utf-8').read()
a=s.index('# ---------------- guide block.'); b=s.index('# ---------------- guide rail')
new='''# ---------------- guide block. A cap that wraps the pillar's middle flange: top on the flange, a cheek down each side, a solid front, and a
# printed bottom plate under the flange that pulls up into the block with three M3 x 12 screws (two in the outer cheek, one in the front),
# so the flange is clamped top and bottom. Your M4 flange bolt heads come up through two holes in the top. Nothing on the pillar changes.
# The inner cheek is thin with no screw: the arm frame passes 1.5 mm from it with the jaws fully open. So the block is handed:
# drawn here for the left upstream corner (+Y = inner, toward the belt); the other hand is its mirror image.
# Block coordinates: X = Fusion x - 925, Y = across, 0 at the middle of the flange, Z above belt.
FL_TOP, BOLT_X, BOLT_Y, PILLAR_FACE = 97.0, -34.5, 5.85, -45.0
FL_BOT = 77.0                                          # underside of the flange (z 294 in Fusion)
FL_HALF = 17.5                                         # the flange is 35 mm wide (y 110..145)
HAUNCH_X = -23.5                                       # the pillar's 45 degree haunch starts here, above and below the flange
HEAD_HOLE_D = 11.0                                     # clears the M4 bolt heads on top and the nuts underneath
CAP_X1 = HAUNCH_X - 1.3                                # the right-hand blocks sit 0.5 mm further along, so stop 1.3 mm short
IN_Y0, IN_Y1 = FL_HALF + 0.3, FL_HALF + 5.4            # inner cheek, 5.1 mm (the open arm reaches 1.5 mm from it)
OUT_Y0, OUT_Y1 = -(FL_HALF + 9.3), -(FL_HALF + 0.3)    # outer cheek, 9 mm, holds two screws and nuts
CHEEK_X0 = PILLAR_FACE + 0.5                           # cheeks start just behind the flange face
SKIRT_X0 = -68.5                                       # solid front, the same width as the body, down the flange's front face
BASE_Z = FL_BOT + 0.8                                  # cheeks and front stop 0.8 mm above the flange underside, so the plate clamps the flange
PLATE_T = 5.0
SCREWS = [(-40.5, (OUT_Y0 + OUT_Y1) / 2, -1), (-28.5, (OUT_Y0 + OUT_Y1) / 2, -1), (-60.0, 6.5, 0)]   # x, y, nut slot opens to: -1 = outer face, 0 = front
BLOCK_ROD_X = -56.0
def block():
    s = fuse([box(-68.5, -41, -13, 13, FL_TOP, 129),                        # body around the rail, in front of the pillar
              box(PILLAR_FACE, CAP_X1, OUT_Y0, IN_Y1, FL_TOP, FL_TOP + 8),  # cap on top of the flange
              wedge_xz([(-41, FL_TOP + 8), (-41, 125), (-26.5, FL_TOP + 8)], 11.5, 15.5),
              wedge_xz([(-41, FL_TOP + 8), (-41, 125), (-26.5, FL_TOP + 8)], -15.5, -11.5),
              box(SKIRT_X0, PILLAR_FACE - 0.3, -13, 13, BASE_Z, FL_TOP + 0.5),       # solid front down the flange's front face
              box(CHEEK_X0, CAP_X1, IN_Y0, IN_Y1, BASE_Z, FL_TOP + 0.5),
              box(CHEEK_X0, CAP_X1, OUT_Y0, OUT_Y1, BASE_Z, FL_TOP + 0.5)])
    gw, gh = RAIL_W / 2 + RAIL_FIT, RAIL_H / 2 + RAIL_FIT
    tools = [box(BLOCK_ROD_X - gw, BLOCK_ROD_X + gw, -14, 14, ROD_Z - gh, ROD_Z + gh)]       # the rail slides through this printed guide
    for sy in (-1, 1):       # small lead-in at each end of the guide
        tools.append(cq.Solid.makeLoft([cq.Wire.makePolygon([V(BLOCK_ROD_X - gw - 1, sy * 13.01, ROD_Z - gh - 1), V(BLOCK_ROD_X + gw + 1, sy * 13.01, ROD_Z - gh - 1), V(BLOCK_ROD_X + gw + 1, sy * 13.01, ROD_Z + gh + 1), V(BLOCK_ROD_X - gw - 1, sy * 13.01, ROD_Z + gh + 1)], close=True),
                                        cq.Wire.makePolygon([V(BLOCK_ROD_X - gw, sy * 12, ROD_Z - gh), V(BLOCK_ROD_X + gw, sy * 12, ROD_Z - gh), V(BLOCK_ROD_X + gw, sy * 12, ROD_Z + gh), V(BLOCK_ROD_X - gw, sy * 12, ROD_Z + gh)], close=True)], True))
    for sy in (-1, 1):
        tools.append(cz(BOLT_X, sy * BOLT_Y, FL_TOP - 1, FL_TOP + 9, HEAD_HOLE_D))                  # your flange bolts come up through these
    nz = BASE_Z + 1.5                                                                               # nut slot 1.5 mm above the bottom face
    h = M3_NUT_AF / 2 + 0.1
    for x, y, side in SCREWS:
        tools.append(cz(x, y, BASE_Z - 1, BASE_Z + 9, M3))
        if side == -1: tools.append(box(x - h, x + h, OUT_Y0 - 1, y + h, nz, nz + 2.8))       # slide the nut in from the outer face
        else: tools.append(box(SKIRT_X0 - 1, x + h, y - h, y + h, nz, nz + 2.8))              # slide the nut in from the front
    return cut(s, tools)

def flange_clamp():
    # flat plate under the flange and the block's front; three M3 x 12 screws go up through it into the nuts in the block
    s = fuse([box(PILLAR_FACE - 0.5, CAP_X1, OUT_Y0, IN_Y1, FL_BOT - PLATE_T, FL_BOT), box(SKIRT_X0, PILLAR_FACE, -13, 13, FL_BOT - PLATE_T, FL_BOT)])
    tools = [cz(x, y, FL_BOT - PLATE_T - 1, FL_BOT + 1, M3) for x, y, _ in SCREWS]
    tools += [cz(BOLT_X, sy * BOLT_Y, FL_BOT - PLATE_T - 1, FL_BOT + 1, HEAD_HOLE_D) for sy in (-1, 1)]   # room for the flange bolts' nuts
    return cut(s, tools)

'''
s=s[:a]+new+s[b:]
old_pb='''def place_block(side, back, rod_x, part=None):
    part = BLOCK if part is None else part
    b = part.mirror('YZ') if back else part'''
new_pb='''def place_block(side, back, rod_x, part=None):
    part = BLOCK if part is None else part
    if side > 0: part = part.mirror('XZ')        # right side: the inner cheek is on the other side
    b = part.mirror('YZ') if back else part'''
assert old_pb in s; s=s.replace(old_pb,new_pb)
old_pr='''    'bushing-block': to_bed(BLOCK),                                               # as it sits: cheeks and front on the bed, cap bridges between
    'flange-clamp': to_bed(CLAMP),                                                # flat plate'''
new_pr='''    # handed: A = left upstream and right downstream, B = left downstream and right upstream (mirror image). Printed as they sit,
    # cheeks and front on the bed, the cap bridging between them.
    'bushing-block-A': to_bed(BLOCK),
    'bushing-block-B': to_bed(BLOCK.mirror('XZ')),
    'flange-clamp-A': to_bed(CLAMP),
    'flange-clamp-B': to_bed(CLAMP.mirror('XZ')),'''
assert old_pr in s; s=s.replace(old_pr,new_pr)
open(p,'w',encoding='utf-8').write(s); print('ok')
