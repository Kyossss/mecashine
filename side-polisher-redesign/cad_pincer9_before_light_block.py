# Side polisher pincer redesign, built around the existing Fusion model ("Conveyor assembly 2").
# Kept as they are: pillars, top plate, rails, covers, pinion, servo, and the rack's toothed bar and neck (so the tower holds it exactly as before).
# New: rack foot (a bolt-on pad), carriage (rack clamp and motor holder in one piece), arm frame, foot bracket with bearing,
# guide rods, bushing blocks, sensor bracket, reflector.
#
# Arm parts are modelled in arm-local coordinates, mm:
#   u  along the belt, 0 at the brush / motor axis, negative = upstream (the side the shoe arrives from)
#   d  across the belt, 0 at the middle of the arm columns, positive = outward (toward the pillar)
#   z  height above the belt top (Fusion z = 217)
# Left arm in Fusion:  x = 925 + u, y = -85 - d + p.   Right arm: x = 925.5 - u, y = 81.5 + d - p (the left side turned half a turn about the
# point the two racks are symmetric about).   p = how far the jaws have closed.
import sys, os, json, math
import cadquery as cq
from cadquery import Vector as V
import cad_ref

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__))

# ---- parameters
BEARING_OD, BEARING_W, BEARING_ID = 22.0, 7.0, 8.0   # 608
# printed guide rails (they replace the steel rods and the LM8UU bushings)
RAIL_W, RAIL_H = 14.0, 20.0                            # rail section: 14 mm along the belt, 20 mm tall
RAIL_D1 = 90.0                                         # rail tip, mm outward from the arm column middle
RAIL_FIT = 0.5                                          # clearance each side in the block's guide hole (0.25 printed too tight)
FLANGE_D = (11.0, 17.0)                                # rail flange: bolts flat on the arm boss's outer face
FLANGE_Z = (94.0, 128.0)
RAIL_BOLT_Z = (97.5, 124.5)                            # two M3 bolts, above and below the rail
BRUSH_D, BRUSH_Z0, BRUSH_Z1 = 50.0, 26.0, 140.0        # bristles: height from the tuft holes in your brush core (Body59); 50 mm across is assumed
# brush core, copied from your Body59: 19 mm tube from 17 to 159 mm above the belt, motor socket at the top
CORE_D, CORE_Z0, CORE_Z1 = 24.0, 22.0, 164.0           # my core: 24 mm body; top at 164, 2 mm under the motor holder, like your Body58
# motor shaft hole, copied from your Body58: 4.15 mm D-hole, flat 1.8 mm from the axis, 15 mm deep; 2.5 mm cross hole for an M3 grub screw onto the flat
SHAFT_D, SHAFT_FLAT, SHAFT_DEPTH = 4.15, 1.8, 15.0
GRUB_D, GRUB_DOWN = 2.5, 5.8
HUB_D, HUB_Z0 = 14.0, 148.0                            # hub round the shaft hole, 14 mm (yours is 10.8) for more wall round the grub screw
BODY_Z1 = 140.0                                         # top of the 24 mm tufted body; a 45 degree taper joins it to the hub
TUFT_D, TUFT_DEPTH = 3.0, 9.0                           # 3 mm tuft holes, 9 mm deep
TUFT_Z = ()                                             # no tuft holes: a plain solid core for a sleeve brush (was 15 rings, 30 to 135 mm)
TUFT_N = 8                                              # 8 tufts per ring, each ring turned half a step from the last (120 tufts)
STUB_D = 7.95                                           # printed axle into the 608ZZ (8 mm bore)
BR_Z0, BR_Z1 = 10.0, 19.0                               # foot bridge: 7 mm above the braces' lip, 10 mm above the belt
TIE_HOLE_D = 38.0                                       # tie beam clears the core and its side boss as they turn
FIT = 0.2
M3, M3_HEAD, M3_NUT_AF, M3_PILOT, M4 = 3.4, 6.5, 5.8, 2.8, 4.4
T = 11.0                                               # half thickness of the columns (22 mm)
AX_D = -8.5                                            # brush / motor axis sits 8.5 mm inboard of the column middle
CF = (-65.0, -43.5)                                    # upstream column, u range (clears the rack clamp, u -43..45)
CB = (45.5, 67.0)                                      # downstream column
ROD_U, ROD_Z = (-56.0, 56.0), 111.0                    # guide rails: one per leg, just above the brush
# carriage: flange under the rack pad, motor cup hanging below it, a lug at each end that the arm columns bolt to
CAR_U = (-43.0, 45.0)                                  # fits between the columns with 0.5 mm each side
CAR_Z0, CAR_Z1 = 217.0, 226.0                          # flange; the rack pad sits on top of it
PAD_U, PAD_D, PAD_Z1 = (-41.0, 43.0), (-23.5, 6.5), 234.0   # new rack foot: 84 x 30 x 8 mm pad, top face where the old foot's top was
CUP_OD, CUP_BORE, CUP_Z0, CUP_FLOOR = 30.0, 25.0, 166.0, 2.0   # motor holder, same inside and outside sizes as the existing cup
LUG_Z0 = 190.0
PAD_BOLTS = [(-27.0, -17.5), (-27.0, 0.5), (29.0, -17.5), (29.0, 0.5)]   # (u, d) of the four M3 bolts, rack pad to carriage
LUG_BOLTS = [(-5.0, 198.0), (5.0, 216.0)]             # (d, z) of the two M3 bolts through each column into the carriage lug
LUG_SINK, PAD_SINK = 10.0, 2.0                         # head counterbores: M3 x 20 through each column into the lug, M3 x 16 up through the carriage into the rack pad
COL_TOP = 234.0
SENSOR_U, SENSOR_Z, SENSOR_HOLE_D = -71.0, 42.0, 2.0
# Shoe clearance. Below the tie beam, everything stays outside the space the shoe sweeps as it passes with the brushes on it
# (measured from the shoe in the Fusion model, see shoe_env.js), with about 5 mm to spare.
LEG = (30.0, 46.0)                                    # the lower legs sit close beside the brush, |u| from 30 to 46
D_IN = -3.5                                            # inner face of the legs; the old arm's bar was at -1
ROD_D0 = 3.0                                           # inner face of the rail bosses
BRUSH_LINE_D = AX_D - BRUSH_D / 2                      # the brush surface that touches the shoe, d = -33.5
BOARD_L, BOARD_W, BOARD_T, BOARD_HOLES = 25.0, 10.7, 1.6, 20.0

