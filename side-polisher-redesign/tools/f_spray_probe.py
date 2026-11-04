import adsk.core, adsk.fusion
def run(_c):
    app = adsk.core.Application.get()
    d = [x for x in app.documents if x.name.startswith('Conveyor assembly 2')][0]
    des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType')); root = des.rootComponent
    occ = [o for o in root.occurrences if o.component.name == 'Spray station (Claude)'][0]; comp = occ.component
    u = [b for b in comp.bRepBodies if b.name.startswith('Nozzle post v8, box')][0]
    P = adsk.core.Point3D.create
    for x in (686.0, 689.0, 691.5):
        print('x', x, ' rows z (above belt) 76..54, cols y 92..105 step 1 ; # = solid')
        for z in range(76, 53, -1):
            row = ''.join('#' if u.pointContainment(P(x / 10, y / 10, (z + 217) / 10)) == 0 else '.' for y in range(92, 106))
            print('  z%3d %s' % (z, row))
    # the face list of the body near the seat
    for f in u.faces:
        b = f.boundingBox
        if b.minPoint.x * 10 > 684 and b.maxPoint.z * 10 > 270 and b.minPoint.z * 10 < 292 and b.minPoint.y * 10 < 104:
            print('face', f.geometry.surfaceType, [round(v * 10, 2) for v in (b.minPoint.x, b.maxPoint.x, b.minPoint.y, b.maxPoint.y, b.minPoint.z - 21.7, b.maxPoint.z - 21.7)])
