# Pull the side-polisher solids out of the Fusion STEP export, name them by bounding box, cache as BREP, and report their features.
import os, sys, json
import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder, GeomAbs_Plane

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, 'ref'); os.makedirs(REF, exist_ok=True)
# name: bbox [x0,x1,y0,y1,z0,z1] in mm, from the Fusion listing
WANT = {
 'pillarL_low': [880, 970, -145, -110, 129, 304], 'pillarL_up': [880, 970, -145, 0, 304, 479],
 'pillarR_low': [880, 970, 110, 145, 129, 304], 'pillarR_up': [880, 970, 0, 145, 304, 479],
 'top_centre': [870, 980, -40, 40, 479, 515], 'cover_c': [870, 980, -40, 40, 496, 501],
 'rail14': [940, 980, 40, 120, 479, 496], 'rail15': [870, 910, 40, 120, 479, 496], 'rail16': [940, 980, -120, -40, 479, 496], 'rail17': [870, 910, -120, -40, 479, 496],
 'cover20': [870, 980, -120, -40, 496, 501], 'cover21': [870, 980, 40, 120, 496, 501], 'servo_brkt': [870, 980, -12, 12, 501, 564],
 'clampL': [882, 970, -94, -69, 434, 454], 'clampR': [882, 970, 66, 93, 434, 469], 'cupL': [900, 950, -92, -62, 383, 434], 'cupR': [902, 952, 58, 88, 383, 434],
 'armL': [865, 980, -96, -84, 250, 459], 'armR': [822, 980, 81, 93, 244, 459], 'sensor': [837, 872, -98, -84, 250, 271],
 'gear': [905, 945, -20, 20, 487, 517], 'rackA': [882, 972, -84, 50, 441, 495], 'rackB': [879, 969, -54, 80, 441, 495],
 'base': [200, 1410, -175, 175, 109, 129],
}
def bbl(s):
    b = s.BoundingBox(); return [b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax]

if not os.path.exists(os.path.join(REF, 'pillarL_low.brep')):
    full = cq.importers.importStep(os.path.join(HERE, 'fusion-full.step'))
    solids = full.solids().vals()
    print('solids in file', len(solids))
    for s in solids:
        b = bbl(s)
        for n, w in WANT.items():
            if all(abs(b[i] - w[i]) < 1.6 for i in range(6)):
                p = os.path.join(REF, n + '.brep')
                if not os.path.exists(p): s.exportBrep(p)
    print('found', sorted(f[:-5] for f in os.listdir(REF)))

def load(n): return cq.Shape.importBrep(os.path.join(REF, n + '.brep'))

if __name__ == '__main__':
    for n in (sys.argv[1:] or sorted(WANT)):
        p = os.path.join(REF, n + '.brep')
        if not os.path.exists(p): print('MISSING', n); continue
        s = load(n); b = bbl(s)
        print('\n##', n, 'bbox', [round(v, 1) for v in b], 'vol cm3', round(s.Volume() / 1000, 1), 'faces', len(s.Faces()))
        cyl = {}
        planes = {}
        for f in s.Faces():
            a = BRepAdaptor_Surface(f.wrapped)
            fb = bbl(f)
            if a.GetType() == GeomAbs_Cylinder:
                c = a.Cylinder(); ax = c.Axis(); d = ax.Direction(); l = ax.Location()
                axis = 'x' if abs(d.X()) > .99 else 'y' if abs(d.Y()) > .99 else 'z' if abs(d.Z()) > .99 else 'skew'
                key = (axis, round(l.X(), 1) if axis != 'x' else None, round(l.Y(), 1) if axis != 'y' else None, round(l.Z(), 1) if axis != 'z' else None, round(c.Radius(), 2))
                k = 'xyz'.find(axis) if axis != 'skew' else 0
                e = cyl.setdefault(key, [1e9, -1e9]); e[0] = min(e[0], fb[2 * k]); e[1] = max(e[1], fb[2 * k + 1])
            elif a.GetType() == GeomAbs_Plane:
                d = a.Plane().Axis().Direction()
                for k, v in enumerate((d.X(), d.Y(), d.Z())):
                    if abs(v) > .999:
                        planes.setdefault('xyz'[k], set()).add(round(fb[2 * k], 1))
        for k, e in sorted(cyl.items(), key=str): print('  cyl axis', k[0], 'at', [v for v in k[1:4] if v is not None], 'r', k[4], 'span', round(e[0], 1), round(e[1], 1))
        for k in 'xyz': print('  planes', k, sorted(planes.get(k, [])))
