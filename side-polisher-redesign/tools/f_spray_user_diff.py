import adsk.core, adsk.fusion
D = 'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/'
def bb(b): return [round(v * 10, 2) for v in (b.minPoint.x, b.maxPoint.x, b.minPoint.y, b.maxPoint.y, b.minPoint.z - 21.7, b.maxPoint.z - 21.7)]
def run(_c):
    app = adsk.core.Application.get()
    d = [x for x in app.documents if x.name.startswith('Conveyor assembly 2')][0]
    des = adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType')); root = des.rootComponent
    occ = [o for o in root.occurrences if o.component.name == 'Spray station (Claude)'][0]; comp = occ.component
    tm = adsk.fusion.TemporaryBRepManager.get()
    for n, f in (('box', 'pbox'), ('far', 'pfar')):
        u = [b for b in comp.bRepBodies if b.name.startswith('Nozzle post v8') and n in b.name][0]
        m = tm.createFromFile(D + f + '.step').item(0)
        print(n, 'user %.3f mine %.3f cm3' % (u.volume, m.volume))
        for lab, a, b in (('removed', m, u), ('added', u, m)):
            t = tm.copy(a); tm.booleanOperation(t, tm.copy(b), adsk.fusion.BooleanTypes.DifferenceBooleanType)
            for k in range(t.lumps.count):
                L = t.lumps.item(k); v = L.volume * 1000 if hasattr(L, 'volume') else 0
                if v > 0.3: print('  ', lab, round(v, 1), 'mm3, x/y/z-above-belt', bb(L.boundingBox))