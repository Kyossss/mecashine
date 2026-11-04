import sys, os
os.chdir(r'F:\Research\ASPS\side-polisher-redesign'); sys.path.insert(0, os.getcwd())
sys.argv = ['cad_pincer9.py', 'x']
src = open('cad_pincer9.py', encoding='utf8').read().split('\ndef overlap')[0]
g = {'__file__': os.path.abspath('cad_pincer9.py'), '__name__': 'partial'}
exec(compile(src, 'cad_pincer9.py', 'exec'), g)
import cadquery as cq
from cadquery import Vector as V
u = cq.importers.importStep(r'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/user_block.step').val()
m = g['assembly'](0)['block_L0']
print('user', round(u.Volume(), 1), 'mine', round(m.Volume(), 1))
# point grid: where mine is solid and user's is not; print slices in block-local coords (x-925, y+127.45)
for zc in (296, 300, 304, 308, 312, 315.5):
    print('slice z', zc, '(local', round(zc - 217, 1), ')   rows y local -27..23, cols x local -67..-24   #=both  R=removed by user  .=air')
    for yl in range(23, -28, -2):
        row = ''
        for xl in range(-67, -23):
            p = V(xl + 925 + 0.5, yl - 127.45 + 0.5, zc)
            a, b = m.isInside(p, 0.01), u.isInside(p, 0.01)
            row += '#' if a and b else ('R' if a else ('A' if b else '.'))
        print(' %4d %s' % (yl, row))
