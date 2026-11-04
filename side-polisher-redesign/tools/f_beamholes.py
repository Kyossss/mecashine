import adsk.core, adsk.fusion
# Read-only: conveyor/frame bodies beside the belt between x 560 and 860, and the M3-size holes in them (cylindrical faces r 1.4..2.0 mm), for mounting the spray posts.
def run(_c):
    root = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct).rootComponent
    rows = []
    def take(b, path):
        if not b.isLightBulbOn or b.faces.count == 0: return
        B = b.boundingBox
        if B.maxPoint.x * 10 < 560 or B.minPoint.x * 10 > 860 or max(abs(B.minPoint.y), abs(B.maxPoint.y)) * 10 < 40: return
        holes = []
        for f in b.faces:
            g = f.geometry
            if isinstance(g, adsk.core.Cylinder) and 0.14 <= g.radius <= 0.20:
                o, a = g.origin, g.axis
                holes.append('r%.1f@(%.0f,%.0f,%.0f) ax(%.0f,%.0f,%.0f)' % (g.radius * 10, o.x * 10, o.y * 10, o.z * 10 - 217, a.x, a.y, a.z))
        rows.append('%s/%s | x %.0f..%.0f y %.0f..%.0f z(belt) %.0f..%.0f | %s' % (path, b.name, B.minPoint.x * 10, B.maxPoint.x * 10, B.minPoint.y * 10, B.maxPoint.y * 10, B.minPoint.z * 10 - 217, B.maxPoint.z * 10 - 217, ' '.join(sorted(set(holes))) or 'no M3 holes'))
    def walk(o, path):
        if not o.isLightBulbOn: return
        for b in o.bRepBodies: take(b, path)
        for c in o.childOccurrences: walk(c, path + '/' + c.component.name)
    for b in root.bRepBodies: take(b, 'root')
    for o in root.occurrences: walk(o, o.component.name)
    print('\n'.join(rows))
