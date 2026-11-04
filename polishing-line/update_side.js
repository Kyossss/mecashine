// Update the Polishing Line page's side station to the current CAD (2026-10-23):
// 52 mm chenille-yarn brushes on the 3-part core with tie discs, the redesigned arm frames, carriage with motor cup,
// guide rails and flange-cap guide blocks, the new sensor bracket and the 145 x 120 reflector, and the model's
// jaw geometry (open = full retraction, sensor-to-reflector 194 mm).
// usage: node update_side.js <live.html> <out.html>
const fs = require('fs');
let s = fs.readFileSync(process.argv[2], 'utf8');
function rep(a, b, all) {
  const n = s.split(a).length - 1;
  if (n === 0) throw new Error('not found: ' + a.slice(0, 80));
  if (!all && n !== 1) throw new Error('found ' + n + 'x: ' + a.slice(0, 80));
  s = s.split(a).join(b);
}

// ---------- 1. shoe widths over the new brush band (23..137 mm), as a correction on the stored numbers
const data = s.slice(s.indexOf('/*DATA-START*/') + 14, s.indexOf('/*DATA-END*/'));
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
  for (let k = 1; k < out.length - 1; k++) if (out[k] === 0 && out[k - 1] > 0 && out[k + 1] > 0) out[k] = (out[k - 1] + out[k + 1]) / 2;
  return out;
}
let newData = data;
SIZES.forEach(sz => {
  const o = wb(sz, 16, 104), n = wb(sz, 23, 137);
  const nw = sz.WB.map((v, k) => Math.max(0, Math.round(v + (n[k] || 0) - (o[k] || 0))));
  const oldStr = 'WB:[' + sz.WB.join(',') + ']';
  if (newData.split(oldStr).length !== 2) throw new Error('WB not unique for ' + sz.name);
  newData = newData.replace(oldStr, 'WB:[' + nw.join(',') + ']');
  console.log(sz.name, 'WB max', Math.max(...sz.WB), '->', Math.max(...nw));
});
s = s.replace(data, newData);

// ---------- 2. side station numbers. a = arm column middle from the belt centre; brush axis 8.5 mm inboard of it.
// open: full retraction (left 93.5, right 90 in the model; drawn symmetric at the mean). Sensor chip 3.9 mm outboard
// of its column middle, reflector face 7 mm outboard of its: reading = 2a + 10.9, 194 mm at open.
rep("var S1 = { sensX: -176, brushX: -105, beamZ: 42, R: 25, open: 105, min: 45, sq: 2, stopAt: 20 };",
    "var S1 = { sensX: -176, brushX: -105, beamZ: 42, R: 26, open: 91.75, min: 53.25, sq: 2, stopAt: 20, ax: 8.5, sens: 3.9, refl: 7 };   // CAD 2026-10-23: 52 mm yarn brush, jaws open = full retraction");
rep("return m + 10; }", "return m + S1.ax; }");
rep("a - 10 - Math.sqrt(R * R - x * x) - look(cur.WB, xl - x)", "a - S1.ax - Math.sqrt(R * R - x * x) - look(cur.WB, xl - x)");
rep("S1.open - 6 - w", "S1.open + S1.sens - w");
rep("s.a - 6 - w", "s.a + S1.sens - w", true);
rep("2 * a - 14", "2 * a + S1.sens + S1.refl");
rep("var openR = 2 * S1.open - 14,", "var openR = Math.round(2 * S1.open + S1.sens + S1.refl),");
rep("2 * s.a - 14", "2 * s.a + S1.sens + S1.refl", true);

