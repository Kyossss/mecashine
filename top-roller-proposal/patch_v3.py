p = r'F:/Research/ASPS/top-roller-proposal/top_roller_concept.py'
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)
rep("AX_D = g['AX_D']; AXZ = 201.0",
    "AX_D = g['AX_D']; AXZ = 186.0          # v3: the carriage's legs are 15 mm longer, so the roller axis sits at 186 (201 now)\nLEG_EXT = 15.0")
a = s.index("IDL_Y0, IDL_PLATE, IDL_Y1 = 45.0, 2.4, 67.0"); b = s.index("# tie discs:")
s = s[:a] + '''IDL_Y0, IDL_PLATE = 45.0, 2.4
WALL_Y = 71.0                                              # inner face of the carriage's far wall (the old 8 mm pin came out of it here)
# idler end: 22 mm plate with 6 yarn tie holes, an 18 mm body holding the bar's hex socket, a shoulder, and an 8 mm axle into a 608ZZ in the wall
idl = cy_(0, AXZ, IDL_Y0, IDL_Y0 + IDL_PLATE, 22).fuse(cy_(0, AXZ, IDL_Y0 + IDL_PLATE - 0.1, WALL_Y - 1.2, 18))
idl = idl.fuse(cy_(0, AXZ, WALL_Y - 1.3, WALL_Y - 0.6, 12)).fuse(cy_(0, AXZ, WALL_Y - 0.7, WALL_Y + 6.6, 7.95)).clean()   # stops 0.6 mm short of the bearing's inner ring
hexsock = cq.Workplane('XZ').polygon(6, (12.8) / 0.8660254).extrude(-6).val().translate(V(0, IDL_Y0 - 1, AXZ))   # 6 deep from the plate face
tools = [hexsock]
for k in range(6):
    a = math.radians(30 + 60 * k)
    tools.append(cy_(8.9 * math.cos(a), AXZ + 8.9 * math.sin(a), IDL_Y0 - 1, IDL_Y0 + IDL_PLATE + 1, 2.4))
for t in tools: idl = idl.cut(t)
IDLER = idl.clean()
# 608ZZ pressed into a 22 mm pocket in the carriage's far wall, where the pin was
BEARING = cy_(0, AXZ, WALL_Y, WALL_Y + 7, 22).cut(cy_(0, AXZ, WALL_Y - 1, WALL_Y + 8, 8))
''' + s[b:]
a = s.index("SX, SZ = 44.0, 226.5"); b = s.index("def enc(s):")
s = s[:a] + '''# new sensor bracket, in front of the roller (v3): bolts to the carriage's top plate through the two holes your bracket uses now (x -34),
# and holds the board 48 mm before the roller axis and 20 mm higher than now, facing down. 4 mm further forward than now so the
# beam clears the top plate's front edge.
SX, SZ = -48.0, 246.5
brk = [box(-40, -28, -18, 16, 237, 240),                   # flange on the top plate, over the two existing holes
       box(-40, -37, -9, 9, 240, 250.5),                   # upright
       box(-58, -37, -9, 9, 248.1, 250.5)]                 # arm the board hangs under
BRACKET = brk[0].fuse(brk[1]).fuse(brk[2]).clean()
for yh in (-15, 13): BRACKET = BRACKET.cut(cq.Solid.makeCylinder(1.7, 10, V(-34, yh, 233), V(0, 0, 1)))
BOARD = box(SX - 5.35, SX + 5.35, -12.5, 12.5, SZ, SZ + 1.6)

''' + s[b:]
rep("'brush_r': 23.0,", "'brush_r': 26.0, 'leg_ext': LEG_EXT, 'wall_y': WALL_Y,")
rep("'sens_x_new': SX, 'sens_x_old': -44.0, 'sens_z': SZ,", "'sens_x_new': SX, 'sens_x_old': -44.0, 'sens_z': SZ, 'sens_z_old': 226.5,")
open(p, 'w', encoding='utf-8').write(s); print('ok')
