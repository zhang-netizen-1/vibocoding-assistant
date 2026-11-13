// node tests/focus_ring_headless.cjs <base-url> -> focus rings whose painted outline is missing on a side (pixel check)
const {chromium}=require('playwright');const base=process.argv[2];
const R=['','basics/','components/','components/cmdk/','interactions/','ai/skills/baseline-ui/','design-system/','bench/'];
(async()=>{const b=await chromium.launch();const out={};let checked=0;
for(const w of [1440,390])for(const r of R){const p=await (await b.newContext({viewport:{width:w,height:900},reducedMotion:'reduce'})).newPage();
 try{await p.goto(base+r,{waitUntil:'networkidle'});}catch(e){continue}
 const n=await p.evaluate(()=>document.querySelectorAll('a[href],button,input,summary,[tabindex="0"]').length);
 await p.keyboard.press('Tab');
 for(let i=0;i<Math.min(n,220);i++){
  const info=await p.evaluate(()=>{const t=document.activeElement;if(!t||t===document.body||t.closest('.demo-scope'))return null;
   const cs=getComputedStyle(t);if(cs.outlineStyle==='none'||parseFloat(cs.outlineWidth)<1)return null;
   t.scrollIntoView({block:'center',inline:'nearest'});const r=t.getBoundingClientRect();if(!r.width||r.height>200)return null;
   const o=parseFloat(cs.outlineOffset)+parseFloat(cs.outlineWidth)/2;
   return {k:t.tagName+'.'+String(t.className||'').slice(0,28)+' "'+(t.textContent||'').trim().slice(0,10)+'"',r:[r.left,r.top,r.right,r.bottom],o,col:cs.outlineColor}});
  if(info){await p.waitForTimeout(60);const [L,T,Rr,B]=info.r,o=info.o;const pts={right:[Rr+o,(T+B)/2],left:[L-o,(T+B)/2],top:[(L+Rr)/2,T-o],bottom:[(L+Rr)/2,B+o]};
   const buf=await p.screenshot();checked++;
   const miss=await p.evaluate(async([b64,pts,col])=>{const img=new Image();img.src='data:image/png;base64,'+b64;await img.decode();const c=document.createElement('canvas');c.width=img.width;c.height=img.height;const x=c.getContext('2d');x.drawImage(img,0,0);
     const m=col.match(/[\d.]+/g).map(Number);const res=[];for(const [s,[px,py]] of Object.entries(pts)){if(px<1||py<1||px>c.width-2||py>c.height-2)continue;let ok=false;for(let dx=-1;dx<=1;dx++)for(let dy=-1;dy<=1;dy++){const d=x.getImageData(Math.round(px)+dx,Math.round(py)+dy,1,1).data;if(Math.abs(d[0]-m[0])+Math.abs(d[1]-m[1])+Math.abs(d[2]-m[2])<90)ok=true}if(!ok)res.push(s)}return res},[buf.toString('base64'),pts,info.col]);
   if(miss.length){const k=w+' '+info.k+' 缺 '+miss.join('/');(out[k]=out[k]||[]).includes(r)||out[k].push(r)}}
  await p.keyboard.press('Tab');}
 await p.context().close();}
console.log('checked',checked);console.log(JSON.stringify(out,null,1));await b.close();process.exit(Object.keys(out).length?1:0)})();
