# Spray page v7: CAD posts and IR shelf (parts-mesh.json), detailed elbow and nozzle, screws and nuts, FC-51 reference model, close-up views.
import os
p = 'F:/Research/ASPS/spray-proposal/spray.html'; s = open(p, encoding='utf-8').read()
a = s.index('// proposal: a post each side'); b = s.index('// the polishing pass at 20 mm/s')
new = r'''// proposal: two posts and the IR shelf are CAD parts (parts-mesh.json, from spray_parts.py); the elbows, screws and the FC-51 module are drawn here
// Elbow frame: C = where the two port axes meet; a = side port / nozzle direction (across the belt, 15° down); b = down port direction.
const C_Y = 110, C_Z = 58, C_X = AX + 11, POST_FACE = AX + 4, UP_FACE = AX - 4;
const dirOf = s => V3(0, -s * Math.cos(TILT), -Math.sin(TILT));
const downOf = s => V3(0, s * Math.sin(TILT), -Math.cos(TILT));
const cOf = s => V3(C_X, s * C_Y, C_Z);
const at = (s, ua, ub) => cOf(s).addScaledVector(dirOf(s), ua).addScaledVector(downOf(s), ub);
const EL = { body: 6.75, sideR: 5.6, sideLen: 19.5, downLen: 21.5, nozLen: 13, lugA: 8.8, lugB: 9.4 };
const tipOf = s => at(s, EL.sideLen + EL.nozLen, 0);
const BLUE = 0x2f6fd0, STEEL = 0xb8bcc0, ZINC = 0x9ea4a8;
const sensorG = new THREE.Group(); scene.add(sensorG);
function metal(col) { return new THREE.MeshStandardMaterial({ color: col, metalness: 0.6, roughness: 0.35, side: THREE.DoubleSide }); }
function cylM(a, b, r, mat, seg) { const d = new THREE.Vector3().subVectors(b, a), m = new THREE.Mesh(new THREE.CylinderGeometry(r, r, d.length(), seg || 24), mat); m.position.copy(a).addScaledVector(d, 0.5); m.quaternion.setFromUnitVectors(V3(0, 1, 0), d.clone().normalize()); return m; }
function hexNut(c, axis) { const m = new THREE.Mesh(new THREE.CylinderGeometry(3.3, 3.3, 2.4, 6), metal(ZINC)); m.position.copy(c); m.quaternion.setFromUnitVectors(V3(0, 1, 0), axis); return m; }
[1, -1].forEach(s => {
  const blk = lam(COL.elbow);
  // elbow body: rounded corner, side port, down port, blue release collets, the lug between the ports
  const ball = new THREE.Mesh(new THREE.SphereGeometry(EL.body, 20, 14), blk); ball.position.copy(cOf(s)); scene.add(ball);
  scene.add(cylM(at(s, 0, 0), at(s, EL.sideLen - 2.2, 0), EL.sideR, blk));
  scene.add(cylM(at(s, EL.sideLen - 2.2, 0), at(s, EL.sideLen - 1.4, 0), EL.sideR - 0.2, metal(STEEL)));
  scene.add(cylM(at(s, EL.sideLen - 1.4, 0), at(s, EL.sideLen, 0), EL.sideR - 0.4, lam(BLUE)));
  scene.add(cylM(at(s, 0, 0), at(s, 0, EL.downLen - 2.5), EL.body, blk));
  scene.add(cylM(at(s, 0, EL.downLen - 2.5), at(s, 0, EL.downLen - 1.6), EL.body - 0.2, metal(STEEL)));
  scene.add(cylM(at(s, 0, EL.downLen - 1.6), at(s, 0, EL.downLen), EL.body - 0.5, lam(BLUE)));
  const lug = at(s, EL.lugA, EL.lugB);
  scene.add(cylM(V3(POST_FACE, lug.y, lug.z), V3(POST_FACE + 7, lug.y, lug.z), 3.6, blk));
  const web = box(-3.5, 3.5, -3, 3, -3, 3, COL.elbow); web.position.copy(at(s, EL.lugA / 2, EL.lugB / 2)); web.position.x = POST_FACE + 3.5; web.rotation.x = s * TILT; web.scale.set(1, 2.2, 2.4); scene.add(web);
  // nozzle: knurled ring, neck, knurled cap, white orifice insert
  const n0 = EL.sideLen, kn = metal(STEEL);
  scene.add(cylM(at(s, n0, 0), at(s, n0 + 5, 0), 4.4, kn, 30));
  scene.add(cylM(at(s, n0 + 5, 0), at(s, n0 + 7, 0), 3.4, kn));
  scene.add(cylM(at(s, n0 + 7, 0), at(s, n0 + 12.6, 0), 4.4, kn, 30));
  scene.add(cylM(at(s, n0 + 12.6, 0), tipOf(s), 1.6, lam(0xf2f2ee)));
  // M3 x 20 through the lug and the post, nut in the pocket on the upstream face
  scene.add(cylM(V3(POST_FACE + 7, lug.y, lug.z), V3(POST_FACE + 9.5, lug.y, lug.z), 2.75, metal(ZINC)));
  scene.add(cylM(V3(POST_FACE + 7, lug.y, lug.z), V3(POST_FACE + 7 - 20, lug.y, lug.z), 1.45, metal(STEEL)));
  scene.add(hexNut(V3(UP_FACE + 1.2, lug.y, lug.z), V3(1, 0, 0)));
  // foot screws: M3 heads, into the board's holes
  [AX - 14, AX + 9].forEach(xh => scene.add(cylM(V3(xh, s * 113, -83), V3(xh, s * 113, -80.6), 2.75, metal(ZINC))));
  // spray cone, apex at the nozzle tip
  const L = 75, g = new THREE.ConeGeometry(L * Math.tan(CONE), L, 28, 1, true); g.translate(0, -L / 2, 0);
  const cone = new THREE.Mesh(g, new THREE.MeshBasicMaterial({ color: 0x3b2a3a, transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide }));
  cone.position.copy(tipOf(s)); cone.quaternion.setFromUnitVectors(V3(0, -1, 0), dirOf(s)); scene.add(cone); coneL.push(cone);
});
// IR shelf: its screw into the post's vertical slot, nut on the far side
scene.add(cylM(V3(AX - 8, -101, 16), V3(AX - 10.5, -101, 16), 2.75, metal(ZINC)));
scene.add(hexNut(V3(POST_FACE + 1.2, -101, 16), V3(1, 0, 0)));
// FC-51 / MH-B module on the shelf (reference only, toggle): 32 x 14 board, M3 hole 5 mm from the header end, LEDs pointing across the belt
const HOLE_Y = -98, PCB_Z = 36;
sensorG.add(box(IRX - 7, IRX + 7, HOLE_Y - 5, HOLE_Y + 27, PCB_Z, PCB_Z + 1.6, 0x1f4fa8));
sensorG.add(box(IRX - 1, IRX + 6, HOLE_Y + 6, HOLE_Y + 13, PCB_Z + 1.6, PCB_Z + 6.6, 0x2f6fd0));
sensorG.add(box(IRX - 6, IRX - 1.5, HOLE_Y + 8, HOLE_Y + 14, PCB_Z + 1.6, PCB_Z + 3.2, 0x222222));
[-2.54, 0, 2.54].forEach(dx => sensorG.add(box(IRX + dx - 0.35, IRX + dx + 0.35, HOLE_Y - 9, HOLE_Y - 3, PCB_Z + 2, PCB_Z + 2.7, 0xd9b44a)));
sensorG.add(box(IRX - 4, IRX + 4, HOLE_Y - 5, HOLE_Y - 2.5, PCB_Z + 1.6, PCB_Z + 4.1, 0x111111));
sensorG.add(cylM(V3(IRX - 3.5, HOLE_Y + 27, PCB_Z + 4.1), V3(IRX - 3.5, HOLE_Y + 33, PCB_Z + 4.1), 2.5, lam(0x151515)));
sensorG.add(cylM(V3(IRX + 3.5, HOLE_Y + 27, PCB_Z + 4.1), V3(IRX + 3.5, HOLE_Y + 33, PCB_Z + 4.1), 2.5, new THREE.MeshLambertMaterial({ color: 0xe8f0f4, transparent: true, opacity: 0.7 })));
sensorG.add(cylM(V3(IRX, HOLE_Y, PCB_Z + 1.6), V3(IRX, HOLE_Y, PCB_Z + 4), 2.75, metal(ZINC)));
irBeam = cylBetween(V3(IRX, HOLE_Y + 33, PCB_Z + 4.1), V3(IRX, -50, PCB_Z + 4.1), 1.2, 0xe0402f, { transparent: true, opacity: 0.6 }); scene.add(irBeam);

'''
s = s[:a] + new + s[b:]
def rep(x, y):
    global s
    assert s.count(x) == 1, (s.count(x), x[:70]); s = s.replace(x, y)
