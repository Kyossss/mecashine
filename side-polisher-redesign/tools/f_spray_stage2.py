import adsk.core, adsk.fusion
# Spray station (approved 2026-10-26): new component with the two nozzle posts, the IR shelf, and reference bodies for the elbows, nozzles and the FC-51.
# Parts come in place from F:\Research\ASPS\spray station\fusion\*.step (made by spray_station.py). Nothing existing is changed.
D = 'F:/Research/ASPS/spray station/fusion/'
PARTS = [('spray-post-box-side', 'Nozzle post, box side'), ('spray-post-far-side', 'Nozzle post, far side (IR slot used)'), ('ir-shelf', 'IR sensor shelf (universal)'),
         ('ref-elbow-box-side', 'REF PV6 elbow, box side'), ('ref-nozzle-box-side', 'REF nozzle, box side'), ('ref-elbow-far-side', 'REF PV6 elbow, far side'),
         ('ref-nozzle-far-side', 'REF nozzle, far side'), ('ref-fc51', 'REF FC-51 IR module')]
def bb(b): return [round(v * 10, 1) for v in (b.minPoint.x, b.maxPoint.x, b.minPoint.y, b.maxPoint.y, b.minPoint.z, b.maxPoint.z)]
def run(_c):
    app = adsk.core.Application.get()
    if not app.activeDocument.name.startswith('Conveyor assembly 2'): raise Exception('active doc ' + app.activeDocument.name)
    root = adsk.fusion.Design.cast(app.activeProduct).rootComponent
    occ = [o for o in root.occurrences if o.component.name == 'Spray station (Claude)'][0]; comp = occ.component
    for o in [o for o in root.occurrences if 'fc51' in o.component.name.lower()]: print('removing leftover import', o.name); o.deleteMe()
    if any(b.name.startswith('REF FC-51') for b in comp.bRepBodies): raise Exception('FC-51 already there')
    before = set(o.entityToken for o in root.occurrences)
    opt = app.importManager.createSTEPImportOptions(D + 'ref-fc51.step'); opt.isViewFit = False
    app.importManager.importToTarget(opt, root)
    tmp = [o for o in root.occurrences if o.entityToken not in before]
    nbs = [b for o in tmp for b in o.bRepBodies] + [b for o in tmp for c in o.childOccurrences for b in c.bRepBodies]
    nbs.sort(key=lambda b: (b.boundingBox.minPoint.x, b.boundingBox.minPoint.y))
    for i, b in enumerate(nbs):
        cp = b.copyToComponent(occ); cp.name = 'REF FC-51 IR module' + ('' if b.volume > 0.3 else ' LED %d' % i)
        print(cp.name, round(cp.volume, 3), bb(cp.boundingBox))
    for o in tmp: o.deleteMe()
    print('component bodies', comp.bRepBodies.count)
    # overlaps with everything visible nearby, and between the new bodies
    tm = adsk.fusion.TemporaryBRepManager.get()
    mine = list(comp.bRepBodies); others = []
    def walk(o):
        if not o.isLightBulbOn or o == occ: return
        others.extend([b for b in o.bRepBodies if b.isLightBulbOn and b.faces.count]); [walk(c) for c in o.childOccurrences]
    others += [b for b in root.bRepBodies if b.isLightBulbOn]
    for o in root.occurrences: walk(o)
    def ov(a, b):
        A, B = a.boundingBox, b.boundingBox
        if A.maxPoint.x < B.minPoint.x or B.maxPoint.x < A.minPoint.x or A.maxPoint.y < B.minPoint.y or B.maxPoint.y < A.minPoint.y or A.maxPoint.z < B.minPoint.z or B.maxPoint.z < A.minPoint.z: return 0.0
        t = tm.copy(a); tm.booleanOperation(t, tm.copy(b), adsk.fusion.BooleanTypes.IntersectionBooleanType)
        return t.volume * 1000 if t else 0.0
    hits = []
    for i, a in enumerate(mine):
        for b in mine[i + 1:] + others:
            v = ov(a, b)
            if v > 0.05: hits.append((a.name, b.name, round(v, 2)))
    print('overlaps (mm3):', hits if hits else 'none')
