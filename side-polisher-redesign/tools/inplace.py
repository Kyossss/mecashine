import sys, os
os.chdir(r'F:\Research\ASPS\side-polisher-redesign'); sys.path.insert(0, os.getcwd())
sys.argv = ['cad_pincer9.py', 'x']
src = open('cad_pincer9.py', encoding='utf8').read().split('\ndef overlap')[0]
g = {'__file__': os.path.abspath('cad_pincer9.py'), '__name__': 'partial'}
exec(compile(src, 'cad_pincer9.py', 'exec'), g)
cq = g['cq']; B, C = g['BLOCK'], g['CLAMP']
print('block Y-symmetric:', round(B.cut(B.mirror('XZ')).Volume(), 3), ' clamp:', round(C.cut(C.mirror('XZ')).Volume(), 3))
D = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] != 'x' else r'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/'
it = g['assembly'](0)
for k in ('block_L0', 'block_L1', 'block_R0', 'block_R1', 'clamp_L0', 'clamp_L1', 'clamp_R0', 'clamp_R1'):
    cq.exporters.export(cq.Workplane().add(it[k]), r'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/' + k + '.step')
    b = it[k].BoundingBox(); print(k, [round(v, 1) for v in (b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax)])
