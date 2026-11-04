import adsk.core, adsk.fusion
D = 'F:/Research/ASPS/side-polisher-redesign/tools/fx/'
# (file, target component, new component?, body names in order of height (by top))
JOBS = [('refl_R', 'Reflector right', False, ['Reflector (145 x 120 face, white insert recess)'])]
def run(_context: str):
    app = adsk.core.Application.get()
    if not app.activeDocument.name.startswith('Conveyor assembly 2'): raise Exception('active doc ' + app.activeDocument.name)
    root = adsk.fusion.Design.cast(app.activeProduct).rootComponent
    top = [o for o in root.occurrences if o.component.name == 'Side polisher redesign (Claude)'][0]
    for f, cname, new, names in JOBS:
        found = [c for c in top.childOccurrences if c.component.name == cname]
        if new:
            if found: raise Exception('already exists: ' + cname)
            occ = top.component.occurrences.addNewComponent(adsk.core.Matrix3D.create())
            occ.component.name = cname
            occ = [c for c in top.childOccurrences if c.component.name == cname][0]      # the occurrence in assembly context
        else:
            if len(found) != 1: raise Exception('not found: ' + cname)
            occ = found[0]
            if any(f.objectType not in (adsk.fusion.CopyPasteBody.classType(), adsk.fusion.BaseFeature.classType()) for f in occ.component.features): raise Exception('user-edited, skipped: ' + cname)
        before = set(o.entityToken for o in root.occurrences)
        opt = app.importManager.createSTEPImportOptions(D + f + '.step'); opt.isViewFit = False
        app.importManager.importToTarget(opt, root)
        tmp = [o for o in root.occurrences if o.entityToken not in before]
        nbs = [b for o in tmp for b in o.bRepBodies] + [b for o in tmp for c in o.childOccurrences for b in c.bRepBodies]
        nbs.sort(key=lambda b: b.boundingBox.maxPoint.z)
        if len(nbs) != len(names): raise Exception('%s: got %d bodies' % (f, len(nbs)))
        olds = [occ.bRepBodies.item(i) for i in range(occ.bRepBodies.count)]
        app_ = olds[0].appearance if olds else None
        ov = round(sum(b.volume for b in olds), 2)
        nv = 0
        for b, n in zip(nbs, names):
            cp = b.copyToComponent(occ); cp.name = n
            if app_: cp.appearance = app_
            nv += cp.volume
        for b in olds: b.deleteMe()
        for o in tmp: o.deleteMe()
        print(cname, 'new' if new else 'replaced', 'vol', ov, '->', round(nv, 2), 'bodies', len(names))
