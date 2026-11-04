import adsk.core, adsk.fusion, os
OUT = 'F:/Research/ASPS/spray station/fusion/user-edit-2026-11-03/'
def run(_c):
    app = adsk.core.Application.get()
    d = [x for x in app.documents if x.name.startswith('Conveyor assembly 2')][0]
    des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType')); root = des.rootComponent
    occ = [o for o in root.occurrences if o.component.name == 'Spray station (Claude)'][0]
    os.makedirs(OUT, exist_ok=True); em = des.exportManager
    for b in occ.bRepBodies:
        if b.name.startswith('Nozzle post v8'):
            n = 'box' if 'box' in b.name else 'far'
            o = em.createSTEPExportOptions(OUT + n + '.step', b); print(n, em.execute(o))
