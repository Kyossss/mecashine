import adsk.core, adsk.fusion
# Bright appearances for the spray station bodies: posts yellow, IR shelf green, elbows blue, nozzles silver-grey, FC-51 blue board with white LEDs.
COLORS = {'Nozzle post': ('Spray - post yellow', (255, 196, 0)), 'IR sensor shelf': ('Spray - shelf green', (60, 200, 90)),
          'REF PV6 elbow': ('Spray - elbow blue', (60, 140, 255)), 'REF nozzle': ('Spray - nozzle silver', (215, 220, 225)),
          'REF FC-51 IR module LED': ('Spray - LED white', (245, 245, 245)), 'REF FC-51 IR module': ('Spray - FC51 blue', (30, 110, 230))}
def run(_c):
    app = adsk.core.Application.get(); d = adsk.fusion.Design.cast(app.activeProduct); root = d.rootComponent
    comp = [o for o in root.occurrences if o.component.name == 'Spray station (Claude)'][0].component
    lib = [l for l in app.materialLibraries if 'Appearance' in l.name][0]
    base = lib.appearances.itemByName('Plastic - Glossy (White)') or lib.appearances.itemByName('Plastic - Matte (White)')
    made = {}
    def ap(name, rgb):
        if name in made: return made[name]
        a = d.appearances.itemByName(name) or d.appearances.addByCopy(base, name)
        for p in a.appearanceProperties:
            if isinstance(p, adsk.core.ColorProperty) and p.id in ('opaque_albedo', 'generic_diffuse') or (isinstance(p, adsk.core.ColorProperty) and p.name == 'Color'):
                p.value = adsk.core.Color.create(rgb[0], rgb[1], rgb[2], 255)
        made[name] = a; return a
    for b in comp.bRepBodies:
        key = next(k for k in sorted(COLORS, key=len, reverse=True) if b.name.startswith(k))
        b.appearance = ap(*COLORS[key]); print(b.name, '->', COLORS[key][0])
