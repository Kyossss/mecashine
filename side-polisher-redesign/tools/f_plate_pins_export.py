import adsk.core, adsk.fusion
OUT = 'F:/Research/ASPS/shoe plate pins/print/'
def run(_c):
    app = adsk.core.Application.get(); des = adsk.fusion.Design.cast(app.activeProduct); root = des.rootComponent; em = des.exportManager
    plate = [o for o in root.occurrences if o.name == 'Shoe plate:1'][0].bRepBodies.item(0)
    pin = [o for o in root.occurrences if o.component.name == 'Shoe plate pins (Claude)'][0].bRepBodies.item(0)
    for b, f in ((plate, 'shoe-plate (pin holes) x1 RAW.stl'), (pin, 'shoe-plate pin x2 RAW.stl')):
        o = em.createSTLExportOptions(b, OUT + f); o.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh; o.isBinaryFormat = True
        print(f, em.execute(o))
