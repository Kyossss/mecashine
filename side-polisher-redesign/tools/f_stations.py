import adsk.core, adsk.fusion
# Read-only: every visible body (root, and inside each top-level occurrence) by x range, to pick what belongs to the side station (around x 925) and the top station (around x 1138).
def run(_c):
    root = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct).rootComponent
    def bb(B): return '%.0f..%.0f %.0f..%.0f %.0f..%.0f' % (B.minPoint.x * 10, B.maxPoint.x * 10, B.minPoint.y * 10, B.maxPoint.y * 10, B.minPoint.z * 10, B.maxPoint.z * 10)
    skip = ('Conveyor', 'Casing box', 'TFT SPI')
    for o in root.occurrences:
        if o.component.name.startswith(skip) or o.component.name.endswith('(Claude)'): continue
        for b in o.bRepBodies:
            if b.faces.count: print('OCC', o.name, '/', b.name, '| vis' if b.isLightBulbOn and o.isLightBulbOn else '| hidden', '|', bb(b.boundingBox))
        print('    occ transform t', [round(v * 10, 1) for v in o.transform2.translation.asArray()], 'refs', o.component.occurrences.count if False else '', 'instances', root.allOccurrencesByComponent(o.component).count)
    for b in root.bRepBodies: print('ROOT', b.name, '| vis' if b.isLightBulbOn else '| hidden', '|', bb(b.boundingBox))