rep("Promise.all(['station-mesh.json', 'shoe.json'].map(f => fetch(f).then(r => r.json()))).then(([M, S]) => {\n  for (const o of Object.values(M)) scene.add(mk(decode(o.m), COL[o.kind] || COL.frame, o.kind !== 'belt' && o.kind !== 'conveyor'));",
    "Promise.all(['station-mesh.json', 'shoe.json', 'parts-mesh.json'].map(f => fetch(f).then(r => r.json()))).then(([M, S, PRT]) => {\n  for (const o of Object.values(M)) scene.add(mk(decode(o.m), COL[o.kind] || COL.frame, o.kind !== 'belt' && o.kind !== 'conveyor'));\n  [PRT.postPos, PRT.postNeg].forEach(m => scene.add(mk(decode(m), COL.brk, true)));\n  scene.add(mk(decode(PRT.irShelf), 0xe0a640, true));")
rep('''      </div>
    </div>
  </main>''', '''        <button type="button" id="sens" aria-pressed="true">Show FC-51</button>
        <span class="seg" role="group" aria-label="View">
          <button type="button" id="vAll" aria-pressed="true">Overview</button>
          <button type="button" id="vNear" aria-pressed="false">Near post</button>
          <button type="button" id="vFar" aria-pressed="false">Far post + IR</button>
        </span>
      </div>
    </div>
  </main>''')
