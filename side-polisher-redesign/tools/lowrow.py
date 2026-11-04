import sys, os
os.chdir(r'F:\Research\ASPS\side-polisher-redesign'); sys.path.insert(0, os.getcwd())
sys.argv = ['cad_pincer9.py', 'x']
src = open('cad_pincer9.py', encoding='utf8').read().split('\ndef overlap')[0]
g = {'__file__': os.path.abspath('cad_pincer9.py'), '__name__': 'partial'}
exec(compile(src, 'cad_pincer9.py', 'exec'), g)
cz, AX_D = g['cz'], g['AX_D']
# lowest row: knots under the bottom plate, tails spinning out to 26 mm, fur about 4.5 mm either side of the tail line
zt = g['BOT_DISC_Z0'] - 1.5
env = cz(0, AX_D, zt - 4.5, zt + 4.5, 52)
print('lowest tail line z', zt, ' fur reaches down to z', zt - 4.5, ' foot bridge top', g['BR_Z1'])
print('low row vs foot', round(env.intersect(g['FOOT']).Volume(), 1), ' vs arm', round(env.intersect(g['ARM']).Volume(), 1))
b = g['CORE_BOT']; bb = b.BoundingBox(); print('bottom part z', round(bb.zmin, 1), '..', round(bb.zmax, 1), ' vol', round(b.Volume() / 1000, 2))
box = g['box']
for z0 in (19.0, 19.5, 20.0, 21.0, 22.0):
    e = cz(0, AX_D, z0, zt + 4.5, 52)
    x = e.intersect(g['FOOT'])
    v = x.Volume(); bb = x.BoundingBox() if v > 0.01 else None
    print('fur from z', z0, ': vs foot', round(v, 1), (' at z %.1f..%.1f, u %.1f..%.1f' % (bb.zmin, bb.zmax, bb.xmin, bb.xmax)) if bb else '')
