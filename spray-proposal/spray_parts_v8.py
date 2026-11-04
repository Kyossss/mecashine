# Spray proposal v8 (2026-11-03, not in Fusion): the post you printed (spray station v4: profile lying on its inner face, gussets to that face,
# base plate, IR teardrop holes), changed: elbow 25 mm higher, nozzle 25 deg down (was 15), base plate ends at |y| 140 (was 150) so the
# box-side post clears the casing box (80 mm from the belt frame), IR shelf on the box side (+y, left as you look in from the entrance).
# Page frame: x = CAD x - 780, y across, z above the belt top (board top z -88). Writes parts-mesh.json for spray.html.
import cadquery as cq, math, json, base64, array
V = cq.Vector
AX = -100.0
TILT = math.radians(25)
T0, T1 = AX - 5, AX + 5
C_X, C_Y, C_Z = T1 + 6.75, 110.0, 83.0
Y_OUT = 140.0                                    # base plate outer edge (was 150)
def at(ua, ub):
    return (C_Y - math.cos(TILT) * ua + math.sin(TILT) * ub, C_Z - math.sin(TILT) * ua - math.cos(TILT) * ub)
LUG = at(8.8, 9.4)
M3, NUT_AF, NUT_T = 3.4, 5.7, 2.6
def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0).translate(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
IR_HOLES_Z = (-9, -3, 3, 9, 15, 21, 27, 33)
BASE = dict(x0=AX - 20, x1=AX + 20, y0=92, y1=Y_OUT, z1=-80)
ZTOP = C_Z + 8
def post():
    prof = [(92, -88), (Y_OUT, -88), (Y_OUT, -80), (122, -80), (118, -40), (118, ZTOP), (92, ZTOP)]
    p = cq.Workplane('YZ', origin=(T0, 0, 0)).polyline(prof).close().extrude(T1 - T0)
    p = p.union(box(BASE['x0'], BASE['x1'], BASE['y0'], BASE['y1'], -88, BASE['z1']))
    for xa, xb in ((T0, T0 - 5), (T1, T1 + 5)):
        g = cq.Workplane('XZ', origin=(0, 118, 0)).polyline([(xa, BASE['z1']), (xb, BASE['z1']), (xa, BASE['z1'] + 35)]).close().extrude(26)
        p = p.union(g)
    p1 = at(13, 5.6); t = (p1[0] - 92) / math.cos(TILT); p2 = (92, p1[1] - t * math.sin(TILT)); zs = C_Z - 25
    seat = [p1, p2, (92, zs), (p1[0] + 2, zs)]
    p = p.union(cq.Workplane('YZ', origin=(T1, 0, 0)).polyline(seat).close().extrude(7))
    p = p.cut(cq.Workplane('YZ', origin=(T0 - 1, 0, 0)).center(*LUG).circle(M3 / 2).extrude(T1 - T0 + 2))
    R = NUT_AF / math.sqrt(3)
    hexpts = [(LUG[0] + R * math.cos(math.radians(60 * i)), LUG[1] + R * math.sin(math.radians(60 * i))) for i in range(6)]
    p = p.cut(cq.Workplane('YZ', origin=(T0 - 0.01, 0, 0)).polyline(hexpts).close().extrude(NUT_T + 0.4))
    r = M3 / 2; k = r / math.sqrt(2)
    for zh in IR_HOLES_Z:
        p = p.cut(cq.Workplane('YZ', origin=(T0 - 1, 0, 0)).center(101, zh).circle(r).extrude(T1 - T0 + 2))
        p = p.cut(cq.Workplane('YZ', origin=(T0 - 1, 0, 0)).polyline([(101 + k, zh - k), (101 + r * math.sqrt(2), zh), (101 + k, zh + k), (101, zh)]).close().extrude(T1 - T0 + 2))
    SL = 30.0                                    # board slots along y, y 101..131 (centres)
    for xh in (BASE['x0'] + 5, BASE['x1'] - 5):
        p = p.cut(cq.Workplane('XY', origin=(0, 0, -89)).center(xh, 116).slot2D(SL + M3, M3, 90).extrude(9))
    try: p = p.edges('|Z').fillet(0.8)
    except Exception: pass
    return p
def ir_shelf():                                  # drawn for -y as before, then mirrored to the box side
    s = box(T0 - 4, T0, -112, -92, 10, 36).union(box(AX - 40, T0, -112, -66, 33, 36))
    s = s.union(cq.Workplane('XZ', origin=(0, -100, 0)).polyline([(T0 - 4, 33), (T0 - 16, 33), (T0 - 4, 18)]).close().extrude(3, both=True))
    s = s.cut(cq.Workplane('YZ', origin=(T0 - 5, 0, 0)).center(-101, 15).circle(M3 / 2).extrude(6))
    s = s.cut(cq.Workplane('XY', origin=(0, 0, 32)).center(AX - 26, -98).slot2D(12 + M3, M3, 90).extrude(5))
    for xz in (AX - 36, AX - 16):
        s = s.cut(box(xz - 1, xz + 1, -84, -80, 32, 37))
    try: s = s.edges('|Z').fillet(0.6)
    except Exception: pass
    return s.mirror('XZ')
def enc(w):
    vs, tris = w.val().tessellate(0.08, 0.3); pts = array.array('h')
    for t in tris:
        for i in t: v = vs[i]; pts.extend((int(round(v.x * 10)), int(round(v.y * 10)), int(round(v.z * 10))))
    return base64.b64encode(pts.tobytes()).decode()
PP = post(); PN = PP.mirror('XZ'); IR = ir_shelf()
# printed lying on the inner face: check overhangs facing down in that orientation
s = PP.val().rotate(V(0, 0, 0), V(1, 0, 0), 90); b = s.BoundingBox()
down = sum(f.Area() for f in s.Faces() if f.geomType() == 'PLANE' and f.normalAt().z < -0.72 and f.Center().z > b.zmin + 0.2)
for n, w in (('post', PP), ('ir shelf', IR)):
    bb = w.val().BoundingBox(); print(n, 'vol %.1f cm3' % (w.val().Volume() / 1000), 'x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f' % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax), 'valid', w.val().isValid())
print('print bed %.0f x %.0f x %.0f, flat down-facing area above the bed %.1f mm2' % (b.xlen, b.ylen, b.zlen, down))
print('post x IR shelf overlap %.2f mm3' % PP.intersect(IR).val().Volume())
tip = (C_Y - math.cos(TILT) * 32.5, C_Z - math.sin(TILT) * 32.5); print('lug y %.1f z %.1f; nozzle tip y %.1f z %.1f' % (LUG + tip))
for hw in (40, 45, 50):
    d = tip[0] - hw; print('side at |y| %d: axis z %.1f, band z %.1f..%.1f' % (hw, tip[1] - d * math.tan(TILT), tip[1] - d * math.tan(TILT + math.radians(30)), tip[1] - d * math.tan(TILT - math.radians(30))))
json.dump({'postPos': enc(PP), 'postNeg': enc(PN), 'irShelf': enc(IR)}, open('F:/Research/ASPS/spray-proposal/parts-mesh.json', 'w'))
