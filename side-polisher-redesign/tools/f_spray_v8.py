import adsk.core, adsk.fusion
# Spray station v8 (2026-11-03): IR shelf + FC-51 on the box side, elbows 25 mm higher at 25 deg down, base plate to |y| 140.
# Deletes the v4 posts, REF elbows/nozzles/FC-51 and the shelf, imports the v8 ones from spray station\fusion with the same appearances.
# The user's base-plate edit stays hidden. Then moves the casing box to its real place (wall 80 mm from the belt frame: y 152, was 175)
# and runs an overlap check of the spray bodies against everything visible.
D = 'F:/Research/ASPS/spray station/fusion/'
BOX_DY = -2.3                                    # cm
def bb(b): return [round(v * 10, 1) for v in (b.minPoint.x, b.maxPoint.x, b.minPoint.y, b.maxPoint.y, b.minPoint.z, b.maxPoint.z)]
def run(_c):
    app = adsk.core.Application.get()
    if not app.activeDocument.name.startswith('Conveyor assembly 2'): raise Exception('active doc ' + app.activeDocument.name)
    des = adsk.fusion.Design.cast(app.activeProduct); root = des.rootComponent
    occ = [o for o in root.occurrences if o.component.name == 'Spray station (Claude)'][0]; comp = occ.component
    ap = {}
    def take(prefix, key):
        bs = [b for b in comp.bRepBodies if b.name.startswith(prefix)]
        if not bs: raise Exception('not found: ' + prefix)
        ap[key] = bs[0].appearance
        for b in bs: b.deleteMe()
    take('Nozzle post v4', 'post'); take('REF PV6 elbow', 'elbow'); take('REF nozzle', 'nozzle'); take('REF FC-51', 'fc'); take('IR sensor shelf', 'shelf')
    items = [('spray-post-box-side-IR', ['Nozzle post v8, box side (IR shelf)'], 'post'),
             ('spray-post-far-side', ['Nozzle post v8, far side'], 'post'),
             ('ir-shelf', ['IR sensor shelf (universal)'], 'shelf'),
             ('ref-elbow-box-side', ['REF PV6 elbow, box side'], 'elbow'), ('ref-nozzle-box-side', ['REF nozzle, box side'], 'nozzle'),
             ('ref-elbow-far-side', ['REF PV6 elbow, far side'], 'elbow'), ('ref-nozzle-far-side', ['REF nozzle, far side'], 'nozzle'),
             ('ref-fc51', ['REF FC-51 IR module', 'REF FC-51 IR module LED 1', 'REF FC-51 IR module LED 2'], 'fc')]
    for f, names, k in items:
        before = set(o.entityToken for o in root.occurrences)
        opt = app.importManager.createSTEPImportOptions(D + f + '.step'); opt.isViewFit = False
        app.importManager.importToTarget(opt, root)
        tmp = [o for o in root.occurrences if o.entityToken not in before]
        nbs = [b for o in tmp for b in o.bRepBodies] + [b for o in tmp for c in o.childOccurrences for b in c.bRepBodies]
        nbs.sort(key=lambda b: -b.volume)
        if len(nbs) > len(names): raise Exception('%s: %d bodies' % (f, len(nbs)))
        for b, n in zip(nbs, names):
            cp = b.copyToComponent(occ); cp.name = n
            if ap[k]: cp.appearance = ap[k]
            print(n, round(cp.volume, 2), 'cm3', bb(cp.boundingBox))
        for o in tmp: o.deleteMe()
    # casing box to its real place
    box = [o for o in root.occurrences if o.component.name == 'Casing box (Claude)'][0]
    m = box.transform2; t = m.translation; t.y = t.y + BOX_DY; m.translation = t; box.transform2 = m
    if des.snapshots.hasPendingSnapshot: des.snapshots.add()
    print('casing box', [bb(b.boundingBox) for b in box.bRepBodies][0])
    # overlaps
    tm = adsk.fusion.TemporaryBRepManager.get()
    new = [b for b in occ.bRepBodies if b.isLightBulbOn]
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
            if a.name.startswith('REF FC-51') and b.name.startswith('REF FC-51'): continue
            v = ov(a, b)
            if v > 0.05: hits.append((a.name, b.name, round(v, 2)))
    print('overlaps (mm3):', hits if hits else 'none')
    pb = [b for b in occ.bRepBodies if b.name.startswith('Nozzle post v8, box')][0]; cb = [b for b in box.bRepBodies if b.name.startswith('Casing box')][0]
    print('box-side post to casing box: %.1f mm' % (app.measureManager.measureMinimumDistance(pb, cb).value * 10))
    print('bodies:', [(b.name, b.isLightBulbOn) for b in comp.bRepBodies])
