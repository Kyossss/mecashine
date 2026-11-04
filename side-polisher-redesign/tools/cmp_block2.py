import sys, os
os.chdir(r'F:\Research\ASPS\side-polisher-redesign'); sys.path.insert(0, os.getcwd())
sys.argv = ['cad_pincer9.py', 'x']
src = open('cad_pincer9.py', encoding='utf8').read().split('\ndef overlap')[0]
g = {'__file__': os.path.abspath('cad_pincer9.py'), '__name__': 'partial'}
exec(compile(src, 'cad_pincer9.py', 'exec'), g)
import cadquery as cq
from cadquery import Vector as V
D = r'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/'
u = cq.importers.importStep(D + 'user_block2.step').val()
m = g['assembly'](0)['block_L0']
print('user', round(u.Volume(), 1), 'mine', round(m.Volume(), 1), 'user faces', len(u.Faces()))
# local coords: X = x-925, Y = y+127.45, Z = z-217
def L(p): return V(p[0] + 925, p[1] - 127.45, p[2] + 217)
step = 0.5
import collections
diff = []
for i in range(int((-66.5 + 67) / step), int((-24 + 67) / step) + 1):
    x = -67 + i * step
    for j in range(int(51 / step) + 1):
        y = -27.5 + j * step
        for k in range(int(48 / step) + 1):
            z = 77.5 + k * step
            a, b = m.isInside(L((x + 0.25, y + 0.25, z + 0.25)), 0.01), u.isInside(L((x + 0.25, y + 0.25, z + 0.25)), 0.01)
            if a != b: diff.append((x, y, z, 'R' if a else 'A'))
print('diff points', len(diff), ' removed', sum(1 for d in diff if d[3] == 'R'), ' added', sum(1 for d in diff if d[3] == 'A'))
# cluster by 6-connectivity
pts = {(round(d[0] / step), round(d[1] / step), round(d[2] / step)): d[3] for d in diff}
seen = set(); clusters = []
for p0 in pts:
    if p0 in seen: continue
    st = [p0]; seen.add(p0); comp = []
    while st:
        p = st.pop(); comp.append(p)
        for dx, dy, dz in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
            q = (p[0]+dx, p[1]+dy, p[2]+dz)
            if q in pts and q not in seen and pts[q] == pts[p0]: seen.add(q); st.append(q)
    clusters.append(comp)
clusters.sort(key=len, reverse=True)
for c in clusters[:25]:
    if len(c) < 4: continue
    xs = [p[0] * step for p in c]; ys = [p[1] * step for p in c]; zs = [p[2] * step for p in c]
    print(pts[c[0]], 'n', len(c), 'approx vol', round(len(c) * step ** 3, 1), 'x', min(xs), max(xs) + step, 'y', min(ys), max(ys) + step, 'z', min(zs), max(zs) + step)
