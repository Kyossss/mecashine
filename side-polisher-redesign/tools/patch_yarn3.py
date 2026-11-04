p = r'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/yarn_concept.py'
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)
rep("PITCH = (ZONE1 - ZONE0 - 0.25) / N_DISC                  # 7.25 mm per disc, 0.25 mm slack in the stack",
    "PITCH = 7.25                                              # per disc; 15 discs fill z 27 .. 135.75 with 1.25 mm slack")
rep("out['spec'] = {'hole_ang0': HOLE_ANG0,", "out['spec'] = {'bottom_row_z': round(g['BOT_DISC_Z0'] - 1.5 - 90, 2), 'hole_ang0': HOLE_ANG0,")
open(p, 'w', encoding='utf-8').write(s)

p = r'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/yarn-brush/chenille-brush.html'
s = open(p, encoding='utf-8').read()
rep("""  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));""",
"""  // lowest row: tied through the bottom part's plate with the knots underneath, just above the bearing
  for (let k = 0; k < spec.n_hole; k++) {
    const ang = -(spec.hole_ang0 + 360 / spec.n_hole * k) * Math.PI / 180;
    const p0 = new THREE.Vector3(R * Math.cos(ang), R * Math.sin(ang), 0);
    const zLine = spec.bottom_row_z - YR * 0.6;
    knot(p0, zLine - YR * 0.2);
    tail(p0, ang, zLine, 1); tail(p0, ang, zLine, -1);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));""")
rep("""  const strands = spec.n_disc * spec.n_hole;""", """  const strands = (spec.n_disc + 1) * spec.n_hole;""")
rep("""    <div class="stat"><b>${spec.n_disc}</b><span>tie discs</span></div>""", """    <div class="stat"><b>${spec.n_disc} + 1</b><span>tie discs + the bottom part</span></div>""")
rep("""      <li>Do all 6 holes, then the next disc.</li>""",
    """      <li>Do all 6 holes, then the next disc.</li>
      <li>The core’s bottom part has 6 tie holes too. Tie those strands from the top, so the knots end up underneath: that row sits just above the bearing, about 23 mm above the belt, and reaches the top edge of the shoe’s sole.</li>""")
rep("""    ['Each tail, hole to tip', `${spec.tail_len} mm`], ['Yarn length between stoppers', `${spec.zone[1] - spec.zone[0]} mm`],""",
    """    ['Each tail, hole to tip', `${spec.tail_len} mm`], ['Lowest yarn above the belt', `${(spec.bottom_row_z + 90).toFixed(0)} mm`], ['Shoe sole in your model', '0–16 mm'],""")
open(p, 'w', encoding='utf-8').write(s)
i = s.rindex('<script>'); j = s.rindex('</script>')
open(r'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/yarn_check.js', 'w', encoding='utf-8').write(s[i + 8:j])
print('ok')
