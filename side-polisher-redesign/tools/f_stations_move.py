import adsk.core, adsk.fusion
# Stations to the real prototype's positions, measured from the casing box's station-side edge (x 700):
# side polisher tower centre 200 mm on (x 900, was 925), top polisher tower centre 440 mm on (x 1140, was 1137.5). Positions only, no shape changes.
CM = 0.1
MOVES = {
    -25.0: {'occ': ('Healical Gear (12R@0.00 m=1.2):1', 'Servo+MG996R:1', 'Component36:1', 'Component8:1', 'Healical Rack (115.0mm R@0.00 m=1.2) (1):1', 'Component38:1', 'Component39:1', 'Side polisher redesign (Claude):1'),
            'body': ('Body10', 'Body11', 'Body14', 'Body15', 'Body16', 'Body17', 'Body20', 'Body21', 'Body25', 'Body28', 'Body29', 'Body33', 'Body34', 'Body116', 'Body47', 'Body53', 'Body59', 'Body105', 'Body113')},
    2.5: {'occ': ('Healical Rack (200.0mm R@0.00 m=2.0):1', 'Healical Gear (12R@0.00 m=2.0):1', 'Servo+MG996R:2', 'Top polisher redesign (Claude):1'),
          'body': ('Body27', 'Body36', 'Body39', 'Body41', 'Body43', 'Body44', 'Body45', 'Body71', 'Body83', 'Body67', 'Body68', 'Body70', 'Body85')},
}
def run(_c):
    app = adsk.core.Application.get()
    if not app.activeDocument.name.startswith('Conveyor assembly 2'): raise Exception('active doc ' + app.activeDocument.name)
    d = adsk.fusion.Design.cast(app.activeProduct); root = d.rootComponent
    occs = {o.name: o for o in root.occurrences}; bodies = {b.name: b for b in root.bRepBodies}
    for dx, s in MOVES.items():
        miss = [n for n in s['occ'] if n not in occs] + [n for n in s['body'] if n not in bodies]
        if miss: raise Exception('not found: %s' % miss)
    for dx, s in MOVES.items():
        oc = adsk.core.ObjectCollection.create(); [oc.add(bodies[n]) for n in s['body']]
        mi = root.features.moveFeatures.createInput2(oc)
        mi.defineAsTranslateXYZ(adsk.core.ValueInput.createByReal(dx * CM), adsk.core.ValueInput.createByReal(0), adsk.core.ValueInput.createByReal(0), True)
        root.features.moveFeatures.add(mi)
        for n in s['occ']:
            o = occs[n]; m = o.transform2.copy(); t = m.translation; t.x += dx * CM; m.translation = t; o.transform2 = m
    try: d.snapshots.add()
    except Exception as e: print('snapshot:', e)
    B = bodies['Body28'].boundingBox; print('side pillar x %.1f..%.1f' % (B.minPoint.x * 10, B.maxPoint.x * 10))
    B = bodies['Body41'].boundingBox; print('top column x %.1f..%.1f' % (B.minPoint.x * 10, B.maxPoint.x * 10))
    B = occs['Side polisher redesign (Claude):1'].boundingBox; print('side component x %.1f..%.1f' % (B.minPoint.x * 10, B.maxPoint.x * 10))
    B = occs['Top polisher redesign (Claude):1'].boundingBox; print('top component x %.1f..%.1f' % (B.minPoint.x * 10, B.maxPoint.x * 10))
