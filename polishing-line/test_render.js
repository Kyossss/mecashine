// Run the page's simulation module in Node: report for each size, and render frames to PNG for a visual check.
const fs = require('fs'), zlib = require('zlib');
const html = fs.readFileSync(process.argv[2], 'utf8');
const scene = html.slice(html.indexOf('//SCENE-START'), html.indexOf('//SCENE-END'));
const module_ = { exports: null };
new Function('module', scene + '\nmodule.exports = Line;')(module_);
const Line = module_.exports;
const objSrc = html.match(/var OBJ = (\{[^}]*\})/)[1];
const OBJ = new Function('return ' + objSrc)();
const pal = {}; Object.keys(OBJ).forEach(k => { const h = OBJ[k]; pal[k] = [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)]; });
[0, 1, 2].forEach(i => {
  Line.use(i); const r = Line.report();
  console.log(Line.SIZES[i].name, 'side contact', Math.round(100 * r.c1 / Math.max(1, r.n1)) + '%', ' jaw travel', Math.round(Line.S1.open - r.aMin), 'mm',
              ' side sensor while measuring', Math.round(r.m1[0]) + '..' + Math.round(r.m1[1]), 'mm', ' nearest when polishing', Math.round(r.near1), 'mm', ' ticks', r.ticks);
});
Line.use(2);
const TL = Line.timeline();
function png(file, W, H, buf) {
  const raw = Buffer.alloc((W * 4 + 1) * H);
  for (let y = 0; y < H; y++) { raw[y * (W * 4 + 1)] = 0; buf.copy ? buf.copy(raw, y * (W * 4 + 1) + 1, y * W * 4, (y + 1) * W * 4) : raw.set(buf.subarray(y * W * 4, (y + 1) * W * 4), y * (W * 4 + 1) + 1); }
  const crcT = []; for (let n = 0; n < 256; n++) { let c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1; crcT[n] = c >>> 0; }
  const crc = b => { let c = 0xffffffff; for (const x of b) c = crcT[(c ^ x) & 255] ^ (c >>> 8); return (c ^ 0xffffffff) >>> 0; };
  const chunk = (t, d) => { const l = Buffer.alloc(4); l.writeUInt32BE(d.length); const td = Buffer.concat([Buffer.from(t), d]); const c = Buffer.alloc(4); c.writeUInt32BE(crc(td)); return Buffer.concat([l, td, c]); };
  const ih = Buffer.alloc(13); ih.writeUInt32BE(W, 0); ih.writeUInt32BE(H, 4); ih[8] = 8; ih[9] = 6;
  fs.writeFileSync(file, Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', ih), chunk('IDAT', zlib.deflateSync(raw)), chunk('IEND', Buffer.alloc(0))]));
}
const W = 1400, H = 860;
[['rest', TL.find(s => s.phase === 'scan' && s.xt > -180)], ['polish', TL.find(s => s.phase === 'polish' && s.s1 === 'follow' && s.xl1 > 140)]].forEach(([name, st]) => {
  const sc = Line.build({ xt: st.xt, a: st.a, zc: st.zc, sp1: st.sp1, sp2: st.sp2, m1: st.m1, m2: st.m2 });
  const buf = new Uint8ClampedArray(W * H * 4).fill(255);
  [{ az: 30, s: 1.08, cx: -215, cz: 75, f: '' }, { az: -20, s: 2.6, cx: -150, cz: 70, f: '-zoom' }].forEach(c => {
    buf.fill(255);
    Line.render(sc, { az: c.az * Math.PI / 180, el: 0.5, s: c.s, cx: c.cx, cz: c.cz }, W, H, pal, buf);
    png('frame-' + name + c.f + '.png', W, H, Buffer.from(buf.buffer));
  });
  console.log(name, 'a', st.a.toFixed(1), 'reading', st.phase, 'tris', sc.tris.length);
});
