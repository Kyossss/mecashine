import adsk.core, adsk.fusion
# Second step of the station move: the side-polisher occurrences (-25 mm in x), captured right away. The bodies already moved.
NAMES = ('Healical Gear (12R@0.00 m=1.2):1', 'Servo+MG996R:1', 'Component36:1', 'Component8:1', 'Healical Rack (115.0mm R@0.00 m=1.2) (1):1', 'Component38:1', 'Component39:1', 'Side polisher redesign (Claude):1')
def run(_c):
    d = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct); root = d.rootComponent
    occs = {o.name: o for o in root.occurrences}
    for n in NAMES:
        o = occs[n]; m = o.transform2.copy(); t = m.translation; t.x += -2.5; m.translation = t; o.transform2 = m
    d.snapshots.add()
    for n in NAMES:
        o = occs[n]; B = o.boundingBox; print(n, 't x %.1f' % (o.transform2.translation.x * 10), 'bb x %.1f..%.1f' % (B.minPoint.x * 10, B.maxPoint.x * 10))
