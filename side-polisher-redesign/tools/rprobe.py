import sys, os
os.chdir(r'F:\Research\ASPS\side-polisher-redesign'); sys.path.insert(0, os.getcwd())
sys.argv = ['cad_pincer9.py', 'x']
src = open('cad_pincer9.py', encoding='utf8').read().split('\ndef overlap')[0]
g = {'__file__': os.path.abspath('cad_pincer9.py'), '__name__': 'partial'}
exec(compile(src, 'cad_pincer9.py', 'exec'), g)
import cad_ref
it = g['assembly'](0)
for n in ('pillarR_low', 'pillarR_up'):
    x = it['block_R1'].intersect(cad_ref.load(n))
    for sol in x.Solids():
        b = sol.BoundingBox(); print(n, round(sol.Volume(), 1), [round(v, 2) for v in (b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax)])
b = it['block_R1'].BoundingBox(); print('block', [round(v, 2) for v in (b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax)])
