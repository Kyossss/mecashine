import adsk.core, adsk.fusion
# Replace the IR shelf body with the rebuilt one (its screw hole moved to z 15 to meet the post's new hole column).
def run(_c):
    app = adsk.core.Application.get(); d = adsk.fusion.Design.cast(app.activeProduct); root = d.rootComponent
    occ = [o for o in root.occurrences if o.component.name == 'Spray station (Claude)'][0]; comp = occ.component
    old = comp.bRepBodies.itemByName('IR sensor shelf (universal)'); ap = old.appearance; old.deleteMe()
    before = set(o.entityToken for o in root.occurrences)
    opt = app.importManager.createSTEPImportOptions('F:/Research/ASPS/spray station/fusion/ir-shelf.step'); opt.isViewFit = False
    app.importManager.importToTarget(opt, root)
    tmp = [o for o in root.occurrences if o.entityToken not in before]
    nb = [b for o in tmp for b in o.bRepBodies][0]
    cp = nb.copyToComponent(occ); cp.name = 'IR sensor shelf (universal)'; cp.appearance = ap
    for o in tmp: o.deleteMe()
    print('shelf', round(cp.volume, 2))
