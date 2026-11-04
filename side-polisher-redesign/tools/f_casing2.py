import adsk.core, adsk.fusion
# Casing box colours like the real one (grey box, one red and one black button), and check the TFT instance.
def run(_c):
    app = adsk.core.Application.get(); d = adsk.fusion.Design.cast(app.activeProduct); root = d.rootComponent
    comp = [o for o in root.occurrences if o.component.name == 'Casing box (Claude)'][0].component
    lib = [l for l in app.materialLibraries if 'Appearance' in l.name][0]
    def ap(names):
        for n in names:
            a = lib.appearances.itemByName(n)
            if a: return d.appearances.itemByName(n) or d.appearances.addByCopy(a, n)
        return None
    grey = ap(['Paint - Enamel Glossy (Grey)', 'Paint - Enamel Glossy (Light Grey)', 'Plastic - Matte (Gray)'])
    red = ap(['Plastic - Glossy (Red)', 'Paint - Enamel Glossy (Red)'])
    black = ap(['Plastic - Glossy (Black)', 'Plastic - Matte (Black)'])
    for b in comp.bRepBodies:
        a = grey if b.name.startswith('Casing') else red if 'red' in b.name else black if 'black' in b.name else None
        if a: b.appearance = a
        print(b.name, b.appearance.name)
    for o in root.occurrences:
        if o.component.name.startswith('TFT SPI'):
            B = o.boundingBox; print('TFT', o.name, o.isLightBulbOn, [round(v * 10, 1) for v in (B.minPoint.x, B.maxPoint.x, B.minPoint.y, B.maxPoint.y, B.minPoint.z, B.maxPoint.z)])
