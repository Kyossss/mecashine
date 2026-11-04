import adsk.core, adsk.fusion
def bb(b): return [round(v * 10, 1) for v in (b.minPoint.x, b.maxPoint.x, b.minPoint.y, b.maxPoint.y, b.minPoint.z, b.maxPoint.z)]
def run(_c):
    app = adsk.core.Application.get()
    d = [x for x in app.documents if x.name.startswith('Conveyor assembly 2')][0]
    print('active', app.activeDocument.name, 'conveyor modified', d.isModified)
    des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType')); root = des.rootComponent
    occ = [o for o in root.occurrences if o.component.name == 'Spray station (Claude)'][0]; comp = occ.component
    for b in comp.bRepBodies: print('B', b.name, b.isLightBulbOn, round(b.volume, 3), b.faces.count, bb(b.boundingBox))
    tl = des.timeline; print('timeline', tl.count)
    for i in range(max(0, tl.count - 25), tl.count):
        it = tl.item(i)
        try: e = it.entity; nm = e.name if hasattr(e, 'name') else ''; pc = e.parentComponent.name if hasattr(e, 'parentComponent') else ''
        except Exception: nm, pc = '?', '?'
        print(i, it.name, type(it.entity).__name__ if it.entity else None, pc, it.isSuppressed)
    for o in root.occurrences:
        if o.component.name in ('Casing box (Claude)',): print('box', [bb(b.boundingBox) for b in o.bRepBodies][0])
