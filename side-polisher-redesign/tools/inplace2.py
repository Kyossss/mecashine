import sys, os
os.chdir(r'F:\Research\ASPS\side-polisher-redesign'); sys.path.insert(0, os.getcwd())
sys.argv = ['cad_pincer9.py', 'x']
src = open('cad_pincer9.py', encoding='utf8').read().split('\ndef overlap')[0]
g = {'__file__': os.path.abspath('cad_pincer9.py'), '__name__': 'partial'}
exec(compile(src, 'cad_pincer9.py', 'exec'), g)
cq = g['cq']
it = g['assembly'](0)
D = r'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/fx/'
for k in ('carriage_L', 'carriage_R', 'core_L', 'core_R', 'discs_L', 'discs_R'):
    s = it[k]
    cq.exporters.export(cq.Workplane().add(s), D + k + '.step')
    print(k, 'solids', len(s.Solids()), 'vol', round(s.Volume() / 1000, 2))
