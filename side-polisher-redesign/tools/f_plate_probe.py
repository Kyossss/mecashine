import adsk.core, adsk.fusion, math
def run(_c):
    app = adsk.core.Application.get(); des = adsk.fusion.Design.cast(app.activeProduct); root = des.rootComponent
    b = [o for o in root.occurrences if o.name == 'Shoe plate:1'][0].bRepBodies.item(0)
    P = adsk.core.Point3D.create; ins = lambda x, y, z: b.pointContainment(P(x / 10, y / 10, z / 10)) == 0
    for cx, cy in ((309, 23), (309, -24)):
        print('peg', cx, cy)
        for z in (221.5, 223, 226, 229, 232, 236):
            hits = [r for r in (0, 1.5, 2.5, 3.0, 3.5) if any(ins(cx + r * math.cos(a), cy + r * math.sin(a), z) for a in [k * math.pi / 8 for k in range(16)])]
            print('  z %.1f solid within radius:' % z, hits[:1] if hits else 'none')
        # distance from the peg centre to the nearest solid above the flat top, in the plane z 221.5
        for r10 in range(5, 80, 5):
            r = r10 / 10
            if any(ins(cx + r * math.cos(a), cy + r * math.sin(a), 221.5) for a in [k * math.pi / 36 for k in range(72)]): print('  nearest wall at r %.1f' % r); break
        print('  plate solid at z 219.5 r 0/2.5/3:', [ins(cx + r, cy, 219.5) for r in (0, 2.5, 3)], 'bottom z 217.9 under plate?', ins(cx + 3, cy, 217.9))
    print('belt top: slats z?')
    for o in root.occurrences:
        if o.component.name == 'Conveyor real length (Claude)':
            zs = [round(x.boundingBox.maxPoint.z * 10, 2) for x in o.bRepBodies if 'upper' in x.name][:3]; print('slat tops', zs)
            near = [(x.name, round(x.boundingBox.minPoint.x * 10, 1), round(x.boundingBox.maxPoint.x * 10, 1)) for x in o.bRepBodies if 'upper' in x.name and 270 < x.boundingBox.maxPoint.x * 10 < 360]
            print(near)
