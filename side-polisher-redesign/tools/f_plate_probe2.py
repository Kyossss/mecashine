import adsk.core, adsk.fusion, math
def run(_c):
    app = adsk.core.Application.get(); des = adsk.fusion.Design.cast(app.activeProduct); root = des.rootComponent
    b = [o for o in root.occurrences if o.name == 'Shoe plate:1'][0].bRepBodies.item(0)
    P = adsk.core.Point3D.create; ins = lambda x, y, z: b.pointContainment(P(x / 10, y / 10, z / 10)) == 0
    for cx, cy in ((309, 23), (309, -24)):
        for z in (221.05, 222, 225):
            for r100 in range(150, 400, 5):
                r = r100 / 100
                hit = [a for a in range(0, 360, 3) if ins(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)), z)]
                if hit: print(cx, cy, 'z', z, 'wall at r %.2f, direction %d deg' % (r, hit[len(hit) // 2])); break
