import adsk.core, adsk.fusion
# Read-only: the conveyor assembly's bodies, grouped by size, to find the belt ends, rollers, frame and base board in the CAD.
def run(_c):
    root = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct).rootComponent
    occ = [o for o in root.occurrences if o.component.name.startswith('Conveyor belt system')][0]
    def bb(b): return (b.minPoint.x * 10, b.maxPoint.x * 10, b.minPoint.y * 10, b.maxPoint.y * 10, b.minPoint.z * 10, b.maxPoint.z * 10)
    rows = []
    def walk(o, d):
        for b in o.bRepBodies:
            if b.isLightBulbOn: rows.append((o.component.name, b.name) + bb(b.boundingBox))
        for c in o.childOccurrences:
            if c.isLightBulbOn: walk(c, d + 1)
    walk(occ, 0)
    big = [r for r in rows if (r[3] - r[2]) > 60 or (r[7] - r[6]) > 60]
    slats = [r for r in rows if 200 <= r[6] and r[7] <= 222]
    print('bodies', len(rows), 'slats', len(slats))
    if slats: print('slat x range %.0f..%.0f' % (min(r[2] for r in slats), max(r[3] for r in slats)))
    for r in sorted(big, key=lambda r: -(r[3] - r[2])): print('%s/%s | %.0f..%.0f %.0f..%.0f %.0f..%.0f' % r)
