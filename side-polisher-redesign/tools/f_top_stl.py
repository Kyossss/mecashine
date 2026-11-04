import adsk.core, adsk.fusion
def run(_c):
    app = adsk.core.Application.get(); d = adsk.fusion.Design.cast(app.activeProduct); root = d.rootComponent
    comp = [o for o in root.occurrences if o.component.name == 'Top polisher redesign (Claude)'][0].component
    b = [x for x in comp.bRepBodies if x.name.startswith('Carriage')][0]
    em = d.exportManager
    o = em.createSTLExportOptions(b, 'F:/Research/ASPS/top polish/carriage-inplace.stl')
    o.isBinaryFormat = True; o.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
    print('stl', em.execute(o), 'volume', round(b.volume, 2))
