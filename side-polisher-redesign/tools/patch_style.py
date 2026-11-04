import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
old_a = s.index('def block():'); old_b = s.index('def flange_clamp():')
new = '''def edge_at(solid, x, z, r, how='fillet'):
    # round (or chamfer) the edge of a box that runs along Y at (x, z); shaping only in the X-Z profile keeps the part printable on its side
    wp = cq.Workplane().add(solid).edges(cq.selectors.BoxSelector((x - 0.05, -1e4, z - 0.05), (x + 0.05, 1e4, z + 0.05)))
    return (wp.fillet(r) if how == 'fillet' else wp.chamfer(r)).val()
FRONT_R, CAP_CHAMFER = 4.5, 12.0                        # rounded front corners round the rail hole; sloped back corner of the cap
def block():
    gw, gh = RAIL_W / 2 + RAIL_FIT, RAIL_H / 2 + RAIL_FIT
    top = ROD_Z + gh + 3.0                                                   # 3 mm over the rail hole
    body = box(SKIRT_X0, -41, OUT_Y0, BODY_Y1, FL_TOP, top)                  # body around the rail, in front of the pillar
    body = edge_at(edge_at(body, SKIRT_X0, top, FRONT_R), SKIRT_X0, FL_TOP, FRONT_R)
    cap = edge_at(box(PILLAR_FACE, CAP_X1, OUT_Y0, IN_Y1, FL_TOP, top), CAP_X1, top, CAP_CHAMFER, 'chamfer')   # cap on the flange
    bx0, bx1, by0, by1 = FRONT_BOSS
    s = fuse([body, cap,
              box(PILLAR_FACE - 0.8 - WALL, PILLAR_FACE - 0.8, OUT_Y0, BODY_Y1, BASE_Z, FL_TOP + 0.5),   # wall down the flange's front face (0.3 mm clear on the right-hand side)
              box(bx0, bx1, by0, by1, BASE_Z, FL_TOP + 0.5),                                             # boss round the front screw
              wedge_xy([(bx1, by0 - (bx1 - bx0)), (bx1, by0), (bx0, by0)], BASE_Z, FL_TOP + 0.5),       # 45 degree slope under the boss, so it prints on its side
              box(CHEEK_X0, CAP_X1, OUT_Y0, OUT_Y1, BASE_Z, FL_TOP + 0.5)])                            # outer cheek
    tools = [box(BLOCK_ROD_X - gw, BLOCK_ROD_X + gw, OUT_Y0 - 1, BODY_Y1 + 1, ROD_Z - gh, ROD_Z + gh)]   # the rail slides through this printed guide
    lead = [cq.Wire.makePolygon([V(BLOCK_ROD_X - gw - e, yy, ROD_Z - gh - e), V(BLOCK_ROD_X + gw + e, yy, ROD_Z - gh - e),
                                 V(BLOCK_ROD_X + gw + e, yy, ROD_Z + gh + e), V(BLOCK_ROD_X - gw - e, yy, ROD_Z + gh + e)], close=True)
            for yy, e in ((BODY_Y1 + 0.01, 1.0), (BODY_Y1 - 1, 0.0))]
    tools.append(cq.Solid.makeLoft(lead, True))                                                     # lead-in where the rail enters, on the inner end
    for sy in (-1, 1):
        tools.append(teardrop_z(BOLT_X, sy * BOLT_Y, FL_TOP - 1, FL_TOP + CAP_SOLID + 1, HEAD_HOLE_D))          # your flange bolts come up through these
    nz = BASE_Z + 1.5                                                                               # nut slot 1.5 mm above the bottom face
    h = M3_NUT_AF / 2 + 0.1
    for x, y, side in SCREWS:
        tools.append(cz(x, y, BASE_Z - 1, BASE_Z + 9, M3))
        if side == -1: tools.append(box(x - h, x + h, OUT_Y0 - 1, y + h, nz, nz + 2.8))       # slide the nut in from the outer face
        else: tools.append(box(x - h, x + h, y - h, BODY_Y1 + 1, nz, nz + 2.8))              # slide the nut in from the inner face
    # the cap is hollow above 5 mm of solid over the flange; the pocket opens on the inner face (the top when printing), so it has no roof
    tools.append(box(BLOCK_ROD_X + gw + 3.0, CAP_X1 - WALL, OUT_Y0 + WALL, IN_Y1 + 1, FL_TOP + CAP_SOLID, top - WALL))
    return cut(s, tools)

'''
s = s[:old_a] + new + s[old_b:]
s = s.replace("# Your M4 flange bolt heads come up through two holes in the cap. Nothing on the pillar changes.\n",
              "# Your M4 flange bolt heads come up through two holes in the cap. Nothing on the pillar changes. The front is open (the user's change):\n"
              "# just a wall down the flange's front face and a boss for the front screw.\n", 1)
open(p, 'w', encoding='utf-8').write(s); print('ok')
