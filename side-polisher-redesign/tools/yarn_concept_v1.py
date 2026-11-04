# Proposal: chenille-yarn brush on the 3-part core. Printed tie discs stack on the hex bar between the two stoppers;
# each disc has 6 tie holes, one folded yarn strand per hole (lark's head), so 2 tails per hole. Visual only.
import sys, os, json, math, base64, array
os.chdir(r'F:\Research\ASPS\side-polisher-redesign'); sys.path.insert(0, os.getcwd())
sys.argv = ['cad_pincer9.py', 'x']
src = open('cad_pincer9.py', encoding='utf8').read().split('\ndef overlap')[0]
g = {'__file__': os.path.abspath('cad_pincer9.py'), '__name__': 'partial'}
exec(compile(src, 'cad_pincer9.py', 'exec'), g)
import cadquery as cq
V = cq.Vector
AX_D = g['AX_D']

HEX_AF = g['HEX_AF']
ZONE0, ZONE1 = g['BOT_DISC_Z1'], g['TOP_STOP_Z0']          # between the stoppers: z 28 .. 137
N_DISC = 15
PITCH = (ZONE1 - ZONE0 - 0.25) / N_DISC                  # 7.25 mm per disc, 0.25 mm slack in the stack
PLATE_T = 2.4
DISC_D = 33.0
COLLAR_D = 17.0                                           # spacer collar: keeps a gap between plates for the knots
HOLE_D, HOLE_R, N_HOLE = 5.0, 11.25, 6                    # tie holes: 5 mm (a folded 6 mm chenille strand squashes through)
BRUSH_R = 26.0                                            # yarn tips when spinning: 52 mm brush, 4 mm inside the arm legs (30 mm from the axis)

HOLE_ANG0 = 15.0                                          # holes 15 deg off the hex corners: flipping every other disc staggers them by 30 deg
def disc():
    # symmetric: plate in the middle, spacer collar on both faces, so a flipped disc stacks the same way
    c = PITCH / 2
    plate = cq.Solid.makeCylinder(DISC_D / 2, PLATE_T, V(0, 0, c - PLATE_T / 2), V(0, 0, 1))
    collar = cq.Solid.makeCylinder(COLLAR_D / 2, PITCH, V(0, 0, 0), V(0, 0, 1))
    sol = plate.fuse(collar).clean()
    hexhole = cq.Workplane('XY').workplane(offset=-1).polygon(6, (HEX_AF + 0.4) / 0.8660254).extrude(PITCH + 2).val()
    sol = sol.cut(hexhole)
    for k in range(N_HOLE):
        a = math.radians(HOLE_ANG0 + 360.0 / N_HOLE * k)
        x, y = HOLE_R * math.cos(a), HOLE_R * math.sin(a)
        sol = sol.cut(cq.Solid.makeCylinder(HOLE_D / 2, PITCH + 2, V(x, y, -1), V(0, 0, 1)))
        # 0.6 mm countersink on both faces, so the hole edges don't cut the yarn
        sol = sol.cut(cq.Solid.makeCone(HOLE_D / 2, HOLE_D / 2 + 0.8, 0.8, V(x, y, c + PLATE_T / 2 - 0.6), V(0, 0, 1)))
        sol = sol.cut(cq.Solid.makeCone(HOLE_D / 2, HOLE_D / 2 + 0.8, 0.8, V(x, y, c - PLATE_T / 2 + 0.6), V(0, 0, -1)))
    return sol.clean()
D = disc()
print('disc valid', D.isValid(), 'vol cm3', round(D.Volume() / 1000, 2), 'web outside holes', round(DISC_D / 2 - HOLE_R - HOLE_D / 2, 2),
      'wall hole-to-hex corner', round(HOLE_R - HOLE_D / 2 - (HEX_AF + 0.4) / 2 / 0.8660254, 2))

def mesh(s, tol=0.12, mirror=True):
    if mirror: s = s.mirror('XZ').translate(V(0, AX_D, 0))      # as on the real left arm, axis at y = 0
    pts = array.array('h')
    for f in s.Faces():
        vs, ts = f.tessellate(tol, 0.25)
        for t in ts:
            for k in t:
                v = vs[k]; pts.extend((int(round(v.x * 20)), int(round(v.y * 20)), int(round((v.z - 90) * 20))))
    return base64.b64encode(pts.tobytes()).decode()

cz = g['cz']
motor = cz(0, AX_D, g['CUP_Z0'] + g['CUP_FLOOR'], g['CUP_Z0'] + g['CUP_FLOOR'] + 40, 24.8)
bearing = cz(0, AX_D, g['BR_Z1'] - g['BEARING_W'], g['BR_Z1'], 22.0).cut(cz(0, AX_D, g['BR_Z1'] - 8, g['BR_Z1'] + 1, 8.0))
out = {'disc': mesh(D.translate(V(0, AX_D, 0)), 0.1),      # disc drawn at the axis, z from 0; the page stacks it
       'top': mesh(g['CORE_TOP']), 'bar': mesh(g['CORE_BAR']), 'bottom': mesh(g['CORE_BOT']),
       'arm': mesh(g['ARM'], 0.4), 'foot': mesh(g['FOOT'], 0.3), 'bearing': mesh(bearing, 0.2), 'motor': mesh(motor, 0.3)}
out['disc_z0'] = [round(ZONE0 + i * PITCH - 90, 3) for i in range(N_DISC)]   # page z of each disc's underside
out['spec'] = {'hole_ang0': HOLE_ANG0, 'n_disc': N_DISC, 'pitch': round(PITCH, 2), 'plate_t': PLATE_T, 'disc_d': DISC_D, 'collar_d': COLLAR_D, 'hole_d': HOLE_D, 'hole_r': HOLE_R,
               'n_hole': N_HOLE, 'brush_r': BRUSH_R, 'yarn_d': 6.0, 'disc_vol': round(D.Volume() / 1000, 2), 'leg_r': 30.0,
               'tail_len': round(BRUSH_R - HOLE_R, 1), 'strand_cut': round(2 * (BRUSH_R - HOLE_R) + 8, 0), 'zone': [ZONE0, ZONE1]}
p = r'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/yarn-brush/yarn-mesh.json'
os.makedirs(os.path.dirname(p), exist_ok=True)
json.dump(out, open(p, 'w'), separators=(',', ':'))
print(json.dumps(out['spec']), os.path.getsize(p))
# discs in place vs the arm / foot, and the 52 mm yarn envelope vs the arm legs
stack = cq.Compound.makeCompound([(D if i % 2 == 0 else D.rotate(V(0, 0, PITCH / 2), V(1, 0, PITCH / 2), 180)).translate(V(0, AX_D, ZONE0 + i * PITCH)) for i in range(N_DISC)])
env = cz(0, AX_D, ZONE0, ZONE1, 2 * BRUSH_R)
print('discs vs arm', round(stack.intersect(g['ARM']).Volume(), 2), ' vs foot', round(stack.intersect(g['FOOT']).Volume(), 2), ' vs bar', round(stack.intersect(g['CORE_BAR']).Volume(), 2))
print('52 mm yarn envelope vs arm', round(env.intersect(g['ARM']).Volume(), 1), ' vs foot', round(env.intersect(g['FOOT']).Volume(), 1))
print('closest arm point to the axis in the brush zone', round(min(v.toTuple()[0] ** 2 + (v.toTuple()[1] - AX_D) ** 2 for v in g['ARM'].intersect(g['box'](-60, 60, AX_D - 60, AX_D + 60, ZONE0, ZONE1)).Vertices()) ** 0.5, 1))