def box(x0, x1, y0, y1, z0, z1): return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))
def cz(x, y, z0, z1, d): return cq.Solid.makeCylinder(d / 2, z1 - z0, V(x, y, z0), V(0, 0, 1))
def cy(x, z, y0, y1, d): return cq.Solid.makeCylinder(d / 2, y1 - y0, V(x, y0, z), V(0, 1, 0))
def cx(y, z, x0, x1, d): return cq.Solid.makeCylinder(d / 2, x1 - x0, V(x0, y, z), V(1, 0, 0))
def hexprism(axis, p, af, depth):
    s = cq.Workplane("XY").polygon(6, af / 0.8660254).extrude(depth).val()
    if axis == 'x': s = s.rotate(V(0, 0, 0), V(0, 1, 0), 90)
    if axis == 'y': s = s.rotate(V(0, 0, 0), V(1, 0, 0), -90)
    return s.translate(V(*p))
def wedge_xz(pts, y0, y1):
    s = cq.Workplane("XY").polyline(pts).close().extrude(y1 - y0).val()
    return s.rotate(V(0, 0, 0), V(1, 0, 0), 90).translate(V(0, y1, 0))
def wedge_xy(pts, z0, z1): return cq.Workplane("XY").polyline(pts).close().extrude(z1 - z0).val().translate(V(0, 0, z0))
def fuse(parts):
    s = parts[0]
    for p in parts[1:]: s = s.fuse(p)
    return s.clean()
def cut(s, tools):
    for t in tools: s = s.cut(t)
    return s.clean()

