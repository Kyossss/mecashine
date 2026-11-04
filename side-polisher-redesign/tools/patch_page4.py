p = r'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/core-concept/slim-brush-core.html'
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)
rep("cscrew:   { color: 0x5f696e, name: 'M3×20 cross screw, top to bar' },", "cscrew:   { color: 0x5f696e, name: 'M3×16 cross screw, top to bar tip' },")
rep("const EXP = { top: [0, 0, 22], sscrew: [26, 0, 22], snut: [0, 0, 50], cscrew: [0, -26, 22], cnut: [0, 22, 22], bar: [0, 0, 0], bottom: [0, 0, -34], material: [0, 0, -12] };",
    "const EXP = { top: [0, 0, 22], sscrew: [26, 0, 22], snut: [0, 0, 50], cscrew: [24, 0, 30], cnut: [-22, 0, 22], bar: [0, 0, 0], bottom: [0, 0, -34], material: [0, 0, -12] };")
a = s.index('const TAGS = ['); b = s.index('const tagEls')
s = s[:a] + '''const TAGS = [
  { p: [0, 0, 74.5], t: 'D-shaped shaft hole, unchanged', n: '1' },
  { p: [11.4, 0, 68.2], t: 'M3×8 into a captive nut', n: '2' },
  { p: [9.2, 2, 52.5], t: 'M3×16 cross screw holds the bar', n: '3' },
  { p: [11, 0, 48.5], t: 'Top stopper, Ø22', n: '4' },
  { p: [6.9, 0, 0], t: 'Middle: 12 mm hex bar', n: '5' },
  { p: [11, 0, -65.5], t: 'Bottom stopper, Ø22, with hex socket', n: '6' },
  { p: [4, 0, -75], t: '8 mm axle into the 608ZZ', n: '7' },
];
''' + s[b:]
rep("['sscrew', 'M3×8 + nut'], ['cscrew', 'M3×20 + nut'],", "['sscrew', 'M3×8 + nut'], ['cscrew', 'M3×16 + nut'],")
rep("<span>Hub</span><span class=\"n\">Ø14</span><span class=\"n new\">Ø24</span>", "<span>Hub</span><span class=\"n\">Ø14</span><span class=\"n new\">Ø${dims.hub_d}</span>\n    <span>Stoppers</span><span class=\"n\">none</span><span class=\"n new\">Ø${dims.stop_d}</span>")
rep("<li>Stopper size: 30 mm across. Bigger holds soft material better but must stay under the brush’s outer size.</li>",
    "<li>The bar’s top end narrows to an 8 mm hex tip, set off-centre so the bar still lies flat on the bed. The cross screw goes through the tip.</li>")
rep("Three printed parts: a top with your motor shaft hole and the top stopper,", "Three printed parts: a slim 16 mm top with your motor shaft hole and a 22 mm stopper,")
rep("and a bottom with the second stopper and the axle into the bearing.", "and a bottom with the second 22 mm stopper and the axle into the bearing.")
open(p, 'w', encoding='utf-8').write(s)
i = s.rindex('<script>'); j = s.rindex('</script>')
open(r'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/core_check.js', 'w', encoding='utf-8').write(s[i + 8:j])
print('ok')