// ---------- 3. the side station geometry
const a0 = s.indexOf('    // ---- station 1: side polishers'), a1 = s.indexOf('    // ---- station 2: top polisher');
if (a0 < 0 || a1 < 0) throw new Error('station block');
const station1 = String.raw`    // ---- station 1: side polishers (current CAD; x = along the belt, brush axis at bx; each arm's local d is outward from its column middle)
    [[-145, -110], [110, 145]].forEach(function (y) { wires.push([bx - 45, bx + 45, y[0], y[1], -89, 261]); });
    wires.push([bx - 55, bx + 55, -120, 120, 261, 298]);
    box(bx - 27, bx + 27, -10, 10, 298, 342, 'servo');
    cyl([bx, 0], 'z', 252, 298, 12, 'pinion');
    box(bx - 24, bx - 12, -a + 6, -a + 140, 238, 252, 'rack');
    box(bx + 12, bx + 24, a - 140, a - 6, 238, 252, 'rack');
    // guide blocks and plates on the pillar flanges (fixed)
    [-1, 1].forEach(function (sy) { [-1, 1].forEach(function (sx) {
      var x0 = sx < 0 ? bx - 68 : bx + 25, x1 = sx < 0 ? bx - 25 : bx + 68, ya = sy * 110, yb = sy * 154;
      box(x0, x1, Math.min(ya, yb), Math.max(ya, yb), 78, 124.5, 'block');
      box(x0 + 13, x1, Math.min(sy * 104.5, yb), Math.max(sy * 104.5, yb), 72, 77, 'clamp');
    }); });
    var spin = p.m1, ph0 = (p.sp1 || 0) * 0.35;
    [-1, 1].forEach(function (sgn) {
      function Y(d) { return sgn * (a + d); }
      function bxy(x0, x1, d0, d1, z0, z1, col) { var u = Y(d0), v = Y(d1); box(x0, x1, Math.min(u, v), Math.max(u, v), z0, z1, col); }
      var by = Y(-S1.ax);
      // arm frame: legs, upper columns, tie beam; foot bracket with its bridge under the brush; guide rails
      [-1, 1].forEach(function (k) {
        var l0 = k < 0 ? bx - 46 : bx + 30, l1 = k < 0 ? bx - 30 : bx + 46;
        bxy(l0, l1, -3.5, 11, 44, 150, 'arm');
        bxy(l0, l1, -3.5, 11, 19, 44, 'foot');
        bxy(k < 0 ? bx - 65 : bx + 45.5, k < 0 ? bx - 43.5 : bx + 67, -11, 11, 144, 234, 'arm');
        bxy(bx + k * 56 - 7, bx + k * 56 + 7, 11, 90, 101, 121, 'rail');
      });
      bxy(bx - 43.5, bx + 45.5, -3.5, 11, 144, 164, 'arm');
      bxy(bx - 46, bx + 46, -21.5, 11, 10, 19, 'foot');
      // carriage: flange and motor cup; the rack's pad on top
      bxy(bx - 43, bx + 45, -23.5, 11, 217, 226, 'carr');
      cyl([bx, by], 'z', 166, 217, 15, 'carr');
      bxy(bx - 41, bx + 43, -23.5, 6.5, 226, 234, 'rack');
      // brush core: bottom plate, hex bar, top stopper and hub; the tie-disc stack
      cyl([bx, by], 'z', 12.5, 24.6, 4, 'core');
      cyl([bx, by], 'z', 24.6, 27, 11, 'core');
      cyl([bx, by], 'z', 27, 137, 6.5, 'core');
      cyl([bx, by], 'z', 137, 140, 11, 'core');
      cyl([bx, by], 'z', 140, 164, 8, 'core');
      var i, k2, rows = [23.1];
      for (i = 0; i < 15; i++) { var z0 = 27 + i * 7.25; cyl([bx, by], 'z', z0, z0 + 2.4, 11, 'disc'); cyl([bx, by], 'z', z0 + 2.4, z0 + 7.25, 7.4, 'disc'); rows.push(z0 + 4.2); }
      // chenille yarn: 2 tails per tie hole, 6 holes per row; flung straight out to 26 mm when spinning, drooping at rest
      var ph = sgn * ph0;
      rows.forEach(function (zr, ri) {
        for (k2 = 0; k2 < 6; k2++) [-0.33, 0.33].forEach(function (sp, si) {
          var ang = (30 + 60 * k2) * Math.PI / 180 + sp + ph + (ri % 2) * 0.12, r0 = 8.9, r1 = spin ? S1.R : 21, dz = spin ? 0 : (ri === 0 ? -3 : -9);   // the bottom row hangs just above the foot bridge
          var ca = Math.cos(ang), sa = Math.sin(ang), hw = 2.8, hh = 2.8;
          var A = [bx + r0 * ca, by + r0 * sa, zr], B = [bx + r1 * ca, by + r1 * sa, zr + dz];
          var nx = -sa * hw, ny = ca * hw, col = (si + ri) % 3 ? 'yarn' : 'yarn2', id = ++fid;
          var P = [[A[0] - nx, A[1] - ny, A[2] - hh], [A[0] + nx, A[1] + ny, A[2] - hh], [A[0] + nx, A[1] + ny, A[2] + hh], [A[0] - nx, A[1] - ny, A[2] + hh],
                   [B[0] - nx, B[1] - ny, B[2] - hh], [B[0] + nx, B[1] + ny, B[2] - hh], [B[0] + nx, B[1] + ny, B[2] + hh], [B[0] - nx, B[1] - ny, B[2] + hh]];
          [[0, 1, 5, 4, [0, 0, -1]], [3, 2, 6, 7, [0, 0, 1]], [0, 3, 7, 4, [-ca, -sa, 0]], [1, 2, 6, 5, [ca, sa, 0]], [4, 5, 6, 7, [ca, sa, 0]]].forEach(function (f) {
            tri(P[f[0]], P[f[1]], P[f[2]], f[4], col, id); tri(P[f[0]], P[f[2]], P[f[3]], f[4], col, id);
          });
        });
      });
    });
    // side sensor on the left foot (board 3.9 mm outboard of its column middle, facing across), reflector on the right
    box(bx - 74.5, bx - 46, -a - 11, -a - 8, 14, 57, 'sensbr');
    box(S1.sensX - 5.35, S1.sensX + 5.35, -a - 5.5, -a - 3.9, 29.5, 54.5, 'sensor');
    box(bx - 191.5, bx - 66.5, a + S1.refl, a + 13.5, 6, 126, 'refl');
    box(bx - 66.5, bx - 46, a + S1.refl, a + 13.5, 6, 93.5, 'refl');
    var w1 = p.noShoe ? 0 : ws(xt - S1.sensX), hit = w1 > 0 ? -w1 : a + S1.refl;
    if (hit > -a - S1.sens) box(S1.sensX - 1.5, S1.sensX + 1.5, -a - S1.sens, hit, 40.5, 43.5, 'beam');
    labels.push({ t: 'side servo + pinion', at: [bx, 0, 342], dx: -110, dy: -50 });
    labels.push({ t: 'side sensor', at: [S1.sensX, -a - 4, 42], dx: -110, dy: 80 });
    labels.push({ t: 'reflector 145 × 120, white insert', at: [bx - 140, a + 7, 100], dx: -170, dy: -60 });
    labels.push({ t: 'guide blocks', at: [bx - 46, -154, 124], dx: -60, dy: -70 });
    labels.push({ t: p.m1 ? 'yarn brushes: spinning' : 'yarn brushes: at rest', at: [bx, -a + S1.ax - 26, 70], dx: -30, dy: 150 });

`;
s = s.slice(0, a0) + station1 + s.slice(a1);

// ---------- 4. colours for the new parts
rep("brush: '#c06a30', brush2: '#4a2410',", "brush: '#c06a30', brush2: '#4a2410', foot: '#3fa874', yarn: '#c39be3', yarn2: '#a173c9', core: '#d98a46', disc: '#4fa3a8', rail: '#c4ccd3', block: '#2f9aa0', clamp: '#f09a3a', carr: '#7fb6cf', sensbr: '#5fc48e',");

// ---------- 5. words that described the old side station
rep("The striped brushes turn in the model whenever their motors are on.", "The side brushes are chenille yarn: they turn and fling out when their motors are on, and droop when they stop.");
rep("(196 mm in this model)", "(194 mm in this model)");
rep("and I assumed 50 mm brushes.", "and the side station is the current CAD: 52 mm chenille-yarn brushes on tie discs, the redesigned arms, guide rails and flange-cap guide blocks, and the 145 × 120 mm reflector.");
rep("9 to 25 mm from the leather, which is closer than a VL53L0X can measure dependably.", "as close as 9 to 10 mm (top) and 19 to 32 mm (side) from the leather, which is closer than a VL53L0X can measure dependably.");
fs.writeFileSync(process.argv[3], s);
console.log('written', process.argv[3], s.length);
