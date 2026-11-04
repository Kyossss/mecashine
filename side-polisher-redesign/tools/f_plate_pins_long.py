import adsk.core, adsk.fusion
# Pins 2 mm longer (2026-11-04): tip at z 214 (was 216), i.e. 4 mm below the plate's bottom. Rebuilds the pin bodies in 'Shoe plate pins (Claude)'.
PEGS = [(30.9, 2.3), (30.9, -2.4)]
Z_TOP, Z_TIP = 22.1, 21.4
def run(_c):
    app = adsk.core.Application.get(); des = adsk.fusion.Design.cast(app.activeProduct); root = des.rootComponent
    if not app.activeDocument.name.startswith('Conveyor assembly 2'): raise Exception('active doc ' + app.activeDocument.name)
    no = [o for o in root.occurrences if o.component.name == 'Shoe plate pins (Claude)'][0]; pc = no.component
    for b in list(pc.bRepBodies): b.deleteMe()
    tm = adsk.fusion.TemporaryBRepManager.get(); U = adsk.fusion.BooleanTypes.UnionBooleanType; P = adsk.core.Point3D.create
    RH, RS = 0.207, 0.115; zc = Z_TOP - (RH - RS)
    bf = pc.features.baseFeatures.add(); bf.startEdit()
    for x, y in PEGS:
        s = tm.createCylinderOrCone(P(x, y, Z_TIP + 0.03), RS, P(x, y, zc), RS)
        tm.booleanOperation(s, tm.createCylinderOrCone(P(x, y, Z_TIP), RS - 0.03, P(x, y, Z_TIP + 0.03), RS), U)
        tm.booleanOperation(s, tm.createCylinderOrCone(P(x, y, zc), RS, P(x, y, Z_TOP), RH), U)
        pc.bRepBodies.add(s, bf)
    bf.finishEdit()
    for i, b in enumerate(pc.bRepBodies): b.name = 'Pin %d (y %+d), 7 mm' % (i + 1, round(PEGS[i][1] * 10)); print(b.name, round(b.volume * 1000, 1), 'mm3', round(b.boundingBox.minPoint.z * 10, 2), round(b.boundingBox.maxPoint.z * 10, 2))
    hits = []
    def walk(oo):
        for b in oo.bRepBodies:
            if not b.isLightBulbOn: continue
            for pb in no.bRepBodies:
                A, B = pb.boundingBox, b.boundingBox
                if A.maxPoint.x < B.minPoint.x or B.maxPoint.x < A.minPoint.x or A.maxPoint.y < B.minPoint.y or B.maxPoint.y < A.minPoint.y or A.maxPoint.z < B.minPoint.z or B.maxPoint.z < A.minPoint.z: continue
                t = tm.copy(pb); tm.booleanOperation(t, tm.copy(b), adsk.fusion.BooleanTypes.IntersectionBooleanType)
                if t and t.volume * 1000 > 0.01: hits.append((pb.name, oo.name, b.name, round(t.volume * 1000, 3)))
        for c in oo.childOccurrences:
            if c.isLightBulbOn: walk(c)
    for o in root.occurrences:
        if o.isLightBulbOn and o != no: walk(o)
    print('pin overlaps (mm3):', hits if hits else 'none')
    o = des.exportManager.createSTLExportOptions(pc.bRepBodies.item(0), 'F:/Research/ASPS/shoe plate pins/print/pin RAW.stl')
    o.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh; o.isBinaryFormat = True; print('export', des.exportManager.execute(o))
