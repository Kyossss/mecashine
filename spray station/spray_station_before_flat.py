# Spray station (approved 2026-10-26): two nozzle posts on the base board just before the reflector, the elbows bolted through their lugs,
# a universal IR sensor shelf on the far post. Writes print STLs (oriented for the bed, no supports) and in-place STEPs for Fusion.
# Built in the proposal frame (x = CAD x - 780, z above the belt top, board top at z -88), then moved to Fusion (x + 780, z + 217).
import cadquery as cq, math, os, json
V = cq.Vector
OUT = os.path.dirname(os.path.abspath(__file__))
AX = -100.0                      # spray position, CAD x 680
TILT = math.radians(15)
C_X, C_Y, C_Z = AX + 11, 110.0, 58.0           # elbow bend point on the box (+y) side
def at(ua, ub):                  # + side elbow: ua along the side port (across the belt, 15 deg down), ub along the down port
    return (C_Y - math.cos(TILT) * ua + math.sin(TILT) * ub, C_Z - math.sin(TILT) * ua - math.cos(TILT) * ub)
LUG = at(8.8, 9.4)
M3, NUT_AF, NUT_T = 3.4, 5.7, 2.6

def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0).translate(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))

def post():
    p = box(AX - 30, AX + 22, 94, 132, -88, -83).union(box(AX - 4, AX + 4, 96, 118, -83, 66))
    for pts in ([(AX - 4, -83), (AX - 22, -83), (AX - 4, -40)], [(AX + 4, -83), (AX + 14, -83), (AX + 4, -55)]):   # ribs, both faces
        p = p.union(cq.Workplane('XZ', origin=(0, 118, 0)).polyline(pts).close().extrude(3))
    # 15 deg seat under the elbow's side port (between its lug and the blue ring), with a 45 deg underside so it prints standing
    top = [at(13, 5.6), at(19.5, 5.6)]
    face = top + [(at(19.5, 13)[0], at(19.5, 13)[1] - 8), (at(13, 13)[0], at(13, 13)[1] - 8)]
    tip = top + [at(19.5, 13), at(13, 13)]
    seat = cq.Workplane('YZ', origin=(AX + 4, 0, 0)).polyline(face).close().workplane(offset=8).polyline(tip).close().loft(ruled=True)
    p = p.union(seat)
    # elbow screw through the upright, nut pocket on the upstream face
    p = p.cut(cq.Workplane('YZ', origin=(AX - 5, 0, 0)).center(*LUG).circle(M3 / 2).extrude(10))
    p = p.cut(cq.Workplane('YZ', origin=(AX - 4.01, 0, 0)).center(*LUG).polygon(6, NUT_AF / math.cos(math.pi / 6)).extrude(NUT_T))
    # vertical slot for the IR shelf (height adjust); both posts have it, so either side can take the sensor
    p = p.cut(cq.Workplane('YZ', origin=(AX - 5, 0, 0)).center(101, 12).slot2D(45 + M3, M3, 90).extrude(10))
    # foot: two slots across the belt direction, to meet the board's existing holes
    for xh in (AX - 26, AX + 18):       # beyond the ribs, so a screw head seats anywhere along the slot
        p = p.cut(cq.Workplane('XY', origin=(0, 0, -89)).center(xh, 113).slot2D(30 + M3, M3, 90).extrude(6))
    try: p = p.edges('|Z').fillet(0.8)
    except Exception: pass
    return p

def ir_shelf():
    # far post (-y): a leg against the post's upstream face, bolted into its slot; a shelf with a slot along y for an FC-51's M3 hole and two zip-tie slots
    s = box(AX - 8, AX - 4, -112, -92, 10, 36).union(box(AX - 40, AX - 4, -112, -66, 33, 36))
    s = s.union(cq.Workplane('XZ', origin=(0, -100, 0)).polyline([(AX - 8, 33), (AX - 20, 33), (AX - 8, 18)]).close().extrude(3, both=True))
    s = s.cut(cq.Workplane('YZ', origin=(AX - 9, 0, 0)).center(-101, 16).circle(M3 / 2).extrude(6))
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
    l = pt(8.8, 9.4); e = e.union(cyl((AX + 4, l[1], l[2]), (AX + 11, l[1], l[2]), 3.6))
    e = e.cut(cyl((AX + 3, l[1], l[2]), (AX + 12, l[1], l[2]), 1.6))
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
    'spray-post box side x1': to_bed(PP.val()),                                              # standing on its foot
    'spray-post far side (IR) x1': to_bed(PN.val()),                                         # standing on its foot (mirror of the other)
    'ir-shelf x1': to_bed(IR.val().rotate(V(0, 0, 0), V(1, 0, 0), 180)),                    # shelf on the bed, leg up
}
rep = {}
for n, s in prints.items():
    cq.exporters.export(cq.Workplane().add(s), os.path.join(PR, n + '.stl'), tolerance=0.02, angularTolerance=0.1)
    b = s.BoundingBox(); rep[n] = {'bed': [round(b.xlen, 1), round(b.ylen, 1), round(b.zlen, 1)], 'vol': round(s.Volume() / 1000, 1), 'valid': s.isValid(), 'solids': len(s.Solids())}
for n, w in inplace.items():
    b = to_fusion(w).val().BoundingBox(); print('%-22s fusion x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f' % (n, b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax))
print(json.dumps(rep, indent=1))
