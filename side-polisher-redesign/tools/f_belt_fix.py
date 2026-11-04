import adsk.core, adsk.fusion
# Redo the slat pattern in 'Conveyor real length (Claude)': the first one tripled every slat. One pattern per run, count checked.
CM = 0.1
def run(_c):
    root = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct).rootComponent
    comp = [o for o in root.occurrences if o.component.name == 'Conveyor real length (Claude)'][0].component
    F = comp.features
    F.rectangularPatternFeatures.item(0).deleteMe()
    print('after delete', comp.bRepBodies.count, [b.name for b in comp.bRepBodies if b.name.startswith('Belt')])
    n = 48; pitch = (1325.0 - 293.0) / (n - 1)
    for label in ('Belt slat upper', 'Belt slat return'):
        seed = [b for b in comp.bRepBodies if b.name == label]
        if len(seed) != 1: raise Exception('seed ' + label + ' ' + str(len(seed)))
        ents = adsk.core.ObjectCollection.create(); ents.add(seed[0])
        pi = F.rectangularPatternFeatures.createInput(ents, comp.xConstructionAxis, adsk.core.ValueInput.createByReal(n), adsk.core.ValueInput.createByReal(pitch * CM), adsk.fusion.PatternDistanceType.SpacingPatternDistanceType)
        pat = F.rectangularPatternFeatures.add(pi)
        got = [b for b in comp.bRepBodies if b.name.startswith(label)]
        print(label, 'bodies', len(got), 'x', round(min(b.boundingBox.minPoint.x for b in got) * 10, 1), '..', round(max(b.boundingBox.maxPoint.x for b in got) * 10, 1))
    print('total', comp.bRepBodies.count)
