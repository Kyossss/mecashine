import sys, os
os.chdir(r'F:\Research\ASPS\side-polisher-redesign'); sys.path.insert(0, os.getcwd())
sys.argv = ['cad_pincer9.py', 'x']
src = open('cad_pincer9.py', encoding='utf8').read().split('\ndef overlap')[0]
g = {'__file__': os.path.abspath('cad_pincer9.py'), '__name__': 'partial'}
exec(compile(src, 'cad_pincer9.py', 'exec'), g)
import cadquery as cq
u = cq.importers.importStep(r'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/user_sensor.step').val()
m = g['placeL'](g['SENSOR'], 0).translate(cq.Vector(0.013, 0, 0))   # tiny shift so the booleans are not coincident
print('intersection', round(u.intersect(m).Volume(), 1), 'user', round(u.Volume(), 1), 'mine', round(m.Volume(), 1), ' faces', len(u.Faces()), len(m.Faces()))
from cadquery import Vector as V
m = g['placeL'](g['SENSOR'], 0); diff = 0; n = 0
for x in [850 + i * 0.5 for i in range(60)]:
    for y in [-96.5 + i * 0.5 for i in range(28)]:
        for z in [230.5 + i * 0.5 for i in range(90)]:
            a, b = u.isInside(V(x, y, z), 0.01), m.isInside(V(x, y, z), 0.01); n += 1
            if a != b: diff += 1
print('grid points', n, 'mismatched', diff)
