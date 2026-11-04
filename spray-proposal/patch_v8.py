# Spray page v8 (2026-11-03): IR on the box side, nozzles 25 mm higher and 25 deg down, box at the real 80 mm gap, v4 printed post revised.
p = 'F:/Research/ASPS/spray-proposal/spray.html'; s = open(p, encoding='utf-8').read()
def rep(x, y):
    global s
    assert s.count(x) == 1, (s.count(x), x[:80]); s = s.replace(x, y)
# ---- 3D
rep('const AX = 680 - 780, TILT = 15 * Math.PI / 180', 'const AX = 680 - 780, TILT = 25 * Math.PI / 180')
rep('const C_Y = 110, C_Z = 58, C_X = AX + 11, POST_FACE = AX + 4, UP_FACE = AX - 4;', 'const C_Y = 110, C_Z = 83, C_X = AX + 11.75, POST_FACE = AX + 5, UP_FACE = AX - 5;')
rep("// Elbow frame: C = where the two port axes meet; a = side port / nozzle direction (across the belt, 15° down)", "// Elbow frame: C = where the two port axes meet; a = side port / nozzle direction (across the belt, 25° down)")
rep('scene.add(box(-580, -80, 175, 470, -108, 77, COL.box));', 'scene.add(box(-580, -80, 152, 447, -108, 77, COL.box));   // casing box wall 80 mm from the belt frame (|y| 72)')
rep("for (const o of Object.values(M)) scene.add(", "for (const [k, o] of Object.entries(M)) if (!k.startsWith('Casing box')) scene.add(")
rep("  [AX - 14, AX + 9].forEach(xh => scene.add(cylM(V3(xh, s * 113, -83), V3(xh, s * 113, -80.6), 2.75, metal(ZINC))));",
    "  [AX - 15, AX + 15].forEach(xh => scene.add(cylM(V3(xh, s * 116, -80), V3(xh, s * 116, -77.6), 2.75, metal(ZINC))));")
rep('''scene.add(cylM(V3(AX - 8, -101, 16), V3(AX - 10.5, -101, 16), 2.75, metal(ZINC)));
scene.add(hexNut(V3(POST_FACE + 1.2, -101, 16), V3(1, 0, 0)));''',
'''scene.add(cylM(V3(AX - 9, 101, 15), V3(AX - 11.5, 101, 15), 2.75, metal(ZINC)));
scene.add(hexNut(V3(POST_FACE + 1.2, 101, 15), V3(1, 0, 0)));''')
a = s.index('// FC-51 / MH-B module on the shelf'); b = s.index('// the polishing pass at 20 mm/s')
s = s[:a] + '''// FC-51 / MH-B module on the box-side shelf (reference only, toggle): 32 x 14 board, M3 hole 5 mm from the header end, LEDs pointing across the belt (-y)
const HOLE_Y = 98, PCB_Z = 36, yb = (a, b) => [HOLE_Y - b, HOLE_Y - a];
const bx = (x0, x1, ya, yz, z0, z1, c) => { const [y0, y1] = yb(ya, yz); return box(x0, x1, y0, y1, z0, z1, c); };
sensorG.add(bx(IRX - 7, IRX + 7, -5, 27, PCB_Z, PCB_Z + 1.6, 0x1f4fa8));
sensorG.add(bx(IRX - 1, IRX + 6, 6, 13, PCB_Z + 1.6, PCB_Z + 6.6, 0x2f6fd0));
sensorG.add(bx(IRX - 6, IRX - 1.5, 8, 14, PCB_Z + 1.6, PCB_Z + 3.2, 0x222222));
[-2.54, 0, 2.54].forEach(dx => sensorG.add(bx(IRX + dx - 0.35, IRX + dx + 0.35, -9, -3, PCB_Z + 2, PCB_Z + 2.7, 0xd9b44a)));
sensorG.add(bx(IRX - 4, IRX + 4, -5, -2.5, PCB_Z + 1.6, PCB_Z + 4.1, 0x111111));
sensorG.add(cylM(V3(IRX - 3.5, HOLE_Y - 27, PCB_Z + 4.1), V3(IRX - 3.5, HOLE_Y - 33, PCB_Z + 4.1), 2.5, lam(0x151515)));
sensorG.add(cylM(V3(IRX + 3.5, HOLE_Y - 27, PCB_Z + 4.1), V3(IRX + 3.5, HOLE_Y - 33, PCB_Z + 4.1), 2.5, new THREE.MeshLambertMaterial({ color: 0xe8f0f4, transparent: true, opacity: 0.7 })));
sensorG.add(cylM(V3(IRX, HOLE_Y, PCB_Z + 1.6), V3(IRX, HOLE_Y, PCB_Z + 4), 2.75, metal(ZINC)));
irBeam = cylBetween(V3(IRX, HOLE_Y - 33, PCB_Z + 4.1), V3(IRX, 50, PCB_Z + 4.1), 1.2, 0xe0402f, { transparent: true, opacity: 0.6 }); scene.add(irBeam);

''' + s[b:]
rep("vNear: [V3(AX + 4, 104, 10), V3(0.75, 0.35, 0.45), 190], vFar: [V3(AX - 14, -100, 20), V3(-0.7, -0.45, 0.5), 170]",
    "vNear: [V3(AX - 12, 102, 35), V3(-0.45, -0.45, 0.77), 200], vFar: [V3(AX + 4, -104, 25), V3(0.75, -0.35, 0.45), 210]")
