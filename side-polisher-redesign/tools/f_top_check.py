import adsk.core, adsk.fusion
# Read-only: overlap volume between every pair of the new top-polisher bodies, and between them and the visible station bodies nearby.
def run(_c):
    app = adsk.core.Application.get(); tm = adsk.fusion.TemporaryBRepManager.get()
    root = adsk.fusion.Design.cast(app.activeProduct).rootComponent
    comp = [o for o in root.occurrences if o.component.name == 'Top polisher redesign (Claude)'][0].component
    mine = [b for b in comp.bRepBodies]
    near = [b for b in root.bRepBodies if b.isLightBulbOn and b.name in ('Body27', 'Body83', 'Body45', 'Body44', 'Body41', 'Body43', 'Body39', 'Body71', 'Body36')]
    def ov(a, b):
        A, B = a.boundingBox, b.boundingBox
        if A.maxPoint.x < B.minPoint.x or B.maxPoint.x < A.minPoint.x or A.maxPoint.y < B.minPoint.y or B.maxPoint.y < A.minPoint.y or A.maxPoint.z < B.minPoint.z or B.maxPoint.z < A.minPoint.z: return 0.0
        t = tm.copy(a); tm.booleanOperation(t, tm.copy(b), adsk.fusion.BooleanTypes.IntersectionBooleanType)
        return t.volume * 1000 if t else 0.0
    hits = []
    for i, a in enumerate(mine):
        for b in mine[i + 1:] + near:
            v = ov(a, b)
            if v > 0.05: hits.append((a.name, b.name, round(v, 2)))
    print('overlaps (mm3):', hits if hits else 'none')
