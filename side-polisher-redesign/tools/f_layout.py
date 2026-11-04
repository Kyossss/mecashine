import adsk.core, adsk.fusion
# Read-only: bounding boxes (mm) of every visible top-level occurrence and root body, to compare the CAD layout with the real prototype.
def run(_c):
    root = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct).rootComponent
    def bb(b): return '%.0f..%.0f  %.0f..%.0f  %.0f..%.0f' % (b.minPoint.x * 10, b.maxPoint.x * 10, b.minPoint.y * 10, b.maxPoint.y * 10, b.minPoint.z * 10, b.maxPoint.z * 10)
    print('ALL', bb(root.boundingBox))
    for o in root.occurrences:
        print('OCC', o.name, '| vis' if o.isLightBulbOn else '| hidden', '|', bb(o.boundingBox), '| children', o.childOccurrences.count, 'bodies', o.bRepBodies.count)
        for c in o.childOccurrences:
            print('   ', c.name, '| vis' if c.isLightBulbOn else '| hidden', '|', bb(c.boundingBox))
    for b in root.bRepBodies:
        if b.isLightBulbOn: print('BODY', b.name, '|', bb(b.boundingBox))