rep('<button type="button" id="vNear" aria-pressed="false">Near post</button>', '<button type="button" id="vNear" aria-pressed="false">Box-side post + IR</button>')
rep('<button type="button" id="vFar" aria-pressed="false">Far post + IR</button>', '<button type="button" id="vFar" aria-pressed="false">Far post</button>')
rep('a nozzle on a post each side of the belt sprays the side of the shoe slightly downward, in bursts triggered by an IR sensor',
    'a nozzle on a post each side of the belt sprays the side of the shoe 25 degrees downward, in bursts triggered by an IR sensor on the casing-box side')
rep('<div class="badge">Proposal · not in Fusion</div>', '<div class="badge">Revision 8 · proposal · not in Fusion</div>')
# ---- text
rep('''<p class="lede">A nozzle on each side of the belt, just before the reflector, spraying the side of the shoe slightly downward. An IR sensor sees the shoe and the pump fires in bursts. The side brushes spread the polish a few seconds later.</p>''',
'''<p class="lede">A nozzle on each side of the belt, just before the reflector, spraying the side of the shoe from higher up and more steeply. An IR sensor on the casing-box side sees the shoe and the pump fires in bursts. The side brushes spread the polish a few seconds later.</p>

    <h2>What changed in this revision</h2>
    <ul>
      <li><b>IR sensor on the box side,</b> the left as you look in from the entrance. The shelf and FC-51 are now on that post.</li>
      <li><b>Nozzles 25 mm higher.</b> The tip is now 69 mm above the belt (was 50).</li>
      <li><b>Tilted 25° down</b> (was 15°).</li>
      <li><b>Real box gap:</b> the casing box is drawn 80 mm from the belt, and the post's base plate is 10 mm shorter so it clears it.</li>
      <li>The posts are the ones you printed, the flat-printing version with the base plate, changed only as above.</li>
    </ul>''')
rep('''<li><b>Holders:</b> one printed post each side, standing on the base board beside the belt, with its foot screwed down by two M3 through the board's existing holes. Nothing touches the belt or its frame.</li>''',
'''<li><b>Holders:</b> one printed post each side, standing on the base board beside the belt. Its base plate is screwed down by two M3 through the board's existing holes. Nothing touches the belt or its frame.</li>
      <li><b>Box gap:</b> I measured your 80 mm from the outside of the belt's side frame, which is 72 mm from the belt centre. That puts the box wall 152 mm from the centre. It also explains the snug fit: the old base plate reached 150. The plate now ends at 140, so it's 12 mm clear. If you measured from the edge of the slats instead (65 mm from the centre), the wall is at 145 and the plate is still 5 mm clear.</li>''')
rep("<li><b>A seat under the side port</b> sets the 15° downward tilt, so the single screw can't let it turn.</li>",
    "<li><b>A seat under the side port</b> sets the 25° downward tilt, so the single screw can't let it turn.</li>")
