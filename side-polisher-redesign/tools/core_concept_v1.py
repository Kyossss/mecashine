# Concept model of the slim brush core (for a visual only; not written into cad_pincer9.py, Fusion or the print files).
import sys, os, json, math, base64, array
os.chdir(r'F:\Research\ASPS\side-polisher-redesign'); sys.path.insert(0, os.getcwd())
sys.argv = ['cad_pincer9.py', 'x']
src = open('cad_pincer9.py', encoding='utf8').read().split('\ndef overlap')[0]
g = {'__file__': os.path.abspath('cad_pincer9.py'), '__name__': 'partial'}
exec(compile(src, 'cad_pincer9.py', 'exec'), g)
import cadquery as cq
V = cq.Vector
AX_D, BR_Z1, BEARING_W = g['AX_D'], g['BR_Z1'], g['BEARING_W']
CORE_Z1, GRUB_DOWN = g['CORE_Z1'], g['GRUB_DOWN']
SHAFT_D, SHAFT_FLAT, SHAFT_DEPTH = g['SHAFT_D'], g['SHAFT_FLAT'], g['SHAFT_DEPTH']

# ---- concept dimensions (arm-local: u along the belt, d across, z above the belt; core axis at (0, AX_D))
HEX_AF = 12.0                 # rod, 12 mm across the flats
ROD_Z0, ROD_Z1 = 22.0, 137.0
SHOULDER_D, SHOULDER_Z0 = 16.0, BR_Z1 + 0.6     # round shoulder just above the bearing; the bottom washer rests on it
STUB_D = 7.95
STOP_D, STOP_T = 30.0, 3.0
HUB_D = 20.0
SCREW_Z = CORE_Z1 - GRUB_DOWN
MAT_Z0, MAT_Z1, MAT_D = ROD_Z0 + STOP_T, ROD_Z1, 50.0

def cz(x, y, z0, z1, d): return cq.Solid.makeCylinder(d / 2, z1 - z0, V(x, y, z0), V(0, 0, 1))
def hexz(af, z0, z1):
    return cq.Workplane('XY').polygon(6, af / 0.8660254).extrude(z1 - z0).val().translate(V(0, AX_D, z0))
def box(x0, x1, y0, y1, z0, z1): return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))

# core: stub + shoulder + hex rod + fixed top stopper + hub
ax0 = BR_Z1 - BEARING_W + 0.5
core = cz(0, AX_D, ax0, SHOULDER_Z0 + 0.1, STUB_D)
core = core.fuse(cz(0, AX_D, SHOULDER_Z0, ROD_Z0, SHOULDER_D))
core = core.fuse(hexz(HEX_AF, ROD_Z0 - 0.1, ROD_Z1 + 0.1))
core = core.fuse(cz(0, AX_D, ROD_Z1, ROD_Z1 + STOP_T, STOP_D))
core = core.fuse(cz(0, AX_D, ROD_Z1 + STOP_T - 0.1, CORE_Z1, HUB_D)).clean()
dhole = cz(0, AX_D, CORE_Z1 - SHAFT_DEPTH, CORE_Z1 + 1, SHAFT_D).cut(box(SHAFT_FLAT, 5, AX_D - 5, AX_D + 5, CORE_Z1 - SHAFT_DEPTH - 1, CORE_Z1 + 2))
screw_hole = cq.Solid.makeCylinder(1.7, HUB_D, V(0, AX_D, SCREW_Z), V(1, 0, 0))
NUT_U0 = 4.2                                  # nut slot: nut sits 4.2..6.8 mm out from the axis, dropped in from the hub's top face
nut_slot = box(NUT_U0, NUT_U0 + 2.6, AX_D - 3.0, AX_D + 3.0, SCREW_Z - 3.4, CORE_Z1 + 1)
core = core.cut(dhole).cut(screw_hole).cut(nut_slot)
# bottom washer: a hex hole that slides over the rod and rests on the shoulder
washer = cz(0, AX_D, ROD_Z0, ROD_Z0 + STOP_T, STOP_D).cut(hexz(HEX_AF + 0.4, ROD_Z0 - 1, ROD_Z0 + STOP_T + 1))
# hardware
def nut_x(u0):
    w = cq.Workplane(cq.Plane(origin=(u0, AX_D, SCREW_Z), xDir=(0, 0, 1), normal=(1, 0, 0)))
    return w.polygon(6, 5.5 / 0.8660254).circle(1.5).extrude(2.4).val()
