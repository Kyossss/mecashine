# Top polisher redesign (approved 2026-10-24): parts, print STLs and in-place STEPs for Fusion.
# Roller like the side brushes (drive end = the side core's top part, 109 mm hex bar, 12 tie discs, idler end with an 8 mm axle into a
# 608ZZ in the carriage's far wall), roller axis 15 mm lower (186 above the belt) because the carriage's legs get 15 mm longer,
# and a new ToF bracket: board 75 mm before the roller axis (60 until 2026-11-03), 20 mm higher than now, mounted like your current bracket (tab under the
# top plate, two screws up into its blind holes).
# Frame for the in-place parts: Fusion mm (x along the belt, y across, z), belt top at Fusion z 217.
import sys, os, json, math, shutil
SP = r'F:\Research\ASPS\side-polisher-redesign'
OUT = os.path.dirname(os.path.abspath(__file__))
os.chdir(SP); sys.path.insert(0, SP)
sys.argv = ['cad_pincer9.py', 'x']
src = open('cad_pincer9.py', encoding='utf8').read().split('\ndef overlap')[0]
g = {'__file__': os.path.join(SP, 'cad_pincer9.py'), '__name__': 'partial'}
exec(compile(src, 'cad_pincer9.py', 'exec'), g)
import cadquery as cq
V = cq.Vector
AX_D = g['AX_D']; box, cz = g['box'], g['cz']
XAX, ZAX = 1138.0, 217.0 + 186.0               # roller axis in Fusion: x 1138, z 403 (186 above the belt)
WALL_Y = 71.0

def side_to_fusion(s):
    # side-core local (u, d, z), axis at (0, AX_D)  ->  Fusion: x = 1138 + u, y = 88 - z, z = 403 + (d - AX_D)
    return s.translate(V(0, -AX_D, 0)).rotate(V(0, 0, 0), V(1, 0, 0), 90).translate(V(XAX, 88, ZAX))
def cy_(x, z, y0, y1, d): return cq.Solid.makeCylinder(d / 2, y1 - y0, V(x, y0, z), V(0, 1, 0))

BAR_LOCAL = g['CORE_BAR'].cut(box(-20, 20, AX_D - 20, AX_D + 20, 0, 38.5))     # the side bar cut to 109 mm
DRIVE = side_to_fusion(g['CORE_TOP']); BAR = side_to_fusion(BAR_LOCAL)
# idler end
IY0, IPL = 45.0, 2.4
idl = cy_(XAX, ZAX, IY0, IY0 + IPL, 22).fuse(cy_(XAX, ZAX, IY0 + IPL - 0.1, WALL_Y - 1.2, 18))
idl = idl.fuse(cy_(XAX, ZAX, WALL_Y - 1.3, WALL_Y - 0.6, 12)).fuse(cy_(XAX, ZAX, WALL_Y - 0.7, WALL_Y + 6.6, 7.95)).clean()
tools = [cq.Workplane('XZ').polygon(6, 12.8 / 0.8660254).extrude(-6).val().translate(V(XAX, IY0 - 1, ZAX))]
for k in range(6):
    a = math.radians(30 + 60 * k)
    tools.append(cy_(XAX + 8.9 * math.cos(a), ZAX + 8.9 * math.sin(a), IY0 - 1, IY0 + IPL + 1, 2.4))
for t in tools: idl = idl.cut(t)
IDLER = idl.clean()
BEARING = cy_(XAX, ZAX, WALL_Y, WALL_Y + 7, 22).cut(cy_(XAX, ZAX, WALL_Y - 1, WALL_Y + 8, 8))
DISCS = [g['TIE_DISC'].rotate(V(0, 0, 0), V(1, 0, 0), -90).translate(V(XAX, -49.0 + i * g['DISC_PITCH'], ZAX)) for i in range(12)]
# ToF bracket: one profile in x-z, the same 35 mm width all along y, so it prints lying on its side
Y0, Y1 = -18.5, 16.5
def zb(z): return z + 217.0                    # height above the belt -> Fusion z
SENS_D = 75.0                                  # sensor beam to roller axis along the belt (was 60: loose yarn fur reached the beam)
prof = [box(XAX - 41, XAX - 31, Y0, Y1, zb(226.5), zb(229.5)),        # tab under the top plate (plate underside at 230)
        box(XAX - 41, XAX - 38, Y0, Y1, zb(226.5), zb(257))]          # upright, 1 mm in front of the plate's front edge