# ---------------- arm frame (local coordinates)
def arm():
    solids = []
    for (u0, u1) in (CF, CB): solids.append(box(u0, u1, -T, T, 144, COL_TOP))            # upper columns, above shoe height; they bolt to the carriage lugs
    solids += [box(CF[1], CB[0], D_IN, T, 144, 164), box(-23, 23, AX_D - 23, T, 144, 164)]  # tie beam under the motor holder, a ring round the brush core
    for s in (-1, 1):
        u0, u1 = sorted((s * LEG[0], s * LEG[1]))
        solids += [box(u0, u1, D_IN, T, 74, 150), box(u0, u1, 4, T, 44, 74)]             # lower leg beside the brush, lap tongue for the foot
    # rail bosses, on the outer side of each leg
    solids += [box(-66, -LEG[1], ROD_D0, T, FLANGE_Z[0], FLANGE_Z[1]), box(LEG[1], 66, ROD_D0, T, FLANGE_Z[0], FLANGE_Z[1])]
    s = fuse(solids)
    tools = [cz(0, AX_D, 143, 165, TIE_HOLE_D),              # the brush core turns inside the tie beam
             cy(0, CORE_Z1 - GRUB_DOWN, AX_D - 25, AX_D - 15, 7.0)]   # hex key hole to the core's shaft screw, from the belt side
    for u in ROD_U:
        # 2 mm deep pocket that the rail flange sits in, so it cannot twist, and two M3 bolts with nuts pressed in from the inner face
        tools.append(box(u - RAIL_W / 2 - 0.2, u + RAIL_W / 2 + 0.2, T - 2, T + 1, FLANGE_Z[0] - 0.2, FLANGE_Z[1] + 0.2))
        for z in RAIL_BOLT_Z:
            tools += [cy(u, z, ROD_D0 - 1, T + 1, M3), hexprism('y', (u, ROD_D0 - 1, z), M3_NUT_AF, 3.6)]
    for sg in (-1, 1):
        uc = sg * (LEG[0] + LEG[1]) / 2
        for z in (52, 66): tools += [cy(uc, z, 3, T + 1, M3), cy(uc, z, T - 3, T + 1, M3_HEAD)]
    for (d, z) in LUG_BOLTS:                                # bolts into the carriage lugs, heads sunk in the columns' end faces
        tools += [cx(d, z, CF[0] - 1, CF[1] + 1, M3), cx(d, z, CF[0] - 1, CF[0] + LUG_SINK, M3_HEAD), cx(d, z, CB[0] - 1, CB[1] + 1, M3), cx(d, z, CB[1] - LUG_SINK, CB[1] + 1, M3_HEAD)]
    return cut(s, tools)

# ---------------- foot bracket (local)
def foot():
    # bridge: bowed away from the shoe. Its inner edge follows the shoe's sweep, with only the bearing seat reaching in under the brush.
    seat = AX_D - 13.0
    outline = [(-LEG[1], T), (LEG[1], T), (LEG[1], D_IN), (30, -10.5), (20, -14.5), (10, -20.5), (4, -21.5), (-4, -21.5), (-10, -20.5), (-20, -14.5), (-30, -10.5), (-LEG[1], D_IN)]
    solids = [wedge_xy(outline, BR_Z0, BR_Z1)]
    for s in (-1, 1):
        u0, u1 = sorted((s * LEG[0], s * LEG[1]))
        solids += [box(u0, u1, D_IN, T, BR_Z1, 44), box(u0, u1, D_IN, 4, 44, 74)]
    s = fuse(solids)
    tools = [cz(0, AX_D, BR_Z1 - BEARING_W, BR_Z1 + 1, BEARING_OD + 0.15), cz(0, AX_D, BR_Z0 - 1, BR_Z1 + 1, BEARING_OD - 8)]
    for sg in (-1, 1):
        uc = sg * (LEG[0] + LEG[1]) / 2
        for z in (52, 66): tools += [cy(uc, z, D_IN - 1, 5, M3), hexprism('y', (uc, D_IN - 1, z), M3_NUT_AF, 3.6)]
        for z in (22, 36):       # sensor / reflector bracket screws, on both end faces
            a, b = sorted((sg * (LEG[1] - 10), sg * (LEG[1] + 1))); tools.append(cx(SENSOR_HOLE_D, z, a, b, M3_PILOT))
    return cut(s, tools)


# ---------------- guide block. A full-height cap that wraps the pillar's middle flange: top on the flange, a cheek down each side, a solid front, and a
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
              box(PILLAR_FACE, CAP_X1, OUT_Y0, IN_Y1, FL_TOP, 129),         # cap on the flange, full height so the whole top is one flat face
              box(SKIRT_X0, PILLAR_FACE - 0.8, -13, 13, BASE_Z, FL_TOP + 0.5),       # solid front down the flange's front face (0.3 mm clear on the right-hand side)
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

