const fs=require('fs');
for(const f of process.argv.slice(2)){const b=fs.readFileSync(f);const E=new Map();let n=0;const key=(p)=>p.map(v=>v.toFixed(3)).join(',');
const add=(A,B)=>{const k=A<B?A+'|'+B:B+'|'+A;E.set(k,(E.get(k)||0)+1)};
if(b.slice(0,5).toString()==='solid'&&b.includes('facet normal')){const m=[...b.toString().matchAll(/vertex\s+(\S+)\s+(\S+)\s+(\S+)/g)].map(q=>key([+q[1],+q[2],+q[3]]));for(let i=0;i<m.length;i+=3){add(m[i],m[i+1]);add(m[i+1],m[i+2]);add(m[i+2],m[i]);n++}}
else{const c=b.readUInt32LE(80);for(let i=0;i<c;i++){const o=84+i*50+12;const v=[0,1,2].map(k=>key([b.readFloatLE(o+k*12),b.readFloatLE(o+k*12+4),b.readFloatLE(o+k*12+8)]));add(v[0],v[1]);add(v[1],v[2]);add(v[2],v[0]);n++}}
let bad=0;for(const v of E.values())if(v!==2)bad++;console.log(f,'triangles',n,'open or non-manifold edges',bad)}
