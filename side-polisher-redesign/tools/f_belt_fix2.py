import adsk.core, adsk.fusion
# Set the second direction of both slat patterns to 1 (Fusion defaulted it to 3 copies at 0 mm, so every slat was tripled).
def run(_c):
    root = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct).rootComponent
    comp = [o for o in root.occurrences if o.component.name == 'Conveyor real length (Claude)'][0].component
    for p in comp.features.rectangularPatternFeatures:
        p.quantityTwo.expression = '1'
    for label in ('Belt slat upper', 'Belt slat return'):
        got = [b for b in comp.bRepBodies if b.name.startswith(label)]
        print(label, len(got), round(min(b.boundingBox.minPoint.x for b in got) * 10, 1), '..', round(max(b.boundingBox.maxPoint.x for b in got) * 10, 1))
    print('total', comp.bRepBodies.count)
