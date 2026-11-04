// Try top-sensor positions in the page's own simulation: nearest sensor-to-shoe distance while polishing, per size.
const fs = require('fs');
const html = fs.readFileSync('polishing-line.html', 'utf8');
const sc = html.slice(html.indexOf('//SCENE-START'), html.indexOf('//SCENE-END'));
const m = {}; new Function('module', sc + '\nmodule.exports = Line;')(m); const L = m.exports;
const S2 = L.S2, base = { sensX: S2.sensX, sensUp: S2.sensUp, R: S2.R };
console.log('roller x', S2.rollX, ' sensor x', S2.sensX, ' sensor above axis', S2.sensUp, ' roller R', S2.R, ' home', S2.home, ' floor', S2.floor);
const opts = [
  ['now: 44 mm upstream, 25.5 above the axis', S2.rollX - 44, 25.5],
  ['raised 30 mm on the carriage', S2.rollX - 44, 55.5],
  ['moved downstream, 44 mm after the roller', S2.rollX + 44, 25.5],
  ['downstream 44 mm, raised 10 mm', S2.rollX + 44, 35.5],
  ['downstream 60 mm, same height', S2.rollX + 60, 25.5],
];
for (const R of [25, 24]) {
  S2.R = R;
  console.log('\nroller radius', R);
  for (const [name, x, up] of opts) {
    S2.sensX = x; S2.sensUp = up;
    const row = [0, 1, 2].map(i => { L.use(i); const r = L.report(); return L.SIZES[i].name + ' ' + Math.round(r.near2) + ' mm (contact ' + Math.round(100 * r.c2 / Math.max(1, r.n2)) + '%)'; });
    console.log('  ' + name.padEnd(44), '| home reading', Math.round(S2.home + up), 'mm |', row.join(' | '));
  }
}
