import adsk.core, adsk.fusion
# Hide the REF clearance bodies again (kept for later checks) and give the user back the document they had active.
def run(_c):
    app = adsk.core.Application.get(); root = adsk.fusion.Design.cast(app.activeProduct).rootComponent
    occ = [o for o in root.occurrences if o.component.name == 'Top polisher redesign (Claude)'][0]
    for b in occ.component.bRepBodies:
        if b.name.startswith('REF'): b.isLightBulbOn = False
    print([(b.name, b.isLightBulbOn) for b in occ.component.bRepBodies if 'ToF' in b.name or b.name.startswith('REF')])
    for d in app.documents:
        if d.name == 'Coin dispenser test fit': d.activate(); print('active again:', d.name)
