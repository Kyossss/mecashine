import adsk.core, adsk.fusion
# Put the new TFT instance into the lid window: its min corner should be at x 364, y 273.5, z 290.4.
def run(_c):
    root = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct).rootComponent
    o = [o for o in root.occurrences if o.component.name.startswith('TFT SPI') and o.isLightBulbOn][0]
    B = o.boundingBox
    d = adsk.core.Vector3D.create(36.40 - B.minPoint.x, 27.35 - B.minPoint.y, 29.04 - B.minPoint.z)
    m = o.transform2.copy(); t = m.translation; t.add(d); m.translation = t; o.transform2 = m
    try: adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct).snapshots.add()
    except Exception as e: print('snapshot:', e)
    B = o.boundingBox; print('TFT', [round(v * 10, 1) for v in (B.minPoint.x, B.maxPoint.x, B.minPoint.y, B.maxPoint.y, B.minPoint.z, B.maxPoint.z)])