# ---------------- guide rail (local, drawn on the upstream leg of the left arm). Printed, it replaces the steel rod.
# A 14 x 20 mm bar with a flange that sits in the boss's pocket and bolts on with two M3 bolts.
def rail():
    u = ROD_U[0]
    u0, u1 = u - RAIL_W / 2, u + RAIL_W / 2
    z0, z1 = ROD_Z - RAIL_H / 2, ROD_Z + RAIL_H / 2
    s = fuse([box(u0, u1, FLANGE_D[0] - 2, FLANGE_D[1], FLANGE_Z[0], FLANGE_Z[1]),       # flange, its first 2 mm inside the pocket
              box(u0, u1, FLANGE_D[1] - 0.5, RAIL_D1, z0, z1),                              # rail
              wedge_xz_d([(FLANGE_D[1], z1), (FLANGE_D[1], FLANGE_Z[1]), (FLANGE_D[1] + 4, z1)], u0, u1),   # gussets above and below
              wedge_xz_d([(FLANGE_D[1], z0), (FLANGE_D[1], FLANGE_Z[0]), (FLANGE_D[1] + 4, z0)], u0, u1)])
    s = s.chamfer(1.5, None, [e for e in s.Edges() if abs(e.Center().y - RAIL_D1) < 0.01])   # lead-in on the tip
    tools = [cy(u, z, FLANGE_D[0] - 3, FLANGE_D[1] + 1, M3) for z in RAIL_BOLT_Z]
    tools += [cy(u, z, FLANGE_D[1], FLANGE_D[1] + 6, M3_HEAD) for z in RAIL_BOLT_Z]        # seat for the bolt head, cut through the gusset
    return cut(s, tools)
def wedge_xz_d(pts, u0, u1):
    # triangle given in (d, z), extruded across u from u0 to u1, built from its six corners
    (d0, za), (d1, zb), (d2, zc) = pts
    a = [V(u0, d0, za), V(u0, d1, zb), V(u0, d2, zc)]
    b = [V(u1, d0, za), V(u1, d1, zb), V(u1, d2, zc)]
    w0 = cq.Wire.makePolygon(a, close=True); w1 = cq.Wire.makePolygon(b, close=True)
    return cq.Solid.makeLoft([w0, w1], True)

# ---------------- sensor bracket (local, on the upstream end of the left foot) and its board
def sensor_bracket():
    f = -LEG[1]                                               # upstream face of the foot upright
    s = fuse([box(SENSOR_U - 3.5, f, 8, T, 14, 57),          # wall the board screws to, on the outer side so the board sits back from the shoe (front edge trimmed by the user)
              box(f - 5, f, -1.5, T, 14, 44),                # base against the foot upright
              wedge_xy([(f - 5, 8), (f - 22, 8), (f - 5, -1.5)], 14, 17),
              cy(SENSOR_U, SENSOR_Z - BOARD_HOLES / 2, 5.5, 8, 7), cy(SENSOR_U, SENSOR_Z + BOARD_HOLES / 2, 5.5, 8, 7)])   # stand-offs
    tools = [cy(SENSOR_U, SENSOR_Z - BOARD_HOLES / 2, 5, T + 1, M3_PILOT), cy(SENSOR_U, SENSOR_Z + BOARD_HOLES / 2, 5, T + 1, M3_PILOT)]
    for z in (22, 36): tools.append(cx(SENSOR_HOLE_D, z, f - 6, f + 1, M3))
    tools.append(box(SENSOR_U - 4, SENSOR_U + 2.5, 8, T + 1, SENSOR_Z - 6.5, SENSOR_Z + 6.5))   # user's notch: the board's male header pins come out the back through it
    return cut(s, tools)
def sensor_board():
    return box(SENSOR_U - BOARD_W / 2, SENSOR_U + BOARD_W / 2, 5.5 - BOARD_T, 5.5, SENSOR_Z - BOARD_L / 2, SENSOR_Z + BOARD_L / 2)

# ---------------- reflector (local, on the right arm; its upstream end is the +u end because the right arm is the left one turned round)
REFL_FACE_D = 6.0
def reflector():
    f = LEG[1]
    s = fuse([box(f, 91, REFL_FACE_D, REFL_FACE_D + 3, 14, 62),                           # target plate, facing the sensor
              box(f, f + 5, -1.5, T, 14, 44),                                             # base against the foot upright
              wedge_xy([(f + 5, REFL_FACE_D), (f + 24, REFL_FACE_D), (f + 5, -1.5)], 14, 17),
              wedge_xy([(f + 5, REFL_FACE_D + 3), (f + 24, REFL_FACE_D + 3), (f + 5, T)], 14, 44)])
    return cut(s, [cx(SENSOR_HOLE_D, z, f - 1, f + 6, M3) for z in (22, 36)])


