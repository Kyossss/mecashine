# Spray station (approved 2026-10-26): two nozzle posts on the base board just before the reflector, the elbows bolted through their lugs,
# a universal IR sensor shelf on the far post. Writes print STLs (oriented for the bed, no supports) and in-place STEPs for Fusion.
# Built in the proposal frame (x = CAD x - 780, z above the belt top, board top at z -88), then moved to Fusion (x + 780, z + 217).
import cadquery as cq, math, os, json
V = cq.Vector
OUT = os.path.dirname(os.path.abspath(__file__))
AX = -100.0                      # spray position, CAD x 680
TILT = math.radians(15)
T0, T1 = AX - 5, AX + 5                        # post thickness along the belt (upstream face on the bed when printing)
C_X, C_Y, C_Z = T1 + 6.75, 110.0, 58.0          # elbow bend point on the box (+y) side; the elbow's back rests on the post's downstream face
def at(ua, ub):                  # + side elbow: ua along the side port (across the belt, 15 deg down), ub along the down port
    return (C_Y - math.cos(TILT) * ua + math.sin(TILT) * ub, C_Z - math.sin(TILT) * ua - math.cos(TILT) * ub)
LUG = at(8.8, 9.4)
M3, NUT_AF, NUT_T = 3.4, 5.7, 2.6

def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0).translate(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))

IR_HOLES_Z = (-9, -3, 3, 9, 15, 21, 27, 33)                    # IR shelf screw heights; the shelf is drawn on z 15
BASE = dict(x0=AX - 20, x1=AX + 20, y0=92, y1=150, z1=-80)      # the user's base plate: CAD x 660..700, out to |y| 150, 8 mm thick
def post():
    # profile seen along the belt: upright to the elbow and the outer gusset, 10 mm thick along the belt
    prof = [(92, -88), (150, -88), (150, -80), (122, -80), (118, -40), (118, 66), (92, 66)]
    p = cq.Workplane('YZ', origin=(T0, 0, 0)).polyline(prof).close().extrude(T1 - T0)
    p = p.union(box(BASE['x0'], BASE['x1'], BASE['y0'], BASE['y1'], -88, BASE['z1']))
    # gussets along the belt, both faces, 45 deg so they print standing
    for xa, xb in ((T0, T0 - 5), (T1, T1 + 5)):     # 5 mm out, 35 mm up: steep, so it prints standing; the plate's slots stay clear of it
        g = cq.Workplane('XZ', origin=(0, 118, 0)).polyline([(xa, BASE['z1']), (xb, BASE['z1']), (xa, BASE['z1'] + 35)]).close().extrude(26)   # y 118 -> 92, flush with the inner face (the print bed)
        p = p.union(g)
    # 15 deg seat under the elbow's side port, reaching down to the inner face so it stands on the bed
    p1 = at(13, 5.6); t = (p1[0] - 92) / math.cos(TILT); p2 = (92, p1[1] - t * math.sin(TILT))
    seat = [p1, p2, (92, 33), (p1[0] + 2, 33)]
    p = p.union(cq.Workplane('YZ', origin=(T1, 0, 0)).polyline(seat).close().extrude(7))
    # elbow screw through the post; nut pocket on the upstream face with a corner at the top (no flat roof)
    p = p.cut(cq.Workplane('YZ', origin=(T0 - 1, 0, 0)).center(*LUG).circle(M3 / 2).extrude(T1 - T0 + 2))
    R = NUT_AF / math.sqrt(3)
    hexpts = [(LUG[0] + R * math.cos(math.radians(60 * i)), LUG[1] + R * math.sin(math.radians(60 * i))) for i in range(6)]   # a corner toward +y: up in the print
    p = p.cut(cq.Workplane('YZ', origin=(T0 - 0.01, 0, 0)).polyline(hexpts).close().extrude(NUT_T + 0.4))
    # IR shelf height: a column of M3 holes at 6 mm pitch, teardrops pointing +y (up in the print); both posts have them
    r = M3 / 2; k = r / math.sqrt(2)
    for zh in IR_HOLES_Z:
        p = p.cut(cq.Workplane('YZ', origin=(T0 - 1, 0, 0)).center(101, zh).circle(r).extrude(T1 - T0 + 2))
        p = p.cut(cq.Workplane('YZ', origin=(T0 - 1, 0, 0)).polyline([(101 + k, zh - k), (101 + r * math.sqrt(2), zh), (101 + k, zh + k), (101, zh)]).close().extrude(T1 - T0 + 2))
    # base plate: two M3 slots running outward, one each side of the upright, for the board's existing holes
    for xh in (BASE['x0'] + 5, BASE['x1'] - 5):
        p = p.cut(cq.Workplane('XY', origin=(0, 0, -89)).center(xh, 121).slot2D(40 + M3, M3, 90).extrude(9))
    try: p = p.edges('|Z').fillet(0.8)
    except Exception: pass
    return p

