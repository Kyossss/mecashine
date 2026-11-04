# downward-facing areas (not on the bed) of each print file, by orientation
import sys, os, math
os.chdir(r'F:\Research\ASPS\side-polisher-redesign'); sys.path.insert(0, os.getcwd())
sys.argv = ['cad_pincer9.py', 'x']
src = open('cad_pincer9.py', encoding='utf8').read().split('\ndef overlap')[0]
g = {'__file__': os.path.abspath('cad_pincer9.py'), '__name__': 'partial'}
exec(compile(src, 'cad_pincer9.py', 'exec'), g)
cq, V = g['cq'], g['V']
def to_bed(s):
    b = s.BoundingBox(); return s.translate(V(-b.xmin, -b.ymin, -b.zmin))
def report(name, s):
    flat, steep = [], 0.0
    for f in s.Faces():
        vs, ts = f.tessellate(0.1, 0.2)
        for t in ts:
            a, b, c = vs[t[0]], vs[t[1]], vs[t[2]]
            n = (b - a).cross(c - a); A = n.Length / 2
            if A < 1e-9: continue
            nz = n.z / n.Length; zc = (a.z + b.z + c.z) / 3
            if nz < -0.99 and zc > 0.05: flat.append((round(zc, 1), A))
            elif -0.99 <= nz < -0.707: steep += A          # steeper than 45 degrees off vertical: would want support
    by = {}
    for z, A in flat: by[z] = by.get(z, 0) + A
    print(name, ' flat ceilings (z: mm2):', {k: round(v) for k, v in sorted(by.items())}, ' overhang >45deg mm2:', round(steep))
B = g['BLOCK']

report('block A on outer face', to_bed(B.rotate(V(0, 0, 0), V(1, 0, 0), 90)))
report('block B on outer face', to_bed(B.mirror('XZ').rotate(V(0, 0, 0), V(1, 0, 0), -90)))
report('clamp flat', to_bed(g['CLAMP']))

print('block vol cm3', round(B.Volume() / 1000, 1), ' clamp vol', round(g['CLAMP'].Volume() / 1000, 1), ' valid', B.isValid(), len(B.Solids()), g['CLAMP'].isValid())
