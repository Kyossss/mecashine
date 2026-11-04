import adsk.core, adsk.fusion
# Read-only: everything in the conveyor assembly that spans the belt's width (drums, axles, slats, frame), and the off-board pieces, to locate the drums.
def run(_c):
    root = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct).rootComponent
    occ = [o for o in root.occurrences if o.component.name.startswith('Conveyor belt system')][0]
    rows = []
    def walk(o, path):
        for b in o.bRepBodies:
            if b.isLightBulbOn:
                B = b.boundingBox; rows.append((path + '/' + b.name, B.minPoint.x * 10, B.maxPoint.x * 10, B.minPoint.y * 10, B.maxPoint.y * 10, B.minPoint.z * 10, B.maxPoint.z * 10))
        for c in o.childOccurrences:
            if c.isLightBulbOn: walk(c, path + '/' + c.name)
    walk(occ, occ.name)
    slats = [r for r in rows if 200 <= r[5] and r[6] <= 222]
    for r in sorted(rows, key=lambda r: r[1]):
        if r in slats: continue
        print('%s | %.0f..%.0f %.0f..%.0f %.0f..%.0f' % r)
    xs = sorted(r[1] for r in slats); print('slats', len(slats), 'pitch', [round(xs[i + 1] - xs[i], 1) for i in range(min(5, len(xs) - 1))], 'first', round(xs[0]), 'last', round(max(r[2] for r in slats)))
