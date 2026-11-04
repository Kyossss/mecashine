import adsk.core, adsk.fusion
D = 'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/'
ONLY = ('block',)
MAP = {'block_L0': 'Guide block left upstream', 'block_L1': 'Guide block left downstream', 'block_R0': 'Guide block right downstream', 'block_R1': 'Guide block right upstream',
       'clamp_L0': 'Flange clamp left upstream', 'clamp_L1': 'Flange clamp left downstream', 'clamp_R0': 'Flange clamp right downstream', 'clamp_R1': 'Flange clamp right upstream'}
NEW = {'block': 'Guide block (flange cap)', 'clamp': 'Flange clamp (bottom plate)'}
def run(_context: str):
    app = adsk.core.Application.get()
    if not app.activeDocument.name.startswith('Conveyor assembly 2'): raise Exception('active doc ' + app.activeDocument.name)
    root = adsk.fusion.Design.cast(app.activeProduct).rootComponent
    top = [o for o in root.occurrences if o.component.name == 'Side polisher redesign (Claude)'][0]
    for f, cname in MAP.items():
        if not f.startswith(ONLY): continue
        occ = [c for c in top.childOccurrences if c.component.name == cname]
        if len(occ) != 1: raise Exception('not found ' + cname)
        occ = occ[0]
        before = set(o.entityToken for o in root.occurrences)
        opt = app.importManager.createSTEPImportOptions(D + f + '.step'); opt.isViewFit = False
        app.importManager.importToTarget(opt, root)
        tmp = [o for o in root.occurrences if o.entityToken not in before]
        nb = ([b for o in tmp for b in o.bRepBodies] + [b for o in tmp for c in o.childOccurrences for b in c.bRepBodies])[0]
        olds = [occ.bRepBodies.item(i) for i in range(occ.bRepBodies.count) if occ.bRepBodies.item(i).isLightBulbOn]
        user_edited = any(not isinstance(f, adsk.fusion.CopyPasteBody) and f.objectType != adsk.fusion.CopyPasteBody.classType() for f in occ.component.features)   # the user added features: keep theirs, hidden
        app_ = olds[0].appearance if olds else None
        # occurrence transform is identity in this assembly; body coords are in cm in root space
        copy = nb.copyToComponent(occ); copy.name = NEW[f.split('_')[0]]
        if app_: copy.appearance = app_
        ov = round(sum(b.volume for b in olds), 2)
        for b in olds:
            if user_edited:
                b.isLightBulbOn = False
                if not b.name.endswith('(your edit, hidden)'): b.name = b.name + ' (your edit, hidden)'
            else: b.deleteMe()
        for o in tmp: o.deleteMe()
        bb = copy.boundingBox
        print(f, '->', cname, 'kept your edited body hidden' if user_edited else '', 'vol', ov, '->', round(copy.volume, 2), [round(v * 10, 1) for v in (bb.minPoint.x, bb.maxPoint.x, bb.minPoint.y, bb.maxPoint.y, bb.minPoint.z, bb.maxPoint.z)])
