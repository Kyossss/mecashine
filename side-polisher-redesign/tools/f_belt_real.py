import adsk.core, adsk.fusion, math
# Conveyor to the real prototype's length: drum axles 93 mm from the entry edge of the board and 85 mm from the exit edge
# (board x 200..1410 -> axles at x 293 and 1325, 1032 mm apart). New component with copies; your original drum and slats are hidden, not changed.
CM = 0.1
AX_IN, AX_OUT = 293.0, 1325.0
DRUM = ('Body34', 'Body35', 'Body36', 'Body66', 'Body70')   # entry drum and the slats wrapped round it (axle at x 233, z 188)
UP, LO = 'Body37', 'Body33'                                  # first slat of the upper run (z 207..217) and of the return run (z 159..169), both centred on the axle
def bb(b): return [round(v * 10, 1) for v in (b.minPoint.x, b.maxPoint.x, b.minPoint.y, b.maxPoint.y, b.minPoint.z, b.maxPoint.z)]
def run(_c):
    app = adsk.core.Application.get()
    if not app.activeDocument.name.startswith('Conveyor assembly 2'): raise Exception('active doc ' + app.activeDocument.name)
    root = adsk.fusion.Design.cast(app.activeProduct).rootComponent
    if [o for o in root.occurrences if o.component.name == 'Conveyor real length (Claude)']: raise Exception('component already exists')
    cv = [o for o in root.occurrences if o.component.name.startswith('Conveyor belt system')][0]
    belt = [o for o in cv.childOccurrences if o.component.name == 'Conveyor belt system'][0]
    src = {b.name: b for b in belt.bRepBodies}
    upper = [b for b in belt.bRepBodies if b.isLightBulbOn and b.boundingBox.minPoint.x >= 21.7 and abs(b.boundingBox.minPoint.z - 20.7) < 0.01]
    lower = [b for b in belt.bRepBodies if b.isLightBulbOn and b.boundingBox.minPoint.x >= 21.7 and abs(b.boundingBox.minPoint.z - 15.9) < 0.01 and b.boundingBox.maxPoint.y - b.boundingBox.minPoint.y > 12.9 and b.boundingBox.maxPoint.x - b.boundingBox.minPoint.x < 3.1]
    print('original slats upper', len(upper), 'lower', len(lower))
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()); comp = occ.component; comp.name = 'Conveyor real length (Claude)'
    F = comp.features
    def move(bodies, dx):
        oc = adsk.core.ObjectCollection.create(); [oc.add(b) for b in bodies]
        mi = F.moveFeatures.createInput2(oc); mi.defineAsTranslateXYZ(adsk.core.ValueInput.createByReal(dx * CM), adsk.core.ValueInput.createByReal(0), adsk.core.ValueInput.createByReal(0), True)
        F.moveFeatures.add(mi)
    # entry drum, 60 mm further in
    d_in = []
    for n in DRUM:
        c = src[n].copyToComponent(occ); c.name = 'Entry drum ' + n; d_in.append(c)
    move(d_in, AX_IN - 233.0)
    # exit drum: the entry drum turned half round a vertical axis midway between the two axles
    d_out = []
    for b in d_in:
        c = b.copyToComponent(occ); c.name = b.name.replace('Entry', 'Exit'); d_out.append(c)
    oc = adsk.core.ObjectCollection.create(); [oc.add(b) for b in d_out]
    m = adsk.core.Matrix3D.create(); m.setToRotation(math.pi, adsk.core.Vector3D.create(0, 0, 1), adsk.core.Point3D.create((AX_IN + AX_OUT) / 2 * CM, 0, 0))
    mi = F.moveFeatures.createInput2(oc); mi.defineAsFreeMove(m); F.moveFeatures.add(mi)
    # both runs of slats, from axle to axle
    n = 48; pitch = (AX_OUT - AX_IN) / (n - 1)
    runs = []
    for nm, label in ((UP, 'Belt slat upper'), (LO, 'Belt slat return')):
        c = src[nm].copyToComponent(occ); c.name = label; move([c], AX_IN - 233.0); runs.append(c)
    ents = adsk.core.ObjectCollection.create(); [ents.add(b) for b in runs]
    pi = F.rectangularPatternFeatures.createInput(ents, comp.xConstructionAxis, adsk.core.ValueInput.createByString(str(n)), adsk.core.ValueInput.createByReal(pitch * CM), adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
    pat = F.rectangularPatternFeatures.add(pi)
    xs = [b.boundingBox.maxPoint.x * 10 for b in comp.bRepBodies if b.name.startswith('Belt') or 'Belt' in b.name]
    print('bodies in component', comp.bRepBodies.count, 'slat max x', round(max(b.boundingBox.maxPoint.x for b in comp.bRepBodies) * 10, 1), 'min x', round(min(b.boundingBox.minPoint.x for b in comp.bRepBodies) * 10, 1))
    for b in d_in + d_out: print(b.name, bb(b.boundingBox))
    # hide your originals
    for b in [src[x] for x in DRUM] + upper + lower: b.isLightBulbOn = False
    print('hid', len(DRUM) + len(upper) + len(lower), 'original bodies; pitch', round(pitch, 2))
