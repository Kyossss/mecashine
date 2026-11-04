import cadquery as cq, sys
D = r'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/out24/'
for n in ('tie-disc', 'brush-core-top', 'brush-core-bar', 'brush-core-bottom'):
    s = cq.importers.importStep(D + n + '.step').val()
    flat, steep = {}, 0.0
    for f in s.Faces():
        vs, ts = f.tessellate(0.1, 0.2)
        for t in ts:
            a, b, c = vs[t[0]], vs[t[1]], vs[t[2]]
            nn = (b - a).cross(c - a); A = nn.Length / 2
            if A < 1e-9: continue
            nz = nn.z / nn.Length; zc = (a.z + b.z + c.z) / 3
            if nz < -0.99 and zc > 0.05: flat[round(zc, 1)] = flat.get(round(zc, 1), 0) + A
            elif -0.99 <= nz < -0.72: steep += A
    print(n.ljust(18), 'flat ceilings z:mm2', {k: round(v) for k, v in sorted(flat.items())}, ' steeper than 45 deg mm2', round(steep))
