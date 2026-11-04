import adsk.core, adsk.fusion
# Top polisher redesign, stage 2: motor holder copy 15 mm lower, the new roller parts, bearing and ToF bracket imported in place,
# and your old motor holder, roller core and sensor bracket hidden (not deleted).
D = 'F:/Research/ASPS/top polish/fusion/'
PARTS = [('drive', ['Roller drive end']), ('bar', ['Roller bar (12 mm hex, 109 mm)']), ('idler', ['Roller idler end (8 mm axle)']), ('bearing', ['608ZZ bearing (in the carriage wall)']),
         ('discs', ['Tie disc %d' % (i + 1) for i in range(12)]), ('bracket', ['ToF bracket (60 mm before the axis, 20 mm higher)']), ('board', ['ToF board (stand-in)'])]
def bb(b): return [round(v * 10, 1) for v in (b.minPoint.x, b.maxPoint.x, b.minPoint.y, b.maxPoint.y, b.minPoint.z, b.maxPoint.z)]
def run(_c):
    app = adsk.core.Application.get()
    if not app.activeDocument.name.startswith('Conveyor assembly 2'): raise Exception('active doc ' + app.activeDocument.name)
    root = adsk.fusion.Design.cast(app.activeProduct).rootComponent
    occ = [o for o in root.occurrences if o.component.name == 'Top polisher redesign (Claude)'][0]; comp = occ.component
    if comp.bRepBodies.count != 1: raise Exception('stage 2 already run? bodies: %d' % comp.bRepBodies.count)
    mh0 = [b for b in root.bRepBodies if b.name == 'Body68'][0]
    mh = mh0.copyToComponent(occ); mh.name = 'Motor holder (15 mm lower)'
    oc = adsk.core.ObjectCollection.create(); oc.add(mh)
    mi = comp.features.moveFeatures.createInput2(oc); mi.defineAsTranslateXYZ(adsk.core.ValueInput.createByReal(0), adsk.core.ValueInput.createByReal(0), adsk.core.ValueInput.createByReal(-1.5), True)
    comp.features.moveFeatures.add(mi)
    mh = [b for b in comp.bRepBodies if b.name.startswith('Motor holder')][0]
    print('motor holder', round(mh.volume, 2), bb(mh.boundingBox))
    for f, names in PARTS:
        before = set(o.entityToken for o in root.occurrences)
        opt = app.importManager.createSTEPImportOptions(D + f + '.step'); opt.isViewFit = False
        app.importManager.importToTarget(opt, root)
        tmp = [o for o in root.occurrences if o.entityToken not in before]
        nbs = [b for o in tmp for b in o.bRepBodies] + [b for o in tmp for c in o.childOccurrences for b in c.bRepBodies]
        nbs.sort(key=lambda b: (b.boundingBox.minPoint.y, b.boundingBox.minPoint.z))
        if len(nbs) != len(names): raise Exception('%s: %d bodies' % (f, len(nbs)))
        for b, n in zip(nbs, names):
            cp = b.copyToComponent(occ); cp.name = n
        for o in tmp: o.deleteMe()
        print(f, 'added', len(names), 'body' if len(names) == 1 else 'bodies')
    for nm in ('Body68', 'Body85', 'Body70'):
        b = [x for x in root.bRepBodies if x.name == nm][0]; b.isLightBulbOn = False
    print('hidden: Body68 motor holder, Body85 roller core, Body70 sensor bracket')
    print('component now has', comp.bRepBodies.count, 'bodies:', [b.name for b in comp.bRepBodies])
