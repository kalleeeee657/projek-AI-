import React,{useLayoutEffect,useRef,useState} from 'react';
import {AbsoluteFill,Audio,Composition,registerRoot,staticFile,useCurrentFrame,delayRender,continueRender,cancelRender} from 'remotion';
import * as T from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {createCharacter} from './characters.mjs';
import project from './project.json';
const W=1080,H=1920,FPS=60;
const ease=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x)};
const rnd=n=>{let v=Math.sin(n*127.1+311.7)*43758.5453;return v-Math.floor(v)};
function world(canvas,spec,onReady,onError){
 const kind=spec.type,late=kind==='ending';
 const renderer=new T.WebGLRenderer({canvas,antialias:true,preserveDrawingBuffer:true,powerPreference:'high-performance'});
 renderer.setSize(W,H,false);renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.02;renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;
 const scene=new T.Scene(),cam=new T.PerspectiveCamera(46,W/H,.1,140);
 scene.background=new T.Color(late?0xf6bf92:0xafd8e6);scene.fog=new T.FogExp2(late?0xf2c59b:0xc6e1df,.019);
 scene.add(new T.HemisphereLight(0xe3f4ff,0x988960,2.2));
 const sun=new T.DirectionalLight(late?0xffb77c:0xffe1b0,3.15);sun.position.set(-9,late?5:15,8);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);Object.assign(sun.shadow.camera,{left:-13,right:13,top:13,bottom:-13,near:.5,far:45});sun.shadow.normalBias=.035;scene.add(sun);
 const fill=new T.DirectionalLight(0xafd9f9,.85);fill.position.set(5,6,-8);scene.add(fill);
 const mat=(color,roughness=.85)=>new T.MeshStandardMaterial({color,roughness});
 function mesh(geo,m,x,y,z,sx=1,sy=1,sz=1,p=scene){const o=new T.Mesh(geo,m);o.position.set(x,y,z);o.scale.set(sx,sy,sz);p.add(o);return o}
 const sphere=new T.SphereGeometry(1,28,18);
 function texture(base,seed){
  const c=document.createElement('canvas');c.width=c.height=256;const ctx=c.getContext('2d');const im=ctx.createImageData(256,256);
  for(let i=0;i<65536;i++){const x=i%256,y=i>>8,n=(rnd(i+seed)-.5)*28+Math.sin(x*.17)*Math.sin(y*.12)*12;for(let j=0;j<3;j++)im.data[i*4+j]=Math.max(0,Math.min(255,base[j]+n));im.data[i*4+3]=255}
  ctx.putImageData(im,0,0);const tx=new T.CanvasTexture(c);tx.colorSpace=T.SRGBColorSpace;tx.wrapS=tx.wrapT=T.RepeatWrapping;tx.repeat.set(18,8);return tx
 }
 const sand=new T.MeshStandardMaterial({map:texture([209,183,138],32),roughness:.92});
 // Shared deterministic color and roughness maps; no external downloads.
 const rough=texture([190,190,190],234);rough.colorSpace=T.NoColorSpace;sand.roughnessMap=rough;
 const ground=mesh(new T.PlaneGeometry(100,14),sand,0,-.03,0);ground.rotation.x=-Math.PI/2;ground.receiveShadow=true;
 const path=mesh(new T.PlaneGeometry(100,2.6),new T.MeshStandardMaterial({map:texture([113,109,99],76),roughness:.96}),0,.005,4.1);path.rotation.x=-Math.PI/2;path.receiveShadow=true;
 const line=mesh(new T.PlaneGeometry(100,.07),mat(0xdad8c3),0,.012,2.84);line.rotation.x=-Math.PI/2;
 const waterGeo=new T.PlaneGeometry(110,65,100,45);waterGeo.rotateX(-Math.PI/2);
 const water=mesh(waterGeo,new T.MeshStandardMaterial({color:0x198f9e,roughness:.34,metalness:.07}),0,-.10,-39);
 const wp=waterGeo.attributes.position,base=Float32Array.from(wp.array);
 for(let i=0;i<13;i++){const hill=mesh(sphere,mat(i%2?0x668b52:0x789c58),-36+i*6,-1.5,-43-rnd(i)*9,8,4+rnd(i+9)*4,8);hill.rotation.y=i*.44}
 const leafMat=mat(0x3f793b),bark=mat(0x796144),leafGeo=new T.BufferGeometry();
 // Smooth tapered palm frond strips with a central ridge, reused by every tree.
 const vv=[],ii=[];for(let j=0;j<=12;j++){let u=j/12,w=.25*Math.sin(Math.PI*u)**.7;vv.push(2*u,.62*Math.sin(Math.PI*u)-.40*u*u,-w,2*u,.62*Math.sin(Math.PI*u)-.40*u*u+.035,0,2*u,.62*Math.sin(Math.PI*u)-.40*u*u,w);if(j<12){let k=j*3;ii.push(k,k+3,k+1,k+1,k+3,k+4,k+1,k+4,k+2,k+2,k+4,k+5)}}leafGeo.setAttribute('position',new T.Float32BufferAttribute(vv,3));leafGeo.setIndex(ii);leafGeo.computeVertexNormals();leafMat.side=T.DoubleSide;
 const crowns=[];for(let i=0;i<13;i++){if(i===5||i===6||i===7)continue;const x=-22+i*3.5,z=-5.8-rnd(i+10)*1.3,h=3.8+rnd(i+20)*1.5;const trunk=mesh(new T.CylinderGeometry(.085,.18,h,10),bark,x,h/2,z);trunk.rotation.z=.065*Math.sin(i);const crown=new T.Group();crown.position.set(x-h*.032*Math.sin(i),h,z);scene.add(crown);crowns.push(crown);for(let j=0;j<10;j++){const f=mesh(leafGeo,leafMat,0,0,0,1,.9+rnd(j+i)*.25,1,crown);f.rotation.y=j*Math.PI/5+.12*rnd(i+j)}}
 const grass=new T.InstancedMesh(new T.ConeGeometry(.055,.32,5),mat(0x78924b),400);const dummy=new T.Object3D();for(let i=0;i<400;i++){dummy.position.set(-31+62*rnd(i+100),.13,-4.5-rnd(i+500)*1.5);dummy.rotation.z=(rnd(i+600)-.5)*.8;dummy.scale.setScalar(.65+rnd(i+700)*.7);dummy.updateMatrix();grass.setMatrixAt(i,dummy.matrix)}scene.add(grass);
 const shadowCanvas=document.createElement('canvas');shadowCanvas.width=shadowCanvas.height=128;const sc=shadowCanvas.getContext('2d');const gr=sc.createRadialGradient(64,64,4,64,64,64);gr.addColorStop(0,'rgba(28,37,27,.48)');gr.addColorStop(1,'rgba(28,37,27,0)');sc.fillStyle=gr;sc.fillRect(0,0,128,128);
 const blob=new T.CanvasTexture(shadowCanvas);const shadow=mesh(new T.PlaneGeometry(6.7,2.8),new T.MeshBasicMaterial({map:blob,transparent:true,depthWrite:false}),-2.8,.02,0);shadow.rotation.x=-Math.PI/2;
 const hero=createCharacter('STICKMAN_001'),ami=createCharacter('AMI_001');
 hero.root.position.set(-1.34,hero.baseY+.01,4.05);ami.root.position.set(-.23,ami.baseY+.01,4.17);
 scene.add(hero.root,ami.root);
 // Local set dressing, chosen by the scene recipe.
 const prop=new T.Group();scene.add(prop);
 const cube=new T.BoxGeometry(1,1,1);
 const wood=mat(0x816044),roof=mat(0x856040),stone=mat(0x8e8878);
 if(kind==='footprint'){
  const print=new T.Mesh(new T.ShapeGeometry((()=>{const s=new T.Shape();s.moveTo(-.75,-.45);s.bezierCurveTo(-1,-.2,-.8,.55,-.5,.78);s.bezierCurveTo(-.35,.98,-.16,.7,-.02,.8);s.bezierCurveTo(.18,1.02,.35,.83,.48,.62);s.bezierCurveTo(.85,.78,1,.18,.68,-.45);s.bezierCurveTo(.42,-.85,-.45,-.85,-.75,-.45);return s})()),new T.MeshStandardMaterial({color:0x887357,roughness:1}));
  print.rotation.x=-Math.PI/2;print.position.set(-.2,.012,1.8);prop.add(print);
 }
 if(kind==='village'){
   for(let i=0;i<4;i++){const x=-7+i*4.2,z=-2.9;mesh(cube,wood,x,.9,z,2.1,1.8,1.9,prop);
    const r=mesh(new T.ConeGeometry(1.75,1.45,4),roof,x,2.45,z,1,1,.92,prop);r.rotation.y=Math.PI/4;
    mesh(cube,mat(0x312c26),x,.54,z+1,0.48,1.08,.05,prop);}
 }
 if(kind==='water'){const pond=mesh(new T.CircleGeometry(1.35,48),mat(0x418e8b,.3),-.2,.02,1.4,1.5,1,1,prop);pond.rotation.x=-Math.PI/2;for(let i=0;i<14;i++)mesh(sphere,stone,-.2+Math.cos(i*.449)*1.85,.08,1.4+Math.sin(i*.449)*1.28,.19,.12,.14,prop);}
 if(kind==='feeding'||kind==='ecosystem'){for(let i=0;i<5;i++){let x=2+i*1.8,z=-1.8-i*.32;mesh(new T.CylinderGeometry(.12,.20,3.3,10),bark,x,1.65,z,1,1,1,prop);mesh(sphere,leafMat,x,3.45,z,1.15,1.4,1.05,prop);}}
 if(kind==='road'){for(let i=0;i<8;i++){const x=-6+i*1.9;mesh(cube,mat(0xd9d3b9),x,.018,4.1,.85,.008,.045,prop)}}
 let mixer=null,clip=null,model=null,disposed=false;
 const draw=(f)=>{
   const t=f/FPS,q=ease(t/spec.seconds),src=q*299/60;
   if(mixer&&clip)mixer.setTime(Math.min(clip.duration-.001,Math.max(0,src)));if(model)model.visible=!['footprint','fact'].includes(kind);shadow.visible=!['footprint','fact'].includes(kind);
   const x=-2.8+.78*src;shadow.position.x=x;
   crowns.forEach((c,i)=>{c.rotation.z=.025*Math.sin(t*1.6+i);c.rotation.x=.015*Math.cos(t*1.4+i)});
   for(let i=0;i<wp.count;i++)wp.setY(i,.035*Math.sin(base[3*i]*1.7+t*2)+.026*Math.cos(base[3*i+2]*2.4-t*1.6));wp.needsUpdate=true;waterGeo.computeVertexNormals();
   const reaction=ease((t-1.25)/1.25),r2=ease((t-1.65)/1.2);
   const walking=kind==='road'||kind==='village'||kind==='ending';
   const turn=walking?.6:0,walkBlend=walking?ease(t/.5)*ease((spec.seconds-t)/.5):0;
   const move=walking?.37/(1.15*.68)*Math.max(0,t-.25):0;
   hero.root.position.set(-1.34+Math.sin(turn)*move,hero.baseY+.01,4.05+Math.cos(turn)*move*.35);
   ami.root.position.set(-.23+Math.sin(turn)*move,ami.baseY+.01,4.17+Math.cos(turn)*move*.35);
   hero.root.rotation.y=walking?turn:.12-.48*reaction;ami.root.rotation.y=walking?turn:-.15-.53*r2;
   const surprised=kind==='reveal'||kind==='scale'||kind==='footprint';
   hero.pose({frame:f,motion:walking?'walk':'idle',walkBlend,expression:surprised&&reaction>.12?'surprised':'happy',reaction:surprised?reaction:0,lookYaw:-.18*reaction});
   ami.pose({frame:f,motion:walking?'walk':kind==='fact'?'phone':'idle',walkBlend,expression:surprised&&r2>.12?'surprised':'happy',reaction:surprised?r2:0,lookYaw:-.17*r2});
   if(kind==='footprint'){cam.position.set(1.8,4.1+q,7.8);cam.lookAt(-.4,.45,2.6)}
   else if(kind==='feeding'){cam.position.set(4.5+q,3.0+1.4*q,12.8);cam.lookAt(.7,3.1,0)}
   else if(kind==='scale'){cam.position.set(1.5,2.0,16.5+q*2);cam.lookAt(-.2,2.7,0)}
   else if(kind==='fact'){cam.position.set(.4,1.65,8.9);cam.lookAt(-.75,1.05,4.1)}
   else if(kind==='village'||kind==='road'||kind==='ending'){cam.position.set(3.2+q,2.35,11.8+move*.35);cam.lookAt(-.4+move*.55,1.5,2.2)}
   else if(kind==='water'){cam.position.set(2.7,3.1,11.5);cam.lookAt(0,1.75,1.1)}
   else if(kind==='ecosystem'){cam.position.set(-4+2*q,5.2,17.5);cam.lookAt(.5,2.25,0)}
   else {cam.position.set(2.5+1.15*q,2.25+1.45*q,12.6+4.5*q);cam.lookAt(-.55+.95*q,1.95+1.28*q,0);}

   renderer.render(scene,cam);
 };
 new GLTFLoader().load(staticFile('dino.glb'),g=>{
  if(disposed)return;
  try{model=g.scene;scene.add(model);model.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true}});if(!g.animations.length)throw Error('Missing dinosaur animation');
   clip=g.animations.reduce((a,b)=>a.tracks.length>=b.tracks.length?a:b);mixer=new T.AnimationMixer(model);const action=mixer.clipAction(clip);action.setLoop(T.LoopOnce,1);action.clampWhenFinished=true;action.play();
   model.traverse(o=>{if(!o.isMesh||!o.name.toLowerCase().includes('continuous'))return;const mm=o.material;for(const m of Array.isArray(mm)?mm:[mm]){
      m.onBeforeCompile=shader=>{shader.vertexShader='varying vec3 vSkinLocal;\n'+shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nvSkinLocal=position;');shader.fragmentShader='varying vec3 vSkinLocal;\n'+shader.fragmentShader.replace('#include <color_fragment>','#include <color_fragment>\nfloat speck=sin(vSkinLocal.x*77.0+sin(vSkinLocal.z*63.0))*sin(vSkinLocal.y*69.0);float broad=sin(vSkinLocal.x*3.2+vSkinLocal.z*4.0)*sin(vSkinLocal.y*5.0);diffuseColor.rgb*=0.91+0.10*speck+0.12*broad;');};m.needsUpdate=true;
   }});
   onReady();
  }catch(e){onError(e)}
 },undefined,onError);
 return {draw,dispose(){disposed=true;mixer?.stopAllAction();scene.traverse(o=>{if(o.isMesh){o.geometry.dispose();for(const m of Array.isArray(o.material)?o.material:[o.material])m.dispose()}});renderer.dispose()}};
}
function Film({spec}){
 const f=useCurrentFrame(),t=f/FPS,q=ease((t-1.1)/4.1);
 const canvas=useRef(null),engine=useRef(null),latest=useRef(f);latest.current=f;
 const [handle]=useState(()=>delayRender('Load locked dinosaur GLB'));
 useLayoutEffect(()=>{if(!canvas.current)return;try{engine.current=world(canvas.current,spec,()=>{engine.current.draw(latest.current);continueRender(handle)},e=>cancelRender(e));}catch(e){cancelRender(e)}return()=>{engine.current?.dispose();engine.current=null}},[handle]);
 useLayoutEffect(()=>{engine.current?.draw(f)},[f]);
 const text=spec.title;
 return <AbsoluteFill style={{background:'#93c5d3',fontFamily:'Arial,sans-serif',color:'white'}}>
  <canvas ref={canvas} width={W} height={H} style={{position:'absolute',inset:0,width:'100%',height:'100%'}}/>
  <AbsoluteFill style={{pointerEvents:'none',background:'linear-gradient(180deg,rgba(12,29,36,.43),transparent 25%,transparent 70%,rgba(10,24,25,.72))'}}/>
  <div style={{position:'absolute',top:94,left:54,right:54,letterSpacing:4,fontSize:25,fontWeight:700,color:'#fff4d7'}}>{spec.place.toUpperCase()}</div>
  <div style={{position:'absolute',top:160,left:60,right:60,fontSize:52,fontWeight:800,textAlign:'center',lineHeight:1.12,textShadow:'0 3px 9px #14291f'}}>{text}</div>
 </AbsoluteFill>
}
registerRoot(()=> <>{project.scenes.map(spec=><Composition key={spec.id} id={'Scene-'+spec.id} component={Film} defaultProps={{spec}} durationInFrames={spec.seconds*FPS} fps={FPS} width={W} height={H}/>)}</>);
