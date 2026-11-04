import adsk.core, adsk.fusion
def bb(b): return [round(v * 10, 1) for v in (b.minPoint.x, b.maxPoint.x, b.minPoint.y, b.maxPoint.y, b.minPoint.z - 21.7, b.maxPoint.z - 21.7)]
def run(_c):
    app = adsk.core.Application.get()
    r = adsk.fusion.Design.cast(app.activeProduct).rootComponent
    for name in ('Body85', 'Body67', 'Body68', 'Body70', 'Body27', 'Body71', 'Body83', 'Body45'):
        bs = [b for b in r.bRepBodies if b.name == name]
        if not bs: print(name, 'not found'); continue
        b = bs[0]
        print('==', name, 'vol', round(b.volume, 1), 'bb (z above belt)', bb(b.boundingBox), 'faces', b.faces.count)
        cyl = {}
        for f in b.faces:
            g = f.geometry
            if g.objectType.endswith('Cylinder'):
                o, a = g.origin, g.axis
                key = (round(g.radius * 10, 2), tuple(round(v, 2) for v in (a.x, a.y, a.z)))
                fb = f.boundingBox
                cyl.setdefault(key, []).append([round(o.x * 10, 1), round(o.y * 10, 1), round(o.z * 10 - 217, 1), round(fb.minPoint.y * 10, 1), round(fb.maxPoint.y * 10, 1), round(fb.minPoint.z * 10 - 217, 1), round(fb.maxPoint.z * 10 - 217, 1)])
        for k, v in sorted(cyl.items()):
            print('   cyl r', k[0], 'axis', k[1], 'x', len(v), v[:3])
