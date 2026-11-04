import adsk.core, adsk.fusion
def run(_c):
    root = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct).rootComponent
    occ = [o for o in root.occurrences if o.component.name == 'Top polisher redesign (Claude)'][0]
    print('occ transform', [round(v * 10, 2) for v in occ.transform2.translation.asArray()])
    for b in occ.component.bRepBodies:
        if 'ToF' in b.name or 'board' in b.name.lower() or 'bracket' in b.name.lower():
            B = b.boundingBox; print(b.name, '| vis' if b.isLightBulbOn else '| hidden', round(b.volume, 2), [round(v * 10, 1) for v in (B.minPoint.x, B.maxPoint.x, B.minPoint.y, B.maxPoint.y, B.minPoint.z, B.maxPoint.z)])