rep('<li><b>Nozzle tip:</b> 79 mm from the centre of the belt (25 mm clear of the widest shoe) and 50 mm above the belt. The spray band is about 27 to 58 mm up the side of the shoe.</li>',
    '''<li><b>Nozzle tip:</b> 80.5 mm from the centre of the belt (about 30 mm clear of the widest shoe) and 69 mm above the belt. The spray's centre line meets the side of the shoe 50 to 55 mm up (it was about 42), and the spray covers about 20 to 72 mm.</li>
      <li><b>Over the toe:</b> the toe is only 50 to 57 mm tall for its first 100 mm, so the top of the spray passes over it there and some lands on the toe cap. Further back, where the shoe is taller, all of it hits the side.</li>''')
a = s.index('    <h2>Universal IR mount</h2>'); b = s.index('    <h2>How much polish</h2>')
s = s[:a] + '''    <h2>Universal IR mount</h2>
    <ul>
      <li><b>A small shelf on the box-side post,</b> 26 mm before the nozzles, looking across the belt. It's drawn with your FC-51 / MH-B module on it; switch it off with "Show FC-51".</li>
      <li><b>Height:</b> the shelf bolts into one of eight holes in the post, 6 mm apart, which puts the sensor anywhere from 16 to 58 mm above the belt. It's drawn at 40 mm. Both posts have the holes, so the shelf can still go on the far side.</li>
      <li><b>Reach:</b> the module's M3 hole sits in a 12 mm slot along the shelf. That puts the LED tips 59 to 71 mm from the belt centre, 9 to 21 mm from the widest shoe. This type of sensor only sees black leather up close, so keep it near the shoe.</li>
      <li><b>Fit by the box:</b> the shelf sits between the post and the belt (66 to 112 mm from the centre), so the box doesn't get in the way.</li>
      <li><b>Other sensors:</b> two zip-tie slots across the shelf hold any board that doesn't fit the M3 hole.</li>
      <li><b>Bursts</b> only on the polishing pass: the first as soon as the sensor sees the shoe, then one 0.4 s burst every few seconds while it still does.</li>
    </ul>

    <h2>Printed parts and screws</h2>
    <table>
      <thead><tr><th>Part</th><th>Qty</th><th>Notes</th></tr></thead>
      <tbody>
        <tr><td>Nozzle post (mirrored pair)</td><td class="v">1 + 1</td><td>63 cm³ solid each. Prints lying on its inner face (the face toward the belt), 179 × 48 × 40 mm, no supports.</td></tr>
        <tr><td>IR shelf</td><td class="v">1</td><td>7 cm³. Prints flat.</td></tr>
        <tr><td>M3 × 20 + nut</td><td class="v">3</td><td>Elbow lug to post (2, nut in the post's pocket), IR shelf to post (1)</td></tr>
        <tr><td>M3 × 8 + nut</td><td class="v">1</td><td>Sensor to shelf</td></tr>
        <tr><td>M3 to the board</td><td class="v">4</td><td>Two per base plate (8 mm thick). The length depends on the board's thickness.</td></tr>
      </tbody>
    </table>
    <p class="small">The base plate has two 30 mm slots running across the belt, 30 mm apart along it. They meet board holes 101 to 131 mm from the belt centre, 36 to 66 mm outside the slats. The shelf screw goes through 14 mm (shelf leg plus post), so it needs an M3 × 20, not M3 × 12.</p>

''' + s[b:]
rep('<li>Mist that misses the shoe crosses toward the other post and lands on the belt and board.</li>',
    '<li>Mist that misses the shoe crosses toward the other post. At 25° more of it lands on the belt between the posts than before.</li>')
rep('''      <li><b>Magnets and the heel plate:</b> later, as you said.</li>''',
    '''      <li><b>Height:</b> is a 69 mm nozzle tip high enough? Going higher only makes the posts taller; the tilt stays at 25°.</li>
      <li><b>The 80 mm gap:</b> was it measured from the belt's side frame or from the edge of the slats? Either way the new plate clears the box.</li>''')
rep('The posts and IR shelf are CAD parts made for this proposal;', 'The posts and IR shelf are CAD parts (your printed post, revised for this proposal);')
open(p, 'w', encoding='utf-8').write(s); print('ok')
