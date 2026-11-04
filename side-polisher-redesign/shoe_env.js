// Keep-out envelope. For every position of the shoe along the belt, the jaws sit where the 50 mm brush touches the shoe's side.
// E(u, band) = the furthest the shoe reaches past the brush-surface line, at a distance u ahead (-) or behind (+) of the brush axis.
// A part at that u is safe if its inner face is further from the brush-surface line than E.
const fs = require('fs');
const b = JSON.parse(fs.readFileSync('shoe2.json', 'utf8'))[0];
const V = []; for (let i = 0; i < b.v.length; i += 3) V.push([b.v[i], b.v[i + 1], b.v[i + 2] - 217]);
const P = [];
for (let t = 0; t < b.i.length; t += 3) { const A = V[b.i[t]], B = V[b.i[t + 1]], C = V[b.i[t + 2]];
  for (let a = 0; a <= 10; a++) for (let c = 0; c <= 10 - a; c++) { const u = a / 10, v = c / 10, w = 1 - u - v; P.push([A[0] * u + B[0] * v + C[0] * w, A[1] * u + B[1] * v + C[1] * w, A[2] * u + B[2] * v + C[2] * w]); } }
const X0 = 755, N = 331, R = 25, MINGAP = 20;   // the jaws never close the brushes to less than MINGAP apart per side from the centre line
const BANDS = { sole: [0, 16], brush: [26, 140], low60: [0, 60], all: [0, 150] };
const res = {}, prof = {};
for (const side of [-1, 1]) {
  const W = {}; for (const k in BANDS) W[k] = new Float64Array(N).fill(-1e9);
  for (const p of P) { const i = Math.round(p[0] - X0); if (i < 0 || i >= N) continue; for (const k in BANDS) if (p[2] >= BANDS[k][0] && p[2] < BANDS[k][1]) W[k][i] = Math.max(W[k][i], side * p[1]); }
  for (const k in BANDS) for (let pass = 0; pass < 3; pass++) for (let i = 1; i < N - 1; i++) if (W[k][i] < -1e8) W[k][i] = Math.max(W[k][i - 1], W[k][i + 1]);   // fill gaps in the sampling
  // brush-surface line (distance from the belt centre line) for each brush position x: the brush is a 50 mm cylinder
  const a = new Float64Array(N + 200).fill(0);
  for (let i = -100; i < N + 100; i++) { let m = -1e9; for (let dx = -R; dx <= R; dx++) { const j = i + dx; if (j < 0 || j >= N || W.brush[j] < -1e8) continue; m = Math.max(m, W.brush[j] + Math.sqrt(R * R - dx * dx) - R); } a[i + 100] = Math.max(m, MINGAP); }
  prof[side] = Array.from({ length: 83 }, (_, q) => +a[(q * 5 - 40) + 100].toFixed(1));   // brush line every 5 mm, from 40 mm before the heel to 40 mm past the toe
  for (const k of ['sole', 'low60', 'all']) { const E = {};
    for (let u = -115; u <= 115; u += 5) { let m = -1e9; for (let i = -100; i < N + 100; i++) { const j = i + u; if (j < 0 || j >= N || W[k][j] < -1e8) continue; m = Math.max(m, W[k][j] - a[i + 100]); } E[u] = m; }
    res[k] = res[k] || {}; for (const u in E) res[k][u] = Math.max(res[k][u] === undefined ? -1e9 : res[k][u], E[u]); }
}
for (const k in res) console.log(k.padEnd(6), Object.keys(res[k]).map(Number).sort((x, y) => x - y).map(u => u + ':' + res[k][u].toFixed(0)).join('  '));
// jaw position that just touches the shoe: left brush surface is at y = -51.5 + p, right at 48 - p
const follow = prof[-1].map((wl, q) => +Math.max(-7, Math.min(30, Math.min(51.5 - wl, 48 - prof[1][q]))).toFixed(1));
fs.writeFileSync('shoe-env.json', JSON.stringify({ env: res, follow: follow, x0: X0 - 40, step: 5 }));
console.log('follow', follow.join(' '));