# ---------------- brush core (local): your Body59, made solid, with a printed axle under it for the 608ZZ
def brush_core():
    # A solid 24 mm core (no tuft holes), a 14 mm hub on top carrying your motor shaft hole and grub screw hole from Body58,
    # and a printed 8 mm axle underneath for the 608ZZ.
    ax0 = BR_Z1 - BEARING_W + 0.5
    taper_h = (CORE_D - HUB_D) / 2
    cone = cq.Solid.makeCone(CORE_D / 2, HUB_D / 2, taper_h, V(0, AX_D, BODY_Z1), V(0, 0, 1))
    s = fuse([cz(0, AX_D, CORE_Z0, BODY_Z1, CORE_D), cone,
              cz(0, AX_D, BODY_Z1 + taper_h - 0.5, CORE_Z1, HUB_D),                                 # hub
              cz(0, AX_D, ax0, CORE_Z0 + 0.5, STUB_D),                                              # axle
              cz(0, AX_D, BR_Z1 + 0.6, CORE_Z0 + 0.5, 12.0)])                                       # collar, 0.6 mm above the bearing's inner ring
    s = s.fillet(0.8, [e for e in s.Edges() if abs(e.Center().z - ax0) < 0.01])                    # lead-in on the axle tip
    s = s.chamfer(1.5, None, [e for e in s.Edges() if abs(e.Center().z - CORE_Z0) < 0.01 and abs(e.Length() - math.pi * CORE_D) < 0.5])   # bottom edge
    # your D-shaped shaft hole: a 4.15 mm hole with the material beyond the flat left in
    dhole = cz(0, AX_D, CORE_Z1 - SHAFT_DEPTH, CORE_Z1 + 1, SHAFT_D).cut(box(SHAFT_FLAT, 5, AX_D - 5, AX_D + 5, CORE_Z1 - SHAFT_DEPTH - 1, CORE_Z1 + 2))
    tools = [dhole, cx(AX_D, CORE_Z1 - GRUB_DOWN, 0, HUB_D, GRUB_D)]                                 # grub screw hole, square to the flat
    r = CORE_D / 2
    for k, z in enumerate(TUFT_Z):
        for n in range(TUFT_N):
            ang = (360.0 / TUFT_N) * (n + 0.5 * (k % 2))
            t = cq.Solid.makeCylinder(TUFT_D / 2, TUFT_DEPTH + 1, V(0, AX_D + r - TUFT_DEPTH, z), V(0, 1, 0)).rotate(V(0, AX_D, 0), V(0, AX_D, 1), ang)
            tools.append(t)
    return cut(s, tools)

# ---------------- carriage (local): rack clamp and motor holder in one piece
def carriage():
    s = fuse([box(CAR_U[0], CAR_U[1], PAD_D[0], T, CAR_Z0, CAR_Z1),                       # flange
              cz(0, AX_D, CUP_Z0, CAR_Z0 + 1, CUP_OD),                                    # motor cup
              box(CAR_U[0], CAR_U[0] + 10, -T, T, LUG_Z0, CAR_Z0 + 1), box(CAR_U[1] - 10, CAR_U[1], -T, T, LUG_Z0, CAR_Z0 + 1)])   # lugs
    tools = [cz(0, AX_D, CUP_Z0 + CUP_FLOOR, CAR_Z1 + 1, CUP_BORE), cz(0, AX_D, CUP_Z0 - 1, CUP_Z0 + CUP_FLOOR + 1, 8),      # motor pocket, shaft hole
             box(-3, 3, AX_D, T + 1, CAR_Z1 - 5, CAR_Z1 + 1)]                             # wire channel, out toward the pillar
    for (u, d) in PAD_BOLTS: tools += [cz(u, d, CAR_Z0 - 1, CAR_Z1 + 1, M3), cz(u, d, CAR_Z0 - 1, CAR_Z0 + PAD_SINK, M3_HEAD)]   # head sunk so an M3 x 16 reaches through the nut
    for (d, z) in LUG_BOLTS:
        tools += [cx(d, z, CAR_U[0] - 1, CAR_U[0] + 11.5, M3), cx(d, z, CAR_U[1] - 11.5, CAR_U[1] + 1, M3)]
        for uc in (CAR_U[0] + 5.2, CAR_U[1] - 5.2):                                       # captive nut slots, open at the bottom of the lug
            tools.append(box(uc - 1.4, uc + 1.4, d - M3_NUT_AF / 2, d + M3_NUT_AF / 2, LUG_Z0 - 1, z + M3_NUT_AF / 2))
    return cut(s, tools)

