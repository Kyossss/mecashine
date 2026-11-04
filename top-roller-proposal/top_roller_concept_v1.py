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
AX_D = g['AX_D']; AXZ = 201.0
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
IDL_Y0, IDL_PLATE, IDL_Y1 = 45.0, 2.4, 67.0
def cy_(x, z, y0, y1, d): return cq.Solid.makeCylinder(d / 2, y1 - y0, V(x, y0, z), V(0, 1, 0))
idl = cy_(0, AXZ, IDL_Y0, IDL_Y0 + IDL_PLATE, 22).fuse(cy_(0, AXZ, IDL_Y0 + IDL_PLATE - 0.1, IDL_Y1, 26)).clean()
hexsock = cq.Workplane('XZ').polygon(6, (12.8) / 0.8660254).extrude(-6).val().translate(V(0, IDL_Y0 - 1, AXZ))   # 6 deep from the plate face
tools = [hexsock, cy_(0, AXZ, 50.9, 60.1, 9.0), cy_(0, AXZ, 60, IDL_Y1 + 1, 22.15)]
for k in range(6):
    a = math.radians(30 + 60 * k)
    tools.append(cy_(8.9 * math.cos(a), AXZ + 8.9 * math.sin(a), IDL_Y0 - 1, IDL_Y0 + IDL_PLATE + 1, 2.4))
for t in tools: idl = idl.cut(t)
IDLER = idl.clean()
BEARING = cy_(0, AXZ, 60, 67, 22).cut(cy_(0, AXZ, 59, 68, 8))
# tie discs: 12, plate toward -y, from the drive stopper (y -49) to the idler plate (y 45)
DISC0, PITCH, NDISC = -49.0, g['DISC_PITCH'], 12
def disc_at(y0):
    d = g['TIE_DISC'].rotate(V(0, 0, 0), V(1, 0, 0), -90)   # local z (plate first) -> +y
    return d.translate(V(0, y0, AXZ))
DISCS = [disc_at(DISC0 + i * PITCH) for i in range(NDISC)]
# new sensor bracket, downstream of the roller: a flange on the carriage's top plate (2 new M3 holes), an arm, and the board 44 mm after the axis
SX, SZ = 44.0, 226.5                                       # board centre x; board face height (same as now)
brk = [box(14.5, 56, -18, 18, 237, 240), box(36, 40, -6, 6, 230, 237), box(50, 54, -6, 6, 230, 237), box(33, 56, -9, 9, 228, 230)]
BRACKET = brk[0].fuse(brk[1]).fuse(brk[2]).fuse(brk[3]).clean()
for yh in (-12, 12): BRACKET = BRACKET.cut(cq.Solid.makeCylinder(1.7, 10, V(20, yh, 233), V(0, 0, 1)))
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
out['spec'] = {'axis_z': AXZ, 'brush_r': 23.0, 'hole_r': 8.9, 'pitch': PITCH, 'plate_t': 2.4, 'n_disc': NDISC, 'idler_plate_y': IDL_Y0, 'sens_x_new': SX, 'sens_x_old': -44.0, 'sens_z': SZ,
               'vol': {'drive': vol(DRIVE), 'bar': vol(BAR), 'idler': vol(IDLER), 'disc': vol(g['TIE_DISC']), 'bracket': vol(BRACKET)},
               'bar_len': round(BAR.BoundingBox().ylen, 1), 'drive_y': bbx(DRIVE)[2:4], 'idler_y': bbx(IDLER)[2:4]}
os.makedirs(r'F:\Research\ASPS\top-roller-proposal', exist_ok=True)
json.dump(out, open(r'F:\Research\ASPS\top-roller-proposal\roller-mesh.json', 'w'), separators=(',', ':'))
print(json.dumps(out['spec']))
for n, s in (('drive', DRIVE), ('bar', BAR), ('idler', IDLER), ('bracket', BRACKET)): print(n, 'valid', s.isValid(), 'solids', len(s.Solids()), 'bb', bbx(s))
print('bar vs drive', round(BAR.intersect(DRIVE).Volume(), 3), ' bar vs idler', round(BAR.intersect(IDLER).Volume(), 3), ' discs vs bar', round(sum(d.intersect(BAR).Volume() for d in DISCS), 3),
      ' discs vs idler', round(sum(d.intersect(IDLER).Volume() for d in DISCS), 3), ' discs vs drive', round(sum(d.intersect(DRIVE).Volume() for d in DISCS), 3))
print('last disc ends at y', DISC0 + NDISC * PITCH, ' idler plate at', IDL_Y0)
