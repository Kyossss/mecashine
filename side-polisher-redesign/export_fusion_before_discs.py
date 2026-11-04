# Builds one STEP of the new parts in place, each as its own named part, for importing into "Conveyor assembly 2".
import sys, os, runpy
sys.argv = ['cad_pincer9.py', 'out9']
g = runpy.run_path('cad_pincer9.py', run_name='__notmain__')
cq, V = g['cq'], g['V']
it = g['assembly'](0)
NAME = {'arm': 'Arm frame', 'foot': 'Foot bracket', 'carriage': 'Carriage', 'rack': 'Rack', 'core': 'Brush core', 'bearing': '608ZZ bearing',
        'rail': 'Guide rail', 'block': 'Guide block', 'clamp': 'Flange clamp', 'sensor': 'Sensor bracket', 'refl': 'Reflector', 'board': 'ToF sensor board (stand-in)'}
COL = {'arm': (0.72, 0.67, 0.86), 'foot': (0.31, 0.70, 0.49), 'carriage': (0.51, 0.77, 0.87), 'rack': (0.37, 0.53, 0.78), 'core': (0.85, 0.55, 0.30),
       'bearing': (0.88, 0.69, 0.25), 'rail': (0.84, 0.86, 0.89), 'block': (0.18, 0.60, 0.63), 'clamp': (0.95, 0.62, 0.20), 'sensor': (0.59, 0.84, 0.67), 'refl': (0.96, 0.96, 0.94), 'board': (0.14, 0.38, 0.77)}
asm = cq.Assembly(name='Side polisher redesign')
for key, shape in sorted(it.items()):
    kind, side = key.split('_')
    if kind not in NAME: continue                     # leaves out the motor and bristle stand-ins
    where = {'L': 'left', 'R': 'right'}.get(side[0], side)
    extra = ''
    if kind in ('rail', 'block', 'clamp'): extra = ' upstream' if side.endswith('0') else ' downstream'
    asm.add(shape, name='%s %s%s' % (NAME[kind], where, extra), color=cq.Color(*COL[kind], 1.0))
out = os.path.abspath('fusion-import.step')
asm.save(out)
print('saved', out, len(asm.children), 'parts')
