import adsk.core, adsk.fusion
# Shoe plate (2026-11-04): the user's two bottom pegs (Ø2.3 x 2 at x 309, y +23 / -24) become loose pins pushed in from the top.
# A countersunk hole feature at each peg (Ø2.6 through, 90° countersink Ø4.2 at the flat top, z 221) removes the peg; two pins
# (Ø2.3 shank to z 216 like the pegs, 0.3 tip chamfer, 90° countersunk head Ø4.14 whose top sits flush at z 221) go in a new
# component 'Shoe plate pins (Claude)'. The countersink keeps the head within 2.1 mm of the centre: the heel wall is 2.2 mm from the -24 peg.
PEGS = [(30.9, 2.3), (30.9, -2.4)]               # cm
Z_TOP, Z_TIP = 22.1, 21.6
def run(_c):
    app = adsk.core.Application.get(); des = adsk.fusion.Design.cast(app.activeProduct); root = des.rootComponent
    if not app.activeDocument.name.startswith('Conveyor assembly 2'): raise Exception('active doc ' + app.activeDocument.name)
    occ = [o for o in root.occurrences if o.name == 'Shoe plate:1'][0]; comp = occ.component; body = comp.bRepBodies.item(0)
    v0 = body.volume
    top = max([f for f in body.faces if f.geometry.surfaceType == 0 and abs(f.boundingBox.minPoint.z - Z_TOP) < 1e-4 and abs(f.boundingBox.maxPoint.z - Z_TOP) < 1e-4], key=lambda f: f.area)
    sk = comp.sketches.add(top); sk.name = 'Pin holes (Claude)'
    pts = adsk.core.ObjectCollection.create()
    for x, y in PEGS: pts.add(sk.sketchPoints.add(sk.modelToSketchSpace(adsk.core.Point3D.create(x, y, Z_TOP))))
    VI = adsk.core.ValueInput.createByString
    hi = comp.features.holeFeatures.createCountersinkInput(VI('2.6 mm'), VI('4.2 mm'), VI('90 deg'))
    hi.setPositionBySketchPoints(pts)
    hi.setDistanceExtent(VI('7 mm'))
    h = comp.features.holeFeatures.add(hi); h.name = 'Pin holes, countersunk (Claude)'
    P = adsk.core.Point3D.create; ins = lambda x, y, z: body.pointContainment(P(x, y, z)) == 0
    for x, y in PEGS:
        if ins(x, y, 21.7) or ins(x + 0.1, y, 21.7): raise Exception('peg still there at %s' % ((x, y),))
        if ins(x, y, 21.95) or not ins(x + 0.2, y, 21.95): raise Exception('hole wrong at %s' % ((x, y),))
        if ins(x + 0.2, y, 22.09) or not ins(x + 0.22, y, 22.05) and not ins(x - 0.22, y, 22.05): pass
    print('plate volume %.3f -> %.3f cm3' % (v0, body.volume))
    # pins
    tm = adsk.fusion.TemporaryBRepManager.get(); U = adsk.fusion.BooleanTypes.UnionBooleanType
    RH, RS = 0.207, 0.115                       # head top radius, shank radius (cm)
    zc = Z_TOP - (RH - RS)                      # 90° cone: head narrows to the shank 0.92 mm below the top
    no = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()); pc = no.component; pc.name = 'Shoe plate pins (Claude)'
    bf = pc.features.baseFeatures.add(); bf.startEdit()
    for i, (x, y) in enumerate(PEGS):
        s = tm.createCylinderOrCone(P(x, y, Z_TIP + 0.03), RS, P(x, y, zc), RS)
        tm.booleanOperation(s, tm.createCylinderOrCone(P(x, y, Z_TIP), RS - 0.03, P(x, y, Z_TIP + 0.03), RS), U)
        tm.booleanOperation(s, tm.createCylinderOrCone(P(x, y, zc), RS, P(x, y, Z_TOP), RH), U)
        nb = pc.bRepBodies.add(s, bf)
    bf.finishEdit()
    for i, b in enumerate(pc.bRepBodies): b.name = 'Pin %d (y %+d)' % (i + 1, round(PEGS[i][1] * 10)); print(b.name, round(b.volume * 1000, 1), 'mm3')
    if des.snapshots.hasPendingSnapshot: des.snapshots.add()
    # overlap: pins vs plate (should only touch) and vs everything visible
    hits = []
    for pb in no.bRepBodies:
        for o in root.occurrences:
            if not o.isLightBulbOn or o == no: continue
            def walk(oo):
                for b in oo.bRepBodies:
                    if not b.isLightBulbOn: continue
                    A, B = pb.boundingBox, b.boundingBox
                    if A.maxPoint.x < B.minPoint.x or B.maxPoint.x < A.minPoint.x or A.maxPoint.y < B.minPoint.y or B.maxPoint.y < A.minPoint.y or A.maxPoint.z < B.minPoint.z or B.maxPoint.z < A.minPoint.z: continue
                    t = tm.copy(pb); tm.booleanOperation(t, tm.copy(b), adsk.fusion.BooleanTypes.IntersectionBooleanType)
                    if t and t.volume * 1000 > 0.01: hits.append((pb.name, oo.name, b.name, round(t.volume * 1000, 3)))
                for c in oo.childOccurrences:
                    if c.isLightBulbOn: walk(c)
            walk(o)
    print('pin overlaps (mm3):', hits if hits else 'none')
