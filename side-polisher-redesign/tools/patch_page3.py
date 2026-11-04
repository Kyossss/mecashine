p = r'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/core-concept/slim-brush-core.html'
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)
rep('''<p class="lede">A thin hex rod with a fixed stopper under the hub and a loose stopper at the bottom, holding whatever brush material you pick. Your motor shaft hole stays exactly as it is.</p>''',
'''<p class="lede">Three printed parts: a top with your motor shaft hole and the top stopper, a plain hex bar in the middle, and a bottom with the second stopper and the axle into the bearing. The brush material sits on the bar between the two stoppers.</p>''')
rep('''<h2>Swapping the brush</h2>
    <ol>
      <li>Remove the foot bracket’s 4 screws and lower the foot with its bearing.</li>
      <li>Loosen the M3×8 through the key hole in the arm’s ring.</li>
      <li>Slide the core down 15 mm off the motor shaft and lift it out.</li>
      <li>Pull the bottom washer off the rod and slide the old material off.</li>
      <li>Slide the new material on, drop the washer back on, and reverse steps 1–3.</li>
    </ol>''',
'''<h2>How each part prints</h2>
    <table id="prints"></table>

    <h2>Swapping the brush</h2>
    <ol>
      <li>Remove the foot bracket’s 4 screws and lower the foot with its bearing.</li>
      <li>Loosen the M3×8 through the key hole in the arm’s ring.</li>
      <li>Slide the core down 15 mm off the motor shaft and lift it out.</li>
      <li>Pull the bottom part off the bar and slide the old material off.</li>
      <li>Slide the new material on, push the bottom part back on, and reverse steps 1–3.</li>
    </ol>
    <p style="margin:10px 0 0;max-width:60ch">The cross screw only comes out for a repair, when you want to separate the top from the bar.</p>''')
rep('''      <li>Rod size: 12 mm hex is a starting point. Once you pick the material, I match the rod to its hole.</li>
      <li>Stopper size: 30 mm across, 3 mm thick. Bigger holds soft material better but must stay under the brush’s outer size.</li>
      <li>Printing: standing up, hub on the bed, is simplest. Lying on a hex flat is stronger, but then the round hub and stopper need a flat side.</li>
      <li>Foot bracket: keep 4 screws, or make it quicker to remove for swaps.</li>''',
'''      <li>Bar size: 12 mm hex is a starting point. Once you pick the material, I match the bar to its hole.</li>
      <li>Stopper size: 30 mm across. Bigger holds soft material better but must stay under the brush’s outer size.</li>
      <li>Foot bracket: keep 4 screws, or make it quicker to remove for swaps.</li>''')
