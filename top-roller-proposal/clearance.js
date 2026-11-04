// Closest approach of each top-station part to the roller axis (x 0, z 201 above the belt), within a y range.
const fs = require('fs');
const M = JSON.parse(fs.readFileSync('top-station-mesh.json', 'utf8'));
function tris(b64) { const b = Buffer.from(b64, 'base64'); const a = new Int16Array(b.buffer, b.byteOffset, b.length / 2); return a; }
const Y0 = +process.argv[2] || -60, Y1 = +process.argv[3] || 47, AZ = 201;
for (const [name, o] of Object.entries(M)) {
  if (o.kind === 'oldcore' || o.kind === 'belt') continue;
  const a = tris(o.m); let best = 1e9, at = null;
  for (let i = 0; i < a.length; i += 9) {
    const P = [0, 3, 6].map(k => [a[i + k] / 10, a[i + k + 1] / 10, a[i + k + 2] / 10]);
    for (let s = 0; s <= 10; s++) for (let t = 0; t <= 10 - s; t++) {
      const u = s / 10, v = t / 10, w = 1 - u - v;
      const x = P[0][0] * u + P[1][0] * v + P[2][0] * w, y = P[0][1] * u + P[1][1] * v + P[2][1] * w, z = P[0][2] * u + P[1][2] * v + P[2][2] * w;
      if (y < Y0 || y > Y1) continue;
      const r = Math.hypot(x, z - AZ); if (r < best) { best = r; at = [x.toFixed(1), y.toFixed(1), z.toFixed(1)]; }
    }
  }
  if (best < 60) console.log(name.padEnd(40), o.kind.padEnd(14), 'closest to the roller axis', best.toFixed(1), 'mm at', at.join(', '));
}
