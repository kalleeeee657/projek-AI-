import React,{useLayoutEffect,useRef} from 'react';
import {AbsoluteFill,Composition,registerRoot,useCurrentFrame} from 'remotion';
import * as T from 'three';
import {createCharacter} from './characters.mjs';
import {populate,seed} from './npc.mjs';
import project from './project.json';
const W=1080,H=1920,FPS=60;
function world(canvas,spec){
 const village=spec.id==='sade',scene=new T.Scene();scene.background=new T.Color(0xa7c1cf);scene.fog=new T.FogExp2(0xb9ced8,.028);
 const renderer=new T.WebGLRenderer({canvas,antialias:true,preserveDrawingBuffer:true});renderer.setSize(W,H,false);renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.toneMappingExposure=1;renderer.shadowMap.enabled=true;renderer.shadowMap.type=T.PCFSoftShadowMap;
 scene.add(new T.HemisphereLight(0xe5f2ff,0x8b9aa0,2.15));const sun=new T.DirectionalLight(0xfff4df,2.4);sun.position.set(-8,13,5);sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);Object.assign(sun.shadow.camera,{left:-10,right:10,top:10,bottom:-10,near:.5,far:40});sun.shadow.normalBias=.03;scene.add(sun);
 const m=(c,r=.85)=>new T.MeshStandardMaterial({color:c,roughness:r});const snow=m(0xeaf1f3,.92),sand=m(0xb5a488,.96),water=m(0x258da1,.35),green=m(0x789a68),wood=m(0x88694a),roof=m(0x7b6042),wall=m(0xb69d76);
 const ball=new T.SphereGeometry(1,24,16),cube=new T.BoxGeometry(1,1,1);
 function obj(g,mat,x,y,z,sx=1,sy=1,sz=1,p=scene){const o=new T.Mesh(g,mat);o.position.set(x,y,z);o.scale.set(sx,sy,sz);o.castShadow=true;o.receiveShadow=true;p.add(o);return o}
 // Deterministic procedural ground texture, mixed sand and snow.
 const c=document.createElement('canvas');c.width=c.height=256;const ctx=c.getContext('2d'),im=ctx.createImageData(256,256);
 for(let i=0;i<65536;i++){const n=seed(i+333),base=village?[227,235,237]:[218,222,218],grain=(n-.5)*23;for(let j=0;j<3;j++)im.data[i*4+j]=base[j]+grain;im.data[i*4+3]=255}ctx.putImageData(im,0,0);const tex=new T.CanvasTexture(c);tex.colorSpace=T.SRGBColorSpace;tex.wrapS=tex.wrapT=T.RepeatWrapping;tex.repeat.set(18,18);
 const ground=obj(new T.PlaneGeometry(65,30),new T.MeshStandardMaterial({map:tex,roughness:.94}),0,-.018,-3);ground.rotation.x=-Math.PI/2;ground.castShadow=false;
 if(!village){const sea=obj(new T.PlaneGeometry(95,60),water,0,-.13,-48);sea.rotation.x=-Math.PI/2;sea.castShadow=false;
 for(let i=0;i<7;i++){const x=-18+i*6;obj(ball,green,x,-1.1,-19-i%2*3,6,2.9+i%3*.65,5);obj(ball,snow,x,.12,-19-i%2*3,5.8,2+i%3*.65,4.9)}
 }else{for(let i=0;i<5;i++){const x=-15+i*7;obj(ball,green,x,-.5,-19,7,4+i%3,5);obj(ball,snow,x,1.5,-19,5.5,2.2+i%3,4.7)}}
 // Curved palms and snow caps.
 const crowns=[];
 for(let i=0;i<(village?5:9);i++){const x=-12+i*(village?6:3.1),z=-8-seed(i+6)*2,h=3.5+seed(i+16)*1.7;const trunk=obj(new T.CylinderGeometry(.09,.16,h,12),wood,x,h/2,z);trunk.rotation.z=.06*Math.sin(i);
 const crown=new T.Group();crown.position.set(x,h,z);scene.add(crown);crowns.push(crown);
 for(let j=0;j<8;j++){const group=new T.Group();group.rotation.y=j*Math.PI/4; crown.add(group);const leaf=obj(ball,green,.84,.03,0,.95,.10,.22,group);leaf.rotation.z=-.16;const cap=obj(ball,snow,.8,.105,0,.78,.06,.13,group);cap.rotation.z=-.16}}
 // Sade-inspired thatch architecture and raised lumbung silhouettes, not geographic replicas.
 if(village){for(let i=0;i<5;i++){const x=-8+i*4,z=-6.2+(i%2)*.4;const g=new T.Group();g.position.set(x,0,z);scene.add(g);
 obj(cube,wall,0,.82,0,2.15,1.64,1.78,g);
 for(let j=0;j<9;j++){obj(cube,wood,-1+j*.25,.82,.9,.025,1.6,.018,g)}
 obj(cube,m(0x3e3328),0,.54,.91,.48,1.08,.04,g);
 const roofShape=new T.Shape();roofShape.moveTo(-1.45,0);roofShape.quadraticCurveTo(-.92,.62,0,1.47);roofShape.quadraticCurveTo(.92,.62,1.45,0);roofShape.lineTo(-1.45,0);
 const rg=new T.ExtrudeGeometry(roofShape,{depth:2.15,bevelEnabled:true,bevelSegments:2,steps:1,bevelSize:.055,bevelThickness:.055});
 obj(rg,roof,0,1.55,-1.08,1,1,1,g);obj(rg,snow,0,1.65,-1.05,1.02,1.025,1,g);
 }const g=new T.Group();g.position.set(-3,0,-3.4);scene.add(g);for(const x of [-.7,.7])for(const z of [-.55,.55])obj(cube,wood,x,.48,z,.13,.96,.13,g);obj(cube,wall,0,1.15,0,1.65,.55,1.4,g);obj(new T.ConeGeometry(1.45,1.6,4),roof,0,2.08,0,1,1,.8,g);obj(new T.ConeGeometry(1.38,1.37,4),snow,0,2.23,0,1,1,.8,g);}
 const npc=populate(scene,village?18:15,village?40:0);
 const hero=createCharacter('STICKMAN_001'),ami=createCharacter('AMI_001');hero.root.position.set(-.65,hero.baseY,3.8);ami.root.position.set(.56,ami.baseY,3.9);scene.add(hero.root,ami.root);
 // Soft round snow sprites, deterministic position at arbitrary frame.
 const flakeCanvas=document.createElement('canvas');flakeCanvas.width=flakeCanvas.height=32;const fc=flakeCanvas.getContext('2d');const gr=fc.createRadialGradient(16,16,1,16,16,16);gr.addColorStop(0,'rgba(255,255,255,1)');gr.addColorStop(.45,'rgba(255,255,255,.9)');gr.addColorStop(1,'rgba(255,255,255,0)');fc.fillStyle=gr;fc.fillRect(0,0,32,32);const ft=new T.CanvasTexture(flakeCanvas);
 const count=1600,positions=new Float32Array(count*3),geo=new T.BufferGeometry();geo.setAttribute('position',new T.BufferAttribute(positions,3));const flakes=new T.Points(geo,new T.PointsMaterial({color:0xffffff,map:ft,size:.082,transparent:true,depthWrite:false,opacity:.85}));scene.add(flakes);flakes.frustumCulled=false;
 const camera=new T.PerspectiveCamera(40,W/H,.1,100);
 return {draw(f){const t=f/FPS;for(let i=0;i<count;i++){positions[3*i]=(seed(i*3+3)-.5)*27+Math.sin(t*.9+i)*.24+t*.19;positions[3*i+1]=((seed(i*3+4)*10-t*(.5+seed(i+88)*.9))%10+10)%10;positions[3*i+2]=seed(i*3+5)*22-13}geo.attributes.position.needsUpdate=true;
 crowns.forEach((g,i)=>{g.rotation.z=.055*Math.sin(t*1.8+i);g.rotation.x=.025*Math.cos(t*1.7+i)});
 npc.draw(t);const a=Math.min(1,t/1.6);hero.root.rotation.y=.12;ami.root.rotation.y=-.17;hero.pose({frame:f,motion:'idle',expression:'surprised',reaction:a,lookYaw:.12});ami.pose({frame:f,motion:'phone',expression:'happy',reaction:.18,lookYaw:-.08});
 if(village){camera.position.set(2.6-t*.18,2.5,10.8);camera.lookAt(0,1.35,1.0)}else{camera.position.set(1.3-t*.18,1.7,8.9+t*.12);camera.lookAt(-.05,1.04,2.7)}
 renderer.render(scene,camera)},dispose(){scene.traverse(o=>{if(o.isMesh||o.isPoints){o.geometry.dispose();o.material.dispose()}});tex.dispose();ft.dispose();renderer.dispose()}};
}
function Film({spec}){const f=useCurrentFrame(),canvas=useRef(null),engine=useRef(null);useLayoutEffect(()=>{engine.current=world(canvas.current,spec);return()=>engine.current?.dispose()},[]);useLayoutEffect(()=>{engine.current?.draw(f)},[f]);const words=spec.line.split(' '),mid=Math.ceil(words.length/2),line=(f<180?words.slice(0,mid):words.slice(mid)).join(' ');
return <AbsoluteFill style={{background:'#a7c1cf',fontFamily:'Arial',color:'white'}}><canvas ref={canvas} width={W} height={H} style={{width:'100%',height:'100%'}}/><AbsoluteFill style={{pointerEvents:'none',background:'linear-gradient(180deg,rgba(18,34,45,.48),transparent 24%,transparent 75%,rgba(18,34,45,.58))'}}/><div style={{position:'absolute',top:95,left:55,right:55,fontSize:26,fontWeight:700,letterSpacing:3}}>{spec.place.toUpperCase()} • SIMULASI</div><div style={{position:'absolute',top:145,left:55,right:55,fontSize:49,fontWeight:800}}>{spec.title}</div><div style={{position:'absolute',bottom:175,left:80,right:80,textAlign:'center',fontWeight:700,fontSize:40,lineHeight:1.2,textShadow:'0 2px 6px #18252f'}}>{line}</div></AbsoluteFill>}
registerRoot(()=> <>{project.scenes.filter(s=>project.previewIds.includes(s.id)).map(spec=><Composition key={spec.id} id={'Scene-'+spec.id} component={Film} defaultProps={{spec}} durationInFrames={360} fps={FPS} width={W} height={H}/>)}</>);
