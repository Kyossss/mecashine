exec(open(r'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/holecount.py').read().split('parts = {')[0])
R = g['RACK']
for f in R.Faces():
    if f.geomType() != 'CYLINDER': continue
    r = round(f._geomAdaptor().Cylinder().Radius(), 2)
    if r in (2.5, 4.5, 5.0):
        b = f.BoundingBox(); d = f._geomAdaptor().Cylinder().Axis().Direction()
        print(r, 'axis', [round(v, 2) for v in (d.X(), d.Y(), d.Z())], 'bb', [round(v, 1) for v in (b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax)])
