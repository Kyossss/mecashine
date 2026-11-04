p = r'F:/Research/ASPS/side-polisher-redesign/cad_pincer9.py'
s = open(p, encoding='utf-8').read()
a = s.index('REFL_FACE_D = 6.0')
b = s.index('return cut(s, [cx(SENSOR_HOLE_D, z, f - 1, f + 6, M3) for z in (22, 36)])', a)
b = s.index(chr(10), b) + 1                              # end of the old reflector()
assert s.count('def reflector():') == 1
new = '''# Side ToF reflector (2026-10-22). The 45 x 48 grey PETG plate gave "signal fail": the VL53L0X's 25 degree cone is about 86 mm across at
# full retraction (193 mm in the model), so most of it missed. Now a flat 145.5 x 120 mm face with a 0.5 mm recess for a matte white paper
# or label insert, square to the beam. It can't be centred on the beam: the arm's legs sit 30..46 mm from the brush axis, right next to the
# beam axis (u 71.5), so the face starts at the leg's end (u 46) and runs upstream; the beam axis lands about 25 mm inside its edge.
# Face plane d = 7: upstream of the brush the shoe bulges up to 35.6 mm past the brush line, so this keeps 4.9 mm clear of it.
# The top-downstream corner is notched round the rail boss (z 94..128), which is above the beam anyway.
# Held three ways: the foot's two end-face screws (as before), and a tab on the leg's outer face under the two foot-to-arm screws (M3 x 20
# instead of M3 x 12 there). Prints face up, back flat on the bed, no supports.
REFL_FACE_D, REFL_BACK_D = 7.0, 13.5                     # face and back planes; the back clears the flange clamp by 1 mm at full retraction
REFL_U1, REFL_Z0, REFL_Z1 = LEG[1] + 145.5, 6.0, 126.0   # upstream edge; bottom (clears the belt and its braces); top
REFL_NOTCH_U, REFL_NOTCH_Z = 66.5, 93.5                  # rail boss: u 46..66, z 94..128
REFL_RECESS, REFL_RIM = 0.5, 4.0                         # insert recess depth, border round it
def reflector():
    f = LEG[1]
    plate = box(f, REFL_U1, REFL_FACE_D, REFL_BACK_D, REFL_Z0, REFL_Z1).cut(box(f - 1, REFL_NOTCH_U, REFL_FACE_D - 1, REFL_BACK_D + 1, REFL_NOTCH_Z, REFL_Z1 + 1))
    s = fuse([plate,
              box(f, f + 5.5, -1.5, REFL_FACE_D + 0.1, 14, 44),                             # flange on the foot's end face, with its two screws
              box(LEG[0], f + 0.1, T, REFL_BACK_D, 45, 71)])                                 # tab on the leg's outer face, under the foot-to-arm screws
    uc = (LEG[0] + LEG[1]) / 2
    r0 = REFL_RIM
    recess = fuse([box(f + 5.5 + r0, REFL_U1 - r0, REFL_FACE_D - 1, REFL_FACE_D + REFL_RECESS, REFL_Z0 + r0, REFL_NOTCH_Z - r0),
                   box(REFL_NOTCH_U + r0, REFL_U1 - r0, REFL_FACE_D - 1, REFL_FACE_D + REFL_RECESS, REFL_NOTCH_Z - r0 - 1, REFL_Z1 - r0)])
    tools = [recess]
    tools += [cx(SENSOR_HOLE_D, z, f - 1, f + 6.5, M3) for z in (22, 36)]                   # M3 x 12 into the foot's end face, as before
    tools += [cy(uc, z, T - 1, REFL_BACK_D + 1, M3) for z in (52, 66)]                      # M3 x 20 through the tab, leg and foot, into the foot's nuts
    return cut(s, tools)

'''
s = s[:a] + new + s[b:]
old_pr = "    'reflector': to_bed(real(REFL)),                                              # standing on its bottom edge"
assert s.count(old_pr) == 1, 'print line'
s = s.replace(old_pr, "    'reflector': to_bed(real(REFL).rotate(V(0, 0, 0), V(1, 0, 0), 90)),           # face up, flat back on the bed")
open(p, 'w', encoding='utf-8').write(s); print('ok')
