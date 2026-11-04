import adsk.core, adsk.fusion
def run(_c):
    app = adsk.core.Application.get(); des = adsk.fusion.Design.cast(app.activeProduct); root = des.rootComponent
    b = [o for o in root.occurrences if o.name == 'Shoe plate:1'][0].bRepBodies.item(0)
    P = adsk.core.Point3D.create; ins = lambda x, y, z: b.pointContainment(P(x / 10, y / 10, z / 10)) == 0
    for (x, y) in ((320, 40), (325, 45), (330, -45), (290, 0), (300, 10)):
        print((x, y), ''.join('#' if ins(x, y, z / 2) else '.' for z in range(436, 478)), '(z 218..239 by 0.5)')
