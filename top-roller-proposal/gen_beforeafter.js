// Polishing passes of the top station before and after the redesign, from the Polishing Line simulation (large shoe),
// plus per-size numbers for the comparison table.
// Before: roller axis home 200, sensor 44 mm before the axis and 25.5 above it, the 50 mm brush the page assumed.
// After: carriage legs +15 (axis home 185), 52 mm yarn, sensor 60 mm before the axis, 60.5 above it (20 mm higher than before).
const fs = require('fs');
const html = fs.readFileSync('F:/Research/ASPS/polishing-line/polishing-line.html', 'utf8');
const sc = html.slice(html.indexOf('//SCENE-START'), html.indexOf('//SCENE-END'));
const m = {}; new Function('module', sc + '\nmodule.exports = Line;')(m); const L = m.exports;
const S2 = L.S2, H0 = S2.home;
const D = { before: { home: H0, up: 25.5, sx: -44, R: 25, faceZ: 226.5 }, after: { home: H0 - 15, up: 25.5 + 15 + 20, sx: -60, R: 26, faceZ: 246.5 } };
function use(d) { S2.home = d.home; S2.sensUp = d.up; S2.sensX = S2.rollX + d.sx; S2.R = d.R; }
const sizes = [0, 1, 2].map(i => {
  L.use(i); const c = L.cur(), ht = Math.max(...c.HT), row = { name: L.SIZES[i].name, len: c.len, ht };
  for (const k of ['before', 'after']) { use(D[k]); const r = L.report(); row[k] = { near: Math.round(r.near2), contact: Math.round(100 * r.c2 / Math.max(1, r.n2)), park: Math.round(D[k].home - D[k].R - ht) }; }
  return row;
});
const out = { sizes, shoe: JSON.parse(html.match(/var SHOE=(\[[^\]]*\])/)[1]) };
for (const k of ['before', 'after']) {
  use(D[k]); L.use(2);
  const fr = [];
  L.timeline().filter(s => s.phase === 'polish').forEach((s, n) => { if (n % 2) return; fr.push([s.xt - S2.rollX, +s.zc.toFixed(1), s.s2, +(s.zc + D[k].up - L.h(s.xt - S2.sensX)).toFixed(1), s.m2 ? 1 : 0]); });
  out[k] = { frames: fr, home: D[k].home, sensX: D[k].sx, faceZ: D[k].faceZ, R: D[k].R, homeReading: Math.round(D[k].home + D[k].up) };
}
fs.writeFileSync('F:/Research/ASPS/top-roller-proposal/beforeafter-timeline.json', JSON.stringify(out));
console.log(JSON.stringify(sizes));
console.log('frames before', out.before.frames.length, 'after', out.after.frames.length, 'home readings', out.before.homeReading, out.after.homeReading);
