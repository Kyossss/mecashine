exec(open(r'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/holecount.py').read().split('parts = {')[0])
C = g['CARRIAGE']
for f in C.Faces():
    t = f.geomType()
    if t in ('CYLINDER', 'CONE'):
        b = f.BoundingBox()
        if b.xlen > 20:
            r = f._geomAdaptor().Cylinder().Radius() if t == 'CYLINDER' else None
            print(t, 'dia', round(2 * r, 2) if r else '-', 'z', round(b.zmin, 1), round(b.zmax, 1), 'width', round(b.xlen, 2))
