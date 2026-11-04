# Proposal only (2026-10-24): top polisher roller redesigned like the side brushes, and the top ToF sensor moved downstream.
# Nothing here goes into Fusion or cad_pincer9.py. Frame: x = Fusion x - 1138 (the roller axis), y = Fusion y (across the belt),
# z = height above the belt top. The roller axis runs along y at z 201 with the carriage at home.
import sys, os, json, math, base64, array
SP = r'F:\Research\ASPS\side-polisher-redesign'
os.chdir(SP); sys.path.insert(0, SP)
sys.argv = ['cad_pincer9.py', 'x']
src = open('cad_pincer9.py', encoding='utf8').read().split('\ndef overlap')[0]
g = {'__file__': os.path.join(SP, 'cad_pincer9.py'), '__name__': 'partial'}
exec(compile(src, 'cad_pincer9.py', 'exec'), g)
import cadquery as cq
V = cq.Vector
AX_D = g['AX_D']; AXZ = 186.0          # v3: the carriage's legs are 15 mm longer, so the roller axis sits at 186 (201 now)
LEG_EXT = 15.0
cz, box = g['cz'], g['box']

def side_to_roller(s):
    # side-core local (u, d, z), axis at (0, AX_D) vertical  ->  roller frame: x = u, y = 88 - z, z = 201 + (d - AX_D)
    s = s.translate(V(0, -AX_D, 0))
    s = s.rotate(V(0, 0, 0), V(1, 0, 0), 90)                 # (u, d, z) -> (u, -z, d)
    return s.translate(V(0, 88, AXZ))

# drive end: the side core's top part as it is (16 mm hub, your D-shaped shaft hole, captive-nut M3 x 8, M3 x 16 cross screw, 22 mm stopper)
DRIVE = side_to_roller(g['CORE_TOP'])
# bar: the side bar cut down so it ends 0.5 mm short of the idler end's socket floor (y 49.5)
BAR = side_to_roller(g['CORE_BAR'].cut(box(-20, 20, AX_D - 20, AX_D + 20, 0, 38.5)))
# idler end: 22 mm plate with 6 yarn tie holes facing the brush, a body round a 608ZZ that slides onto the carriage's 8 mm pin
IDL_Y0, IDL_PLATE = 45.0, 2.4
def cy_(x, z, y0, y1, d): return cq.Solid.makeCylinder(d / 2, y1 - y0, V(x, y0, z), V(0, 1, 0))
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
# tie discs: 12, plate toward -y, from the drive stopper (y -49) to the idler plate (y 45)
DISC0, PITCH, NDISC = -49.0, g['DISC_PITCH'], 12
def disc_at(y0):
    d = g['TIE_DISC'].rotate(V(0, 0, 0), V(1, 0, 0), -90)   # local z (plate first) -> +y
    return d.translate(V(0, y0, AXZ))
DISCS = [disc_at(DISC0 + i * PITCH) for i in range(NDISC)]
# new sensor bracket, downstream of the roller: a flange on the carriage's top plate (2 new M3 holes), an arm, and the board 44 mm after the axis
# new sensor bracket, in front of the roller (v3): bolts to the carriage's top plate through the two holes your bracket uses now (x -34),
# and holds the board 48 mm before the roller axis and 20 mm higher than now, facing down. 4 mm further forward than now so the
# beam clears the top plate's front edge.
SX, SZ = -60.0, 246.5                                     # v5: arm longer (60 mm before the axis), same height as v3 (20 mm above the current sensor), so the beam's cone clears the spinning yarn
brk = [box(-40, -28, -18, 16, 237, 240),                   # flange on the top plate, over the two existing holes
       box(-40, -37, -9, 9, 240, 250.5),                   # upright
       box(-69, -37, -9, 9, 248.1, 250.5),                 # longer arm the board hangs under
       box(-50, -37, -2, 2, 240, 248.1)]                   # web between the upright and the arm, so the longer arm doesn't droop
BRACKET = brk[0].fuse(brk[1]).fuse(brk[2]).fuse(brk[3]).clean()
for yh in (-15, 13): BRACKET = BRACKET.cut(cq.Solid.makeCylinder(1.7, 10, V(-34, yh, 233), V(0, 0, 1)))
BOARD = box(SX - 5.35, SX + 5.35, -12.5, 12.5, SZ, SZ + 1.6)

def enc(s):
    pts = array.array('h')
    for f in s.Faces():
        vs, ts = f.tessellate(0.12, 0.25)
        for t in ts:
            for k in t:
                v = vs[k]; pts.extend((int(round(v.x * 10)), int(round(v.y * 10)), int(round(v.z * 10))))
    return base64.b64encode(pts.tobytes()).decode()
out = {'drive': enc(DRIVE), 'bar': enc(BAR), 'idler': enc(IDLER), 'bearing': enc(BEARING), 'bracket': enc(BRACKET), 'board': enc(BOARD),
       'disc': enc(disc_at(0)), 'disc_y0': [DISC0 + i * PITCH for i in range(NDISC)]}
vol = lambda s: round(s.Volume() / 1000, 1)
bbx = lambda s: [round(v, 1) for v in (s.BoundingBox().xmin, s.BoundingBox().xmax, s.BoundingBox().ymin, s.BoundingBox().ymax, s.BoundingBox().zmin, s.BoundingBox().zmax)]
out['spec'] = {'axis_z': AXZ, 'brush_r': 26.0, 'leg_ext': LEG_EXT, 'wall_y': WALL_Y, 'hole_r': 8.9, 'pitch': PITCH, 'plate_t': 2.4, 'n_disc': NDISC, 'idler_plate_y': IDL_Y0, 'sens_x_new': SX, 'sens_x_old': -44.0, 'sens_z': SZ, 'sens_z_old': 226.5,
               'vol': {'drive': vol(DRIVE), 'bar': vol(BAR), 'idler': vol(IDLER), 'disc': vol(g['TIE_DISC']), 'bracket': vol(BRACKET)},
               'bar_len': round(BAR.BoundingBox().ylen, 1), 'drive_y': bbx(DRIVE)[2:4], 'idler_y': bbx(IDLER)[2:4]}
os.makedirs(r'F:\Research\ASPS\top-roller-proposal', exist_ok=True)
json.dump(out, open(r'F:\Research\ASPS\top-roller-proposal\roller-mesh.json', 'w'), separators=(',', ':'))
print(json.dumps(out['spec']))
for n, s in (('drive', DRIVE), ('bar', BAR), ('idler', IDLER), ('bracket', BRACKET)): print(n, 'valid', s.isValid(), 'solids', len(s.Solids()), 'bb', bbx(s))
print('bar vs drive', round(BAR.intersect(DRIVE).Volume(), 3), ' bar vs idler', round(BAR.intersect(IDLER).Volume(), 3), ' discs vs bar', round(sum(d.intersect(BAR).Volume() for d in DISCS), 3),
      ' discs vs idler', round(sum(d.intersect(IDLER).Volume() for d in DISCS), 3), ' discs vs drive', round(sum(d.intersect(DRIVE).Volume() for d in DISCS), 3))
print('last disc ends at y', DISC0 + NDISC * PITCH, ' idler plate at', IDL_Y0)
