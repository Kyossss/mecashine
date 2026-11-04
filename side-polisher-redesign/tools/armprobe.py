import sys, os
os.chdir(r'F:\Research\ASPS\side-polisher-redesign'); sys.path.insert(0, os.getcwd())
sys.argv = ['cad_pincer9.py', 'x']
src = open('cad_pincer9.py', encoding='utf8').read().split('\ndef overlap')[0]
g = {'__file__': os.path.abspath('cad_pincer9.py'), '__name__': 'partial'}
exec(compile(src, 'cad_pincer9.py', 'exec'), g)
it = g['assembly'](-7)
for k in ('block_L0', 'clamp_L0'):
    x = it['arm_L'].intersect(it[k]); b = x.BoundingBox()
    print(k, 'overlap bbox', [round(v, 1) for v in (b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax)])
# arm extent (outermost y) in slabs near the flange, p=-7 and p=-10 margin
a = it['arm_L']
box = g['box']
for z0, z1 in ((285, 294), (294, 314), (314, 323)):
    for x0, x1 in ((860, 880), (880, 902)):
        s = a.intersect(box(x0, x1, -160, -60, z0, z1))
        if s.Volume() > 0.01:
            b = s.BoundingBox(); print('arm z', z0, z1, 'x', x0, x1, ' y min', round(b.ymin, 1))
        else: print('arm z', z0, z1, 'x', x0, x1, ' empty')
