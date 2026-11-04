// Proposal v3 station meshes from your Fusion meshes: the carriage's far wall and motor-side mount 15 mm deeper (vertices below
// the top plate moved down), the 8 mm pin removed (a 608ZZ goes into the wall instead), the motor holder 15 mm lower.
// The old core and the old sensor bracket are left out. Then: clearances of the proposal against everything.
const fs = require('fs');
const M = JSON.parse(fs.readFileSync('top-station-mesh.json', 'utf8'));
const R = JSON.parse(fs.readFileSync('roller-mesh.json', 'utf8')), SP = R.spec, D = SP.leg_ext;
const dec = b64 => { const b = Buffer.from(b64, 'base64'); return Array.from(new Int16Array(b.buffer, b.byteOffset, b.length / 2), v => v / 10); };
const enc = arr => Buffer.from(new Int16Array(arr.map(v => Math.round(v * 10))).buffer).toString('base64');
const out = {};
for (const [name, o] of Object.entries(M)) {
  if (o.kind === 'oldcore' || o.kind === 'sensorbracket') continue;
  let a = dec(o.m);
  if (name === 'Body67') {
    const keep = [];
    for (let i = 0; i < a.length; i += 9) {
      const P = [0, 3, 6].map(k => [a[i + k], a[i + k + 1], a[i + k + 2]]);
      const onPin = P.every(p => p[1] > 50.5 && p[1] < 71.2 && Math.hypot(p[0], p[2] - 201) < 4.4);
      if (onPin) continue;                                     // the 8 mm pin is gone
      for (const p of P) {
        if ((p[1] > 60 && p[2] < 224) || (p[1] < -90 && p[2] < 226)) p[2] -= D;   // far wall and motor-side mount 15 mm deeper
        keep.push(p[0], p[1], p[2]);
      }
    }
    a = keep;
  }
  if (name === 'Body68') for (let i = 2; i < a.length; i += 3) a[i] -= D;        // motor holder 15 mm lower
  out[name] = { kind: o.kind, m: enc(a) };
}
fs.writeFileSync('top-station-v3.json', JSON.stringify(out));
// clearance checks at home (roller axis 186)
const AX = SP.axis_z;
function closest(arr, fn) { let best = 1e9, at = null; for (let i = 0; i < arr.length; i += 9) { const P = [0, 3, 6].map(k => [arr[i + k], arr[i + k + 1], arr[i + k + 2]]);
  for (let s = 0; s <= 8; s++) for (let t = 0; t <= 8 - s; t++) { const u = s / 8, v = t / 8, w = 1 - u - v; const p = [0, 1, 2].map(j => P[0][j] * u + P[1][j] * v + P[2][j] * w); const d = fn(p); if (d < best) { best = d; at = p.map(x => x.toFixed(1)); } } }
  return [best, at]; }
const yarnGap = p => (p[1] < -60 || p[1] > 47) ? 1e9 : Math.hypot(p[0], p[2] - AX) - SP.brush_r;
console.log('yarn (52 mm, y -60..47) to:');
for (const [name, o] of Object.entries(out)) { const [d, at] = closest(dec(o.m), yarnGap); if (d < 30) console.log('  ', name.padEnd(36), o.kind.padEnd(12), d.toFixed(1), 'mm at', at.join(',')); }
const br = dec(R.bracket), bb = [Math.min(...br.filter((_, i) => i % 3 === 0)), Math.max(...br.filter((_, i) => i % 3 === 0)), Math.min(...br.filter((_, i) => i % 3 === 1)), Math.max(...br.filter((_, i) => i % 3 === 1)), Math.min(...br.filter((_, i) => i % 3 === 2)), Math.max(...br.filter((_, i) => i % 3 === 2))];
const boxGap = p => { const dx = Math.max(bb[0] - p[0], 0, p[0] - bb[1]), dy = Math.max(bb[2] - p[1], 0, p[1] - bb[3]), dz = Math.max(bb[4] - p[2], 0, p[2] - bb[5]); return Math.hypot(dx, dy, dz); };
console.log('new sensor bracket (box', bb.map(v => v.toFixed(1)).join(','), ') to:');
for (const [name, o] of Object.entries(out)) { const [d, at] = closest(dec(o.m), boxGap); if (d < 10) console.log('  ', name.padEnd(36), o.kind.padEnd(12), d.toFixed(1), 'mm at', at.join(',')); }
// beam from the board (x -48, face 246.5) down past the top plate's front edge: the 25 degree cone's edge vs the carriage
const cone = p => { const depth = SP.sens_z - p[2]; if (depth < 0 || depth > 40) return 1e9; const half = 5.35 + depth * Math.tan(12.5 * Math.PI / 180); return Math.max(Math.abs(p[0] - SP.sens_x_new) - half, Math.abs(p[1]) - 12.5 - depth * 0.22); };
for (const n of ['Body67']) { const [d, at] = closest(dec(out[n].m), cone); console.log('beam cone to the carriage', d.toFixed(1), 'mm (negative would mean it clips) at', at.join(',')); }
