// Recompute WB (widest half-width over the brush band) from the page's own SHOE mesh, per size.
const fs = require('fs');
const html = fs.readFileSync(process.argv[2], 'utf8');
const data = html.slice(html.indexOf('/*DATA-START*/') + 14, html.indexOf('/*DATA-END*/'));
const { SHOE, SIZES } = new Function(data + '; return { SHOE: SHOE, SIZES: SIZES };')();
function wb(sz, z0, z1) {
  const out = new Array(sz.len + 1).fill(0);
  for (let i = 0; i < SHOE.length; i += 9) {
    const P = [0, 3, 6].map(k => [SHOE[i + k] * sz.sx, SHOE[i + k + 1] * sz.sy, SHOE[i + k + 2] * sz.sz]);
    for (let a = 0; a <= 12; a++) for (let b = 0; b <= 12 - a; b++) {
      const u = a / 12, v = b / 12, w = 1 - u - v;
      const x = P[0][0] * u + P[1][0] * v + P[2][0] * w, y = P[0][1] * u + P[1][1] * v + P[2][1] * w, z = P[0][2] * u + P[1][2] * v + P[2][2] * w;
      if (z < z0 || z > z1) continue;
      const k = Math.round(x); if (k < 0 || k > sz.len) continue;
      out[k] = Math.max(out[k], Math.abs(y));
    }
  }
  // fill tiny gaps from sparse sampling
  for (let k = 1; k < out.length - 1; k++) if (out[k] === 0 && out[k - 1] > 0 && out[k + 1] > 0) out[k] = (out[k - 1] + out[k + 1]) / 2;
  return out.map(v => Math.round(v));
}
const mode = process.argv[3] || 'check';
SIZES.forEach(sz => {
  if (mode === 'check') {
    const mine = wb(sz, 16, 104), d = sz.WB.map((v, k) => Math.abs(v - (mine[k] || 0)));
    console.log(sz.name, 'old band 16..104: mean diff', (d.reduce((a, b) => a + b, 0) / d.length).toFixed(2), 'max', Math.max(...d), ' stored max', Math.max(...sz.WB), 'mine max', Math.max(...mine));
  } else {
    const nw = wb(sz, 23 * 1, 137 * 1);
    console.log(sz.name, 'new band 23..137: max', Math.max(...nw), ' old max', Math.max(...sz.WB));
  }
});
