import sys, os
os.chdir(r'F:\Research\ASPS\side-polisher-redesign'); sys.path.insert(0, os.getcwd())
import cad_ref
from cadquery import Vector as V
for side in ('L','R'):
    lo, up = cad_ref.load('pillar%s_low'%side), cad_ref.load('pillar%s_up'%side)
    for n,s in (('low',lo),('up',up)):
        b=s.BoundingBox(); print(side,n,[round(v,2) for v in (b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax)])
    ins=lambda p: lo.isInside(p) or up.isInside(p)
    sg = -1 if side=='L' else 1
    for x in (885, 960):
        ys=[y/4 for y in range(int(sg*100*4), int(sg*155*4), sg) if ins(V(x, y/4, 304))]
        print(side,'x',x,'flange y', min(ys), max(ys))
        xs=[xx/4 for xx in range(860*4, 990*4) if ins(V(xx/4, sg*126.5, 304))]
        zs=[z/4 for z in range(280*4,330*4) if ins(V(x, sg*126.5, z/4))]
        print('  flange z at x', x, min(zs), max(zs), ' x-run', min(xs), max(xs))
    # haunch start: smallest x>880 where solid at z 315.5 and z 292.5 (upstream pillar)
    for z in (314.5,316,318,293.5,292,290):
        xs=[xx/4 for xx in range(880*4, 925*4) if ins(V(xx/4, sg*126.5, z))]
        print('  z',z,'first solid x', min(xs) if xs else None)
