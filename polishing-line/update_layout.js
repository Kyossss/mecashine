// Polishing Line to the real prototype layout (2026-10-24) and the redesigned top polisher.
// Sim x = CAD x - 1005 (side brush axis CAD 900 = sim -105). Top roller CAD 1140 = sim 135, 240 mm after the side brushes.
// Belt drum axles CAD 293 / 1325 = sim -712 / 320, belt servo on the exit drum, base plate CAD 200..1410 = sim -805..405.
// Top polisher: legs +15 (home 185), 52 mm yarn roller (R 26), sensor 60 mm ahead of the roller and 60.5 above its axis.
// usage: node update_layout.js polishing-line.html polishing-line.html
const fs = require('fs');
let s = fs.readFileSync(process.argv[2], 'utf8');
function rep(a, b) { const n = s.split(a).length - 1; if (n !== 1) throw new Error('expected 1 match, got ' + n + ': ' + a.slice(0, 80)); s = s.replace(a, b); }

// ---------- 1. station 2 numbers
rep("var S2 = { sensX: 64, rollX: 108, R: 25, lead: 44, sensUp: 26, home: 200, floor: 55, sq: 2, stopAt: 14 };",
    "var S2 = { sensX: 75, rollX: 135, R: 26, lead: 60, sensUp: 60.5, home: 185, floor: 55, sq: 2, stopAt: 14 };   // real layout 2026-10-24: 240 mm after the side brushes; redesigned top polisher");

// ---------- 2. belt at its real length, servo on the exit drum
rep("var XA = -797, XB = 330, zc0 = -29,", "var XA = -712, XB = 320, zc0 = -29,");
rep("box(-830, 380, -175, 175, -109, -89, 'base');", "box(-805, 405, -175, 175, -109, -89, 'base');");
rep("[-665, -309, -9].forEach(", "[-640, -284, 16].forEach(");
rep("box(-674, -655, -115, -76, -67, -13, 'servo');", "box(310, 330, -115, -76, -67, -13, 'servo');");
rep("{ t: 'belt servo', at: [-665, -115, -40], dx: -90, dy: 70 }", "{ t: 'belt servo', at: [320, -115, -40], dx: 60, dy: 70 }");

// ---------- 3. the redesigned top carriage (top plate unchanged in height, so everything above the axis sits 15 mm higher relative to it)
rep(`    box(rx - 37, rx + 26, -102, 88, zc + 26, zc + 36, 'car');
    box(rx - 37, rx + 26, -102, -92, zc - 15, zc + 26, 'car');
    box(rx - 37, rx + 26, 78, 88, zc - 15, zc + 26, 'car');
    cyl([rx, zc], 'y', -60, 60, S2.R, 'brush', (p.sp2 || 0) * 0.35, 'brush2');
    cyl([rx, zc], 'y', -92, 78, 5, 'motor');
    cyl([rx, zc], 'y', -150, -102, 12.5, 'motor');
    cyl([rx, zc + 50], 'y', -186, 124, 7, 'motor');
    cyl([rx, zc + 50], 'y', -165, -131, 22, 'pinion');
    cyl([rx, zc + 50], 'y', 92, 126, 22, 'pinion');
    box(rx - 10, rx + 9, -225, -186, zc + 32, zc + 86, 'servo');
    box(rx - 52, rx - 37, -19, 16, zc + 30, zc + 40, 'arm');
    box(rx - 50, rx - 38, -8, 8, zc + 26, zc + 30, 'sensor');
    var hs = p.noShoe ? 0 : h(xt - S2.sensX);
    if (zc + 26 > hs) box(S2.sensX - 1.5, S2.sensX + 1.5, -1.5, 1.5, hs, zc + 26, 'beam');
    labels.push({ t: 'top sensor', at: [S2.sensX, -19, zc + 35], dx: -90, dy: -150 });`,
`    box(rx - 37, rx + 26, -102, 88, zc + 41, zc + 51, 'car');
    box(rx - 37, rx + 26, -102, -92, zc - 15, zc + 41, 'car');
    box(rx - 37, rx + 26, 78, 88, zc - 15, zc + 41, 'car');
    cyl([rx, zc], 'y', -49, 45, S2.R, 'yarn', (p.sp2 || 0) * 0.35, 'yarn2');
    cyl([rx, zc], 'y', -92, 78, 6, 'core');
    cyl([rx, zc], 'y', 71, 78, 11, 'disc');
    cyl([rx, zc], 'y', -150, -102, 12.5, 'motor');
    cyl([rx, zc + 65], 'y', -186, 124, 7, 'motor');
    cyl([rx, zc + 65], 'y', -165, -131, 22, 'pinion');
    cyl([rx, zc + 65], 'y', 92, 126, 22, 'pinion');
    box(rx - 10, rx + 9, -225, -186, zc + 47, zc + 101, 'servo');
    box(rx - 41, rx - 38, -18, 16, zc + 41, zc + 65.5, 'sensbr');
    box(rx - 69, rx - 38, -18, 16, zc + 63, zc + 65.5, 'sensbr');
    box(S2.sensX - 5, S2.sensX + 5, -12, 12, zc + 60, zc + 61.5, 'sensor');
    var hs = p.noShoe ? 0 : h(xt - S2.sensX);
    if (zc + S2.sensUp > hs) box(S2.sensX - 1.5, S2.sensX + 1.5, -1.5, 1.5, hs, zc + S2.sensUp, 'beam');
    labels.push({ t: 'top sensor, 60 mm ahead', at: [S2.sensX, -19, zc + 64], dx: -90, dy: -150 });`);
rep("labels.push({ t: p.m2 ? 'roller: spinning' : 'roller: off',", "labels.push({ t: p.m2 ? 'yarn roller: spinning' : 'yarn roller: off',");

// ---------- 4. words
rep("In your model the slats stop about 60 mm before the top roller, and this cycle needs the belt to carry the toe roughly 170 mm further, so I drew the belt out to the end of the base plate.",
    "The belt, the belt servo and both stations are at your prototype's measured positions: drum axles 1032 mm apart, the belt servo on the exit drum, and the two towers 240 mm apart.");
rep("and the 145 × 120 mm reflector.", "and the 145 × 120 mm reflector. The top station is the redesign: legs 15 mm longer, a 52 mm chenille roller turning in a 608ZZ, and the sensor 60 mm ahead of the roller.");
rep("reads the home distance to the belt (226 mm).", "reads the home distance to the belt (246 mm).");
rep("reads the home distance to the belt, about 226 mm.", "reads the home distance to the belt, about 246 mm.");
rep("The two sensors are 240 mm apart along the belt.", "The two sensors are 251 mm apart along the belt.");

fs.writeFileSync(process.argv[3], s);
console.log('written', process.argv[3], s.length);
