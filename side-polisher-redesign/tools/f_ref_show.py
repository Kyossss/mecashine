import adsk.core, adsk.fusion
def run(_c):
    root = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct).rootComponent
    occ = [o for o in root.occurrences if o.component.name == 'Top polisher redesign (Claude)'][0]
    for b in occ.component.bRepBodies:
        if b.name.startswith('REF'): b.isLightBulbOn = True; b.opacity = 0.35
    print('ok')
