import adsk.core, adsk.fusion
# Post v3: built from the user's base-plate edit of the far post. The user's edited body is hidden and renamed (kept), the old box-side post is
# replaced, and the new mirrored pair comes in place from spray station\fusion. Then an overlap check against everything visible.
D = 'F:/Research/ASPS/spray station/fusion/'
def bb(b): return [round(v * 10, 1) for v in (b.minPoint.x, b.maxPoint.x, b.minPoint.y, b.maxPoint.y, b.minPoint.z, b.maxPoint.z)]
def run(_c):
    app = adsk.core.Application.get()
    if not app.activeDocument.name.startswith('Conveyor assembly 2'): raise Exception('active doc ' + app.activeDocument.name)
    root = adsk.fusion.Design.cast(app.activeProduct).rootComponent
    occ = [o for o in root.occurrences if o.component.name == 'Spray station (Claude)'][0]; comp = occ.component
    mine = comp.bRepBodies.itemByName('Nozzle post, box side')
    user = comp.bRepBodies.itemByName('Nozzle post, far side (IR slot used)')
    if not mine or not user: raise Exception('posts not found')
    user.name = 'Nozzle post, far side - your base-plate edit (hidden)'; user.isLightBulbOn = False
    mine.deleteMe()
    for f, name in (('spray-post-box-side', 'Nozzle post v3, box side'), ('spray-post-far-side', 'Nozzle post v3, far side (IR slot used)')):
        before = set(o.entityToken for o in root.occurrences)
        opt = app.importManager.createSTEPImportOptions(D + f + '.step'); opt.isViewFit = False
        app.importManager.importToTarget(opt, root)
        tmp = [o for o in root.occurrences if o.entityToken not in before]
        nbs = [b for o in tmp for b in o.bRepBodies] + [b for o in tmp for c in o.childOccurrences for b in c.bRepBodies]
        if len(nbs) != 1: raise Exception('%s: %d bodies' % (f, len(nbs)))
        cp = nbs[0].copyToComponent(occ); cp.name = name
        ap = [b for b in comp.bRepBodies if b.name.startswith('IR sensor')][0].appearance
        y = app.activeProduct.appearances.itemByName('Spray - post yellow')
        if y: cp.appearance = y
        for o in tmp: o.deleteMe()
        print(name, round(cp.volume, 2), 'cm3', bb(cp.boundingBox))
    tm = adsk.fusion.TemporaryBRepManager.get()
    new = [b for b in comp.bRepBodies if b.isLightBulbOn]
    others = [b for b in root.bRepBodies if b.isLightBulbOn]
    def walk(o):
        if not o.isLightBulbOn or o == occ: return
        others.extend([b for b in o.bRepBodies if b.isLightBulbOn and b.faces.count]); [walk(c) for c in o.childOccurrences]
    for o in root.occurrences: walk(o)
    def ov(a, b):
        A, B = a.boundingBox, b.boundingBox
        if A.maxPoint.x < B.minPoint.x or B.maxPoint.x < A.minPoint.x or A.maxPoint.y < B.minPoint.y or B.maxPoint.y < A.minPoint.y or A.maxPoint.z < B.minPoint.z or B.maxPoint.z < A.minPoint.z: return 0.0
        t = tm.copy(a); tm.booleanOperation(t, tm.copy(b), adsk.fusion.BooleanTypes.IntersectionBooleanType)
        return t.volume * 1000 if t else 0.0
    hits = []
    for i, a in enumerate(new):
        for b in new[i + 1:] + others:
            v = ov(a, b)
            if v > 0.05: hits.append((a.name, b.name, round(v, 2)))
    print('overlaps (mm3):', hits if hits else 'none')
    print('bodies:', [(b.name, b.isLightBulbOn) for b in comp.bRepBodies])
