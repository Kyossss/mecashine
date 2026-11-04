import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = s.index('# ---------------- guide block.'); b = s.index('# ---------------- guide rail')
new = open(sys.argv[2], encoding='utf-8').read()
s = s[:a] + new + s[b:]
a2 = """    # handed: A = left upstream and right downstream, B = left downstream and right upstream (mirror image). Printed upside down on the
    # flat top: the cheeks point up, and the rail hole and nut slots are short bridges, so no supports are needed.
    'bushing-block-A': to_bed(BLOCK.rotate(V(0, 0, 0), V(1, 0, 0), 180)),
    'bushing-block-B': to_bed(BLOCK.mirror('XZ').rotate(V(0, 0, 0), V(1, 0, 0), 180)),"""
b2 = """    # handed: A = left upstream and right downstream, B = left downstream and right upstream (mirror image). Printed lying on the outer
    # face, rail hole upright, no supports.
    'bushing-block-A': to_bed(BLOCK.rotate(V(0, 0, 0), V(1, 0, 0), 90)),
    'bushing-block-B': to_bed(BLOCK.mirror('XZ').rotate(V(0, 0, 0), V(1, 0, 0), -90)),"""
assert a2 in s
s = s.replace(a2, b2)
open(p, 'w', encoding='utf-8').write(s); print('ok')
