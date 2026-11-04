import sys, os
os.chdir(r'F:\Research\ASPS\side-polisher-redesign'); sys.path.insert(0, os.getcwd())
sys.argv = ['cad_pincer9.py', 'x']
src = open('cad_pincer9.py', encoding='utf8').read().split('\ndef overlap')[0]
g = {'__file__': os.path.abspath('cad_pincer9.py'), '__name__': 'partial'}
exec(compile(src, 'cad_pincer9.py', 'exec'), g)
import cadquery as cq
u = cq.importers.importStep(sys.argv[1] if False else r'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/user_sensor.step').val()
mine = g['placeL'](g['SENSOR'], 0)
f = lambda s: [round(v, 2) for v in (s.BoundingBox().xmin, s.BoundingBox().xmax, s.BoundingBox().ymin, s.BoundingBox().ymax, s.BoundingBox().zmin, s.BoundingBox().zmax)]
print('user', round(u.Volume(), 1), f(u), 'valid', u.isValid(), 'solids', len(u.Solids()))
print('mine', round(mine.Volume(), 1), f(mine))
rem = mine.cut(u); add = u.cut(mine)
for name, s in (('REMOVED by user', rem), ('ADDED by user', add)):
    for sol in s.Solids():
        if sol.Volume() > 0.05: print(name, round(sol.Volume(), 2), f(sol))
print('board', f(g['placeL'](g['BOARD'], 0)))
box = g['box']
notch = rem.cut(box(840, 850.5, -100, -80, 220, 280))
for sol in notch.Solids(): print('notch', round(sol.Volume(), 2), f(sol))
# bosses on the plate face (board standoffs)
st = u.intersect(box(846, 879, -93, -90, 240, 280))
for sol in st.Solids(): print('standoff/wall', f(sol))
