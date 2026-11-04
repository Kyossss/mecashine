import adsk.core, adsk.fusion
def run(_c):
    d = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct); root = d.rootComponent
    print('design type', d.designType, 'snapshots', d.snapshots.count, 'hasPendingSnapshot', d.snapshots.hasPendingSnapshot)
    for o in root.occurrences:
        if o.name.startswith(('Healical', 'Servo', 'Component', 'Side', 'Top')):
            B = o.boundingBox; print(o.name, 't', [round(v * 10, 1) for v in o.transform2.translation.asArray()], 'bb x %.1f..%.1f' % (B.minPoint.x * 10, B.maxPoint.x * 10), 'grounded', o.isGrounded)
