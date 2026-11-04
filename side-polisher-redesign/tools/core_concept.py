# Concept model of the slim 3-part brush core (for a visual only; not written into cad_pincer9.py, Fusion or the print files).
# Top: hub (your D-shaped shaft hole, captive-nut M3x8 on the flat), fixed top stopper, hex socket held to the bar by an M3x20 cross screw.
# Middle: a plain 12 mm hex bar. Bottom: stopper disc with a hex socket, shoulder and the 8 mm axle into the 608ZZ.
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
HEX_AF = 12.0
STOP_D = 22.0                                   # both stoppers: 5 mm past the 12 mm bar all round
HUB_D = 16.0                                    # slimmest hub that holds the shaft screw's captive nut
TOP_STOP_Z0, TOP_STOP_Z1 = 137.0, 140.0          # fixed top stopper
TOP_SOCK_Z1 = CORE_Z1 - SHAFT_DEPTH - 1.0       # top socket stops 1 mm under the shaft hole (z 148)
BOT_SHOULDER_Z0 = BR_Z1 + 0.6                   # round shoulder just above the bearing
BOT_DISC_Z0, BOT_DISC_Z1 = 21.0, 28.0           # bottom stopper disc, 7 mm thick
BOT_SOCK_Z0 = 22.0                              # bottom socket floor
BAR_Z0, BAR_Z1 = BOT_SOCK_Z0 + 0.5, TOP_SOCK_Z1 - 0.5
SCREW_Z = CORE_Z1 - GRUB_DOWN                   # shaft screw height, as on your current core
CROSS_Z = TOP_STOP_Z0 + 5.5                     # cross screw through the hub and the bar's tip
TIP_AF, TIP_OFF = 8.0, -2.0                     # bar's top end: an 8 mm hex tip, set 2 mm off-centre so one flat is flush with a bar flat (prints flat)
TIP_Z0 = TOP_STOP_Z0                            # the bar's shoulder butts against the top stopper
FIT_TOP, FIT_BOT = 0.25, 0.4                    # hex clearance: snug at the top, loose at the bottom
MAT_Z0, MAT_Z1, MAT_D = BOT_DISC_Z1, TOP_STOP_Z0, 50.0
NUT_AF, NUT_T, M3 = 5.8, 2.4, 3.4

def cz(x, y, z0, z1, d): return cq.Solid.makeCylinder(d / 2, z1 - z0, V(x, y, z0), V(0, 0, 1))
def hexz(af, z0, z1):
    return cq.Workplane('XY').polygon(6, af / 0.8660254).extrude(z1 - z0).val().translate(V(0, AX_D, z0))   # flats face +-d
def box(x0, x1, y0, y1, z0, z1): return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))
def nut_on(axis_pt, normal, xdir):
    w = cq.Workplane(cq.Plane(origin=axis_pt, xDir=xdir, normal=normal))
    return w.polygon(6, 5.5 / 0.8660254).circle(1.5).extrude(2.4).val()

# ---- top part
top = cz(0, AX_D, TOP_STOP_Z0, TOP_STOP_Z1, STOP_D).fuse(cz(0, AX_D, TOP_STOP_Z1 - 0.1, CORE_Z1, HUB_D)).clean()
dhole = cz(0, AX_D, CORE_Z1 - SHAFT_DEPTH, CORE_Z1 + 1, SHAFT_D).cut(box(SHAFT_FLAT, 5, AX_D - 5, AX_D + 5, CORE_Z1 - SHAFT_DEPTH - 1, CORE_Z1 + 2))
def hexz_at(af, d0, z0, z1):
    return cq.Workplane('XY').polygon(6, af / 0.8660254).extrude(z1 - z0).val().translate(V(0, AX_D + d0, z0))