# ---------------- rack: the existing body with its foot replaced by a wider pad that bolts to the carriage. Built in Fusion coordinates.
def new_rack():
    old = cad_ref.load('rackA')
    # keep everything above the old foot: bar, teeth, neck. The cut is 0.3 mm above the foot's top face, inside the neck's flare.
    keep = max(old.cut(box(800, 1000, -200, 200, 400, 451.3)).Solids(), key=lambda q: q.Volume())
    fx = lambda u: 925 + u
    fy = lambda d: -85 - d
    pad = box(fx(PAD_U[0]), fx(PAD_U[1]), fy(PAD_D[1]), fy(PAD_D[0]), 217 + CAR_Z1, 217 + PAD_Z1)
    pad = pad.fuse(box(912, 933, -83.5, -69.5, 450, 451.8)).clean()                         # a nub that overlaps the neck, so the two join as one solid
    tools = []
    for (u, d) in PAD_BOLTS:
        tools += [cz(fx(u), fy(d), 217 + CAR_Z1 - 1, 217 + PAD_Z1 + 1, M3), hexprism('z', (fx(u), fy(d), 217 + PAD_Z1 - 2.8), M3_NUT_AF, 4)]   # nut pocket in the pad's top face
    return keep.fuse(cut(pad, tools))

ARM, FOOT, BLOCK, SENSOR, BOARD, REFL = arm(), foot(), block(), sensor_bracket(), sensor_board(), reflector()
CLAMP = flange_clamp()
CARRIAGE, RACK = carriage(), new_rack()
RAIL = rail()
RAIL_B = RAIL.mirror('YZ')          # the downstream rail is the same part turned round
CORE = brush_core()
RACK_R = RACK.rotate(V(925.25, -1.75, 0), V(925.25, -1.75, 1), 180)

# ---------------- placement in Fusion coordinates
def placeL(s, p=0): return s.mirror('XZ').translate(V(925, -85 + p, 217))
def placeR(s, p=0): return s.mirror('YZ').translate(V(925.5, 81.5 - p, 217))
def place_block(side, back, rod_x, part=None):
    part = BLOCK if part is None else part
    if side > 0: part = part.mirror('XZ')        # right side: the inner cheek is on the other side
    b = part.mirror('YZ') if back else part
    shift = rod_x - (925 + (-BLOCK_ROD_X if back else BLOCK_ROD_X))
    return b.translate(V(925 + shift, side * 127.45, 217))

def assembly(p):
    it = {}
    for side, place, xs, ys in (('L', placeL, 1, -1), ('R', placeR, -1, 1)):
        ax = (925 if side == 'L' else 925.5)
        it['arm_' + side] = place(ARM, p); it['foot_' + side] = place(FOOT, p); it['carriage_' + side] = place(CARRIAGE, p)
        it['rack_' + side] = RACK.translate(V(0, p, 0)) if side == 'L' else RACK_R.translate(V(0, -p, 0))
        it['motor_' + side] = place(cz(0, AX_D, CUP_Z0 + CUP_FLOOR, CUP_Z0 + CUP_FLOOR + 49, CUP_BORE - 0.2), p)
        it['core_' + side] = place(CORE, p)
        it['brush_' + side] = place(cz(0, AX_D, BRUSH_Z0, BRUSH_Z1, BRUSH_D).cut(cz(0, AX_D, BRUSH_Z0 - 1, BRUSH_Z1 + 1, CORE_D + 0.4)), p)
        it['bearing_' + side] = place(cz(0, AX_D, BR_Z1 - BEARING_W, BR_Z1, BEARING_OD).cut(cz(0, AX_D, BR_Z1 - 8, BR_Z1 + 1, BEARING_ID)), p)
        for i, u in enumerate(ROD_U):
            it['rail_%s%d' % (side, i)] = place(RAIL if u < 0 else RAIL_B, p)
            rx = ax + xs * u; back = rx > 925
            it['block_%s%d' % (side, i)] = place_block(ys, back, rx)
            it['clamp_%s%d' % (side, i)] = place_block(ys, back, rx, CLAMP)
    it['sensor_L'] = placeL(SENSOR, p); it['board_L'] = placeL(BOARD, p); it['refl_R'] = placeR(REFL, p)
    return it

