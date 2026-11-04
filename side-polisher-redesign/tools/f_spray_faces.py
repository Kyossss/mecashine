import adsk.core, adsk.fusion
# The imported STEP faces carry their own (dark) appearance, which overrides the body's. Give every face its body's bright appearance.
def run(_c):
    root = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct).rootComponent
    occ = [o for o in root.occurrences if o.component.name == 'Spray station (Claude)'][0]
    print('occurrence override:', occ.appearance.name if occ.appearance else None)
    if occ.appearance: occ.appearance = None
    for b in occ.component.bRepBodies:
        fa = set(f.appearance.name for f in b.faces if f.appearance)
        for f in b.faces: f.appearance = b.appearance
        print(b.name, 'faces', b.faces.count, 'had', sorted(fa)[:3], '-> now', b.appearance.name)
