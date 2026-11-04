# Export just the reflector (print file + in-place STEP for Fusion) and report its numbers.
import sys, os
os.chdir(r'F:\Research\ASPS\side-polisher-redesign'); sys.path.insert(0, os.getcwd())
sys.argv = ['cad_pincer9.py', 'x']
src = open('cad_pincer9.py', encoding='utf8').read().split('\ndef overlap')[0]
g = {'__file__': os.path.abspath('cad_pincer9.py'), '__name__': 'partial'}
exec(compile(src, 'cad_pincer9.py', 'exec'), g)
cq, V = g['cq'], g['V']
R = g['REFL']
s = R.mirror('XZ').rotate(V(0, 0, 0), V(1, 0, 0), 90); b = s.BoundingBox(); s = s.translate(V(-b.xmin, -b.ymin, -b.zmin))
for f in ('reflector.step', 'reflector.stl', r'print\reflector x1.stl'):
    (cq.exporters.export(cq.Workplane().add(s), f, tolerance=0.02, angularTolerance=0.1) if f.endswith('stl') else cq.exporters.export(cq.Workplane().add(s), f))
cq.exporters.export(cq.Workplane().add(g['assembly'](0)['refl_R']), r'tools\fx\refl_R.step')
b = s.BoundingBox()
print('valid', s.isValid(), 'solids', len(s.Solids()), 'vol', round(s.Volume() / 1000, 1), 'bed', [round(b.xlen, 1), round(b.ylen, 1), round(b.zlen, 1)])
r0, f = g['REFL_RIM'], g['LEG'][1]
print('insert: lower part %.1f x %.1f mm, upper part %.1f x %.1f mm' % (g['REFL_U1'] - r0 - (f + 5.5 + r0), g['REFL_NOTCH_Z'] - r0 - (g['REFL_Z0'] + r0), g['REFL_U1'] - r0 - (g['REFL_NOTCH_U'] + r0), g['REFL_Z1'] - r0 - (g['REFL_NOTCH_Z'] - r0)))