BRACE = cad_ref.load('brace164')
BRACES = fuse([BRACE.translate(V(dx, 0, 0)) for dx in (-216, 0, 216, 432)])
BRACES_R = BRACES.mirror('XZ')
STATIC = ['pillarL_low', 'pillarL_up', 'pillarR_low', 'pillarR_up', 'top_centre', 'cover_c', 'rail14', 'rail15', 'rail16', 'rail17', 'cover20', 'cover21', 'servo_brkt', 'base']
MOVE_L, MOVE_R = [], []        # the old racks, clamps and cups are replaced
REFS = {n: cad_ref.load(n) for n in STATIC + MOVE_L + MOVE_R}
REFS_X = {n: cad_ref.load(n) for n in ('roller155', 'roller156')}
def existing(p):
    e = {n: REFS[n] for n in STATIC}
    e['brace_L'] = BRACES; e['brace_R'] = BRACES_R; e['roller155'] = REFS_X['roller155']; e['roller156'] = REFS_X['roller156']
    for n in MOVE_L: e[n] = REFS[n].translate(V(0, p, 0))
    for n in MOVE_R: e[n] = REFS[n].translate(V(0, -p, 0))
    return e

def overlap(a, b):
    b1, b2 = a.BoundingBox(), b.BoundingBox()
    if b1.xmax < b2.xmin or b2.xmax < b1.xmin or b1.ymax < b2.ymin or b2.ymax < b1.ymin or b1.zmax < b2.zmin or b2.zmax < b1.zmin: return 0
    return a.intersect(b).Volume()
def clashes(p):
    it, ex, out = assembly(p), existing(p), []
    names = sorted(it)
    for i, n in enumerate(names):
        for m in names[i + 1:]:
            v = overlap(it[n], it[m])
            if v > 0.5: out.append([n, m, round(v, 1)])
        for m, s in ex.items():
            v = overlap(it[n], s)
            if v > 0.5: out.append([n, 'EXISTING ' + m, round(v, 1)])
    return out

def bb(s):
    b = s.BoundingBox(); return [round(b.xlen, 1), round(b.ylen, 1), round(b.zlen, 1)]
def to_bed(s):
    b = s.BoundingBox(); return s.translate(V(-b.xmin, -b.ymin, -b.zmin))
# print copies: the real parts are the mirror image of the local models (see the placement functions), so mirror first
real = lambda s: s.mirror('XZ')
prints = {
    'arm-frame': to_bed(real(ARM).rotate(V(0, 0, 0), V(1, 0, 0), 90)),          # outer face down
    'carriage': to_bed(real(CARRIAGE).rotate(V(0, 0, 0), V(1, 0, 0), 180)),      # upside down: flange on the bed, cup pointing up
    'rack': to_bed(RACK),
    'brush-core': to_bed(real(CORE).rotate(V(0, 0, 0), V(1, 0, 0), 180)),        # upside down: socket on the bed, axle at the top                                                        # as it sits in the machine; turn it the way you printed the current rack
    'foot-bracket': to_bed(real(FOOT)),
    # handed: A = left upstream and right downstream, B = left downstream and right upstream (mirror image). Printed upside down on the
    # flat top: the cheeks point up, and the rail hole and nut slots are short bridges, so no supports are needed.
    'bushing-block-A': to_bed(BLOCK.rotate(V(0, 0, 0), V(1, 0, 0), 180)),
    'bushing-block-B': to_bed(BLOCK.mirror('XZ').rotate(V(0, 0, 0), V(1, 0, 0), 180)),
    'flange-clamp-A': to_bed(CLAMP),
    'flange-clamp-B': to_bed(CLAMP.mirror('XZ')),
    'guide-rail': to_bed(real(RAIL).rotate(V(0, 0, 0), V(0, 1, 0), 90)),        # lying on one side, so the layers run along the rail
    'sensor-bracket': to_bed(real(SENSOR)),
    'reflector': to_bed(real(REFL)),                                              # standing on its bottom edge
}
report = {'parts': {}}
for name, s in prints.items():
    cq.exporters.export(cq.Workplane("XY").add(s), os.path.join(OUT, name + '.step'))
    cq.exporters.export(cq.Workplane("XY").add(s), os.path.join(OUT, name + '.stl'), tolerance=0.02, angularTolerance=0.1)
    report['parts'][name] = {'bed_xyz': bb(s), 'volume_cm3': round(s.Volume() / 1000, 1), 'valid': s.isValid(), 'solids': len(s.Solids())}
