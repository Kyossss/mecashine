import sys, os
os.chdir(r'F:\Research\ASPS\side-polisher-redesign'); sys.path.insert(0, os.getcwd())
sys.argv = ['cad_pincer9.py', 'x']
src = open('cad_pincer9.py', encoding='utf8').read().split('\ndef overlap')[0]
g = {'__file__': os.path.abspath('cad_pincer9.py'), '__name__': 'partial'}
exec(compile(src, 'cad_pincer9.py', 'exec'), g)
cq = g['cq']; s = g['SENSOR'].mirror('XZ'); b = s.BoundingBox(); s = s.translate(cq.Vector(-b.xmin, -b.ymin, -b.zmin))
for f in (r'sensor-bracket.step', r'sensor-bracket.stl', r'print\sensor-bracket x1.stl'):
    (cq.exporters.export(cq.Workplane().add(s), f, tolerance=0.02, angularTolerance=0.1) if f.endswith('stl') else cq.exporters.export(cq.Workplane().add(s), f))
b = s.BoundingBox(); print('valid', s.isValid(), 'solids', len(s.Solids()), 'vol', round(s.Volume() / 1000, 2), 'bed', [round(b.xlen, 1), round(b.ylen, 1), round(b.zlen, 1)])