rep('''function frameCam() {
  const t = V3(-80, 0, 40), dir = V3(-0.62, -0.62, 0.48).normalize();
  const fov = camera.fov * Math.PI / 180, dist = 560 / (2 * Math.tan(fov / 2)) * (camera.aspect < 0.8 ? 1.4 : 1);
  controls.target.copy(t); camera.position.copy(t).add(dir.multiplyScalar(dist));
}''', '''function aim(t, dir, span) {
  const fov = camera.fov * Math.PI / 180, dist = span / (2 * Math.tan(fov / 2)) * (camera.aspect < 0.8 ? 1.4 : 1);
  controls.target.copy(t); camera.position.copy(t).add(dir.clone().normalize().multiplyScalar(dist));
}
const VIEWS = { vAll: [V3(-80, 0, 40), V3(-0.62, -0.62, 0.48), 560], vNear: [V3(AX + 4, 104, 10), V3(0.75, 0.35, 0.45), 190], vFar: [V3(AX - 14, -100, 20), V3(-0.7, -0.45, 0.5), 170] };
function frameCam(k) { k = k || 'vAll'; aim(VIEWS[k][0], VIEWS[k][1], VIEWS[k][2]); Object.keys(VIEWS).forEach(id => $(id).setAttribute('aria-pressed', String(id === k))); }
Object.keys(VIEWS).forEach(id => $(id).onclick = () => frameCam(id));
$('sens').onclick = () => { const on = !sensorG.visible; sensorG.visible = on; $('sens').setAttribute('aria-pressed', String(on)); place(); };''')
rep("  irBeam.visible = f.seen; $('t').value = i;", "  irBeam.visible = f.seen && sensorG.visible; $('t').value = i;")
open(p, 'w', encoding='utf-8').write(s)
open(os.environ.get('TEMP', '.') + '/sp.js', 'w', encoding='utf-8').write(s[s.rindex('<script>') + 8:s.rindex('</script>')])
print('ok')
