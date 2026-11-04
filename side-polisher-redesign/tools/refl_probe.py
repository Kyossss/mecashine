import sys, os, json, math
os.chdir(r'F:\Research\ASPS\side-polisher-redesign'); sys.path.insert(0, os.getcwd())
sys.argv = ['cad_pincer9.py', 'x']
src = open('cad_pincer9.py', encoding='utf8').read().split('\ndef bb(s)')[0]
g = {'__file__': os.path.abspath('cad_pincer9.py'), '__name__': 'partial'}
exec(compile(src, 'cad_pincer9.py', 'exec'), g)
V = g['V']; box = g['box']; AX_D = g['AX_D']
print('SENSOR_U,Z', g['SENSOR_U'], g['SENSOR_Z'], ' board d', 5.5 - g['BOARD_T'], '..5.5   REFL_FACE_D', g['REFL_FACE_D'], ' LEG', g['LEG'], ' D_IN', g['D_IN'], ' T', g['T'], ' CB', g['CB'], ' COL_TOP', g['COL_TOP'])
# sensor -> reflector distance vs p (left sensor chip face at d 3.9, right reflector face at d 6)
for p in (-7, -8, 0, 30): print('p', p, ' sensor y', -85 - 3.9 + p, ' reflector face y', 81.5 + 6 - p, ' gap', round(81.5 + 6 - p - (-85 - 3.9 + p), 1))
# outward limit: smallest p (down to -25) where moving parts first touch the static parts / blocks
it0 = None
for p in [-7 - 0.5 * k for k in range(0, 37)]:
    it = g['assembly'](p); ex = g['existing'](p)
    hits = []
    for n in ('arm_L', 'arm_R', 'rail_L0', 'rail_L1', 'rail_R0', 'rail_R1', 'foot_L', 'foot_R', 'carriage_L', 'carriage_R', 'rack_L', 'rack_R', 'refl_R', 'sensor_L'):
        for m, o in list(ex.items()) + [(k, v) for k, v in it.items() if k.startswith(('block', 'clamp'))]:
            v = g['overlap'](it[n], o)
            if v > 0.5: hits.append((n, m, round(v, 1)))
    if hits: print('first contact going outward at p', p, hits[:6]); break
else: print('no contact down to p -25')
# shoe envelope beyond the brush line, by u (mm upstream (+) / downstream (-) of the brush axis)
print('env(u):', {u: round(g['env'](u), 1) for u in (-115, -90, -70, -50, -30, 0, 30, 50, 70, 90, 115)} if 'env' in g else 'n/a')
ENV = json.load(open(os.path.join(os.getcwd(), 'shoe-env.json')))['env']
for band in ('all', 'low60', 'sole'):
    E = ENV[band]
    print('env', band, {u: round(E[str(u)], 1) for u in range(-115, 120, 15) if str(u) in E})