socket = hexz_at(TIP_AF + 2 * FIT_TOP, TIP_OFF, TOP_STOP_Z0 - 1, TOP_SOCK_Z1)
# shaft screw along +u: M3x8 tip on the flat (1.8 from the axis), head seat recessed to 9.8 from the axis
shaft_hole = cq.Solid.makeCylinder(M3 / 2, HUB_D, V(0, AX_D, SCREW_Z), V(1, 0, 0))
shaft_seat = cq.Solid.makeCylinder(3.25, HUB_D, V(9.8, AX_D, SCREW_Z), V(1, 0, 0))
NUT_U0 = 3.2                                    # nut 3.3..5.7 mm out: 1.4 mm of plastic to the shaft's flat, about 1.5 mm to the hub surface
shaft_nut_slot = box(NUT_U0, NUT_U0 + 2.6, AX_D - 3.0, AX_D + 3.0, SCREW_Z - 3.4, CORE_Z1 + 1)   # nut dropped in from the top face
# cross screw along d through the hub and the bar's flats: M3x20, head recessed 2 mm on one side, nut in a pocket on the other
CROSS_D = AX_D + TIP_OFF
cross_hole = cq.Solid.makeCylinder(M3 / 2, HUB_D + 2, V(-HUB_D / 2 - 1, CROSS_D, CROSS_Z), V(1, 0, 0))
HEAD_U = 7.5                                    # head seat, just under the hub surface on this chord
cross_seat = cq.Solid.makeCylinder(3.25, 3, V(HEAD_U, CROSS_D, CROSS_Z), V(1, 0, 0))
NUT_U1 = -(TIP_AF / 2 / 0.8660254 + FIT_TOP) - 0.3    # nut pocket starts just outside the tip's corner
cross_nut_pocket = cq.Workplane(cq.Plane(origin=(-HUB_D / 2 - 1, CROSS_D, CROSS_Z), xDir=(0, 0, 1), normal=(1, 0, 0))).polygon(6, NUT_AF / 0.8660254).extrude(HUB_D / 2 + 1 + NUT_U1).val()
top = top.cut(dhole).cut(socket).cut(shaft_hole).cut(shaft_seat).cut(shaft_nut_slot).cut(cross_hole).cut(cross_seat).cut(cross_nut_pocket)

# ---- middle bar
bar = cq.Workplane().add(hexz(HEX_AF, BAR_Z0, TIP_Z0)).edges('|Z').fillet(0.6).val()
bar = bar.fuse(hexz_at(TIP_AF, TIP_OFF, TIP_Z0 - 0.1, BAR_Z1)).clean()
bar = bar.cut(cq.Solid.makeCylinder(M3 / 2, 20, V(-10, CROSS_D, CROSS_Z), V(1, 0, 0)))

# ---- bottom part
ax0 = BR_Z1 - BEARING_W + 0.5
bot = cz(0, AX_D, ax0, BOT_SHOULDER_Z0 + 0.1, 7.95).fuse(cz(0, AX_D, BOT_SHOULDER_Z0, BOT_DISC_Z0 + 0.1, 16.0)).fuse(cz(0, AX_D, BOT_DISC_Z0, BOT_DISC_Z1, STOP_D)).clean()
bot = bot.cut(hexz(HEX_AF + 2 * FIT_BOT, BOT_SOCK_Z0, BOT_DISC_Z1 + 1))

# ---- hardware
shaft_screw = cq.Solid.makeCylinder(1.5, 8, V(1.8, AX_D, SCREW_Z), V(1, 0, 0)).fuse(cq.Solid.makeCylinder(2.85, 1.65, V(9.8, AX_D, SCREW_Z), V(1, 0, 0)))
shaft_nut = nut_on((NUT_U0 + 0.1, AX_D, SCREW_Z), (1, 0, 0), (0, 0, 1))
cross_screw = cq.Solid.makeCylinder(1.5, 16, V(HEAD_U, CROSS_D, CROSS_Z), V(-1, 0, 0)).fuse(cq.Solid.makeCylinder(2.85, 1.65, V(HEAD_U, CROSS_D, CROSS_Z), V(1, 0, 0)))   # M3x16
cross_nut = nut_on((NUT_U1 - 0.1 - 2.4, CROSS_D, CROSS_Z), (1, 0, 0), (0, 0, 1))
material = cz(0, AX_D, MAT_Z0 + 0.5, MAT_Z1 - 0.5, MAT_D).cut(hexz(HEX_AF + 0.6, MAT_Z0, MAT_Z1))
shaft = cz(0, AX_D, CORE_Z1 - SHAFT_DEPTH + 0.5, g['CUP_Z0'] + g['CUP_FLOOR'], 4.0).cut(box(1.75, 5, AX_D - 5, AX_D + 5, 0, 400))
motor = cz(0, AX_D, g['CUP_Z0'] + g['CUP_FLOOR'], g['CUP_Z0'] + g['CUP_FLOOR'] + 40, 24.8)
bearing = cz(0, AX_D, BR_Z1 - BEARING_W, BR_Z1, 22.0).cut(cz(0, AX_D, BR_Z1 - 8, BR_Z1 + 1, 8.0))
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

