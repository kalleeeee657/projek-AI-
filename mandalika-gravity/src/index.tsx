import React,{useLayoutEffect,useRef} from 'react';
import {AbsoluteFill,Audio,Composition,registerRoot,staticFile,useCurrentFrame} from 'remotion';
import * as T from 'three';
import script from '../narasi.json';
import timing from './timing.json';
const W=1080,H=1920,FPS=60;
const clamp=(x:number)=>Math.max(0,Math.min(1,x));
const ease=(x:number)=>{x=clamp(x);return x*x*(3-2*x)};
const rand=(n:number)=>{let a=Math.sin(n*127.1+311.7)*43758.5453;return a-Math.floor(a)};
const mat=(c:number,r=.72)=>new T.MeshStandardMaterial({color:c,roughness:r});
const geo={ball:new T.SphereGeometry(1,18,14),box:new T.BoxGeometry(1,1,1),cyl:new T.CylinderGeometry(1,1,1,14),cone:new T.ConeGeometry(1,1,14)};
function group(p:T.Object3D,x=0,y=0,z=0){const g=new T.Group();g.position.set(x,y,z);p.add(g);return g}
function mesh(p:T.Object3D,g:T.BufferGeometry,m:T.Material,x:number,y:number,z:number,sx:number,sy:number,sz:number){let o=new T.Mesh(g,m);o.position.set(x,y,z);o.scale.set(sx,sy,sz);p.add(o);return o}
const ball=(p:T.Object3D,m:T.Material,x:number,y:number,z:number,sx:number,sy:number,sz:number)=>mesh(p,geo.ball,m,x,y,z,sx,sy,sz);
const box=(p:T.Object3D,m:T.Material,x:number,y:number,z:number,sx:number,sy:number,sz:number)=>mesh(p,geo.box,m,x,y,z,sx,sy,sz);
const cyl=(p:T.Object3D,m:T.Material,x:number,y:number,z:number,sx:number,sy:number,sz:number)=>mesh(p,geo.cyl,m,x,y,z,sx,sy,sz);
function label(p:T.Object3D,text:string,x:number,y:number,z:number,w:number,h:number){
 const c=document.createElement('canvas');c.width=1024;c.height=256;const g=c.getContext('2d')!;
 g.fillStyle='#e7f5f5';g.fillRect(0,0,1024,256);g.fillStyle='#10636b';g.font='bold 96px Arial';g.textAlign='center';g.textBaseline='middle';g.fillText(text,512,128,970);
 const tx=new T.CanvasTexture(c);tx.colorSpace=T.SRGBColorSpace;const o=new T.Mesh(new T.PlaneGeometry(w,h),new T.MeshBasicMaterial({map:tx,side:T.DoubleSide}));o.position.set(x,y,z);p.add(o);
}
function world(canvas:HTMLCanvasElement,id:number){
 const renderer=new T.WebGLRenderer({canvas,antialias:true,preserveDrawingBuffer:true});renderer.setSize(W,H,false);renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.15;
 const scene=new T.Scene(),cam=new T.PerspectiveCamera(43,W/H,.1,150);
 const dusk=id===7;scene.background=new T.Color(id===4?0x07152f:dusk?0xf5b27c:0x9bd8f7);if(id!==4)scene.fog=new T.FogExp2(dusk?0xf2c596:0xb1e2f2,.018);
 scene.add(new T.HemisphereLight(0xf1faff,0x74915f,2.15));const sun=new T.DirectionalLight(dusk?0xffa663:0xfff0cf,3.0);sun.position.set(-6,10,7);scene.add(sun);
 const rim=new T.DirectionalLight(0x6dbeff,1.15);rim.position.set(4,6,-5);scene.add(rim);
 const yellow=mat(0xf2b53a),denim=mat(0x315b89),skin=mat(0xd99a6f),hair=mat(0x222434),white=mat(0xf6f3e9),dark=mat(0x26323c),sand=mat(0xe9d2a1),grass=mat(0x79ab4d),hill=mat(0x639842),road=mat(0x485560),red=mat(0xd54837),bark=mat(0x846346),leaf=mat(0x32865c),sea=mat(0x1caeb8,.35),wood=mat(0x935c40),coffee=mat(0x925326,.25);
 const trees:T.Group[]=[],clouds:T.Group[]=[],vehicles:T.Group[]=[],drops:T.Mesh[]=[], people:ReturnType<typeof human>[]=[];
 const floorShadow=new T.MeshBasicMaterial({color:0x283546,transparent:true,opacity:.20,depthWrite:false});const disk=new T.CircleGeometry(1,30);
 function shadow(x:number,z:number,rx:number,rz:number){const o=mesh(scene,disk,floorShadow,x,.035,z,rx,rz,1);o.rotation.x=-Math.PI/2;return o}
 function palm(x:number,z:number,k:number){const a=group(scene,x,0,z);a.scale.setScalar(k);trees.push(a);for(let j=0;j<7;j++){const b=cyl(a,bark,.025*j,.23+j*.43,0,.11-j*.008,.48,.11-j*.008);b.rotation.z=-.07;}
  for(let j=0;j<8;j++){const fr=group(a,.17,3,0);fr.rotation.y=j*Math.PI/4;for(let k=0;k<6;k++){const f=ball(fr,leaf,.22+k*.17,-.035*k*k,0,.26,.045,.17*(1-k*.075));f.rotation.z=-.16*k;}}
  for(let j=0;j<3;j++)ball(a,wood,.17+Math.cos(j*2.1)*.13,2.9,Math.sin(j*2.1)*.13,.11,.13,.11);
 }
 function human(x:number,z:number,main:boolean,i=0){
  const root=group(scene,x,0,z),body=group(root,0,.87,0),head=group(root,0,1.57,0);let top=main?yellow:mat([0x67aaba,0xe78a6a,0xa18fc0,0x4d927c][i%4]);
  ball(body,top,0,0,0,.31,.39,.22);ball(body,top,0,.24,-.12,.25,.19,.21);box(body,top,0,-.10,.19,.27,.15,.04);for(const a of [-1,1]){cyl(body,white,a*.075,.13,.22,.012,.17,.012);}
  ball(head,skin,0,0,0,.29,.32,.25);ball(head,hair,0,.17,-.035,.30,.19,.26);for(let j=0;j<5;j++)ball(head,hair,-.21+j*.105,.16,.15,.085,.09,.10);
  const eyes:T.Mesh[]=[];for(const a of [-1,1]){ball(head,skin,a*.275,-.02,0,.065,.085,.06);ball(head,white,a*.10,.045,.226,.07,.082,.032);eyes.push(ball(head,dark,a*.10,.04,.253,.031,.042,.018));const brow=ball(head,hair,a*.1,.14,.225,.071,.017,.023);brow.rotation.z=a*.12;}
  ball(head,skin,0,-.045,.26,.053,.06,.043);const mouth=ball(head,dark,0,-.14,.224,.072,.032,.018);
  const arms:T.Group[]=[],legs:T.Group[]=[];for(const a of [-1,1]){const arm=group(root,a*.30,1.12,0);ball(arm,top,0,-.18,0,.10,.25,.10);ball(arm,skin,0,-.40,.01,.08,.10,.075);arms.push(arm);const leg=group(root,a*.14,.58,0);ball(leg,denim,0,-.16,0,.12,.29,.12);ball(leg,white,0,-.40,.065,.135,.095,.21);legs.push(leg);}
  const cup=group(arms[1],0,-.39,.11);cyl(cup,white,0,.12,0,.09,.23,.09);cyl(cup,coffee,0,.245,0,.082,.012,.082);cup.visible=main;
  if(!main)root.scale.setScalar(.70+.08*(i%3));const sh=shadow(x,z,.37,.25);
  return {root,head,body,arms,legs,eyes,mouth,cup,sh,x,z};
 }
 function bike(x:number,z:number,i:number,race:boolean){
  const a=group(scene,x,0,z);vehicles.push(a);const color=mat([0xeb4f46,0x2c9cd4,0xf5ba37,0xe5e6e5][i%4]);const wheel=new T.TorusGeometry(.26,.085,8,20);
  for(const z of [-.51,.51]){let w=new T.Mesh(wheel,dark);w.position.set(0,.33,z);w.rotation.y=Math.PI/2;a.add(w);const hub=cyl(a,white,0,.33,z,.11,.13,.11);hub.rotation.z=Math.PI/2;}
  ball(a,color,0,.60,0,.25,.25,.49);ball(a,dark,0,.76,-.17,.20,.08,.28);ball(a,color,0,.68,.43,.22,.23,.30);ball(a,white,0,.72,.66,.12,.10,.04);box(a,dark,0,.86,.39,.58,.055,.06);
  ball(a,race?color:denim,0,1.03,-.13,.22,.33,.18);ball(a,dark,0,1.43,.03,.24,.24,.22);ball(a,white,0,1.43,.21,.18,.08,.045);
  for(const s of [-1,1]){let arm=ball(a,color,s*.20,1.01,.20,.075,.19,.075);arm.rotation.x=-.9;let leg=ball(a,denim,s*.22,.67,-.05,.09,.23,.11);leg.rotation.x=-.6;}
  shadow(x,z,.40,.78);return a;
 }
 function hut(x:number,z:number,i:number){
  const h=group(scene,x,0,z);box(h,wood,0,.44,0,1.3,.19,1.4);for(const a of [-1,1])for(const b of [-1,1])cyl(h,wood,a*.52,.65,b*.48,.055,1.3,.055);box(h,mat(0xc69b62),0,.96,0,1.2,.90,1.28);
  box(h,dark,0,.91,.65,.40,.61,.03);for(let j=0;j<7;j++){let roof=ball(h,mat(0xb38a4c),0,1.44+j*.085,0, .87-j*.068,.16,.96-j*.077);roof.rotation.y=.03*Math.sin(j);}
  for(let j=0;j<9;j++)box(h,wood,-.54+j*.135,.95,.655,.015,.85,.025);
  if(i%2===0){box(h,red,0,.36,.80,.66,.06,.48);}
 }
 let hero:ReturnType<typeof human>|undefined,water:T.Mesh|undefined,baseWater:Float32Array|undefined,earth:T.Mesh|undefined;
 if(id!==4){
   box(scene,id===5?grass:sand,0,-.18,-4,44,.35,48);
   for(let i=0;i<11;i++){ball(scene,hill,-15+i*3.2,-.4,-22-rand(i)*5,4.6,2.8+rand(i+33)*3.2,5.5);}
   const ocean=id!==2; if(ocean){const g=new T.PlaneGeometry(45,45,42,42);g.rotateX(-Math.PI/2);water=new T.Mesh(g,sea);water.position.set(10,-.045,-16);scene.add(water);baseWater=new Float32Array(g.attributes.position.array as Float32Array);}
   if(id===0||id===1||id===6||id===7){box(scene,road,-1.9,.015,-4,3.5,.04,28);for(let i=0;i<14;i++)box(scene,white,-1.9,.045,7-i*1.65,.08,.015,.8);box(scene,mat(0xd1bfa4),.45,.05,-4,1.4,.14,24);
     for(let i=0;i<5;i++)hut(-5.4,-2-i*3.4,i);label(scene,'KUTA MANDALIKA',2.5,1.0,-4.6,3.9,.75);
     for(let i=0;i<4;i++)bike(-2.5+i%2*.9,2-i*4,i,false);
     for(let i=0;i<5;i++)people.push(human(-.25+i%2*.38,4-i*2.7,false,i));
   }
   if(id===2){box(scene,road,0,.01,-5,7.2,.05,36);for(let i=0;i<20;i++)for(const a of [-1,1])box(scene,i%2?white:red,a*3.55,.06,8-i*1.5,.45,.10,1.5);for(let i=0;i<6;i++)bike(-2.2+i%3*2.1,3-Math.floor(i/3)*4,i,true);for(let i=0;i<8;i++){box(scene,mat(0x8693a0),-5.2, .25+i*.16,-10,1.3,.23,6);};label(scene,'MANDALIKA CIRCUIT',0,3.3,-12,6,1.2);}
   if(id===3){for(let i=0;i<4;i++){const b=group(scene,4+i*2,-.01,-5-i*1.6);ball(b,wood,0,.1,0,.4,.20,1.3);box(b,white,0,.35,-.15,.48,.08,1.1);for(const a of [-1,1]){cyl(b,wood,a*.82,.11,0,.055,1.7,.055).rotation.x=Math.PI/2;box(b,wood,a*.44,.18,0,.8,.07,.08);}vehicles.push(b);}for(let i=0;i<5;i++)people.push(human(-1-i*.65,3-i*.7,false,i));}
   if(id===5){for(let i=0;i<35;i++){const x=(rand(i+55)-.5)*14,z=5-rand(i+85)*18;for(let j=0;j<3;j++){const g=ball(scene,leaf,x+j*.04,.1,z,.035,.20,.035);g.rotation.z=(j-1)*.3;}}}
   if(id!==2){for(let i=0;i<12;i++)palm(i%2?-3.4:3.3,5-Math.floor(i/2)*3.4,.75+rand(i+9)*.4);}
   if([0,1,5,6,7].includes(id))hero=human(.55,3,true);
   if([1,3,5,6].includes(id))for(let i=0;i<32;i++){const r=.045+rand(i+300)*.085;drops.push(ball(scene,id===1||id===6?coffee:sea,0,0,0,r,r,r));}
   for(let i=0;i<5;i++){const c=group(scene,-12+i*5,7+i%2,-19-i);for(let j=0;j<4;j++)ball(c,white,j*.75,.18*Math.sin(j),0,1.05,.41,.65);clouds.push(c);}
 }else{
   const c=document.createElement('canvas');c.width=1024;c.height=512;const g=c.getContext('2d')!;g.fillStyle='#267fc2';g.fillRect(0,0,1024,512);g.fillStyle='#69b77c';
   for(const pts of [[[110,60],[230,90],[285,155],[210,190],[165,220],[100,142]],[[220,230],[305,200],[320,300],[275,400],[230,340]],[[465,85],[610,65],[805,90],[900,150],[710,210],[615,185],[525,150]],[[510,200],[610,220],[575,365],[520,315]],[[790,320],[900,300],[925,380],[820,390]]]){g.beginPath();pts.forEach((p,j)=>j?g.lineTo(p[0],p[1]):g.moveTo(p[0],p[1]));g.closePath();g.fill();}
   const tx=new T.CanvasTexture(c);tx.colorSpace=T.SRGBColorSpace;earth=ball(scene,new T.MeshStandardMaterial({map:tx,roughness:.75}),0,.2,0,2.6,2.6,2.6);const halo=ball(scene,new T.MeshBasicMaterial({color:0x64bbff,transparent:true,opacity:.16,side:T.BackSide}),0,.2,0,2.72,2.72,2.72);let tor=new T.Mesh(new T.TorusGeometry(3.05,.025,8,80),new T.MeshBasicMaterial({color:0x92d9ff}));tor.rotation.x=1.1;scene.add(tor);
   for(let i=0;i<180;i++)ball(scene,white,(rand(i)-.5)*40,(rand(i+200)-.5)*40,-10-rand(i+500)*20,.025,.025,.025);
 }
 function draw(t:number,p:number){
   const q=ease(p);const lift=id===1?ease((p-.12)/.5)*.45:id===5?.25+.14*Math.sin(t*1.2):id===6?.48*(1-ease(p/.35)):0;
   if(hero){const a=hero;const walk=id===0?Math.sin(t*7)*.6:0;a.root.position.set(.55,lift+(id===0?.035*Math.abs(walk):0),3-(id===0?q*.6:0));a.root.rotation.y=id===0?.1:id===7?-.05:.18*Math.sin(t);a.root.rotation.z=id===1?.12*q:id===6?.08*Math.sin(t*5)*(1-q):0;a.head.rotation.x=id===7?.20:id===1?-.13:0;a.legs[0].rotation.x=walk;a.legs[1].rotation.x=-walk;a.arms[0].rotation.x=-walk*.6-(id===1?.8*q:0);a.arms[1].rotation.x=-.85-(id===1?.2*q:0);a.mouth.scale.y=id===1||id===5?.075:.025;for(const e of a.eyes)e.scale.y=(t%3.1>.0&&t%3.1<.1)?.006:.042;a.sh.position.z=a.root.position.z;a.sh.scale.set(.37+lift*.2,.25+lift*.2,1);}
   people.forEach((a,i)=>{const k=Math.sin(t*6+i);a.root.position.z=a.z-.35*q;a.root.position.y=id===1?.22*q:0;a.legs[0].rotation.x=k*.3;a.legs[1].rotation.x=-k*.3;a.arms[0].rotation.x=-k*.24;a.arms[1].rotation.x=k*.24;});
   trees.forEach((a,i)=>a.rotation.z=.035*Math.sin(t*1.8+i));
   clouds.forEach((a,i)=>a.position.x=-12+i*5+t*.18);
   vehicles.forEach((a,i)=>{if(id===3){a.position.y=.1*Math.sin(t*2+i);a.rotation.z=.09*Math.sin(t*2+i);}else{a.position.z=(id===2?3-Math.floor(i/3)*4:2-i*4)+t*(id===2?-1.15:-.55);a.position.y=id===2?.10*q:id===6?.12*(1-q):0;a.rotation.z=id===2?.12*Math.sin(t*1.2+i)*q:0;}});
   drops.forEach((a,i)=>{const f=id===6?1-ease(p/.45):q;const x=(rand(i+13)-.5)*2.7;const z=3+(rand(i+83)-.5)*2.6;a.position.set((id===3?3:.65)+x*f,1.15+rand(i+113)*.9*f,z);a.visible=f>.04;});
   if(water&&baseWater){const a=water.geometry.attributes.position as T.BufferAttribute;for(let i=0;i<a.count;i++)a.setY(i,.065*Math.sin(baseWater[i*3]*1.8+t*2.5)+.055*Math.sin(baseWater[i*3+2]*1.2-t*2));a.needsUpdate=true;water.geometry.computeVertexNormals();}
   if(earth){earth.rotation.y=.4+t*.32;cam.position.set(1.4*Math.sin(t*.22),1.3,14);cam.lookAt(0,0,0);}
   else if(id===2){cam.position.set(4.0-q*2.2,3.5+q*.5,12-q*2.2);cam.lookAt(0,.7,-3);}
   else if(id===3){cam.position.set(-5+q*1.7,4.1,12);cam.lookAt(2,.4,-4);}
   else {cam.position.set(3.9-q*1.1,2.6+q*.35,10.2-q*.65);cam.lookAt(.4,1.25,1.1-q*.6);}
   renderer.render(scene,cam);
 }
 function dispose(){scene.traverse(o=>{if(o instanceof T.Mesh){const m=Array.isArray(o.material)?o.material:[o.material];m.forEach(a=>{if((a as T.MeshStandardMaterial).map)(a as T.MeshStandardMaterial).map?.dispose();a.dispose()});}});renderer.dispose();}
 return {draw,dispose};
}
const starts=script.map((_,i)=>script.slice(0,i).reduce((a,b)=>a+b.sec,0));
function Film(){const frame=useCurrentFrame(),time=frame/FPS;const id=Math.max(0,starts.findLastIndex(s=>s<=time)),s=script[id],local=time-starts[id],p=clamp(local/s.sec);
 const ref=useRef<HTMLCanvasElement>(null),w=useRef<ReturnType<typeof world>|null>(null);
 useLayoutEffect(()=>{if(!ref.current)return;w.current=world(ref.current,id);return()=>{w.current?.dispose();w.current=null}},[id]);
 useLayoutEffect(()=>{w.current?.draw(local,p)},[frame,id,local,p]);
 const words=timing[id] as {text:string;start:number;end:number}[];const active=words.findIndex(v=>local>=v.start&&local<v.end);const last=words.findLastIndex(v=>v.start<=local);const idx=active>=0?active:last;const show=idx>=0&&local<=words[idx].end+.23;const start=Math.max(0,Math.floor(idx/4)*4);
 return <AbsoluteFill style={{background:'#11253b',fontFamily:'Arial,sans-serif',color:'white'}}><canvas ref={ref} width={W} height={H} style={{position:'absolute',inset:0,width:'100%',height:'100%'}}/><AbsoluteFill style={{background:'linear-gradient(180deg,rgba(9,25,43,.66),transparent 32%,transparent 61%,rgba(5,17,36,.86))'}}/><div style={{position:'absolute',top:90,left:55,right:55,display:'flex',justifyContent:'space-between',fontSize:25,fontWeight:800,letterSpacing:2}}><span>BAGAIMANA JIKA?</span><span>{id+1}/8</span></div><div style={{position:'absolute',top:156,left:40,right:40,textAlign:'center',fontWeight:900}}><div style={{fontSize:28,color:'#d5f5ed',letterSpacing:3}}>{s.place}</div><div style={{fontSize:68,lineHeight:1.03,color:'#ffdf66',textShadow:'0 4px 0 #263745,0 8px 18px #273548',marginTop:16}}>{s.title}</div></div>{id===5&&<div style={{position:'absolute',top:435,left:0,right:0,textAlign:'center',fontSize:160,fontWeight:900,color:'#fff1ae',textShadow:'0 5px 18px #213140'}}>{Math.max(1,3-Math.floor(p*3))}</div>}<div style={{position:'absolute',bottom:245,left:65,right:65,textAlign:'center',fontWeight:900,fontSize:59,lineHeight:1.16,textShadow:'0 3px 8px black,0 0 3px black'}}>{show&&words.slice(start,start+4).map((v,i)=><span key={i} style={{color:start+i===active?'#ffe05c':'white'}}>{v.text} </span>)}</div><div style={{position:'absolute',bottom:143,left:50,right:50,textAlign:'center',fontSize:24,color:'#d8eee9'}}>Ilustrasi hipotetis • Mandalika Edition</div><div style={{position:'absolute',bottom:110,left:65,right:65,height:8,background:'#4b6272',borderRadius:8}}><div style={{height:'100%',width:time/60*100+'%',background:'#ffde60',borderRadius:8}}/></div><Audio src={staticFile('mix.mp3')}/></AbsoluteFill>;
}
registerRoot(()=> <Composition id="MandalikaGravity" component={Film} durationInFrames={3600} fps={FPS} width={W} height={H}/>);
