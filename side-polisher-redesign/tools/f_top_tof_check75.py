import adsk.core, adsk.fusion, math
# Reference bodies for the top ToF clearance (REF yarn + fur envelope, R 30; REF beam cone, 35 deg full, from the sensor face to the belt),
# the cone-to-envelope clearance measured on the solids, and an overlap check of the new bracket against everything visible (world positions).
AX_X, AX_Z = 113.8, 40.3                      # roller axis, component frame (cm)
SX, SZ = 113.8 - 7.5, 46.35                   # sensor centre and face: 75 mm before the axis, 246.5 above the belt (cm)
def run(_c):
    app = adsk.core.Application.get(); d = adsk.fusion.Design.cast(app.activeProduct); root = d.rootComponent
    occ = [o for o in root.occurrences if o.component.name == 'Top polisher redesign (Claude)'][0]; comp = occ.component
    for n in ('REF yarn + fur envelope (R30)', 'REF ToF beam cone (35 deg)'):
        b = comp.bRepBodies.itemByName(n)
        if b: b.deleteMe()
    tm = adsk.fusion.TemporaryBRepManager.get(); P = adsk.core.Point3D.create
    env = tm.createCylinderOrCone(P(AX_X, -4.9, AX_Z), 3.0, P(AX_X, 4.5, AX_Z), 3.0)
    h = SZ - 21.7; r = h * math.tan(math.radians(17.5))
    cone = tm.createCylinderOrCone(P(SX, 0, SZ), 0.001, P(SX, 0, 21.7), r)
    bf = comp.features.baseFeatures.add(); bf.startEdit()
    e = comp.bRepBodies.add(env, bf); c = comp.bRepBodies.add(cone, bf); bf.finishEdit()
    bods = list(comp.bRepBodies)
    e = [b for b in bods if abs(b.volume - env.volume) < 1e-6][0]; c = [b for b in bods if abs(b.volume - cone.volume) < 1e-6][0]
    e.name = 'REF yarn + fur envelope (R30)'; c.name = 'REF ToF beam cone (35 deg)'
    mr = app.measureManager.measureMinimumDistance(e.createForAssemblyContext(occ), c.createForAssemblyContext(occ))
    print('cone to yarn+fur envelope: %.1f mm (target >= 15)' % (mr.value * 10))
    # overlaps of the new bracket and board with everything visible, as world-placed proxies
    mine = [b for b in occ.bRepBodies if b.name.startswith('ToF bracket (75') or b.name.startswith('ToF board (stand-in, 75')]
    others = []
    def walk(o):
        if not o.isLightBulbOn: return
        others.extend([b for b in o.bRepBodies if b.isLightBulbOn and b.faces.count and not b.name.startswith('REF') and b not in mine]); [walk(x) for x in o.childOccurrences]
    others += [b for b in root.bRepBodies if b.isLightBulbOn]
    for o in root.occurrences: walk(o)
    hits = []
    for a in mine:
        A = a.boundingBox
        for b in others:
            B = b.boundingBox
            if A.maxPoint.x < B.minPoint.x or B.maxPoint.x < A.minPoint.x or A.maxPoint.y < B.minPoint.y or B.maxPoint.y < A.minPoint.y or A.maxPoint.z < B.minPoint.z or B.maxPoint.z < A.minPoint.z: continue
            t = tm.copy(a); tm.booleanOperation(t, tm.copy(b), adsk.fusion.BooleanTypes.IntersectionBooleanType)
            if t and t.volume * 1000 > 0.05: hits.append((a.name, b.name, round(t.volume * 1000, 2)))
    print('overlaps (mm3):', hits if hits else 'none')
    # the beam cone must not hit the bracket or the carriage either
    hits = []
    cp = [b for b in occ.bRepBodies if b.name == 'REF ToF beam cone (35 deg)'][0]
    for b in occ.bRepBodies:
        if b.isLightBulbOn and not b.name.startswith('REF') and 'board' not in b.name.lower():
            t = tm.copy(cp); tm.booleanOperation(t, tm.copy(b), adsk.fusion.BooleanTypes.IntersectionBooleanType)
            if t and t.volume * 1000 > 0.05: hits.append((b.name, round(t.volume * 1000, 2)))
    print('beam cone hits:', hits if hits else 'nothing on the carriage')
