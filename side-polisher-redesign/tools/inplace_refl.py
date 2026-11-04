import sys, os
os.chdir(r'F:\Research\ASPS\side-polisher-redesign'); sys.path.insert(0, os.getcwd())
sys.argv = ['cad_pincer9.py', 'x']
src = open('cad_pincer9.py', encoding='utf8').read().split('\ndef overlap')[0]
g = {'__file__': os.path.abspath('cad_pincer9.py'), '__name__': 'partial'}
exec(compile(src, 'cad_pincer9.py', 'exec'), g)
cq = g['cq']
it = g['assembly'](0)
D = r'F:/Research/ASPS/side-polisher-redesign/tools/fx/'
for k in sys.argv[1:] if len(sys.argv) > 1 and sys.argv[1] != 'x' else ('refl_R',):
    s = it[k]
    cq.exporters.export(cq.Workplane().add(s), D + k + '.step')
    print(k, 'solids', len(s.Solids()), 'vol', round(s.Volume() / 1000, 2))
