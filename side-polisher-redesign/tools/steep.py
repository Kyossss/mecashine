exec(open(r'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/overhang.py').read().split("B = g['BLOCK']")[0])
B = g['BLOCK']
s = B.rotate(V(0, 0, 0), V(1, 0, 0), 90)
bz = s.BoundingBox().zmin
for f in s.Faces():
    vs, ts = f.tessellate(0.1, 0.2); A = 0; nzs = []
    for t in ts:
        a, b, c = vs[t[0]], vs[t[1]], vs[t[2]]; n = (b - a).cross(c - a)
        if n.Length < 1e-9: continue
        nz = n.z / n.Length
        if -0.99 <= nz < -0.707: A += n.Length / 2; nzs.append(nz)
    if A > 1:
        bb = f.BoundingBox()
        print(f.geomType(), round(A, 1), 'min angle from vertical deg', round(math.degrees(math.acos(-min(nzs))) if nzs else 0, 1), 'center local', [round(v, 1) for v in (bb.center.x, bb.center.y, bb.center.z)])
