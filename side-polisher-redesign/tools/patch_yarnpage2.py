p = r'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/yarn-brush/chenille-brush.html'
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)
rep("""      <li>Slide the tied discs onto the hex bar, flipping every other disc upside down. The holes sit 15° off the hex, so a flipped disc puts its strands in the gaps of the one below.</li>""",
    """      <li>Slide the tied discs onto the hex bar. Every disc is the same and goes on either way up; the holes sit opposite the hex’s flats, where the plastic is thickest.</li>""")
rep("""    <div class="note">The 6 mm yarn thickness is an estimate from your photo. Once you send a picture of a strand next to a ruler or someone’s fingers, I’ll set the tie hole size to match.</div>""",
    """    <div class="note">Sized for your yarn: a 1 mm core, about 9 mm across with the fur. The 2.4 mm tie holes take the strand folded double; if your yarn fights going through, I can open them to 2.6 mm.</div>""")
rep("""      <li>Density: 6 strands per disc is the proposal. 8 per disc also fits on this disc and makes it a third fuller.</li>""",
    """      <li>Density: 6 strands per disc on 15 discs. A 22 mm disc only has room for holes opposite the 6 flats of the hex bar, so for a fuller brush the option is more, thinner discs (for example 18 at 6 mm).</li>""")
rep("""<p>The two tails come out on top of the disc and spread out to each side. Each hole holds one strand, so two fluffy tails.</p>""",
    """<p>The two tails come out on top of the disc and spread out to each side. Each 2.4 mm hole holds one strand folded double, so two fluffy tails.</p>""")
rep("""    ['Size', `Ø${spec.disc_d} × ${spec.pitch} mm`], ['Plate', `${spec.plate_t} mm thick, spacer collar Ø${spec.collar_d} both sides`],""",
    """    ['Size', `Ø${spec.disc_d} × ${spec.pitch} mm, as big as the bearing`], ['Plate', `${spec.plate_t} mm thick, hex spacer collar on both faces`],""")
rep("""    ['Print', 'flat on the bed, no supports; both sides are the same'],""", """    ['Print', 'flat on the bed, no supports; both faces are the same'],""")
# furrier, thicker yarn; smaller knots
rep("const SEG = 12, RAD = 7;", "const SEG = 14, RAD = 9;")
rep("for (let r = 0; r < RAD; r++) row.push((rnd() - 0.5) * 0.9);", "for (let r = 0; r < RAD; r++) row.push((rnd() - 0.5) * 1.6);")
rep("const LAT = 6, LON = 9, r0 = YR * 1.15;", "const LAT = 6, LON = 9, r0 = YR * 0.8;")
rep("const R = spec.hole_r, TIP = spec.brush_r, YR = spec.yarn_d / 2 * 0.85;", "const R = spec.hole_r, TIP = spec.brush_r, YR = spec.yarn_d / 2 * 0.8;")
rep("if (i % 2) holder.rotation.x = Math.PI;               // flipped", "")
rep("const flip = i % 2 ? 1 : -1;                          // the page is the mirrored (left arm) view, and odd discs are flipped", "const flip = -1;                                       // the page is the mirrored (left arm) view")
open(p, 'w', encoding='utf-8').write(s)
i = s.rindex('<script>'); j = s.rindex('</script>')
open(r'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/yarn_check.js', 'w', encoding='utf-8').write(s[i + 8:j])
print('ok')
