import adsk.core, adsk.fusion, collections
# Read-only: what is in 'Conveyor real length (Claude)', grouped by name and height.
def run(_c):
    root = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct).rootComponent
    comp = [o for o in root.occurrences if o.component.name == 'Conveyor real length (Claude)'][0].component
    g = collections.defaultdict(list)
    for b in comp.bRepBodies:
        B = b.boundingBox; g[(b.name.split(' (')[0], round(B.minPoint.z * 10), round(B.maxPoint.z * 10))].append(round(B.minPoint.x * 10, 1))
    for k, v in sorted(g.items()): print(k, len(v), sorted(v)[:4], '...', sorted(v)[-2:])
    print('timeline features', comp.features.rectangularPatternFeatures.count, comp.features.moveFeatures.count)
