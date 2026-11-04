import adsk.core, adsk.fusion
def run(_c):
    root = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct).rootComponent
    comp = [o for o in root.occurrences if o.component.name == 'Conveyor real length (Claude)'][0].component
    p = comp.features.rectangularPatternFeatures.item(0)
    print('q1', p.quantityOne.value, 'q2', p.quantityTwo.value, 'd2', p.distanceTwo.value, 'dir2', p.directionTwoEntity.objectType if p.directionTwoEntity else None)
    for b in [b for b in comp.bRepBodies if b.name.startswith('Belt slat upper')][:4]:
        B = b.boundingBox; print(b.name, [round(v * 10, 1) for v in (B.minPoint.x, B.minPoint.y, B.maxPoint.y, B.minPoint.z)])
