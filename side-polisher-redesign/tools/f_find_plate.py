import adsk.core, adsk.fusion
def bb(b): return [round(v * 10, 2) for v in (b.minPoint.x, b.maxPoint.x, b.minPoint.y, b.maxPoint.y, b.minPoint.z, b.maxPoint.z)]
def run(_c):
    app = adsk.core.Application.get()
    print('active', app.activeDocument.name, [d.name for d in app.documents])
    d = [x for x in app.documents if x.name.startswith('Conveyor assembly 2')][0]
    des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType')); root = des.rootComponent
    def walk(o, path):
        for b in o.bRepBodies:
            if 'plate' in b.name.lower() or 'shoe' in (path + b.name).lower() or 'peg' in b.name.lower():
                print(path, '|', b.name, b.isLightBulbOn, round(b.volume, 2), b.faces.count, bb(b.boundingBox))
        for c in o.childOccurrences: walk(c, path + '/' + c.name)
    for b in root.bRepBodies:
        B = b.boundingBox
        if 'plate' in b.name.lower() or (B.minPoint.x > 25 and B.maxPoint.x < 45 and b.isLightBulbOn and B.minPoint.z > 20):
            print('root |', b.name, b.isLightBulbOn, round(b.volume, 2), b.faces.count, bb(B))
    for o in root.occurrences:
        if 'shoe' in o.name.lower() or 'plate' in o.name.lower(): print('OCC', o.name, o.isLightBulbOn)
        walk(o, o.name)
    tl = des.timeline; print('timeline', tl.count, [tl.item(i).name for i in range(1550, tl.count)])
