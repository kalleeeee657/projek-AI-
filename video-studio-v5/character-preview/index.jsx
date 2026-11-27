import React,{useLayoutEffect,useRef} from 'react';
import {AbsoluteFill,Composition,registerRoot,useCurrentFrame} from 'remotion';
import * as T from 'three';
import {createCharacter} from './characters.mjs';
const W=1080,H=1920,FPS=60;
function world(canvas){
 const renderer=new T.WebGLRenderer({canvas,antialias:true,preserveDrawingBuffer:true});renderer.setSize(W,H,false);renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1.04;
 renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;
 const s=new T.Scene();s.background=new T.Color(0xaed1dd);s.fog=new T.Fog(0xaed1dd,9,28);
 s.add(new T.HemisphereLight(0xeaf6ff,0x9e8060,2.0));const sun=new T.DirectionalLight(0xffe2b8,3.0);sun.position.set(-3,6,4);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);sun.shadow.camera.left=-4;sun.shadow.camera.right=4;sun.shadow.camera.top=4;sun.shadow.camera.bottom=-4;sun.shadow.normalBias=.025;s.add(sun);const rim=new T.DirectionalLight(0xcde7ff,1.2);rim.position.set(3,4,-5);s.add(rim);
 const floor=new T.Mesh(new T.PlaneGeometry(60,60),new T.MeshStandardMaterial({color:0xc8b89b,roughness:.98}));floor.rotation.x=-Math.PI/2;floor.receiveShadow=true;s.add(floor);
 const a=createCharacter('STICKMAN_001'),b=createCharacter('AMI_001');a.root.position.x=-.58;b.root.position.x=.58;s.add(a.root,b.root);
 const hills=new T.SphereGeometry(1,24,16);for(let i=0;i<7;i++){const h=new T.Mesh(hills,new T.MeshStandardMaterial({color:i%2?0x7d9e79:0x91ad8b}));h.position.set(-12+i*4,-.8,-11-i%2*2);h.scale.set(4,2+i%3*.4,3);s.add(h)}
 const cam=new T.PerspectiveCamera(36,W/H,.1,80);
 return {draw(f){const t=f/FPS;const angle=.30*Math.sin(t*.72);cam.position.set(4.75*Math.sin(angle),1.33,4.75*Math.cos(angle));cam.lookAt(0,.91,0);
 a.root.rotation.y=.09;b.root.rotation.y=-.10;
 a.pose({frame:f,motion:t<2?'idle':t<4?'wave':'talk',expression:t<4?'happy':'surprised'});
 b.pose({frame:f,motion:t<2?'idle':t<4?'wave':'phone',expression:'happy'});
 renderer.render(s,cam)},dispose(){s.traverse(o=>{if(o.isMesh){o.geometry.dispose();o.material.dispose()}});renderer.dispose()}};
}
function Preview(){const f=useCurrentFrame(),ref=useRef(null),w=useRef(null);useLayoutEffect(()=>{w.current=world(ref.current);return()=>w.current?.dispose()},[]);useLayoutEffect(()=>{w.current?.draw(f)},[f]);return <AbsoluteFill style={{background:'#a1c9d4',fontFamily:'Arial',color:'white'}}><canvas ref={ref} width={W} height={H} style={{width:'100%',height:'100%'}}/><div style={{position:'absolute',top:88,left:55,right:55,fontSize:30,fontWeight:800,letterSpacing:3,textShadow:'0 2px 6px #253940'}}>V5 • CHARACTER LAB</div><div style={{position:'absolute',bottom:115,left:35,right:35,textAlign:'center',fontSize:35,fontWeight:700,textShadow:'0 2px 8px #253940'}}>STICKMAN_001 &amp; Ami<br/><span style={{fontSize:24,fontWeight:400}}>Semi-3D • Prototype rig</span></div></AbsoluteFill>}
registerRoot(()=> <Composition id="CharacterDuo" component={Preview} durationInFrames={360} fps={FPS} width={W} height={H}/>);
