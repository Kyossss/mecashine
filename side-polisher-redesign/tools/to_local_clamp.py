import cadquery as cq
from cadquery import Vector as V
u = cq.importers.importStep(r'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/user_clamp3.step').val()
sol = u.Solids()
print('solids', len(sol), 'valid', u.isValid(), 'vol', round(u.Volume(), 1))
s = sol[0] if len(sol) == 1 else u
loc = s.translate(V(-925, 127.45, -217))          # left upstream clamp: X = x - 925, Y = y + 127.45, Z = z - 217 (no shift, no mirror)
b = loc.BoundingBox(); print('local bb', [round(v, 2) for v in (b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax)])
cq.exporters.export(cq.Workplane().add(loc), r'F:\Research\ASPS\side-polisher-redesign\flange-clamp-user-shape.step')