# arm: same underside height as before (board face 246.5 above the belt), 15 mm longer, its top tapering from 257 at the upright to 251.5 at
# the tip so it doesn't flex; still one x-z profile across the full width, so it prints lying on its side
arm = cq.Workplane('XZ').polyline([(XAX - 38, zb(248.1)), (XAX - SENS_D - 10, zb(248.1)), (XAX - SENS_D - 10, zb(251.5)), (XAX - 38, zb(257))]).close().extrude(-(Y1 - Y0)).val().translate(V(0, Y0, 0))
gus = cq.Workplane('XZ').polyline([(XAX - 41, zb(238)), (XAX - 41, zb(248.2)), (XAX - 51, zb(248.2))]).close().extrude(-(Y1 - Y0)).val().translate(V(0, Y0, 0))
BRACKET = prof[0].fuse(prof[1]).fuse(arm).fuse(gus).clean()
for yh in (-15.0, 13.0): BRACKET = BRACKET.cut(cz(XAX - 34, yh, zb(225), zb(231), 3.4))            # two screws up into the plate's blind holes
for yh in (-10.0, 10.0): BRACKET = BRACKET.cut(cz(XAX - SENS_D, yh, zb(247), zb(258), 3.4))        # board screws (M3 x 12 + nuts)
BOARD = box(XAX - SENS_D - 5.35, XAX - SENS_D + 5.35, -12.5, 12.5, zb(246.5), zb(248.1))

# ---- print files, each lying the way it prints
PR = os.path.join(OUT, 'print'); os.makedirs(PR, exist_ok=True)
def to_bed(s): b = s.BoundingBox(); return s.translate(V(-b.xmin, -b.ymin, -b.zmin))
real = lambda s: s.mirror('XZ')
prints = {
    'top-roller-bar x1': to_bed(real(BAR_LOCAL).rotate(V(0, 0, 0), V(1, 0, 0), -90)),           # lying on the flat its tip is flush with
    'top-roller-idler-end x1': to_bed(IDLER.rotate(V(0, 0, 0), V(1, 0, 0), 90)),               # plate on the bed, axle up
    'top-tof-bracket x1': to_bed(BRACKET.rotate(V(0, 0, 0), V(1, 0, 0), 90)),                  # lying on its side
}
rep = {}
for n, s in prints.items():
    cq.exporters.export(cq.Workplane().add(s), os.path.join(PR, n + '.stl'), tolerance=0.02, angularTolerance=0.1)
    cq.exporters.export(cq.Workplane().add(s), os.path.join(OUT, n.split(' ')[0] + '.step'))
    b = s.BoundingBox(); rep[n] = {'bed': [round(b.xlen, 1), round(b.ylen, 1), round(b.zlen, 1)], 'vol': round(s.Volume() / 1000, 1), 'valid': s.isValid(), 'solids': len(s.Solids())}
# the drive end and the tie discs are the same parts as on the side brushes
shutil.copy(os.path.join(SP, 'print', 'brush-core-top x2.stl'), os.path.join(PR, 'top-roller-drive-end x1 (same as brush-core-top).stl'))
shutil.copy(os.path.join(SP, 'print', 'tie-disc x30.stl'), os.path.join(PR, 'tie-disc x12 (same as the side brushes).stl'))
# ---- in-place STEPs for Fusion
FX = os.path.join(OUT, 'fusion'); os.makedirs(FX, exist_ok=True)
inplace = {'drive': DRIVE, 'bar': BAR, 'idler': IDLER, 'bearing': BEARING, 'bracket': BRACKET, 'board': BOARD, 'discs': cq.Compound.makeCompound(DISCS)}
for n, s in inplace.items(): cq.exporters.export(cq.Workplane().add(s), os.path.join(FX, n + '.step'))
print(json.dumps(rep, indent=1))
print('discs vs bar', round(sum(d.intersect(BAR).Volume() for d in DISCS), 3), ' bar vs drive', round(BAR.intersect(DRIVE).Volume(), 3), ' bar vs idler', round(BAR.intersect(IDLER).Volume(), 3))
