// usage: node pngpix.js file.png x y  -> prints the r g b at that pixel (8-bit RGB/RGBA PNG, any filter)
const fs = require('fs'), zlib = require('zlib');
const b = fs.readFileSync(process.argv[2]); let p = 8, W, H, ct, idat = [];
while (p < b.length) { const L = b.readUInt32BE(p), t = b.toString('ascii', p + 4, p + 8), d = b.slice(p + 8, p + 8 + L);
  if (t === 'IHDR') { W = d.readUInt32BE(0); H = d.readUInt32BE(4); ct = d[9]; } if (t === 'IDAT') idat.push(d); p += 12 + L; }
const bpp = ct === 6 ? 4 : 3, raw = zlib.inflateSync(Buffer.concat(idat)), st = W * bpp, img = Buffer.alloc(H * st);
for (let y = 0; y < H; y++) { const f = raw[y * (st + 1)], s = raw.slice(y * (st + 1) + 1, (y + 1) * (st + 1));
  for (let x = 0; x < st; x++) { const a = x >= bpp ? img[y * st + x - bpp] : 0, u = y ? img[(y - 1) * st + x] : 0, c = (x >= bpp && y) ? img[(y - 1) * st + x - bpp] : 0;
    let v = s[x]; if (f === 1) v += a; else if (f === 2) v += u; else if (f === 3) v += (a + u) >> 1; else if (f === 4) { const q = a + u - c, pa = Math.abs(q - a), pb = Math.abs(q - u), pc = Math.abs(q - c); v += pa <= pb && pa <= pc ? a : pb <= pc ? u : c; }
    img[y * st + x] = v & 255; } }
const x = +process.argv[3], y = +process.argv[4], o = y * st + x * bpp; console.log(img[o], img[o + 1], img[o + 2]);