out = {'top': mesh(top), 'bar': mesh(bar), 'bottom': mesh(bot), 'snut': mesh(shaft_nut, 0.05), 'sscrew': mesh(shaft_screw, 0.05),
       'cnut': mesh(cross_nut, 0.05), 'cscrew': mesh(cross_screw, 0.05), 'material': mesh(material, 0.3), 'shaft': mesh(shaft, 0.1),
       'motor': mesh(motor, 0.3), 'bearing': mesh(bearing, 0.2), 'arm': mesh(g['ARM'], 0.4), 'foot': mesh(g['FOOT'], 0.3), 'old': mesh(old, 0.2)}
vol = lambda s: round(s.Volume() / 1000, 1)
dims = {'hex_af': HEX_AF, 'bar_len': round(BAR_Z1 - BAR_Z0, 1), 'stop_d': STOP_D, 'hub_d': HUB_D, 'top_len': round(CORE_Z1 - TOP_STOP_Z0, 1),
        'bot_len': round(BOT_DISC_Z1 - ax0, 1), 'material_len': MAT_Z1 - MAT_Z0, 'top_sock': round(TOP_SOCK_Z1 - TOP_STOP_Z0, 1), 'bot_sock': BOT_DISC_Z1 - BOT_SOCK_Z0,
        'vol_top': vol(top), 'vol_bar': vol(bar), 'vol_bot': vol(bot), 'vol_old': vol(old), 'core_len': round(CORE_Z1 - ax0, 1),
        'valid': [top.isValid(), bar.isValid(), bot.isValid()], 'solids': [len(top.Solids()), len(bar.Solids()), len(bot.Solids())]}
out['dims'] = dims
p = r'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/core-concept/core-mesh.json'
json.dump(out, open(p, 'w'), separators=(',', ':'))
print(json.dumps(dims), os.path.getsize(p))
# fit checks: parts against the arm and foot, hardware inside its holes, screws vs the bar's hex and each other
for n, s in (('top', top), ('bar', bar), ('bottom', bot), ('material', material), ('shaft screw', shaft_screw), ('cross screw', cross_screw)):
    print(n.ljust(12), 'vs arm', round(s.intersect(g['ARM']).Volume(), 2), ' vs foot', round(s.intersect(g['FOOT']).Volume(), 2))
for n, s in (('shaft screw', shaft_screw), ('shaft nut', shaft_nut), ('cross screw', cross_screw), ('cross nut', cross_nut)):
    print(n.ljust(12), 'vs top', round(s.intersect(top).Volume(), 3), ' vs bar', round(s.intersect(bar).Volume(), 3))
print('bar vs top', round(bar.intersect(top).Volume(), 3), ' bar vs bottom', round(bar.intersect(bot).Volume(), 3), ' shaft vs top', round(shaft.intersect(top).Volume(), 3))
nb = cross_nut.BoundingBox()
print('cross nut u', round(nb.xmin, 2), '..', round(nb.xmax, 2), ' screw tip at', round(HEAD_U - 16, 2), '-> passes the nut by', round(nb.xmin - (HEAD_U - 16), 2), 'mm;  hub surface on that chord at u', round(-math.sqrt((HUB_D / 2) ** 2 - TIP_OFF ** 2), 2))
print('hub radius', HUB_D / 2, ' ring radius', g['TIE_HOLE_D'] / 2)
