import adsk.core, adsk.fusion, json, base64, array
OUT = 'F:/Research/ASPS/top-roller-proposal/top-station-mesh.json'
WANT = {'Body67': 'carriage', 'Body68': 'motorholder', 'Body70': 'sensorbracket', 'Body27': 'liftshaft', 'Body83': 'liftbrkt', 'Body45': 'liftbrkt', 'Body44': 'servo', 'Body41': 'column', 'Body43': 'column', 'Body39': 'column', 'Body85': 'oldcore'}
def enc(b, tol):
    if isinstance(b, adsk.fusion.MeshBody):
        m = b.displayMesh
    else:
        calc = b.meshManager.createMeshCalculator(); calc.setQuality(adsk.fusion.TriangleMeshQualityOptions.NormalQualityTriangleMesh)
        m = calc.calculate()
    c = m.nodeCoordinatesAsFloat; ix = m.nodeIndices
    pts = array.array('h')
    for i in ix:
        pts.extend((int(round(c[3 * i] * 100)) - 11380, int(round(c[3 * i + 1] * 100)), int(round(c[3 * i + 2] * 100)) - 2170))   # 0.1 mm units, origin at the roller axis x, belt top
    return base64.b64encode(pts.tobytes()).decode(), len(ix) // 3
def run(_c):
    app = adsk.core.Application.get()
    r = adsk.fusion.Design.cast(app.activeProduct).rootComponent
    out = {}
    for b in r.bRepBodies:
        if b.name in WANT and b.isLightBulbOn:
            out[b.name] = {'kind': WANT[b.name], 'm': enc(b, 0)[0]}
    def walk(occs):
        for o in occs:
            if not o.isLightBulbOn: continue
            nm = o.component.name
            if 'FMB_Shoes' in nm:
                for mb in o.meshBodies:
                    if mb.isLightBulbOn: out['shoe'] = {'kind': 'shoe', 'm': enc(mb, 0)[0]}
            for b in o.bRepBodies:
                if not b.isLightBulbOn or b.faces.count == 0: continue
                bb = b.boundingBox
                if 'Healical Rack (200' in nm or 'Healical Gear' in nm: out[nm + '/' + b.name] = {'kind': 'rack', 'm': enc(b, 0)[0]}
                elif 'Servo+MG996R:2' in o.fullPathName and b.name in ('Axel',): out['servoaxle'] = {'kind': 'servo', 'm': enc(b, 0)[0]}
                elif nm == 'Conveyor belt system' and bb.minPoint.z * 10 > 200 and bb.maxPoint.z * 10 < 220 and 950 < bb.minPoint.x * 10 < 1320: out['slat' + b.name] = {'kind': 'belt', 'm': enc(b, 0)[0]}
            walk(o.childOccurrences)
    walk(r.occurrences)
    import os
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, 'w'))
    print('saved', len(out), 'meshes:', sorted(set(v['kind'] for v in out.values())))
