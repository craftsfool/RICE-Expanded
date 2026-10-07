// Production texture conversion. No original game artwork is redistributed.
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const require=createRequire(import.meta.url);
const sharp=require(process.env.CAUC_NODE_MODULES+'/sharp');
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const source=process.argv[2];
if(!source)throw new Error('Provide the generated PNG path.');
const rgb565=c=>((c[0]>>3)<<11)|((c[1]>>2)<<5)|(c[2]>>3);
const from565=n=>[(n>>11)*255/31,((n>>5)&63)*255/63,(n&31)*255/31];
function bc1(data,w,h){
 const out=Buffer.alloc(Math.ceil(w/4)*Math.ceil(h/4)*8);let pos=0;
 for(let by=0;by<h;by+=4)for(let bx=0;bx<w;bx+=4){
  const pixels=[];
  for(let y=0;y<4;y++)for(let x=0;x<4;x++){const i=(Math.min(h-1,by+y)*w+Math.min(w-1,bx+x))*3;pixels.push([data[i],data[i+1],data[i+2]]);}
  let pair=[pixels[0],pixels[0]],longest=-1;
  for(let i=0;i<16;i++)for(let j=i+1;j<16;j++){const d=pixels[i].reduce((s,v,k)=>s+(v-pixels[j][k])**2,0);if(d>longest){longest=d;pair=[pixels[i],pixels[j]];}}
  let a=rgb565(pair[0]),b=rgb565(pair[1]);if(a<b)[a,b]=[b,a];if(a===b){if(a<65535)a++;else b--;}
  const p0=from565(a),p1=from565(b),palette=[p0,p1,p0.map((v,k)=>(2*v+p1[k])/3),p0.map((v,k)=>(v+2*p1[k])/3)];
  let bits=0;
  pixels.forEach((p,i)=>{let best=0,min=Infinity;palette.forEach((q,j)=>{const d=p.reduce((s,v,k)=>s+(v-q[k])**2,0);if(d<min){min=d;best=j;}});bits|=best<<(2*i);});
  out.writeUInt16LE(a,pos);out.writeUInt16LE(b,pos+2);out.writeUInt32LE(bits>>>0,pos+4);pos+=8;
 }
 return out;
}
const dir=path.join(root,'art/source');fs.mkdirSync(dir,{recursive:true});
fs.copyFileSync(source,path.join(dir,'CAUC_derbent_generated.png'));
const preview=path.join(root,'art/previews/CAUC_derbent_banner.png');fs.mkdirSync(path.dirname(preview),{recursive:true});
await sharp(source).resize(1100,440,{fit:'cover'}).removeAlpha().png().toFile(preview);
const levels=[];let w=1100,h=440;
while(true){const data=await sharp(preview).resize(w,h).removeAlpha().raw().toBuffer();levels.push(bc1(data,w,h));if(w===1&&h===1)break;w=Math.max(1,w>>1);h=Math.max(1,h>>1);}
const header=Buffer.alloc(128);header.write('DDS ',0);header.writeUInt32LE(124,4);header.writeUInt32LE(0xA1007,8);header.writeUInt32LE(440,12);header.writeUInt32LE(1100,16);header.writeUInt32LE(levels[0].length,20);header.writeUInt32LE(levels.length,28);header.writeUInt32LE(32,76);header.writeUInt32LE(4,80);header.write('DXT1',84);header.writeUInt32LE(0x401008,108);
const target=path.join(root,'gfx/interface/illustrations/decisions/CAUC_derbent_pass.dds');fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,Buffer.concat([header,...levels]));
console.log(JSON.stringify({source:dir,preview,texture:target,width:1100,height:440,format:'DXT1',mipmaps:levels.length}));