a = s.index('const PARTS = {'); b = s.index('const canvas')
s = s[:a] + '''const PARTS = {
  top:      { color: 0xd98a46, name: 'Top: hub, shaft hole, top stopper' },
  bar:      { color: 0xe7b273, name: 'Middle: 12 mm hex bar' },
  bottom:   { color: 0xc4673f, name: 'Bottom: stopper, socket, axle' },
  sscrew:   { color: 0x5f696e, name: 'M3×8 onto the shaft’s flat' },
  snut:     { color: 0x8a9297, name: 'M3 nut, dropped in from the top' },
  cscrew:   { color: 0x5f696e, name: 'M3×20 cross screw, top to bar' },
  cnut:     { color: 0x8a9297, name: 'M3 nut for the cross screw' },
  material: { color: 0x9fd3c7, name: 'Brush material (any, with a hole)', key: 'tMat', opacity: 0.38 },
  shaft:    { color: 0xb7bec2, name: 'Motor shaft (D-shaped)', key: 'tMot' },
  motor:    { color: 0x9aa3a8, name: 'Motor body', key: 'tMot' },
  bearing:  { color: 0xc9a23a, name: '608ZZ bearing', key: 'tFoot' },
  foot:     { color: 0x3fa874, name: 'Foot bracket', key: 'tFoot', opacity: 0.55 },
  arm:      { color: 0x8f7fd1, name: 'Arm frame', key: 'tArm', opacity: 0.22 },
  old:      { color: 0xc06c4a, name: 'Current core', key: 'cmp' },
};
// explode directions (mm at 100%)
const EXP = { top: [0, 0, 22], sscrew: [26, 0, 22], snut: [0, 0, 50], cscrew: [0, -26, 22], cnut: [0, 22, 22], bar: [0, 0, 0], bottom: [0, 0, -34], material: [0, 0, -12] };

''' + s[b:]
a = s.index('const TAGS = ['); b = s.index('const tagEls')
s = s[:a] + '''const TAGS = [
  { p: [0, 0, 74.5], t: 'D-shaped shaft hole, unchanged', n: '1' },
  { p: [12, 0, 68.2], t: 'M3×8 into a captive nut', n: '2' },
  { p: [0, -12, 52.5], t: 'M3×20 cross screw holds the bar', n: '3' },
  { p: [15, 0, 48.5], t: 'Top stopper, Ø30', n: '4' },
  { p: [6.9, 0, 0], t: 'Middle: 12 mm hex bar', n: '5' },
  { p: [15, 0, -65.5], t: 'Bottom stopper with hex socket', n: '6' },
  { p: [4, 0, -75], t: '8 mm axle into the 608ZZ', n: '7' },
];
''' + s[b:]
a = s.index('function buildTables() {'); b = s.index('function vis(k)')
s = s[:a] + '''function buildTables() {
  const sw = (k) => `<span class="sw" style="background:#${PARTS[k].color.toString(16).padStart(6, '0')}"></span>`;
  const rows = [
    ['top', `${dims.top_len} mm, Ø${dims.hub_d} hub`], ['bar', `${dims.bar_len} mm long`], ['bottom', `${dims.bot_len} mm, Ø${dims.stop_d} disc`],
    ['sscrew', 'M3×8 + nut'], ['cscrew', 'M3×20 + nut'], ['material', `${dims.material_len} mm of bar`],
  ];
  $('parts').innerHTML = rows.map(r => `<tr><td>${sw(r[0])}${PARTS[r[0]].name}</td><td class="v">${r[1]}</td></tr>`).join('');
  const pr = [
    ['top', 'Stopper face on the bed; the shaft hole points up and comes out round', `${dims.vol_top} cm³`],
    ['bar', 'Lying on a flat side, cross hole pointing up; layers run along the bar', `${dims.vol_bar} cm³`],
    ['bottom', 'Socket face on the bed, axle pointing up', `${dims.vol_bot} cm³`],
  ];
  $('prints').innerHTML = pr.map(r => `<tr><td>${sw(r[0])}${r[1]}</td><td class="v">${r[2]}</td></tr>`).join('') +
    `<tr><td>No supports on any of the three</td><td class="v"></td></tr>`;
  const total = (dims.vol_top + dims.vol_bar + dims.vol_bot).toFixed(1);
  $('cmp').innerHTML = `<span class="h"></span><span class="h n">Current</span><span class="h n">Slim</span>
    <span>Printed parts</span><span class="n">1</span><span class="n new">3</span>
    <span>Body</span><span class="n">Ø24 round</span><span class="n new">12 hex</span>
    <span>Hub</span><span class="n">Ø14</span><span class="n new">Ø24</span>
    <span>Shaft screw hole</span><span class="n">Ø2.5, no nut</span><span class="n new">Ø3.4 + nut</span>
    <span>Holds material</span><span class="n">no</span><span class="n new">2 stoppers</span>
    <span>Plastic</span><span class="n">${dims.vol_old} cm³</span><span class="n new">${total} cm³</span>`;
}

''' + s[b:]
rep('<div class="eyebrow">MecaShine · brush core redesign</div>', '<div class="eyebrow">MecaShine · brush core redesign · 3 parts</div>')
open(p, 'w', encoding='utf-8').write(s)
i = s.rindex('<script>'); j = s.rindex('</script>')
open(r'C:/Users/kyo/AppData/Local/Temp/claude/f--Research/60bbfa67-81a5-4e34-b9ca-a3e53978cd7c/scratchpad/core_check.js', 'w', encoding='utf-8').write(s[i + 8:j])
print('ok')
