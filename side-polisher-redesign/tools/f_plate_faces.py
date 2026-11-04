import adsk.core, adsk.fusion
T = {0: 'plane', 1: 'cyl', 2: 'cone', 3: 'sphere', 4: 'torus', 5: 'ellcyl', 6: 'ellcone', 7: 'nurbs'}
def bb(b): return [round(v * 10, 2) for v in (b.minPoint.x, b.maxPoint.x, b.minPoint.y, b.maxPoint.y, b.minPoint.z, b.maxPoint.z)]
def run(_c):
    app = adsk.core.Application.get(); des = adsk.fusion.Design.cast(app.activeProduct); root = des.rootComponent
    occ = [o for o in root.occurrences if o.name == 'Shoe plate:1'][0]
    t = occ.transform2.translation; print('occ T', [round(v * 10, 2) for v in (t.x, t.y, t.z)], 'comp', occ.component.name, 'bodies', [b.name for b in occ.component.bRepBodies])
    b = occ.bRepBodies.item(0); print('vol', round(b.volume, 3), 'area', round(b.area, 2))
    for f in b.faces:
        g = f.geometry; ex = ''
        if T.get(g.surfaceType) == 'cyl': ex = 'r %.2f axis %s org %s' % (g.radius * 10, [round(v, 2) for v in g.axis.asArray()], [round(v * 10, 2) for v in g.origin.asArray()])
        if T.get(g.surfaceType) == 'plane': ex = 'n %s' % [round(v, 2) for v in g.normal.asArray()]
        print(T.get(g.surfaceType), round(f.area * 100, 1), bb(f.boundingBox), ex)
    tl = des.timeline
    for i in range(1555, tl.count):
        it = tl.item(i); e = it.entity
        pc = ''
        try: pc = e.parentComponent.name
        except Exception: pass
        print(i, it.name, type(e).__name__, pc)
