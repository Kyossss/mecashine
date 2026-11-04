import adsk.core, adsk.fusion
# Top ToF at 75 mm before the roller axis: replaces the 70 mm bracket and board stand-in (mine, superseded) with the new ones from top polish\fusion.
# The original 60 mm bodies stay hidden. Activates "Conveyor assembly 2" first.
D = 'F:/Research/ASPS/top polish/fusion/'
def bb(b): return [round(v * 10, 1) for v in (b.minPoint.x, b.maxPoint.x, b.minPoint.y, b.maxPoint.y, b.minPoint.z, b.maxPoint.z)]
def run(_c):
    app = adsk.core.Application.get()
    doc = [d for d in app.documents if d.name.startswith('Conveyor assembly 2')]
    if not doc: raise Exception('Conveyor assembly 2 is not open')
    doc[0].activate()
    root = adsk.fusion.Design.cast(app.activeProduct).rootComponent
    occ = [o for o in root.occurrences if o.component.name == 'Top polisher redesign (Claude)'][0]; comp = occ.component
    for n in ('ToF bracket (70 mm before the axis)', 'ToF board (stand-in, 70 mm)'):
        b = comp.bRepBodies.itemByName(n)
        if not b: raise Exception('not found: ' + n)
        b.deleteMe()
    for f, name in (('bracket', 'ToF bracket (75 mm before the axis)'), ('board', 'ToF board (stand-in, 75 mm)')):
        before = set(o.entityToken for o in root.occurrences)
        opt = app.importManager.createSTEPImportOptions(D + f + '.step'); opt.isViewFit = False
        app.importManager.importToTarget(opt, root)
        tmp = [o for o in root.occurrences if o.entityToken not in before]
        nbs = [b for o in tmp for b in o.bRepBodies] + [b for o in tmp for c in o.childOccurrences for b in c.bRepBodies]
        if len(nbs) != 1: raise Exception('%s: %d bodies' % (f, len(nbs)))
        cp = nbs[0].copyToComponent(occ); cp.name = name
        for o in tmp: o.deleteMe()
        print(name, round(cp.volume, 2), 'cm3', bb(cp.boundingBox))
