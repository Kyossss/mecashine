import adsk.core, adsk.fusion
# Read-only: Sketch261 and Extrude1 (the user's change to the far-side post), and a slice report of that post's new geometry.
def run(_c):
    d = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct); root = d.rootComponent
    tl = d.timeline
    sk = tl.item(1544).entity; ex = tl.item(1545).entity
    print('sketch', sk.name, 'in', sk.parentComponent.name, 'plane origin', [round(v * 10, 2) for v in sk.origin.asArray()], 'normal', [round(v, 3) for v in sk.xDirection.crossProduct(sk.yDirection).asArray()])
    for c in sk.sketchCurves:
        g = c.worldGeometry
        if isinstance(g, adsk.core.Line3D): print('  line', [round(v * 10, 2) for v in g.startPoint.asArray()], '->', [round(v * 10, 2) for v in g.endPoint.asArray()])
        elif isinstance(g, adsk.core.Circle3D): print('  circle c', [round(v * 10, 2) for v in g.center.asArray()], 'r', round(g.radius * 10, 2))
        elif isinstance(g, adsk.core.Arc3D): print('  arc c', [round(v * 10, 2) for v in g.center.asArray()], 'r', round(g.radius * 10, 2), 'from', [round(v * 10, 2) for v in g.startPoint.asArray()], 'to', [round(v * 10, 2) for v in g.endPoint.asArray()])
        else: print('  curve', c.objectType)
    print('extrude op', ex.operation, 'profiles', ex.profile.objectType if not isinstance(ex.profile, adsk.core.ObjectCollection) else ex.profile.count)
    try:
        e1 = ex.extentOne; print('extent1', e1.objectType, round(e1.distance.value * 10, 2) if hasattr(e1, 'distance') else '')
    except Exception as e: print('extent1 ?', e)
    try:
        e2 = ex.extentTwo; print('extent2', e2.objectType if e2 else None, round(e2.distance.value * 10, 2) if e2 and hasattr(e2, 'distance') else '')
    except Exception as e: print('extent2 ?', e)
    try: print('start', ex.startExtent.objectType, 'side', ex.extentType)
    except Exception: pass
    print('participant / bodies', [b.name for b in ex.bodies])
    # faces of the far post outside the old post's x range 675..692
    b = [x for x in root.allOccurrences if x.component.name == 'Spray station (Claude)'][0].component.bRepBodies.itemByName('Nozzle post, far side (IR slot used)')
    for f in b.faces:
        B = f.boundingBox
        if B.minPoint.x * 10 < 674.9 or B.maxPoint.x * 10 > 692.1:
            print('  face', f.geometry.objectType.split('::')[-1], 'area %.0f mm2' % (f.area * 100), [round(v * 10, 1) for v in (B.minPoint.x, B.maxPoint.x, B.minPoint.y, B.maxPoint.y, B.minPoint.z, B.maxPoint.z)])
