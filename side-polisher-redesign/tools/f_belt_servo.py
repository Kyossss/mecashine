import adsk.core, adsk.fusion
# Belt servo to the exit end of the track, like the real one: servo Servo+MG996R:3 and its mount Body35 move +959.5 mm in x so the
# servo axle (x 365.5) lines up with the exit drum axle (x 1325). Same side (-y) and height. Positions only.
DX = 1325.0 - 365.5
def run(_c):
    app = adsk.core.Application.get()
    if not app.activeDocument.name.startswith('Conveyor assembly 2'): raise Exception('active doc ' + app.activeDocument.name)
    d = adsk.fusion.Design.cast(app.activeProduct); root = d.rootComponent
    mount = [b for b in root.bRepBodies if b.name == 'Body35'][0]
    servo = [o for o in root.occurrences if o.name == 'Servo+MG996R:3'][0]
    oc = adsk.core.ObjectCollection.create(); oc.add(mount)
    mi = root.features.moveFeatures.createInput2(oc)
    mi.defineAsTranslateXYZ(adsk.core.ValueInput.createByReal(DX / 10), adsk.core.ValueInput.createByReal(0), adsk.core.ValueInput.createByReal(0), True)
    root.features.moveFeatures.add(mi)
    m = servo.transform2.copy(); t = m.translation; t.x += DX / 10; m.translation = t; servo.transform2 = m
    d.snapshots.add()
    # anything it now touches?
    tm = adsk.fusion.TemporaryBRepManager.get()
    mine = [mount] + [b for b in servo.bRepBodies]
    others = [b for b in root.bRepBodies if b.isLightBulbOn and b != mount]
    def walk(occs):
        for o in occs:
            if not o.isLightBulbOn or o == servo: continue
            others.extend([b for b in o.bRepBodies if b.isLightBulbOn and b.faces.count]); walk(o.childOccurrences)
    walk(root.occurrences)
    hits = []
    for a in mine:
        A = a.boundingBox
        for b in others:
            B = b.boundingBox
            if A.maxPoint.x < B.minPoint.x or B.maxPoint.x < A.minPoint.x or A.maxPoint.y < B.minPoint.y or B.maxPoint.y < A.minPoint.y or A.maxPoint.z < B.minPoint.z or B.maxPoint.z < A.minPoint.z: continue
            t1 = tm.copy(a); tm.booleanOperation(t1, tm.copy(b), adsk.fusion.BooleanTypes.IntersectionBooleanType)
            if t1 and t1.volume * 1000 > 0.05: hits.append((a.name, b.name, round(t1.volume * 1000, 1)))
    def bb(B): return [round(v * 10, 1) for v in (B.minPoint.x, B.maxPoint.x, B.minPoint.y, B.maxPoint.y, B.minPoint.z, B.maxPoint.z)]
    print('mount', bb(mount.boundingBox)); print('servo', bb(servo.boundingBox)); print('overlaps (mm3):', hits or 'none')