nut = nut_x(NUT_U0 + 0.1)
screw = cq.Solid.makeCylinder(1.5, 8, V(1.8, AX_D, SCREW_Z), V(1, 0, 0)).fuse(cq.Solid.makeCylinder(2.85, 1.65, V(9.8, AX_D, SCREW_Z), V(1, 0, 0)))
# brush material stand-in (generic sleeve with a hex hole)
material = cz(0, AX_D, MAT_Z0 + 0.5, MAT_Z1 - 0.5, MAT_D).cut(hexz(HEX_AF + 0.6, MAT_Z0, MAT_Z1))
# motor shaft stand-in (D shaft going 15 mm into the hub) and the motor body above it
shaft = cz(0, AX_D, CORE_Z1 - SHAFT_DEPTH + 0.5, g['CUP_Z0'] + g['CUP_FLOOR'], 4.0).cut(box(1.75, 5, AX_D - 5, AX_D + 5, 0, 400))
motor = cz(0, AX_D, g['CUP_Z0'] + g['CUP_FLOOR'], g['CUP_Z0'] + g['CUP_FLOOR'] + 40, 24.8)
bearing = cz(0, AX_D, BR_Z1 - BEARING_W, BR_Z1, 22.0).cut(cz(0, AX_D, BR_Z1 - 8, BR_Z1 + 1, 8.0))

# current core, for comparison
old = g['CORE']

def mesh(s, tol=0.12):
    s = s.mirror('XZ').translate(V(0, AX_D, 0))     # as on the real left arm, axis at y = 0
    pts = array.array('h')
    for f in s.Faces():
        vs, ts = f.tessellate(tol, 0.25)
        for t in ts:
            for k in t:
                v = vs[k]; pts.extend((int(round(v.x * 20)), int(round(v.y * 20)), int(round((v.z - 90) * 20))))
    return base64.b64encode(pts.tobytes()).decode()

out = {
  'core': mesh(core), 'washer': mesh(washer), 'nut': mesh(nut, 0.05), 'screw': mesh(screw, 0.05),
  'material': mesh(material, 0.3), 'shaft': mesh(shaft, 0.1), 'motor': mesh(motor, 0.3), 'bearing': mesh(bearing, 0.2),
  'arm': mesh(g['ARM'], 0.4), 'foot': mesh(g['FOOT'], 0.3), 'old': mesh(old, 0.2),
}
dims = {'hex_af': HEX_AF, 'rod_len': ROD_Z1 - ROD_Z0, 'stop_d': STOP_D, 'stop_t': STOP_T, 'hub_d': HUB_D, 'material_len': MAT_Z1 - MAT_Z0,
        'core_len': CORE_Z1 - ax0, 'core_vol_cm3': round(core.Volume() / 1000, 1), 'washer_vol_cm3': round(washer.Volume() / 1000, 1),
        'old_vol_cm3': round(old.Volume() / 1000, 1), 'screw_head_r': 11.45, 'ring_r': g['TIE_HOLE_D'] / 2, 'valid': core.isValid()}
out['dims'] = dims
p = r'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/core-concept/core-mesh.json'
os.makedirs(os.path.dirname(p), exist_ok=True)
json.dump(out, open(p, 'w'), separators=(',', ':'))
print(json.dumps(dims), os.path.getsize(p))
# does the concept fit? core + washer + material against the arm and foot (local, as built)
for n, s in (('core', core), ('washer', washer), ('material', material), ('screw head', screw)):
    print(n, 'vs arm', round(s.intersect(g['ARM']).Volume(), 2), 'vs foot', round(s.intersect(g['FOOT']).Volume(), 2))
