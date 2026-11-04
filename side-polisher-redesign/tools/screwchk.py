import sys, os
os.chdir(r'F:\Research\ASPS\side-polisher-redesign'); sys.path.insert(0, os.getcwd())
sys.argv = ['cad_pincer9.py', 'x']
src = open('cad_pincer9.py', encoding='utf8').read()
src = src[:src.index("\nbb = lambda") if "\nbb = lambda" in src else src.index('\ndef bb(s)')]
g = {'__file__': os.path.abspath('cad_pincer9.py'), '__name__': 'partial'}
exec(compile(src, 'cad_pincer9.py', 'exec'), g)
cz, fuse, FL_BOT, PT, BASE_Z, M3_NUT_AF = g['cz'], g['fuse'], g['FL_BOT'], g['PLATE_T'], g['BASE_Z'], g['M3_NUT_AF']
z0 = FL_BOT - PT
# one screw: button/socket head 5.7 x 3 under the plate, 3 mm shank 12 long
scr = [fuse([cz(x, y, z0 - 3, z0, 5.7), cz(x, y, z0, z0 + 12, 3.0)]) for x, y, _ in g['SCREWS']]
nut_top = BASE_Z + 1.5 + 2.4
print('screw tip z', z0 + 12, ' nut top z', round(nut_top, 2), ' -> sticks out', round(z0 + 12 - nut_top, 2), 'mm past the nut')
LOCAL = fuse(scr)
B, C = g['BLOCK'], g['CLAMP']
print('shank vs block (should be 0, all in holes):', round(LOCAL.intersect(B).Volume(), 2), ' vs plate:', round(LOCAL.intersect(C).Volume(), 2))
def place(side, back, rx, part):
    return g['place_block'](side, back, rx, part)
bad = []
for p in (-7, 0, 15, 30):
    it, ex = g['assembly'](p), g['existing'](p)
    for side, xs, ys in (('L', 1, -1), ('R', -1, 1)):
        ax = 925 if side == 'L' else 925.5
        for i, u in enumerate(g['ROD_U']):
            rx = ax + xs * u; back = rx > 925
            s = place(ys, back, rx, LOCAL)
            for n, o in list(ex.items()) + [(k, v) for k, v in it.items() if not k.startswith(('block', 'clamp'))]:
                v = g['overlap'](s, o)
                if v > 0.05: bad.append((p, side, i, n, round(v, 2)))
print('screw clashes:', bad)
