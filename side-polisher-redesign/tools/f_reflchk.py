import adsk.core, adsk.fusion
# Read-only: where the reflector, sensor bracket and arms sit now, to keep the spray arch clear of them.
def run(_c):
    root = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct).rootComponent
    o = [o for o in root.occurrences if o.component.name == 'Side polisher redesign (Claude)'][0]
    for c in o.childOccurrences:
        if any(k in c.name for k in ('Reflector', 'Sensor bracket', 'ToF', 'Arm frame', 'Guide rail', 'Guide block left up', 'Guide block right up')):
            B = c.boundingBox; print(c.name, [round(v * 10, 1) for v in (B.minPoint.x, B.maxPoint.x, B.minPoint.y, B.maxPoint.y, B.minPoint.z - 21.7, B.maxPoint.z - 21.7)])
