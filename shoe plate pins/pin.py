# Shoe plate pin, 7 mm (2026-11-04): Ø2.3 shank, 0.3 tip chamfer, 90° countersunk head Ø4.14 that sits flush in the plate's Ø4.2 countersink.
# Built head down (head top on the bed at z 0), the way it prints. Length 7 mm = 3 mm plate + 4 mm below the plate's bottom (was 5 / 2).
import cadquery as cq
RH, RS, L = 2.07, 1.15, 7.0
H = RH - RS                                       # cone height (90°)
pin = cq.Workplane('XZ').polyline([(0, 0), (RH, 0), (RS, H), (RS, L - 0.3), (RS - 0.3, L), (0, L)]).close().revolve(360, (0, 0, 0), (0, 1, 0))
s = pin.val(); b = s.BoundingBox()
print('valid', s.isValid(), 'vol %.1f mm3' % s.Volume(), 'size %.2f x %.2f x %.2f' % (b.xlen, b.ylen, b.zlen), 'z', round(b.zmin, 2), round(b.zmax, 2))
cq.exporters.export(pin, 'F:/Research/ASPS/shoe plate pins/print/shoe-plate pin 7mm x2.stl', tolerance=0.005, angularTolerance=0.05)
