import adsk.core, adsk.fusion, json, base64, array, os
# Read-only: display meshes for the before/after page. Before = your original top-station bodies (now hidden),
# after = the bodies in 'Top polisher redesign (Claude)'; shared = the station parts both use. Frame: x - 1138, z above the belt, 0.1 mm units.
OUT = 'F:/Research/ASPS/top-roller-proposal/beforeafter-mesh.json'
def enc(b):
    if isinstance(b, adsk.fusion.MeshBody): m = b.displayMesh
    else:
        calc = b.meshManager.createMeshCalculator(); calc.setQuality(adsk.fusion.TriangleMeshQualityOptions.NormalQualityTriangleMesh); m = calc.calculate()
    c = m.nodeCoordinatesAsFloat; ix = m.nodeIndices; pts = array.array('h')
    for i in ix: pts.extend((int(round(c[3 * i] * 100)) - 11380, int(round(c[3 * i + 1] * 100)), int(round(c[3 * i + 2] * 100)) - 2170))
    return base64.b64encode(pts.tobytes()).decode()
def run(_c):
    root = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct).rootComponent
    out = {'before': {}, 'after': {}, 'shared': {}}
    KIND = {'Body67': 'carriage', 'Body68': 'motorholder', 'Body85': 'oldcore', 'Body70': 'sensorbracket'}
    SHARED = {'Body27': 'liftshaft', 'Body83': 'liftbrkt', 'Body45': 'liftbrkt', 'Body44': 'servo', 'Body41': 'column', 'Body43': 'column', 'Body39': 'column'}
    for b in root.bRepBodies:
        if b.name in KIND: out['before'][b.name] = {'kind': KIND[b.name], 'move': True, 'm': enc(b)}
        elif b.name in SHARED and b.isLightBulbOn: out['shared'][b.name] = {'kind': SHARED[b.name], 'move': SHARED[b.name] not in ('column',), 'm': enc(b)}
    comp = [o for o in root.occurrences if o.component.name == 'Top polisher redesign (Claude)'][0].component
    def kind(n):
        for k, v in (('Carriage', 'carriage'), ('Motor holder', 'motorholder'), ('drive', 'drive'), ('bar', 'bar'), ('idler', 'idler'), ('608ZZ', 'bearing'), ('Tie disc', 'disc'), ('ToF bracket', 'bracket'), ('ToF board', 'board')):
            if k.lower() in n.lower(): return v
        return 'other'
    for b in comp.bRepBodies: out['after'][b.name] = {'kind': kind(b.name), 'move': True, 'm': enc(b)}
    def walk(occs):
        for o in occs:
            if not o.isLightBulbOn: continue
            nm = o.component.name
            for b in o.bRepBodies:
                if not b.isLightBulbOn or b.faces.count == 0: continue
                bb = b.boundingBox
                if 'Healical Rack (200' in nm: out['shared'][nm + '/' + b.name] = {'kind': 'rack', 'move': False, 'm': enc(b)}
                elif 'Healical Gear' in nm: out['shared'][nm + '/' + b.name] = {'kind': 'rack', 'move': True, 'm': enc(b)}
                elif nm == 'Conveyor belt system' and bb.minPoint.z * 10 > 200 and bb.maxPoint.z * 10 < 220 and 950 < bb.minPoint.x * 10 < 1320: out['shared']['slat' + b.name] = {'kind': 'belt', 'move': False, 'm': enc(b)}
            walk(o.childOccurrences)
    walk(root.occurrences)
    json.dump(out, open(OUT, 'w'))
    print('before', sorted(out['before']), '| after', len(out['after']), '| shared', len(out['shared']))
