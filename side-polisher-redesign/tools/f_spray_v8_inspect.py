import adsk.core, adsk.fusion
def bb(b): return [round(v * 10, 1) for v in (b.minPoint.x, b.maxPoint.x, b.minPoint.y, b.maxPoint.y, b.minPoint.z, b.maxPoint.z)]
def run(_c):
    app = adsk.core.Application.get()
    print('docs', [d.name for d in app.documents], 'active', app.activeDocument.name)
    ds = [d for d in app.documents if d.name.startswith('Conveyor assembly 2')]
    if not ds: print('conveyor doc not open'); return
    des = adsk.fusion.Design.cast(ds[0].products.itemByProductType('DesignProductType')); root = des.rootComponent
    for o in root.occurrences:
        if o.component.name in ('Spray station (Claude)', 'Casing box (Claude)'):
            t = o.transform2.translation; print('OCC', o.name, 'vis', o.isLightBulbOn, 'T', round(t.x*10,1), round(t.y*10,1), round(t.z*10,1))
            for b in o.bRepBodies: print('   ', b.name, b.isLightBulbOn, bb(b.boundingBox))
            for c in o.childOccurrences: print('   child', c.name, c.isLightBulbOn, bb(c.boundingBox))
