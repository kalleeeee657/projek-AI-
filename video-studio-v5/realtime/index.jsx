import React,{useLayoutEffect,useRef,useState} from 'react';
import {AbsoluteFill,Audio,Composition,registerRoot,staticFile,useCurrentFrame,delayRender,continueRender,cancelRender} from 'remotion';
import * as T from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {characterSVG,CHARACTER_ID} from '../character-lock/STICKMAN_001.mjs';
const W=1080,H=1920,FPS=60;
const ease=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x)};
const rnd=n=>{let v=Math.sin(n*127.1+311.7)*43758.5453;return v-Math.floor(v)};
function world(canvas,onReady,onError){
 const renderer=new T.WebGLRenderer({canvas,antialias:true,preserveDrawingBuffer:true,powerPreference:'high-performance'});
 renderer.setSize(W,H,false);renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.12;
 const scene=new T.Scene(),cam=new T.PerspectiveCamera(46,W/H,.1,140);
 scene.background=new T.Color(0xafd8e6);scene.fog=new T.FogExp2(0xc6e1df,.019);
 scene.add(new T.HemisphereLight(0xe3f4ff,0x988960,2.2));
 const sun=new T.DirectionalLight(0xffe1b0,3.15);sun.position.set(-9,15,8);scene.add(sun);
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
 const ground=mesh(new T.PlaneGeometry(100,14),sand,0,-.03,0);ground.rotation.x=-Math.PI/2;
 const path=mesh(new T.PlaneGeometry(100,2.6),new T.MeshStandardMaterial({map:texture([113,109,99],76),roughness:.96}),0,.005,4.1);path.rotation.x=-Math.PI/2;
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
 let mixer=null,clip=null,model=null,disposed=false;
 const draw=(f)=>{
   const t=f/FPS,q=ease((t-1.1)/4.1),src=t*299/359;
   if(mixer&&clip)mixer.setTime(Math.min(clip.duration-.001,Math.max(0,src)));
   const x=-2.8+.78*src;shadow.position.x=x;
   crowns.forEach((c,i)=>{c.rotation.z=.025*Math.sin(t*1.6+i);c.rotation.x=.015*Math.cos(t*1.4+i)});
   for(let i=0;i<wp.count;i++)wp.setY(i,.035*Math.sin(base[3*i]*1.7+t*2)+.026*Math.cos(base[3*i+2]*2.4-t*1.6));wp.needsUpdate=true;waterGeo.computeVertexNormals();
   cam.position.set(x+3.6+1.2*q,2.1+1.9*q,10.8+8.7*q);cam.lookAt(x+.4,1.35+2.25*q,0);
   renderer.render(scene,cam);
 };
 new GLTFLoader().load(staticFile('dino.glb'),g=>{
  if(disposed)return;
  try{model=g.scene;scene.add(model);if(!g.animations.length)throw Error('Missing dinosaur animation');
   clip=g.animations.reduce((a,b)=>a.tracks.length>=b.tracks.length?a:b);mixer=new T.AnimationMixer(model);const action=mixer.clipAction(clip);action.setLoop(T.LoopOnce,1);action.clampWhenFinished=true;action.play();
   model.traverse(o=>{if(!o.isMesh||!o.name.toLowerCase().includes('continuous'))return;const mm=o.material;for(const m of Array.isArray(mm)?mm:[mm]){
      m.onBeforeCompile=shader=>{shader.vertexShader='varying vec3 vSkinLocal;\n'+shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nvSkinLocal=position;');shader.fragmentShader='varying vec3 vSkinLocal;\n'+shader.fragmentShader.replace('#include <color_fragment>','#include <color_fragment>\nfloat speck=sin(vSkinLocal.x*77.0+sin(vSkinLocal.z*63.0))*sin(vSkinLocal.y*69.0);float broad=sin(vSkinLocal.x*3.2+vSkinLocal.z*4.0)*sin(vSkinLocal.y*5.0);diffuseColor.rgb*=0.91+0.10*speck+0.12*broad;');};m.needsUpdate=true;
   }});
   onReady();
  }catch(e){onError(e)}
 },undefined,onError);
 return {draw,dispose(){disposed=true;mixer?.stopAllAction();scene.traverse(o=>{if(o.isMesh){o.geometry.dispose();for(const m of Array.isArray(o.material)?o.material:[o.material])m.dispose()}});renderer.dispose()}};
}
function Film(){
 const f=useCurrentFrame(),t=f/FPS,q=ease((t-1.1)/4.1);
 const canvas=useRef(null),engine=useRef(null),latest=useRef(f);latest.current=f;
 const [handle]=useState(()=>delayRender('Load locked dinosaur GLB'));
 useLayoutEffect(()=>{if(!canvas.current)return;try{engine.current=world(canvas.current,()=>{engine.current.draw(latest.current);continueRender(handle)},e=>cancelRender(e));}catch(e){cancelRender(e)}return()=>{engine.current?.dispose();engine.current=null}},[handle]);
 useLayoutEffect(()=>{engine.current?.draw(f)},[f]);
 const svg=characterSVG({id:CHARACTER_ID,frame:f,fps:FPS,motion:'idle',expression:t<1.5?'happy':'surprised'}).replace('<svg ','<svg width="100%" height="100%" ');
 const size=330-95*q;
 const text=t<2?'Bayangkan di Mandalika...':t<4?'Tiba-tiba muncul':'dinosaurus raksasa!';
 return <AbsoluteFill style={{background:'#93c5d3',fontFamily:'Arial,sans-serif',color:'white'}}>
  <canvas ref={canvas} width={W} height={H} style={{position:'absolute',inset:0,width:'100%',height:'100%'}}/>
  <div style={{position:'absolute',left:100+35*q,top:1120+45*q,width:size,height:size*415/290}} dangerouslySetInnerHTML={{__html:svg}}/>
  <AbsoluteFill style={{pointerEvents:'none',background:'linear-gradient(180deg,rgba(12,29,36,.43),transparent 25%,transparent 70%,rgba(10,24,25,.72))'}}/>
  <div style={{position:'absolute',top:94,left:54,right:54,letterSpacing:4,fontSize:25,fontWeight:700,color:'#fff4d7'}}>BAGAIMANA JIKA?  •  MANDALIKA</div>
  <div style={{position:'absolute',bottom:180,left:60,right:60,fontSize:54,fontWeight:800,textAlign:'center',lineHeight:1.12,textShadow:'0 3px 9px #14291f'}}>{text}</div>
  <Audio src={staticFile('ambience.wav')}/>
 </AbsoluteFill>
}
registerRoot(()=> <Composition id="DinosaurV5" component={Film} durationInFrames={360} fps={FPS} width={W} height={H}/>);
