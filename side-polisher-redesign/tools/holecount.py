import sys, os, math
os.chdir(r'F:\Research\ASPS\side-polisher-redesign'); sys.path.insert(0, os.getcwd())
sys.argv = ['cad_pincer9.py', 'x']
src = open('cad_pincer9.py', encoding='utf8').read().split('\ndef overlap')[0]
g = {'__file__': os.path.abspath('cad_pincer9.py'), '__name__': 'partial'}
exec(compile(src, 'cad_pincer9.py', 'exec'), g)
parts = {'arm': g['ARM'], 'foot': g['FOOT'], 'carriage': g['CARRIAGE'], 'rack': g['RACK'], 'core': g['CORE'], 'rail': g['RAIL'],
         'block': g['BLOCK'], 'clamp': g['CLAMP'], 'sensor': g['SENSOR'], 'reflector': g['REFL']}
for n, s in parts.items():
    holes = {}
    for f in s.Faces():
        if f.geomType() != 'CYLINDER': continue
        r = round(f._geomAdaptor().Cylinder().Radius(), 2)
        if r > 6: continue
        ax = f._geomAdaptor().Cylinder().Axis(); loc = ax.Location(); d = ax.Direction()
        # key: radius + axis line (rounded), so the split faces of one hole count once
        dirv = tuple(round(abs(v), 2) for v in (d.X(), d.Y(), d.Z()))
        p = (loc.X(), loc.Y(), loc.Z())
        # project the location onto the plane perpendicular to the axis
        k = max(range(3), key=lambda i: dirv[i]); q = tuple(round(p[i], 1) for i in range(3) if i != k)
        holes.setdefault(r, set()).add((dirv, q))
    print(n.ljust(10), {r: len(v) for r, v in sorted(holes.items())})
