# Shoe carrier proposal (not in Fusion): a 5 mm, 70 mm wide plate on the belt (two pieces), a fixed 120 deg heel V-block and a sliding
# 140 deg toe V-block with a thumb screw. Frame: x along the belt (direction of travel), y across, z up from the belt top.
# The heel V's inner corner is at x 0. Each shoe size rests where fit.json says (worked out from the shoe mesh).
# Writes parts-mesh.json for the proposal page and reports sizes and bed fit.
import cadquery as cq, math, json, base64, array
T = 5.0                                  # plate thickness
W = 70.0                                 # plate width (the sole rests on it)
M3, NUT_AF, NUT_T = 3.4, 5.7, 2.6
LEN = {'Small': 250, 'Medium': 290, 'Large': 330}
def box(x0, x1, y0, y1, z0, z1): return cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0).translate(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
def csk(w, x, y, z_top):                 # countersunk M3 from the top face
    w = w.cut(cq.Workplane('XY', origin=(0, 0, z_top - 30)).center(x, y).circle(M3 / 2).extrude(31))
    return w.cut(cq.Workplane('XY').add(cq.Solid.makeCone(1.7, 3.4, 1.7, cq.Vector(x, y, z_top - 1.7))))
def hexpocket(w, x, y, z0, depth):
    return w.cut(cq.Workplane('XY', origin=(0, 0, z0)).center(x, y).polygon(6, NUT_AF / math.cos(math.pi / 6)).extrude(depth))
def v_walls(apex_x, opening, half_angle_deg, arm, wall, z0, z1, back):
    # two walls whose inner faces meet at (apex_x, 0); opening = +1 (opens toward +x) or -1; back = material behind the corner
    a = math.radians(half_angle_deg); out = None
    for s in (1, -1):
        dx, dy = opening * math.cos(a), s * math.sin(a)
        nx, ny = (-dy, dx) if dx * s > 0 else (dy, -dx)   # outward normal of the inner face: away from the V's axis
        if ny * s < 0: nx, ny = -nx, -ny
        p0 = (apex_x, 0); p1 = (apex_x + dx * arm, dy * arm)
        q1 = (p1[0] + nx * wall, p1[1] + ny * wall); q0 = (apex_x - opening * back, 0)
        w = cq.Workplane('XY', origin=(0, 0, z0)).polyline([p0, p1, q1, q0]).close().extrude(z1 - z0)
        out = w if out is None else out.union(w)
    return out

# ---- rear plate with the heel V-block (fixed), bolted to one belt slat
REAR = (-10, 170)
rear = box(REAR[0], REAR[1], -W / 2, W / 2, 0, T)
rear = rear.cut(box(150, REAR[1] + 1, -W / 2 - 1, W / 2 + 1, T / 2, T + 1))                  # lap joint: the rear keeps the lower half
rear = rear.union(v_walls(0, +1, 60, 46, 3.0, 0, T + 18, 5))                                 # walls stand on the bed where they pass the plate's edge
rear = rear.cut(box(78, 140, -22, 22, -1, T + 1))                                            # lightening window
for y in (-12, 12):
    rear = csk(rear, 55, y, T)                                                               # 2 x M3 into one belt slat (nut under the slat)
    rear = rear.cut(cq.Workplane('XY', origin=(0, 0, -1)).center(160, y).circle(M3 / 2).extrude(T + 2))
    rear = hexpocket(rear, 160, y, -0.01, NUT_T)                                             # joint nuts, open underneath (the belt keeps them in)

# ---- front plate: lap joint over the rear one, a slot for the toe block with a nut channel underneath, windows
FRONT = (150, 354)
front = box(FRONT[0], FRONT[1], -W / 2, W / 2, 0, T).cut(box(FRONT[0] - 1, 170, -W / 2 - 1, W / 2 + 1, -1, T / 2))
for y in (-12, 12): front = csk(front, 160, y, T)
SLOT = (246, 350)
front = front.cut(cq.Workplane('XY', origin=(0, 0, -1)).center((SLOT[0] + SLOT[1]) / 2, 0).slot2D(SLOT[1] - SLOT[0], M3, 0).extrude(T + 2))
front = front.cut(box(SLOT[0] - 3, SLOT[1] + 3, -NUT_AF / 2 - 0.2, NUT_AF / 2 + 0.2, -0.01, NUT_T + 0.2))   # the hex nut slides in this channel
front = front.cut(box(180, 236, -22, 22, -1, T + 1))
for y0, y1 in ((9, 26), (-26, -9)): front = front.cut(box(252, 344, y0, y1, -1, T + 1))

# ---- toe V-block: V walls with a screw boss at the corner and a key under the boss that rides in the slot.
# Prints upside down on its wall tops: everything sits inside the walls' and boss's footprint, so nothing overhangs.
def toe_block(ax):                       # ax = the toe V's inner corner
    v = v_walls(ax, -1, 70, 34, 3.0, T, T + 12, 3)
    b = v.union(box(ax, ax + 14, -7, 7, T, T + 12)).union(box(ax + 2, ax + 12, -1.5, 1.5, T - 2, T))
    return b.cut(cq.Workplane('XY', origin=(0, 0, T - 3)).center(ax + 7, 0).circle(M3 / 2).extrude(20))
def knob(ax):                            # thumb knob: an M3 x 20 socket head sits in it from the top, the screw goes down into the nut in the plate
    k = cq.Workplane('XY', origin=(0, 0, T + 12)).center(ax + 7, 0).polygon(8, 15).extrude(7)
    k = k.cut(cq.Workplane('XY', origin=(0, 0, T + 15)).center(ax + 7, 0).circle(2.9).extrude(5))
    return k.cut(cq.Workplane('XY', origin=(0, 0, T + 11)).center(ax + 7, 0).circle(M3 / 2).extrude(9))

def enc(w):
    vs, tris = w.val().tessellate(0.05, 0.3); pts = array.array('h')
    for t in tris:
        for i in t: v = vs[i]; pts.extend((int(round(v.x * 10)), int(round(v.y * 10)), int(round(v.z * 10))))
    return base64.b64encode(pts.tobytes()).decode()
FIT = json.load(open('F:/Research/ASPS/shoe-holder-proposal/fit.json'))
out = {'rear': enc(rear), 'front': enc(front), 'toe': {}, 'knob': {}, 'fit': FIT, 'T': T}
for n in LEN:
    ax = FIT[n]['toeCorner']; out['toe'][n] = enc(toe_block(ax)); out['knob'][n] = enc(knob(ax))
json.dump(out, open('F:/Research/ASPS/shoe-holder-proposal/parts-mesh.json', 'w'))
for n, w in (('rear plate + heel V', rear), ('front plate', front), ('toe block', toe_block(335.3)), ('knob', knob(335.3))):
    b = w.val().BoundingBox(); print('%-20s %5.1f cm3  %.0f x %.0f x %.0f mm  valid %s' % (n, w.val().Volume() / 1000, b.xlen, b.ylen, b.zlen, w.val().isValid()))
