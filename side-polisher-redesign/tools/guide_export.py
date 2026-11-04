# Export meshes for the assembly-guide page: every part, screw and nut of the left arm (plus context), in Fusion mm.
import sys, os, json, math, base64, array
os.chdir(r'F:\Research\ASPS\side-polisher-redesign'); sys.path.insert(0, os.getcwd())
sys.argv = ['cad_pincer9.py', 'x']
src = open('cad_pincer9.py', encoding='utf8').read().split('\ndef overlap')[0]
g = {'__file__': os.path.abspath('cad_pincer9.py'), '__name__': 'partial'}
exec(compile(src, 'cad_pincer9.py', 'exec'), g)
import cadquery as cq
import cad_ref
V = cq.Vector
cz, cy, cx, fuse, box = g['cz'], g['cy'], g['cx'], g['fuse'], g['box']
placeL, placeR, place_block = g['placeL'], g['placeR'], g['place_block']
it = g['assembly'](0)
AX_D = g['AX_D']

def mesh(s, tol=0.25):
    pts = array.array('h')
    for f in s.Faces():
        vs, ts = f.tessellate(tol, 0.4)
        for t in ts:
            for k in t:
                v = vs[k]; pts.extend((int(round(v.x * 10)), int(round(v.y * 10)), int(round(v.z * 10))))
    return base64.b64encode(pts.tobytes()).decode(), len(pts) // 9

def screw(p0, d, length, head=True):
    # button-head M3: shank from p0 along unit d, head on the p0 side
    d = V(*d).normalized(); p0 = V(*p0)
    sh = cq.Solid.makeCylinder(1.5, length, p0, d)
    hd = cq.Solid.makeCylinder(2.85, 1.65, p0 - d * 1.65, d)
    return sh.fuse(hd)
def nut(c, d):
    # M3 nut (5.5 across flats, 2.4 thick) centred on c, its axis along d
    d = V(*d).normalized(); c = V(*c)
    xd = V(1, 0, 0) if abs(d.x) < 0.9 else V(0, 0, 1)
    xd = (xd - d * xd.dot(d)).normalized()
    w = cq.Workplane(cq.Plane(origin=(c - d * 1.2).toTuple(), xDir=xd.toTuple(), normal=d.toTuple()))
    return w.polygon(6, 5.5 / 0.8660254).circle(1.5).extrude(2.4).val()

objs = []
def add(name, solid, kind, step, tol=0.25, frm=None, hidden=None, anim=None, label=None, group=None):
    m, n = mesh(solid, tol)
    o = {'name': name, 'kind': kind, 'step': step, 'm': m, 'n': n}
    if frm: o['from'] = frm
    if hidden: o['hidden'] = hidden
    if anim: o['anim'] = anim
    if label: o['label'] = label
    if group: o['group'] = group
    objs.append(o)

ARM_GROUP_HIDE = [9]           # the arm assembly is off the machine while the guide blocks go on
ARM_IN = {'10': [[0, 60, 0], [0, 0, 0]]}   # then it slides outward into the blocks
def armlike(extra=None):
    a = dict(ARM_IN)
    if extra: a.update(extra)
    return a

# ---- step 1: bearing into the foot bracket
add('foot', it['foot_L'], 'foot', 1, hidden=[2, 3, 9], anim=armlike({'4': [[0, 0, -45], [0, 0, 0]]}), label='Foot bracket')
add('bearing', it['bearing_L'], 'bearing', 1, frm=[0, 0, 28], hidden=[2, 3, 9], anim=armlike({'4': [[0, 0, -45], [0, 0, 0]]}), label='608ZZ bearing')
# ---- step 2: guide rails onto the arm frame
add('arm', it['arm_L'], 'arm', 2, hidden=ARM_GROUP_HIDE, anim=armlike(), label='Arm frame')
for i in (0, 1):
    add('rail%d' % i, it['rail_L%d' % i], 'rail', 2, frm=[0, -35, 0], hidden=ARM_GROUP_HIDE, anim=armlike(), label='Guide rail')
