import sys, os, math
os.chdir(r'F:\Research\ASPS\side-polisher-redesign'); sys.path.insert(0, os.getcwd())
sys.argv = ['cad_pincer9.py', 'x']
src = open('cad_pincer9.py', encoding='utf8').read().split('\ndef overlap')[0]
g = {'__file__': os.path.abspath('cad_pincer9.py'), '__name__': 'partial'}
exec(compile(src, 'cad_pincer9.py', 'exec'), g)
import cadquery as cq
V = cq.Vector
T, B, BO = g['CORE_TOP'], g['CORE_BAR'], g['CORE_BOT']
AX_D, Z = g['AX_D'], g['CORE_SCREW_Z']
cd = AX_D + g['TIP_OFF']; CZ = g['CROSS_Z']; hu = g['CROSS_HEAD_U']
def nut_on(o, n, x):
    return cq.Workplane(cq.Plane(origin=o, xDir=x, normal=n)).polygon(6, 5.5 / 0.8660254).circle(1.5).extrude(2.4).val()
shaft_screw = cq.Solid.makeCylinder(1.5, 8, V(1.8, AX_D, Z), V(1, 0, 0)).fuse(cq.Solid.makeCylinder(2.85, 1.65, V(9.8, AX_D, Z), V(1, 0, 0)))
shaft_nut = nut_on((g['NUT_U0'] + 0.1, AX_D, Z), (1, 0, 0), (0, 0, 1))
nut_u1 = -(g['TIP_AF'] / 2 / 0.8660254 + g['FIT_TOP']) - 0.3
cross_screw = cq.Solid.makeCylinder(1.5, 16, V(hu, cd, CZ), V(-1, 0, 0)).fuse(cq.Solid.makeCylinder(2.85, 1.65, V(hu, cd, CZ), V(1, 0, 0)))
cross_nut = nut_on((nut_u1 - 0.1 - 2.4, cd, CZ), (1, 0, 0), (0, 0, 1))
motor_shaft = cq.Solid.makeCylinder(2.0, 20, V(0, AX_D, g['CORE_Z1'] - g['SHAFT_DEPTH'] + 0.5), V(0, 0, 1)).cut(cq.Solid.makeBox(5, 10, 40, V(1.75, AX_D - 5, 140)))
for n, s in (('top', T), ('bar', B), ('bottom', BO)):
    print(n.ljust(7), 'valid', s.isValid(), 'solids', len(s.Solids()), 'vol', round(s.Volume() / 1000, 2))
for n, s in (('shaft screw', shaft_screw), ('shaft nut', shaft_nut), ('cross screw', cross_screw), ('cross nut', cross_nut), ('motor shaft', motor_shaft)):
    print(n.ljust(12), 'vs top', round(s.intersect(T).Volume(), 3), ' vs bar', round(s.intersect(B).Volume(), 3))
print('bar vs top', round(B.intersect(T).Volume(), 3), ' bar vs bottom', round(B.intersect(BO).Volume(), 3))
print('shaft screw tip at r', 1.8, '(the flat);  cross screw tip passes its nut by', round((nut_u1 - 2.5) - (hu - 16), 2), 'mm')
for n, s in (('top', T), ('bar', B), ('bottom', BO)):
    for o, os_ in (('arm', g['ARM']), ('foot', g['FOOT'])):
        v = s.intersect(os_).Volume()
        if v > 0.01: print('CLASH', n, o, round(v, 2))
print('ring radius', g['TIE_HOLE_D'] / 2, ' screw head max radius', 9.8 + 1.65)
