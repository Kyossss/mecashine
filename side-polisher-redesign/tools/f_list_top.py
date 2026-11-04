import adsk.core, adsk.fusion
def bb(b): return [round(v * 10, 1) for v in (b.minPoint.x, b.maxPoint.x, b.minPoint.y, b.maxPoint.y, b.minPoint.z, b.maxPoint.z)]
def run(_c):
    app = adsk.core.Application.get()
    d = adsk.fusion.Design.cast(app.activeProduct); r = d.rootComponent
    rows = []
    def walk(occs, depth):
        for o in occs:
            if not o.isLightBulbOn: continue
            for b in o.bRepBodies:
                if not b.isLightBulbOn: continue
                q = bb(b.boundingBox)
                if q[1] > 1000 and q[0] < 1300: rows.append((o.fullPathName, b.name, round(b.volume, 1), q))
            walk(o.childOccurrences, depth + 1)
    walk(r.occurrences, 0)
    for b in r.bRepBodies:
        if b.isLightBulbOn:
            q = bb(b.boundingBox)
            if q[1] > 1000 and q[0] < 1300: rows.append(('<root>', b.name, round(b.volume, 1), q))
    rows.sort(key=lambda t: t[3][4])
    for t in rows: print(t[0][-60:], '|', t[1], '|', t[2], '|', t[3])
