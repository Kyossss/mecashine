import adsk.core, adsk.fusion
def run(_c):
    app = adsk.core.Application.get()
    print('active', app.activeDocument.name, 'modified', app.activeDocument.isModified)
    d = adsk.fusion.Design.cast(app.activeProduct); r = d.rootComponent
    print('design type', 'parametric' if d.designType == adsk.fusion.DesignTypes.ParametricDesignType else 'direct')
    for nm in ('Body67', 'Body68', 'Body85', 'Body70'):
        b = [x for x in r.bRepBodies if x.name == nm]
        print(nm, 'found' if b else 'MISSING', b[0].isLightBulbOn if b else '')
    print('existing comps', [o.component.name for o in r.occurrences if 'Claude' in o.component.name])
