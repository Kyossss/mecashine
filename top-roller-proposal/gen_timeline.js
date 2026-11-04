// One polishing pass of the top station (proposal v3) from the Polishing Line simulation:
// carriage legs 15 mm longer (roller axis home 185 in the simulation's frame), 52 mm yarn roller, sensor in front of the roller
// 48 mm before the axis and 20 mm higher than now. Also the current design's numbers, for comparison.
const fs = require('fs');
const html = fs.readFileSync('F:/Research/ASPS/polishing-line/polishing-line.html', 'utf8');
const sc = html.slice(html.indexOf('//SCENE-START'), html.indexOf('//SCENE-END'));
const m = {}; new Function('module', sc + '\nmodule.exports = Line;')(m); const L = m.exports;
const S2 = L.S2, H0 = S2.home, X0 = S2.sensX;
const CUR = { home: H0, up: 25.5, sx: -44, R: 26 }, NEW = { home: H0 - 15, up: 25.5 + 15 + 20, sx: -60, R: 26 };   // v5: sensor 60 mm before the axis (longer arm), 20 mm higher than now
function use(d) { S2.home = d.home; S2.sensUp = d.up; S2.sensX = S2.rollX + d.sx; S2.R = d.R; }
const sizes = [];
for (const i of [0, 1, 2]) {
  L.use(i); const c = L.cur(), ht = Math.max(...c.HT);
  use(CUR); const rc = L.report(); const parkC = CUR.home - CUR.R - ht;
  use(NEW); const rn = L.report(); const parkN = NEW.home - NEW.R - ht;
  sizes.push({ name: L.SIZES[i].name, len: c.len, contact: Math.round(100 * rn.c2 / Math.max(1, rn.n2)), nearOld: Math.round(rc.near2), nearNew: Math.round(rn.near2), parkOld: Math.round(parkC), parkNew: Math.round(parkN) });
}
use(NEW); L.use(2);
const c = L.cur(), TL = L.timeline().filter(s => s.phase === 'polish');
const frames = [];
TL.forEach((s, k) => {
  if (k % 2) return;
  const X = s.xt - S2.rollX, hS = L.h(s.xt - S2.sensX);
  frames.push([X, +s.zc.toFixed(1), s.s2, +(s.zc + NEW.up - hS).toFixed(1), s.m2 ? 1 : 0]);
});
const shoe = html.match(/var SHOE=(\[[^\]]*\])/)[1];
fs.writeFileSync('F:/Research/ASPS/top-roller-proposal/timeline.json', JSON.stringify({ sizes, frames, shoe: JSON.parse(shoe), home: NEW.home, up: NEW.up, homeReading: Math.round(NEW.home + NEW.up), homeReadingOld: Math.round(CUR.home + CUR.up) }));
console.log(sizes, 'frames', frames.length, 'min sensor', Math.min(...frames.map(f => f[3])), 'home reading', Math.round(NEW.home + NEW.up));
