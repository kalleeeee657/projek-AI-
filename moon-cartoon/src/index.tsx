import React,{useLayoutEffect,useRef} from 'react';
import {AbsoluteFill,Audio,Composition,registerRoot,staticFile,useCurrentFrame} from 'remotion';
import * as T from 'three';
import script from '../narasi.json';
import timings from './subtitle-timing.json';
import {addCityDetails} from './city-details';
const W=1080,H=1920,FPS=60;
const clamp=(x:number)=>Math.max(0,Math.min(1,x));
const smooth=(x:number)=>{x=clamp(x);return x*x*(3-2*x)};
const rnd=(n:number)=>{let x=Math.sin(n*127.1+311.7)*43758.5453;return x-Math.floor(x)};
const mat=(c:number,rough=.65)=>new T.MeshStandardMaterial({color:c,roughness:rough});
function sphere(rad:number,m:T.Material){return new T.Mesh(new T.SphereGeometry(rad,48,32),m)}
function box(w:number,h:number,d:number,m:T.Material,x=0,y=0,z=0){const a=new T.Mesh(new T.BoxGeometry(w,h,d),m);a.position.set(x,y,z);return a}
function texture(earth:boolean){
 const c=document.createElement('canvas');c.width=1024;c.height=512;const g=c.getContext('2d')!;
 g.fillStyle=earth?'#258fdf':'#b3b6c7';g.fillRect(0,0,1024,512);
 if(earth){
  const land=[[[105,75],[160,52],[228,91],[270,130],[245,170],[190,180],[167,223],[127,190],[110,145]],[[210,225],[275,207],[305,249],[297,323],[255,407],[224,338]],[[480,90],[540,69],[605,89],[644,72],[733,106],[825,92],[885,140],[806,194],[736,178],[684,229],[605,186],[550,193],[505,140]],[[503,200],[573,195],[620,247],[590,328],[545,370],[502,309],[484,250]],[[797,321],[860,298],[922,326],[912,377],[845,388]],[[905,253],[943,264],[931,288]]];
  for(const p of land){g.beginPath();g.moveTo(p[0][0],p[0][1]);for(const q of p.slice(1))g.lineTo(q[0],q[1]);g.closePath();g.lineJoin='round';g.lineWidth=14;g.strokeStyle='#83dc99';g.stroke();g.fillStyle='#42b983';g.fill();}
  g.globalAlpha=.24;g.fillStyle='#f9f8df';for(let i=0;i<85;i++){let x=rnd(i+300)*1024,y=rnd(i+800)*512;g.beginPath();g.ellipse(x,y,14+rnd(i+900)*45,3+rnd(i+1200)*9,-.15,0,Math.PI*2);g.fill();}g.globalAlpha=1;
 }else{
  for(let i=0;i<110;i++){const x=rnd(i+20)*1024,y=rnd(i+120)*512,r=3+rnd(i+220)*23;let gr=g.createRadialGradient(x-r*.15,y-r*.2,r*.15,x,y,r);gr.addColorStop(0,'#8c90a2');gr.addColorStop(.75,'#9296a6');gr.addColorStop(.89,'#e2e3eb');gr.addColorStop(1,'#b3b6c7');g.fillStyle=gr;g.beginPath();g.arc(x,y,r,0,Math.PI*2);g.fill();}
 }
 const tx=new T.CanvasTexture(c);tx.colorSpace=T.SRGBColorSpace;return tx;
}
function makeWorld(canvas:HTMLCanvasElement,id:number){
 const renderer=new T.WebGLRenderer({canvas,antialias:true,alpha:false,preserveDrawingBuffer:true});renderer.setSize(W,H,false);renderer.setPixelRatio(1);renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.3;
 const scene=new T.Scene();const cam=new T.PerspectiveCamera(42,W/H,.1,180);
 const city=id===0||id===2||id===3;
 scene.background=new T.Color(city?0x172c56:0x090f29);
 scene.add(new T.HemisphereLight(0xc1deff,0x464361,2.0));
 const sun=new T.DirectionalLight(0xffe6bd,3.1);sun.position.set(-8,12,8);scene.add(sun);
 const rim=new T.DirectionalLight(0x6c9cff,1.7);rim.position.set(8,3,-9);scene.add(rim);
 const starPos=[];for(let i=0;i<900;i++){starPos.push((rnd(i+5)-.5)*110,(rnd(i+1000)-.5)*110,-25-rnd(i+2000)*50)}
 const starGeom=new T.BufferGeometry();starGeom.setAttribute('position',new T.Float32BufferAttribute(starPos,3));scene.add(new T.Points(starGeom,new T.PointsMaterial({color:0xc4d9ff,size:.12,sizeAttenuation:true,transparent:true,opacity:.85})));
 const earthTex=texture(true),moonTex=texture(false);
 const earth=sphere(2.4,new T.MeshStandardMaterial({map:earthTex,roughness:.8}));
 const moon=sphere(1.05,new T.MeshStandardMaterial({map:moonTex,roughness:.9}));
 scene.add(earth,moon);
 const halo=sphere(2.47,new T.MeshBasicMaterial({color:0x60baff,transparent:true,opacity:.12,side:T.BackSide}));earth.add(halo);
 let water:T.Mesh|undefined;let baseWater:Float32Array|undefined;let boat:T.Group|undefined;let person:T.Group|undefined;
 const debris=new T.Group();scene.add(debris);
 const rockMat=mat(0x9da4ba);for(let i=0;i<145;i++){const a=new T.Mesh(new T.IcosahedronGeometry(.045+rnd(i+600)*.14,0),rockMat);debris.add(a)}debris.visible=false;
 const orbit=new T.Mesh(new T.TorusGeometry(3.85,.018,8,100),new T.MeshBasicMaterial({color:0x7ea8f5,transparent:true,opacity:.5}));orbit.rotation.x=1.1;scene.add(orbit);orbit.visible=false;
 let cityDetails: ReturnType<typeof addCityDetails>|undefined;
 if(city){
 earth.visible=false;
 cityDetails=addCityDetails(scene,id);
 const ground=box(23,.35,22,mat(0x63768a),0,-.25,-4);scene.add(ground);
 const road=box(3.1,.02,23,mat(0x34445e),0,-.058,-4);scene.add(road);
 for(let j=0;j<15;j++)scene.add(box(.12,.025,.55,mat(0xf9df9e),0,-.04,5-j*1.4));
 const facade=[mat(0x789db3),mat(0x9f91bc),mat(0x577894),mat(0xc1a98d)];const win=new T.MeshStandardMaterial({color:0xffe2a0,emissive:0xe8b66d,emissiveIntensity:.42,roughness:.5});
 for(let side of [-1,1])for(let row=0;row<5;row++)for(let col=0;col<3;col++){const n=row*3+col+(side+1)*20;let x=side*(2.5+col*2.4),z=1-row*2.7,h=1.4+rnd(n+49)*4.1;const b=box(1.65,h,1.8,facade[n%4],x,h/2,z);scene.add(b);scene.add(box(1.76,.12,1.88,mat(0x53617d),x,h+.06,z));for(let k=0;k<Math.floor(h/.65);k++)for(let a of [-.43,.43]){scene.add(box(.25,.28,.03,win,x+a,.4+k*.65,z+.916));}}
 const plaza=box(2.1,.25,2.1,mat(0xbec6cb),0,.12,-7);scene.add(plaza);scene.add(box(.48,3.7,.48,mat(0xf1e9d8),0,2.05,-7));const flame=new T.Mesh(new T.ConeGeometry(.27,.8,12),mat(0xffbe43,.4));flame.position.set(0,4.3,-7);scene.add(flame);
 if(id===0){
  person=new T.Group();const skin=mat(0xe1a16d),shirt=mat(0xf1aa37),pants=mat(0x244d80),hair=mat(0x293042);
  const body=sphere(.4,shirt);body.scale.set(.8,1.15,.63);body.position.y=.83;person.add(body);
  const head=sphere(.35,skin);head.position.y=1.48;person.add(head);const cap=sphere(.35,hair);cap.scale.set(1,.55,1);cap.position.y=1.68;person.add(cap);
  for(const a of [-1,1]){person.add(box(.19,.55,.2,pants,a*.16,.32,0));const eye=sphere(.045,mat(0x202637));eye.position.set(a*.115,1.51,.32);person.add(eye);const arm=sphere(.12,shirt);arm.scale.set(1,2.6,1);arm.position.set(a*.38,.85,0);arm.rotation.z=a*.35;person.add(arm)}
  person.position.set(.5,0,3);scene.add(person);
 }else{
  const geo=new T.PlaneGeometry(29,29,48,48);geo.rotateX(-Math.PI/2);water=new T.Mesh(geo,new T.MeshStandardMaterial({color:0x2396c9,roughness:.28,metalness:.18,transparent:true,opacity:.9,side:T.DoubleSide}));scene.add(water);baseWater=new Float32Array(geo.attributes.position.array as Float32Array);
  boat=new T.Group();boat.add(box(.62,.22,1.3,mat(0xf3ab58),0,.13,0));boat.add(box(.4,.29,.48,mat(0xf8ebd9),0,.35,-.12));scene.add(boat);
 }
 }
 function draw(p:number,t:number){
 const q=smooth(p),a=t*.32;
 if(city){
   moon.position.set(-.5,7.8,-13);moon.scale.setScalar(id===0?2.5+q*2.1:4.1);moon.rotation.y=.2+t*.06;
   cam.position.set(3.4-2.8*q, id===0?2.1+2.4*q:4.2+2.2*q, 14+2*q);cam.lookAt(0,3.5+q*.7,-3.4);
   if(person){person.visible=false;}
   cityDetails?.animate(t,q);
   if(water&&baseWater){let pos=water.geometry.attributes.position as T.BufferAttribute;const level=id===2?-.25+q*.55:.22+q*2.5;for(let i=0;i<pos.count;i++){const x=baseWater[i*3],z=baseWater[i*3+2];pos.setY(i,level+.16*Math.sin(x*1.5+t*3)+(.10+q*.13)*Math.sin(z*.9+t*2.1));}pos.needsUpdate=true;water.geometry.computeVertexNormals();if(boat){boat.position.set(-.75,level+.21+.16*Math.sin(-.75*1.5+t*3),2.7-q*2);boat.rotation.z=.13*Math.sin(t*3);}}
 }else{
 cam.position.set(Math.sin(a)*2.1,1.1+Math.sin(a*.6)*.6,15.8);cam.lookAt(0,.4,0);
 earth.position.set(0,-1.25,0);earth.rotation.y=t*.42;earth.scale.set(1,1,1);
 moon.position.set(.5,4.5-q*1.5,-.1);moon.rotation.y=t*.23;moon.scale.setScalar(1.1);
 if(id===1){moon.position.y=4.35-q*.65;orbit.visible=true;orbit.position.copy(earth.position);}
 if(id===4){earth.scale.set(1+.14*q,1-.06*q,1);moon.position.set(.1,3.9-q*.25,0);moon.scale.setScalar(1.3);}
 if(id===5){moon.scale.setScalar(1.2*(1-smooth((p-.22)/.7))+.05);debris.visible=true;const k=smooth((p-.2)/.8);for(let i=0;i<debris.children.length;i++){const b=debris.children[i],theta=i*2.399+t*.2,r=(.25+rnd(i+220)*2.2)*k;b.position.set(moon.position.x+Math.cos(theta)*r,moon.position.y+Math.sin(theta)*r*.7,Math.sin(theta*1.4)*r);b.scale.setScalar(k);b.rotation.set(t*.7+i,t*.4,0);}}
 if(id===6){earth.position.set(0,.15,0);earth.rotation.z=.12;moon.visible=false;debris.visible=true;for(let i=0;i<debris.children.length;i++){const b=debris.children[i],theta=i*2.399+t*.35,r=3.05+rnd(i+320)*1.45;b.position.set(Math.cos(theta)*r,Math.sin(theta)*r*.34+.15,Math.sin(theta)*r*.7);b.rotation.set(t*.35+i,t*.3,0);}cam.position.set(2.2*Math.sin(a),2.1,18);cam.lookAt(0,.4,0);}
 if(id===7){earth.position.set(0,-.7,0);moon.position.set(1.1,3.6+q*.9,-.5);moon.scale.setScalar(.75);orbit.visible=true;orbit.position.copy(earth.position);}
 }
 renderer.render(scene,cam);
 }
 function dispose(){scene.traverse(o=>{if(o instanceof T.Mesh||o instanceof T.Points){o.geometry.dispose();const m=Array.isArray(o.material)?o.material:[o.material];m.forEach(a=>a.dispose())}});earthTex.dispose();moonTex.dispose();renderer.dispose();}
 return {draw,dispose};
}
const starts=script.map((_,i)=>script.slice(0,i).reduce((s,a)=>s+a.sec,0));
function Film(){const f=useCurrentFrame();const time=f/FPS;let id=starts.findLastIndex(s=>s<=time);id=Math.max(0,id);const item=script[id],local=time-starts[id],p=clamp(local/item.sec);const ref=useRef<HTMLCanvasElement>(null);const world=useRef<ReturnType<typeof makeWorld>|null>(null);
 useLayoutEffect(()=>{if(!ref.current)return;world.current=makeWorld(ref.current,id);return()=>{world.current?.dispose();world.current=null}},[id]);
 useLayoutEffect(()=>{world.current?.draw(p,local)},[f,id,p,local]);
 const sceneWords=timings[id] as {text:string;start:number;end:number}[];const active=sceneWords.findIndex(w=>local>=w.start&&local<w.end);const latest=sceneWords.findLastIndex(w=>w.start<=local);const idx=active>=0?active:latest;const show=idx>=0&&local<=sceneWords[idx].end+.22;const start=Math.max(0,Math.floor(idx/4)*4);const words=sceneWords;const edge=Math.min(smooth(p*20),smooth((1-p)*20));return <AbsoluteFill style={{background:'#0b142d',fontFamily:'Arial,sans-serif',color:'white'}}><canvas ref={ref} width={W} height={H} style={{position:'absolute',inset:0,width:'100%',height:'100%'}}/><AbsoluteFill style={{background:'linear-gradient(180deg,rgba(3,10,29,.78),transparent 28%,transparent 60%,rgba(3,10,29,.92))'}}/><div style={{position:'absolute',top:87,left:60,right:60,display:'flex',alignItems:'center',justifyContent:'space-between',fontSize:24,fontWeight:800,letterSpacing:3,color:'#a1d8ff'}}><span>SAINS • BAGAIMANA JIKA</span><span>{String(id+1).padStart(2,'0')}/08</span></div><div style={{position:'absolute',top:145,left:55,right:55,textAlign:'center',fontWeight:900,opacity:.65+.35*edge,transform:'translateY('+((1-edge)*12)+'px)'}}><div style={{fontSize:25,letterSpacing:3,color:'#a0d8ff'}}>{item.tag}</div><div style={{fontSize:70,lineHeight:1.04,marginTop:20,color:'#ffe063',textShadow:'0 5px 0 #111c32,0 10px 25px #0a1024'}}>{item.title}</div></div><div style={{position:'absolute',bottom:245,left:65,right:65,textAlign:'center',fontSize:54,lineHeight:1.2,fontWeight:900,textShadow:'0 3px 8px black'}}>{show&&words.slice(start,start+4).map((w,i)=><span key={i} style={{color:start+i===active?'#ffe063':'white'}}>{w.text} </span>)}</div><div style={{position:'absolute',bottom:145,left:65,right:65,fontSize:22,textAlign:'center',color:'#b1c9e3'}}>{id===7?'Sumber: NASA Science':'Ilustrasi hipotetis • tidak berskala'}</div><div style={{position:'absolute',bottom:107,left:65,right:65,height:7,borderRadius:8,background:'#3f516c'}}><div style={{width:(time/60*100)+'%',height:'100%',background:'#ffe063',borderRadius:8}}/></div><Audio src={staticFile('moon-mix.mp3')}/></AbsoluteFill>}
registerRoot(()=> <Composition id="MoonCartoon" component={Film} durationInFrames={3600} fps={FPS} width={W} height={H}/>);
