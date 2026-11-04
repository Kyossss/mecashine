# Shoe carrier proposal v2 (not in Fusion): a 5 mm, 70 mm wide plate (two pieces) bolted to the belt with 2 x M4 through a slat gap into a
# clamp bar under the top run; a fixed 120 deg heel V-block; a 140 deg toe V-block pulled back against the toe by a rubber band (nothing to set per shoe). Frame: x along the belt (direction of travel), y across, z up from the belt top.
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

M4, M4_AF, M4_T = 4.4, 7.0, 3.2
GAP_X = 55.0                             # the belt gap the plate is bolted through (plate x); the carrier sits on the belt so a slat gap is here
def csk4(w, x, y, z_top):                # countersunk M4 from the top face
    w = w.cut(cq.Workplane('XY', origin=(0, 0, z_top - 30)).center(x, y).circle(M4 / 2).extrude(31))
    return w.cut(cq.Workplane('XY').add(cq.Solid.makeCone(2.2, 4.4, 2.2, cq.Vector(x, y, z_top - 2.2))))

# ---- rear plate with the heel V-block (fixed), bolted through a slat gap
REAR = (-10, 170)
rear = box(REAR[0], REAR[1], -W / 2, W / 2, 0, T)
rear = rear.cut(box(150, REAR[1] + 1, -W / 2 - 1, W / 2 + 1, T / 2, T + 1))                  # lap joint: the rear keeps the lower half
rear = rear.union(v_walls(0, +1, 60, 46, 3.0, 0, T + 18, 5))                                 # walls stand on the bed where they pass the plate's edge
rear = rear.cut(box(78, 140, -22, 22, -1, T + 1))                                            # lightening window
for y in (-14, 14): rear = csk4(rear, GAP_X, y, T)                                           # 2 x M4 down through the slat gap
for y in (-12, 12):
    rear = rear.cut(cq.Workplane('XY', origin=(0, 0, -1)).center(160, y).circle(M3 / 2).extrude(T + 2))
    rear = hexpocket(rear, 160, y, -0.01, NUT_T)                                             # joint nuts, open underneath (the belt keeps them in)

# ---- clamp bar under the top run: spans the gap, presses up on both slats; M4 nuts sit in pockets on its top face
SLAT_BOT = -10.0
clamp = box(GAP_X - 13, GAP_X + 13, -28, 28, SLAT_BOT - 6, SLAT_BOT)
for y in (-14, 14):
    clamp = clamp.cut(cq.Workplane('XY', origin=(0, 0, SLAT_BOT - 7)).center(GAP_X, y).circle(M4 / 2).extrude(8))
    clamp = clamp.cut(cq.Workplane('XY', origin=(0, 0, SLAT_BOT - M4_T - 0.2)).center(GAP_X, y).polygon(6, M4_AF / math.cos(math.pi / 6)).extrude(M4_T + 0.3))

# ---- front plate: lap joint over the rear one, an 8 mm slot for the toe block's key, a bridge to hook the band on, windows
FRONT = (150, 362)
front = box(FRONT[0], FRONT[1], -W / 2, W / 2, 0, T).cut(box(FRONT[0] - 1, 170, -W / 2 - 1, W / 2 + 1, -1, T / 2))
for y in (-12, 12): front = csk(front, 160, y, T)
SLOT = (238, 354)                         # key travel; the band hooks round the bridge left at x 230..234
front = front.cut(box(SLOT[0], SLOT[1], -4, 4, -1, T + 1)).cut(box(222, 230, -4, 4, -1, T + 1)).cut(box(229.9, 238.1, -4, 4, -1, 2.5))
front = front.cut(box(180, 218, -22, 22, -1, T + 1))
for y0, y1 in ((9, 26), (-26, -9)): front = front.cut(box(246, 350, y0, y1, -1, T + 1))

# ---- toe V-block: V walls, a boss with a pull tab, and a key in the slot with a hole for the band.
# Prints upside down on its wall and boss tops: everything else sits inside that footprint, so nothing overhangs.
def toe_block(ax):                       # ax = the toe V's inner corner
    v = v_walls(ax, -1, 70, 34, 3.0, T, T + 12, 3)
    b = v.union(box(ax, ax + 24, -7, 7, T, T + 12))                                          # boss and pull tab
    b = b.cut(cq.Workplane('XZ', origin=(0, 7.5, 0)).center(ax + 18, T + 14).circle(5).extrude(15))   # finger notch across the tab's top
    b = b.union(box(ax + 3, ax + 13, -3.6, 3.6, 0.6, T))                                     # key, rides in the slot
    return b.cut(cq.Workplane('XZ', origin=(0, 4, 0)).center(ax + 6, 2.6).circle(1.3).extrude(8))   # band hole through the key
def knob(ax): return None

def enc(w):
    vs, tris = w.val().tessellate(0.05, 0.3); pts = array.array('h')
    for t in tris:
        for i in t: v = vs[i]; pts.extend((int(round(v.x * 10)), int(round(v.y * 10)), int(round(v.z * 10))))
    return base64.b64encode(pts.tobytes()).decode()
FIT = json.load(open('F:/Research/ASPS/shoe-holder-proposal/fit.json'))
out = {'rear': enc(rear), 'front': enc(front), 'clamp': enc(clamp), 'toe': {}, 'fit': FIT, 'T': T, 'gapX': GAP_X}
for n in LEN:
    ax = FIT[n]['toeCorner']; out['toe'][n] = enc(toe_block(ax))
out['toeRest'] = enc(toe_block(SLOT[0] - 3))
json.dump(out, open('F:/Research/ASPS/shoe-holder-proposal/parts-mesh.json', 'w'))
for n, w in (('rear plate + heel V', rear), ('front plate', front), ('toe block', toe_block(335.3)), ('clamp bar', clamp)):
    b = w.val().BoundingBox(); print('%-20s %5.1f cm3  %.0f x %.0f x %.0f mm  valid %s' % (n, w.val().Volume() / 1000, b.xlen, b.ylen, b.zlen, w.val().isValid()))