FL1 = g['FLANGE_D'][1]
for u in g['ROD_U']:
    for z in g['RAIL_BOLT_Z']:
        # local: head on the rail flange's outer face (d = 17), shank inward 16 mm; nut in the boss's inner-face pocket
        add('rs', placeL(screw((u, FL1, z), (0, -1, 0), 16)), 'screw', 2, tol=0.1, frm=[0, -22, 0], hidden=ARM_GROUP_HIDE, anim=armlike(), label='M3×16')
        add('rn', placeL(nut((u, g['ROD_D0'] + 0.2, z), (0, -1, 0))), 'nut', 2, tol=0.1, frm=[0, 14, 0], hidden=ARM_GROUP_HIDE, anim=armlike(), label='M3 nut')
# ---- step 3: brush core (turned so its screw hole faces the key hole) and the optional duster sleeve
core = it['core_L'].rotate(V(925, -85 - AX_D, 0), V(925, -85 - AX_D, 1), 90)
add('core', core, 'core', 3, frm=[0, 0, -70], hidden=ARM_GROUP_HIDE, anim=armlike(), label='Brush core')
add('sleeve', it['brush_L'], 'sleeve', 3, tol=0.6, frm=[0, 0, -70], hidden=ARM_GROUP_HIDE, anim=armlike(), label='Duster sleeve (optional)')
# ---- step 4: foot bracket (with its bearing) onto the arm legs
for s in (-1, 1):
    for z in (52, 66):
        add('fs', placeL(screw((s * 38, 8, z), (0, -1, 0), 12)), 'screw', 4, tol=0.1, frm=[0, -20, 0], hidden=ARM_GROUP_HIDE, anim=armlike(), label='M3×12')
        add('fn', placeL(nut((s * 38, g['D_IN'] + 0.2, z), (0, 1, 0))), 'nut', 4, tol=0.1, frm=[0, 14, 0], hidden=ARM_GROUP_HIDE, anim=armlike(), label='M3 nut')
# ---- step 5: ToF sensor bracket and board (left arm); the right arm gets the reflector
add('sensor', it['sensor_L'], 'sensor', 5, frm=[-28, 0, 0], hidden=ARM_GROUP_HIDE, anim=armlike(), label='Sensor bracket')
add('board', it['board_L'], 'board', 5, frm=[0, 18, 0], hidden=ARM_GROUP_HIDE, anim=armlike(), label='ToF board')
f = -g['LEG'][1]
for z in (22, 36):
    add('ss', placeL(screw((f - 5, g['SENSOR_HOLE_D'], z), (1, 0, 0), 12)), 'screw', 5, tol=0.1, frm=[-22, 0, 0], hidden=ARM_GROUP_HIDE, anim=armlike(), label='M3×12')
for dz in (-1, 1):
    add('bs', placeL(screw((g['SENSOR_U'], 5.5 - g['BOARD_T'], g['SENSOR_Z'] + dz * g['BOARD_HOLES'] / 2), (0, 1, 0), 8)), 'screw', 5, tol=0.1, frm=[0, 18, 0], hidden=ARM_GROUP_HIDE, anim=armlike(), label='M3×8 (or M2)')
# ---- step 6: motor and rack onto the carriage, on the bench (held 90 mm above its final place), then step 7 lowers it
UP = [0, 0, 90]
car_anim = armlike({'6': [UP, UP], '7': [UP, [0, 0, 0]]})
def car_anim_from(frm):
    return armlike({'6': [[UP[0] + frm[0], UP[1] + frm[1], UP[2] + frm[2]], UP], '7': [UP, [0, 0, 0]]})
add('carriage', it['carriage_L'], 'carriage', 6, hidden=ARM_GROUP_HIDE, anim=car_anim, label='Carriage')
add('motor', it['motor_L'], 'motor', 6, hidden=ARM_GROUP_HIDE, anim=car_anim_from([0, 0, 70]), label='Brush motor')
add('rack', it['rack_L'], 'rack', 6, tol=0.15, hidden=ARM_GROUP_HIDE, anim=car_anim_from([0, 0, 50]), label='Rack')
for (u, d) in g['PAD_BOLTS']:
    add('ps', placeL(screw((u, d, 219), (0, 0, 1), 16)), 'screw', 6, tol=0.1, hidden=ARM_GROUP_HIDE, anim=car_anim_from([0, 0, -22]), label='M3×16')
    add('pn', placeL(nut((u, d, 217 + 17 - 2.8 + 1.2), (0, 0, 1))), 'nut', 6, tol=0.1, hidden=ARM_GROUP_HIDE, anim=car_anim_from([0, 0, 16]), label='M3 nut')
