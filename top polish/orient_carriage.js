// Turn the carriage upside down (top plate on the bed, legs up) and move it onto the bed origin.
const fs = require('fs');
const b = fs.readFileSync(process.argv[2]), n = b.readUInt32LE(80), out = Buffer.from(b);
let mn = [1e9, 1e9, 1e9];
const P = (o) => [b.readFloatLE(o), b.readFloatLE(o + 4), b.readFloatLE(o + 8)];
const T = (p) => [p[0], -p[1], -p[2]];             // 180 degrees about x
for (let i = 0; i < n; i++) for (let k = 1; k <= 3; k++) { const q = T(P(84 + i * 50 + k * 12)); for (let j = 0; j < 3; j++) mn[j] = Math.min(mn[j], q[j]); }
for (let i = 0; i < n; i++) {
  const o = 84 + i * 50, nn = T(P(o)); for (let j = 0; j < 3; j++) out.writeFloatLE(nn[j], o + 4 * j);
  for (let k = 1; k <= 3; k++) { const q = T(P(o + k * 12)); for (let j = 0; j < 3; j++) out.writeFloatLE(q[j] - mn[j], o + k * 12 + 4 * j); }
}
fs.writeFileSync(process.argv[3], out);
let mx = [-1e9, -1e9, -1e9]; for (let i = 0; i < n; i++) for (let k = 1; k <= 3; k++) { const o = 84 + i * 50 + k * 12; for (let j = 0; j < 3; j++) mx[j] = Math.max(mx[j], out.readFloatLE(o + 4 * j)); }
console.log('triangles', n, 'bed size', mx.map(v => v.toFixed(1)).join(' x '), 'mm');