report['clashes'] = {str(p): clashes(p) for p in (-7, 0, 15, 30)}

# ---- shoe sweep: smallest gap between each part and the space the shoe passes through, below the tie beam
ENV = json.load(open(os.path.join(HERE, 'shoe-env.json')))['env']['all']
def env(u):
    u = max(-115.0, min(115.0, u)); lo = int(math.floor(u / 5.0)) * 5; hi = min(115, lo + 5); t = (u - lo) / 5.0
    return ENV[str(lo)] * (1 - t) + ENV[str(hi)] * t
def shoe_gap(s, sign, both=False):
    worst = (1e9, None)
    for f in s.Faces():
        vs, _ = f.tessellate(1.0, 0.3)
        for v in vs:
            if v.z > 143.5: continue
            e = max(env(v.x), env(-v.x)) if both else env(sign * v.x)
            g = (v.y - BRUSH_LINE_D) - e
            if g < worst[0]: worst = (g, (round(v.x, 1), round(v.y, 1), round(v.z, 1)))
    return [round(worst[0], 1), worst[1]]
def gap(p):
    it = assembly(p); out = {}
    for n in ('foot_L', 'foot_R', 'sensor_L', 'refl_R', 'core_L', 'core_R', 'bearing_L', 'bearing_R'):
        out[n] = round(min(it[n].distance(BRACES), it[n].distance(BRACES_R)), 1)
    return out
report['brace_gap_mm'] = {str(p): gap(p) for p in (-7, 0, 30)}
report['shoe_gap_mm'] = {'brush-core': shoe_gap(CORE, 1, True), 'arm-frame': shoe_gap(ARM, 1, True), 'foot-bracket': shoe_gap(FOOT, 1, True), 'sensor-bracket': shoe_gap(SENSOR, 1), 'sensor-board': shoe_gap(BOARD, 1), 'reflector': shoe_gap(REFL, -1), 'guide-rail': shoe_gap(RAIL, 1, True)}

asm = cq.Assembly(name='side_polisher_new_parts')
for n in ('rackA', 'rackB', 'clampL', 'clampR', 'cupL', 'cupR'): pass
COL = {'rail': (0.84, 0.86, 0.89), 'core': (0.85, 0.55, 0.3), 'carriage': (0.61, 0.78, 0.85), 'rack': (0.37, 0.53, 0.78), 'motor': (0.7, 0.72, 0.75), 'arm': (0.72, 0.67, 0.86), 'foot': (0.31, 0.70, 0.49), 'block': (0.18, 0.60, 0.63), 'clamp': (0.95, 0.62, 0.20), 'rod': (0.84, 0.86, 0.89), 'bush': (0.7, 0.72, 0.75), 'bearing': (0.88, 0.69, 0.25),
       'shaft': (0.84, 0.86, 0.89), 'brush': (0.75, 0.42, 0.19), 'sensor': (0.59, 0.84, 0.67), 'refl': (0.96, 0.96, 0.94), 'board': (0.14, 0.38, 0.77)}
for n, s in assembly(0).items():
    c = COL[n.split('_')[0]]; asm.add(s, name=n, color=cq.Color(c[0], c[1], c[2], 1.0))
asm.save(os.path.join(OUT, 'new-parts-in-place.step'))

def mesh(s, tol=0.25):
    tris, ids = [], []
    for fi, f in enumerate(s.Faces()):
        vs, ts = f.tessellate(tol, 0.35)
        for t in ts:
            for k in t: tris += [round(vs[k].x * 10), round(vs[k].y * 10), round(vs[k].z * 10)]
            ids.append(fi)
    return {'t': tris, 'f': ids}
RACK_PAGE = RACK.translate(V(-925, 0, -217))        # page coordinates
json.dump({'arm': mesh(ARM), 'foot': mesh(FOOT), 'block': mesh(BLOCK), 'clamp': mesh(CLAMP), 'sensor': mesh(SENSOR), 'refl': mesh(REFL), 'carriage': mesh(CARRIAGE), 'rack': mesh(RACK_PAGE, 0.1), 'core': mesh(CORE, 0.3), 'rail': mesh(RAIL)}, open(os.path.join(HERE, 'pincer9-mesh.json'), 'w'), separators=(',', ':'))
print(json.dumps(report))
