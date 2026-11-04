import adsk.core, adsk.fusion
def run(_c):
    r = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct).rootComponent
    for nm in ('Body70', 'Body67'):
        b = [x for x in r.bRepBodies if x.name == nm][0]
        # planar faces facing up/down near the top plate's front end (x 1086..1110), to see where the plate and the bracket's flanges are
        rows = []
        for f in b.faces:
            g = f.geometry
            if g.objectType.endswith('Plane'):
                n = g.normal; bb = f.boundingBox
                if abs(n.z) > 0.99 and bb.minPoint.x * 10 < 1112 and bb.maxPoint.x * 10 > 1080:
                    rows.append((round(bb.minPoint.z * 10 - 217, 1), 'up' if n.z > 0 else 'down', [round(v * 10, 1) for v in (bb.minPoint.x, bb.maxPoint.x, bb.minPoint.y, bb.maxPoint.y)]))
        rows.sort()
        print('==', nm); [print('  z', r_[0], r_[1], r_[2]) for r_ in rows]
