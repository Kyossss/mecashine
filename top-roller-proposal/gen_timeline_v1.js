// One polishing pass of the top station from the Polishing Line simulation, with the 52 mm yarn roller:
// shoe toe position, roller axis height, and sensor-to-shoe distance for the current and the proposed sensor position.
const fs = require('fs');
const html = fs.readFileSync('F:/Research/ASPS/polishing-line/polishing-line.html', 'utf8');
const sc = html.slice(html.indexOf('//SCENE-START'), html.indexOf('//SCENE-END'));
const m = {}; new Function('module', sc + '\nmodule.exports = Line;')(m); const L = m.exports;
const S2 = L.S2; S2.R = 23;   // yarn tips 23 mm from the axis: 6 mm under the carriage's top plate
const UP = 25.5, OLD = -44, NEW = 44;
const sizes = [];
for (const i of [0, 1, 2]) {
  L.use(i); const c = L.cur();
  S2.sensX = S2.rollX + OLD; const rOld = L.report();
  S2.sensX = S2.rollX + NEW; const rNew = L.report();
  sizes.push({ name: L.SIZES[i].name, len: c.len, contact: Math.round(100 * rNew.c2 / Math.max(1, rNew.n2)), nearOld: Math.round(rOld.near2), nearNew: Math.round(rNew.near2) });
}
L.use(2);
const c = L.cur(), TL = L.timeline().filter(s => s.phase === 'polish');
const frames = [];
TL.forEach((s, k) => {
  if (k % 2) return;
  const X = s.xt - S2.rollX;                           // toe position relative to the roller axis
  const hOld = L.h(s.xt - (S2.rollX + OLD)), hNew = L.h(s.xt - (S2.rollX + NEW));
  frames.push([X, +s.zc.toFixed(1), s.s2, +(s.zc + UP - hOld).toFixed(1), +(s.zc + UP - hNew).toFixed(1), s.m2 ? 1 : 0, +(s.gap).toFixed(1)]);
});
const shoe = html.match(/var SHOE=(\[[^\]]*\])/)[1];
fs.writeFileSync('F:/Research/ASPS/top-roller-proposal/timeline.json', JSON.stringify({ sizes, frames, shoe: JSON.parse(shoe), home: S2.home, floor: S2.floor, up: UP, len: c.len }));
console.log(sizes, 'frames', frames.length, 'min old', Math.min(...frames.map(f => f[3])), 'min new', Math.min(...frames.map(f => f[4])));
