# Spray station proposal parts, in the proposal page's frame: x = CAD x - 780 (along the belt), y across it, z above the belt top (board top at z -88).
# Post (one per side, mirrored), and a universal IR sensor shelf for the far (-y) post. Writes parts-mesh.json for the page. Not in Fusion.
import cadquery as cq, json, base64, array, math

AX = -100.0                      # spray position (CAD x 680)
TILT = math.radians(15)
C_X, C_Y, C_Z = AX + 11, 110.0, 58.0          # elbow bend point on the + side
def at(ua, ub):                  # point on the + side elbow: ua along the side port (across the belt, 15 deg down), ub along the down port
    a = (0, -math.cos(TILT), -math.sin(TILT)); b = (0, math.sin(TILT), -math.cos(TILT))
    return (C_Y + a[1] * ua + b[1] * ub, C_Z + a[2] * ua + b[2] * ub)
LUG = at(8.8, 9.4)               # elbow lug hole (y, z)
M3, NUT_AF, NUT_T = 3.4, 5.7, 2.6

def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane('XY').box(x1 - x0, y1 - y0, z1 - z0).translate(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
def slot_x(y0, y1, zc, w, x0, x1):   # slot running along y, cut through in z... helper not used
    pass

def post():
    foot = box(AX - 22, AX + 14, 94, 132, -88, -83)
    up = box(AX - 4, AX + 4, 96, 118, -83, 66)
    p = foot.union(up)
    # ribs on the outer edge, both faces
    for x0, x1, top in ((AX - 22, AX - 4, -40), (AX + 4, AX + 14, -55)):
        xa, xb = (x1, x0) if x0 < AX else (x0, x1)
        pts = [(xa, -83), (xb, -83), (xa, top)] if x0 < AX else [(x0, -83), (x1, -83), (x0, top)]
        rib = cq.Workplane('XZ', origin=(0, 118, 0)).polyline(pts).close().extrude(3)   # XZ normal is -y: from y 118 to 115
        p = p.union(rib)
    # 15 deg seat under the elbow's side port, between its lug and the blue ring
    seat_pts = [at(13, 5.6), at(19.5, 5.6), at(19.5, 13), at(13, 13)]
    seat = cq.Workplane('YZ', origin=(AX + 4, 0, 0)).polyline(seat_pts).close().extrude(8)
    p = p.union(seat)
    # elbow screw through the upright, nut pocket on the upstream face
    p = p.cut(cq.Workplane('YZ', origin=(AX - 5, 0, 0)).center(*LUG).circle(M3 / 2).extrude(10))
    p = p.cut(cq.Workplane('YZ', origin=(AX - 4.01, 0, 0)).center(*LUG).polygon(6, NUT_AF / math.cos(math.pi / 6)).extrude(NUT_T))
    # vertical slot for the IR shelf (height adjust), through the upright along x
    p = p.cut(cq.Workplane('YZ', origin=(AX - 5, 0, 0)).center(101, 12).slot2D(45 + M3, M3, 90).extrude(10))
    # foot: two slots across the belt direction so the foot can meet the board's existing holes
    for xh in (AX - 14, AX + 9):
        p = p.cut(cq.Workplane('XY', origin=(0, 0, -89)).center(xh, 113).slot2D(30 + M3, M3, 90).extrude(8))
    try: p = p.edges('|Z').fillet(0.8)
    except Exception: pass
    return p

def ir_shelf():
    # for the far post (-y): a leg against the post's upstream face, bolted into its slot; a shelf with a slot along y for the module's M3 hole
    leg = box(AX - 8, AX - 4, -112, -92, 10, 36)
    shelf = box(AX - 40, AX - 4, -112, -66, 33, 36)
    s = leg.union(shelf)
    gus = cq.Workplane('XZ', origin=(0, -100, 0)).polyline([(AX - 8, 33), (AX - 20, 33), (AX - 8, 18)]).close().extrude(3, both=True)
    s = s.union(gus)
    s = s.cut(cq.Workplane('YZ', origin=(AX - 9, 0, 0)).center(-101, 16).circle(M3 / 2).extrude(6))
    s = s.cut(cq.Workplane('XY', origin=(0, 0, 32)).center(AX - 26, -98).slot2D(12 + M3, M3, 90).extrude(5))
    for xz in (AX - 36, AX - 16):
        s = s.cut(box(xz - 1, xz + 1, -84, -80, 32, 37))
    try: s = s.edges('|Z').fillet(0.6)
    except Exception: pass
    return s

def enc(shape):
    vs, tris = shape.val().tessellate(0.08, 0.3)
    pts = array.array('h')
    for t in tris:
        for i in t:
            v = vs[i]; pts.extend((int(round(v.x * 10)), int(round(v.y * 10)), int(round(v.z * 10))))
    return base64.b64encode(pts.tobytes()).decode()

pp = post(); pn = pp.mirror('XZ'); ir = ir_shelf()
for n, s in (('post', pp), ('ir', ir)):
    bb = s.val().BoundingBox(); print(n, 'vol %.1f cm3' % (s.val().Volume() / 1000), 'bbox x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f' % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax), 'valid', s.val().isValid())
json.dump({'postPos': enc(pp), 'postNeg': enc(pn), 'irShelf': enc(ir)}, open('F:/Research/ASPS/spray-proposal/parts-mesh.json', 'w'))
print('lug at y %.1f z %.1f' % LUG)