# ---- step 7: carriage onto the arm columns
for (d, z) in g['LUG_BOLTS']:
    add('ls', placeL(screw((-55, d, z), (1, 0, 0), 20)), 'screw', 7, tol=0.1, frm=[-30, 0, 0], hidden=ARM_GROUP_HIDE, anim=armlike(), label='M3×20')
    add('ls', placeL(screw((57, d, z), (-1, 0, 0), 20)), 'screw', 7, tol=0.1, frm=[30, 0, 0], hidden=ARM_GROUP_HIDE, anim=armlike(), label='M3×20')
    add('ln', placeL(nut((-37.8, d, z), (1, 0, 0))), 'nut', 7, tol=0.1, frm=[0, 0, -16], hidden=ARM_GROUP_HIDE, anim=armlike(), label='M3 nut')
    add('ln', placeL(nut((37.8, d, z), (-1, 0, 0))), 'nut', 7, tol=0.1, frm=[0, 0, -16], hidden=ARM_GROUP_HIDE, anim=armlike(), label='M3 nut')
# ---- step 8: lock the core onto the motor shaft through the key hole (toward the belt)
GZ = g['CORE_Z1'] - g['GRUB_DOWN']
add('cs', placeL(screw((0, AX_D - 9.8, GZ), (0, 1, 0), 8)), 'screw', 8, tol=0.1, frm=[0, 26, 0], hidden=ARM_GROUP_HIDE, anim=armlike(), label='M3×8')
# ---- step 9: guide blocks and plates on the pillar flanges (both corners of this side)
FLB = g['FL_BOT']; BASE_Z = g['BASE_Z']
for i, u in enumerate(g['ROD_U']):
    rx = 925 + u; back = rx > 925
    add('block%d' % i, it['block_L%d' % i], 'block', 9, frm=[0, 0, 45], label='Guide block ' + ('A' if i == 0 else 'B'))
    add('clamp%d' % i, it['clamp_L%d' % i], 'clamp', 9, frm=[0, 0, -32], label='Flange clamp ' + ('A' if i == 0 else 'B'))
    for x, y, side in g['SCREWS']:
        add('ks', place_block(-1, back, rx, screw((x, y, FLB - g['PLATE_T']), (0, 0, 1), 12)), 'screw', 9, tol=0.1, frm=[0, 0, -32], label='M3×12')
        nz = BASE_Z + 1.5 + 1.4
        add('kn', place_block(-1, back, rx, nut((x, y, nz), (0, 0, 1))), 'nut', 9, tol=0.1, frm=[0, 16 * side, 0], label='M3 nut')
# ---- context (drawn faint) and the right side (overview only)
for n in ('pillarL_low', 'pillarL_up'):
    add(n, cad_ref.load(n), 'ctx', 0, tol=0.6, label='Pillar (yours, unchanged)')
add('belt', box(760, 1090, -66, 66, 205, 217), 'belt', 0, tol=1.0, label='Belt')
add('braces', g['BRACES'].intersect(box(760, 1090, -100, 100, 0, 400)), 'ctx', 0, tol=0.6, label='Belt brace (yours)')
RIGHT = [k for k in it if k.endswith('_R') or k.startswith(('rail_R', 'block_R', 'clamp_R'))]
for k in RIGHT:
    if k.startswith(('brush', 'board')): continue
    add('R_' + k, it[k], 'right', 11, tol=0.4, label='Right side (mirror image)')
for n in ('pillarR_low', 'pillarR_up'):
    add(n, cad_ref.load(n), 'ctx', 11, tol=0.6, label='Pillar (yours, unchanged)')
add('bracesR', g['BRACES_R'].intersect(box(760, 1090, -100, 100, 0, 400)), 'ctx', 11, tol=0.6, label='Belt brace (yours)')

out = r'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/guide-mesh.json'
json.dump(objs, open(out, 'w'), separators=(',', ':'))
print('objects', len(objs), 'triangles', sum(o['n'] for o in objs), 'bytes', os.path.getsize(out))
for k in sorted(set(o['kind'] for o in objs)): print(k, sum(o['n'] for o in objs if o['kind'] == k))
