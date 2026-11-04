import adsk.core, adsk.fusion
def bb(b): return [round(v * 10, 2) for v in (b.minPoint.x, b.maxPoint.x, b.minPoint.y, b.maxPoint.y, b.minPoint.z, b.maxPoint.z)]
def run(_c):
    app = adsk.core.Application.get()
    d = [x for x in app.documents if x.name.startswith('Conveyor assembly 2')][0]
    des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType'))
    tl = des.timeline
    for i in range(1551, 1555):
        e = adsk.fusion.ExtrudeFeature.cast(tl.item(i).entity)
        ops = {0: 'join', 1: 'cut', 2: 'intersect', 3: 'new body', 4: 'new comp'}
        print(e.name, ops.get(e.operation, e.operation), 'extentType', e.extentType)
        try:
            ext = e.extentOne; print('  extentOne', type(ext).__name__, getattr(getattr(ext, 'distance', None), 'expression', None))
        except Exception as x: print('  ext?', x)
        try:
            pr = e.profile
            prs = [pr] if not hasattr(pr, 'count') else [pr.item(k) for k in range(pr.count)]
            for p in prs:
                sk = p.parentSketch; print('  sketch', sk.name, 'plane', type(sk.referencePlane).__name__, 'profile bbox', bb(p.boundingBox))
                for c in sk.sketchCurves:
                    g = c.worldGeometry
                    if hasattr(g, 'center'): print('    circle', [round(v*10,2) for v in g.center.asArray()], 'r', round(g.radius*10, 2))
                    elif hasattr(g, 'startPoint'): print('    line', [round(v*10,2) for v in g.startPoint.asArray()], [round(v*10,2) for v in g.endPoint.asArray()])
        except Exception as x: print('  profile?', x)
        try: print('  participants', [b.name for b in e.participantBodies])
        except Exception as x: print('  part?', x)
        try: print('  bodies', [b.name for b in e.bodies], 'faces', e.faces.count, [bb(f.boundingBox) for f in e.faces][:6])
        except Exception as x: print('  bodies?', x)
