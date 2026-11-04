p = r'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/core_concept.py'
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)
rep("STOP_D = 30.0", "STOP_D = 22.0                                   # both stoppers: 5 mm past the 12 mm bar all round")
rep("HUB_D = 24.0", "HUB_D = 16.0                                    # slimmest hub that holds the shaft screw's captive nut")
rep("CROSS_Z = TOP_STOP_Z0 + 5.5                     # cross screw through the hub and the bar",
    "CROSS_Z = TOP_STOP_Z0 + 5.5                     # cross screw through the hub and the bar's tip\n"
    "TIP_AF, TIP_OFF = 8.0, -2.0                     # bar's top end: an 8 mm hex tip, set 2 mm off-centre so one flat is flush with a bar flat (prints flat)\n"
    "TIP_Z0 = TOP_STOP_Z0                            # the bar's shoulder butts against the top stopper")
rep("socket = hexz(HEX_AF + 2 * FIT_TOP, TOP_STOP_Z0 - 1, TOP_SOCK_Z1)",
    "def hexz_at(af, d0, z0, z1):\n"
    "    return cq.Workplane('XY').polygon(6, af / 0.8660254).extrude(z1 - z0).val().translate(V(0, AX_D + d0, z0))\n"
    "socket = hexz_at(TIP_AF + 2 * FIT_TOP, TIP_OFF, TOP_STOP_Z0 - 1, TOP_SOCK_Z1)")
rep("NUT_U0 = 4.2", "NUT_U0 = 3.2                                    # nut 3.3..5.7 mm out: 1.4 mm of plastic to the shaft's flat, about 1.5 mm to the hub surface")
# cross screw: along u, through the tip's centre line; head seat on +u, nut pocket on -u
a = s.index("cross_hole = "); b = s.index("top = top.cut(")
s = s[:a] + '''CROSS_D = AX_D + TIP_OFF
cross_hole = cq.Solid.makeCylinder(M3 / 2, HUB_D + 2, V(-HUB_D / 2 - 1, CROSS_D, CROSS_Z), V(1, 0, 0))
HEAD_U = 7.5                                    # head seat, just under the hub surface on this chord
cross_seat = cq.Solid.makeCylinder(3.25, 3, V(HEAD_U, CROSS_D, CROSS_Z), V(1, 0, 0))
NUT_U1 = -(TIP_AF / 2 / 0.8660254 + FIT_TOP) - 0.3    # nut pocket starts just outside the tip's corner
cross_nut_pocket = cq.Workplane(cq.Plane(origin=(-HUB_D / 2 - 1, CROSS_D, CROSS_Z), xDir=(0, 0, 1), normal=(1, 0, 0))).polygon(6, NUT_AF / 0.8660254).extrude(HUB_D / 2 + 1 + NUT_U1).val()
''' + s[b:]
rep("bar = hexz(HEX_AF, BAR_Z0, BAR_Z1).cut(cq.Solid.makeCylinder(M3 / 2, 20, V(0, AX_D - 10, CROSS_Z), V(0, 1, 0)))\nbar = cq.Workplane().add(bar).edges('|Z').fillet(0.6).val()",
    "bar = cq.Workplane().add(hexz(HEX_AF, BAR_Z0, TIP_Z0)).edges('|Z').fillet(0.6).val()\n"
    "bar = bar.fuse(hexz_at(TIP_AF, TIP_OFF, TIP_Z0 - 0.1, BAR_Z1)).clean()\n"
    "bar = bar.cut(cq.Solid.makeCylinder(M3 / 2, 20, V(-10, CROSS_D, CROSS_Z), V(1, 0, 0)))")
rep("yh = AX_D + HUB_D / 2 - 2                       # cross screw head seat\ncross_screw = cq.Solid.makeCylinder(1.5, 20, V(0, yh, CROSS_Z), V(0, -1, 0)).fuse(cq.Solid.makeCylinder(2.85, 1.65, V(0, yh, CROSS_Z), V(0, 1, 0)))\ncross_nut = nut_on((0, AX_D + CROSS_NUT_D0 - 0.1, CROSS_Z), (0, 1, 0), (1, 0, 0))     # nut 9.3..6.9 mm from the axis, inner end of the pocket",
    "cross_screw = cq.Solid.makeCylinder(1.5, 16, V(HEAD_U, CROSS_D, CROSS_Z), V(-1, 0, 0)).fuse(cq.Solid.makeCylinder(2.85, 1.65, V(HEAD_U, CROSS_D, CROSS_Z), V(1, 0, 0)))   # M3x16\n"
    "cross_nut = nut_on((NUT_U1 - 0.1 - 2.4, CROSS_D, CROSS_Z), (1, 0, 0), (0, 0, 1))")
# the old report line used the removed names
a = s.index("nb = cross_nut.BoundingBox()"); b = s.index("print('hub radius'")
s = s[:a] + '''nb = cross_nut.BoundingBox()
print('cross nut u', round(nb.xmin, 2), '..', round(nb.xmax, 2), ' screw tip at', round(HEAD_U - 16, 2), '-> passes the nut by', round(nb.xmin - (HEAD_U - 16), 2), 'mm;  hub surface on that chord at u', round(-math.sqrt((HUB_D / 2) ** 2 - TIP_OFF ** 2), 2))
''' + s[b:]
open(p, 'w', encoding='utf-8').write(s); print('ok')
