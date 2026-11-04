import adsk.core, adsk.fusion
# Top ToF moved to 70 mm before the roller axis (was 60): the new bracket and board stand-in come in from top polish\fusion; the old ones are
# hidden and renamed, not deleted. Checks the new bodies land where the component's other parts are (the component is moved +2.5 in x).
D = 'F:/Research/ASPS/top polish/fusion/'
def bb(b): return [round(v * 10, 1) for v in (b.minPoint.x, b.maxPoint.x, b.minPoint.y, b.maxPoint.y, b.minPoint.z, b.maxPoint.z)]
def run(_c):
    app = adsk.core.Application.get()
    if not app.activeDocument.name.startswith('Conveyor assembly 2'): raise Exception('active doc ' + app.activeDocument.name)
    root = adsk.fusion.Design.cast(app.activeProduct).rootComponent
    occ = [o for o in root.occurrences if o.component.name == 'Top polisher redesign (Claude)'][0]; comp = occ.component
    oldb = comp.bRepBodies.itemByName('ToF bracket (60 mm before the axis, 20 mm higher)'); oldp = comp.bRepBodies.itemByName('ToF board (stand-in)')
    if not oldb or not oldp: raise Exception('old ToF bodies not found')
    ref = bb(oldb.boundingBox)
    oldb.name = 'ToF bracket, 60 mm (old, hidden)'; oldb.isLightBulbOn = False
    oldp.name = 'ToF board stand-in, 60 mm (old, hidden)'; oldp.isLightBulbOn = False
    for f, name in (('bracket', 'ToF bracket (70 mm before the axis)'), ('board', 'ToF board (stand-in, 70 mm)')):
        before = set(o.entityToken for o in root.occurrences)
        opt = app.importManager.createSTEPImportOptions(D + f + '.step'); opt.isViewFit = False
        app.importManager.importToTarget(opt, root)
        tmp = [o for o in root.occurrences if o.entityToken not in before]
        nbs = [b for o in tmp for b in o.bRepBodies] + [b for o in tmp for c in o.childOccurrences for b in c.bRepBodies]
        if len(nbs) != 1: raise Exception('%s: %d bodies' % (f, len(nbs)))
        cp = nbs[0].copyToComponent(occ); cp.name = name
        for o in tmp: o.deleteMe()
        print(name, round(cp.volume, 2), 'cm3', bb(cp.boundingBox))
    nb = comp.bRepBodies.itemByName('ToF bracket (70 mm before the axis)')
    print('old bracket world bbox', ref, '-> expected new: x min', ref[0] - 11, 'x max same', ref[1], 'z max', ref[5] + 6.5)
