// One-time preservation/export step after image generation.
// Requires record 35's verified wall.png and the generated candidate named below.
// Candidate was removed after export to retain only requested pictures.
// Run from the repository root: node line-4/finish_wall36.js
'use strict';
const fs = require('node:fs');
const zlib = require('node:zlib');
const crypto = require('node:crypto');
const {decode, thumbnail} = require('../gathering/thumbnail.js');
const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const ancestor = 'd043c6f6f2aa58fe6d46a53c0759203353a01cdf8970dad3feba14e16dbe5e69';
const oldBytes = fs.readFileSync('artifacts/line-4/wall.png');
if (hash(oldBytes) !== ancestor) throw new Error('requires unchanged record-35 ancestor');
const generated = fs.readFileSync('artifacts/line-4/b03a1f82-38f6-4098-b6c8-a3482bd3b832-1.png');
const old = decode(oldBytes), fresh = decode(generated);
if (old.width !== 1254 || old.height !== 1254 || old.channels !== 3 ||
    fresh.width !== 1254 || fresh.height !== 1254)
  throw new Error('unexpected image dimensions');
const out = Buffer.from(old.pixels);
// This reviewed bare-rock rectangle contains only the newly generated nested-stone motif.
// No ancestral pigment is inside it. All other pixels come from the ancestor.
const bounds = [840, 95, 970, 220];
function distance(x,y,ax,ay,bx,by) {
  const t=Math.max(0,Math.min(1,((x-ax)*(bx-ax)+(y-ay)*(by-ay))/((bx-ax)**2+(by-ay)**2)));
  return Math.hypot(x-ax-t*(bx-ax),y-ay-t*(by-ay));
}
function motif(x,y) {
  return Math.hypot(x-864,y-111)<14 || Math.hypot(x-950,y-117)<14 ||
    Math.hypot(x-899,y-202)<17 || distance(x,y,864,120,901,164)<12 ||
    distance(x,y,901,164,947,125)<12 || distance(x,y,901,164,899,191)<11;
}
for (let y=bounds[1]; y<=bounds[3]; y++) for (let x=bounds[0]; x<=bounds[2]; x++) {
  const p=(y*old.width+x)*3, q=(y*fresh.width+x)*fresh.channels;
  // Extract only the generated pigment inside the reviewed motif silhouette.
  // All other generated pixels, including repainted ancestors, are discarded.
  if (!motif(x,y)) continue;
  const chalk = Math.hypot(x-899,y-202)<8;
  const dark = fresh.pixels[q]<125 && fresh.pixels[q+1]<92 && fresh.pixels[q+2]<72;
  if (!chalk && !dark) continue;
  const difference = old.pixels[p+1]-fresh.pixels[q+1];
  if (!chalk && difference<14) continue;
  const alpha=chalk?0.88:Math.min(1,(difference-14)/14);
  for (let c=0;c<3;c++) out[p+c]=Math.round(old.pixels[p+c]*(1-alpha)+fresh.pixels[q+c]*alpha);
}
let changed=0, outside=0, box=[old.width,old.height,-1,-1];
for (let y=0;y<old.height;y++) for (let x=0;x<old.width;x++) {
  const p=(y*old.width+x)*3;
  if (out[p]!==old.pixels[p] || out[p+1]!==old.pixels[p+1] || out[p+2]!==old.pixels[p+2]) {
    changed++;
    box=[Math.min(box[0],x),Math.min(box[1],y),Math.max(box[2],x),Math.max(box[3],y)];
    if (x<bounds[0]||x>bounds[2]||y<bounds[1]||y>bounds[3]) outside++;
  }
}
if (!changed || outside) throw new Error('new mark absent or preservation failed');
function crc32(bytes) {
  let crc=0xffffffff;
  for (const v of bytes) { crc^=v; for(let b=0;b<8;b++) crc=(crc>>>1)^((crc&1)?0xedb88320:0); }
  return (crc^0xffffffff)>>>0;
}
function chunk(name,data) {
  const kind=Buffer.from(name), length=Buffer.alloc(4), crc=Buffer.alloc(4);
  length.writeUInt32BE(data.length); crc.writeUInt32BE(crc32(Buffer.concat([kind,data])));
  return Buffer.concat([length,kind,data,crc]);
}
const header=Buffer.alloc(13);
header.writeUInt32BE(old.width); header.writeUInt32BE(old.height,4); header[8]=8; header[9]=2;
const stride=old.width*3, scan=Buffer.alloc(old.height*(stride+1));
for (let y=0;y<old.height;y++) out.copy(scan,y*(stride+1)+1,y*stride,(y+1)*stride);
const png=Buffer.concat([Buffer.from('89504e470d0a1a0a','hex'),chunk('IHDR',header),
  chunk('IDAT',zlib.deflateSync(scan,{level:9})),chunk('IEND',Buffer.alloc(0))]);
const jpeg=thumbnail(png,512,75);
if (jpeg.length>=100000) throw new Error('JPEG over budget');
fs.writeFileSync('artifacts/line-4/wall-v16.png',png);
fs.writeFileSync('artifacts/line-4/wall.png',png);
fs.writeFileSync('dist/line-4/36.jpg',jpeg);
const result={ancestor_sha256:ancestor,generated_sha256:hash(generated),
  png:{path:'artifacts/line-4/wall-v16.png',format:'PNG',mode:'RGB',dimensions:[1254,1254],bytes:png.length,sha256:hash(png)},
  jpeg:{path:'dist/line-4/36.jpg',format:'JPEG',dimensions:[512,512],bytes:jpeg.length,sha256:hash(jpeg)},
  preservation:{rectangle:bounds,changed_pixels:changed,changed_bounds:box,outside_rectangle_changed_pixels:outside},
  visual_review_required:true,visual_review_completed:false,unmet_visual_requirements:[]};
fs.writeFileSync('line-4/image-checks36.json',JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));
