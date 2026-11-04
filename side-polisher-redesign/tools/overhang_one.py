import sys, cadquery as cq
s = cq.importers.importStep(sys.argv[1]).val()
flat, steep = {}, 0.0
for f in s.Faces():
    vs, ts = f.tessellate(0.1, 0.2)
    for t in ts:
        a, b, c = vs[t[0]], vs[t[1]], vs[t[2]]
        n = (b - a).cross(c - a); A = n.Length / 2
        if A < 1e-9: continue
        nz = n.z / n.Length; zc = (a.z + b.z + c.z) / 3
        if nz < -0.99 and zc > 0.05: flat[round(zc, 1)] = flat.get(round(zc, 1), 0) + A
        elif -0.99 <= nz < -0.72: steep += A
print('flat ceilings z:mm2', {k: round(v) for k, v in sorted(flat.items())}, ' steeper than 45 deg mm2', round(steep))