def ir_shelf():
    # far post (-y): a leg against the post's upstream face, bolted into its slot; a shelf with a slot along y for an FC-51's M3 hole and two zip-tie slots
    s = box(T0 - 4, T0, -112, -92, 10, 36).union(box(AX - 40, T0, -112, -66, 33, 36))
    s = s.union(cq.Workplane('XZ', origin=(0, -100, 0)).polyline([(T0 - 4, 33), (T0 - 16, 33), (T0 - 4, 18)]).close().extrude(3, both=True))
    s = s.cut(cq.Workplane('YZ', origin=(T0 - 5, 0, 0)).center(-101, 15).circle(M3 / 2).extrude(6))
    s = s.cut(cq.Workplane('XY', origin=(0, 0, 32)).center(AX - 26, -98).slot2D(12 + M3, M3, 90).extrude(5))
    for xz in (AX - 36, AX - 16):
        s = s.cut(box(xz - 1, xz + 1, -84, -80, 32, 37))
    try: s = s.edges('|Z').fillet(0.6)
    except Exception: pass
    return s

def cyl(p0, p1, r):
    d = V(*p1) - V(*p0); return cq.Workplane().add(cq.Solid.makeCylinder(r, d.Length, V(*p0), d.normalized()))
def elbow_ref(sgn):
    # PV 6 mm push-in elbow with the nozzle, sizes read from the user's photo (about +-1 mm); reference only, not printed
    a = V(0, -sgn * math.cos(TILT), -math.sin(TILT)); b = V(0, sgn * math.sin(TILT), -math.cos(TILT)); c = V(C_X, sgn * C_Y, C_Z)
    pt = lambda ua, ub: tuple(c + a * ua + b * ub)
    e = cq.Workplane().add(cq.Solid.makeSphere(6.75, c))
    e = e.union(cyl(pt(0, 0), pt(19.5, 0), 5.6)).union(cyl(pt(0, 0), pt(0, 21.5), 6.75))
    l = pt(8.8, 9.4); e = e.union(cyl((T1, l[1], l[2]), (T1 + 7, l[1], l[2]), 3.6))
    e = e.cut(cyl((T1 - 1, l[1], l[2]), (T1 + 8, l[1], l[2]), 1.6))
    noz = cyl(pt(19.5, 0), pt(32.5, 0), 4.4)
    return e, noz
def fc51_ref():
    x, hy, z = AX - 26, -98, 36
    m = box(x - 7, x + 7, hy - 5, hy + 27, z, z + 1.6).union(box(x - 1, x + 6, hy + 6, hy + 13, z + 1.6, z + 6.6))
    m = m.union(cyl((x - 3.5, hy + 27, z + 4.1), (x - 3.5, hy + 33, z + 4.1), 2.5)).union(cyl((x + 3.5, hy + 27, z + 4.1), (x + 3.5, hy + 33, z + 4.1), 2.5))
    return m.cut(cyl((x, hy, z - 1), (x, hy, z + 3), 1.5))

PP = post(); PN = PP.mirror('XZ'); IR = ir_shelf()
EP, NP = elbow_ref(1); EN, NN = elbow_ref(-1); FC = fc51_ref()
to_fusion = lambda w: w.translate(V(780, 0, 217))

# ---- in-place STEPs for Fusion
FU = os.path.join(OUT, 'fusion'); os.makedirs(FU, exist_ok=True)
inplace = {'spray-post-box-side': PP, 'spray-post-far-side': PN, 'ir-shelf': IR,
           'ref-elbow-box-side': EP, 'ref-nozzle-box-side': NP, 'ref-elbow-far-side': EN, 'ref-nozzle-far-side': NN, 'ref-fc51': FC}
for n, w in inplace.items(): cq.exporters.export(to_fusion(w), os.path.join(FU, n + '.step'))

# ---- print files, each the way it prints
PR = os.path.join(OUT, 'print'); os.makedirs(PR, exist_ok=True)
def to_bed(s): b = s.BoundingBox(); return s.translate(V(-b.xmin, -b.ymin, -b.zmin))
prints = {
    'spray-post box side x1': to_bed(PP.val().rotate(V(0, 0, 0), V(1, 0, 0), 90)),           # lying on its inner face (the face toward the belt)
    'spray-post far side (IR) x1': to_bed(PN.val().rotate(V(0, 0, 0), V(1, 0, 0), -90)),     # lying on its inner face (mirror of the other)
    'ir-shelf x1': to_bed(IR.val().rotate(V(0, 0, 0), V(1, 0, 0), 180)),                    # shelf on the bed, leg up
}
rep = {}
for n, s in prints.items():
    cq.exporters.export(cq.Workplane().add(s), os.path.join(PR, n + '.stl'), tolerance=0.02, angularTolerance=0.1)
    b = s.BoundingBox(); rep[n] = {'bed': [round(b.xlen, 1), round(b.ylen, 1), round(b.zlen, 1)], 'vol': round(s.Volume() / 1000, 1), 'valid': s.isValid(), 'solids': len(s.Solids())}
for n, w in inplace.items():
    b = to_fusion(w).val().BoundingBox(); print('%-22s fusion x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f' % (n, b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax))
print(json.dumps(rep, indent=1))
