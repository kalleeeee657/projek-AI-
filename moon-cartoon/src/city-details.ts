import * as T from 'three';
const material=(color:number,emissive=0)=>new T.MeshStandardMaterial({color,roughness:.72,emissive,emissiveIntensity:emissive?.7:0});
const greens=[material(0x287a56),material(0x429c63),material(0x70bc72)], bark=material(0x77523d), pavement=material(0xb0b5bc), tire=material(0x182638), glass=material(0x87bdcf), lamp=material(0xffe4a3,0xffcb78), dark=material(0x334254);
const ballGeo=new T.SphereGeometry(1,12,9),boxGeo=new T.BoxGeometry(1,1,1),cylGeo=new T.CylinderGeometry(1,1,1,12),wheelGeo=new T.CylinderGeometry(.16,.16,.12,14);
function mesh(parent:T.Object3D,geo:T.BufferGeometry,mat:T.Material,x:number,y:number,z:number,sx:number,sy:number,sz:number){const o=new T.Mesh(geo,mat);o.position.set(x,y,z);o.scale.set(sx,sy,sz);parent.add(o);return o}
function ball(p:T.Object3D,m:T.Material,x:number,y:number,z:number,sx:number,sy:number,sz:number){return mesh(p,ballGeo,m,x,y,z,sx,sy,sz)}
function cube(p:T.Object3D,m:T.Material,x:number,y:number,z:number,sx:number,sy:number,sz:number){return mesh(p,boxGeo,m,x,y,z,sx,sy,sz)}
function group(p:T.Object3D,x=0,y=0,z=0){const g=new T.Group();g.position.set(x,y,z);p.add(g);return g}
export function addCityDetails(scene:T.Scene,id:number){
 const world=group(scene);const trees:T.Group[]=[], cars:T.Group[]=[], walkers:{root:T.Group;head:T.Group;arms:T.Group[];legs:T.Group[];x:number;z:number}[]=[], clouds:T.Group[]=[], foam:T.Mesh[]=[];
 const shade=new T.MeshBasicMaterial({color:0x101a2a,transparent:true,opacity:.22,depthWrite:false});const disk=new T.CircleGeometry(1,20);
 const shadow=(x:number,z:number,rx:number,rz:number)=>{const o=mesh(world,disk,shade,x,.075,z,rx,rz,1);o.rotation.x=-Math.PI/2;return o};
 for(const side of [-1,1]){
  cube(world,pavement,side*1.95,.055,-4,0.78,.18,22);
  for(let i=0;i<7;i++){const z=5.3-i*2.7,x=side*(2.05+(i%2)*.17);const tree=group(world,x,0,z);trees.push(tree);
   mesh(tree,cylGeo,bark,0,.68,0,.085,1.35,.085);
   for(let j=0;j<5;j++){const a=j*2.4;ball(tree,greens[j%3],Math.cos(a)*.24,1.42+j%2*.22,Math.sin(a)*.24,.39,.48,.39);}
   ball(tree,greens[2],0,1.9,0,.37,.42,.37);shadow(x,z,.52,.45);
   if(i%2===0){const l=group(world,side*1.59,0,z-.8);mesh(l,cylGeo,dark,0,1.03,0,.035,2.06,.035);cube(l,dark,-side*.13,2.02,0,.28,.06,.06);ball(l,lamp,-side*.26,1.98,0,.14,.075,.12);}
  }
 }
 const colors=[0xef8c5d,0x6db9d6,0xf2dfb0,0x997dba].map(c=>material(c));
 for(let i=0;i<4;i++){
  const c=group(world);cars.push(c);const m=colors[i];
  cube(c,m,0,.25,0,.65,.28,1.2);cube(c,m,0,.48,-.08,.55,.23,.61);cube(c,glass,0,.5,.24,.49,.16,.025);cube(c,glass,0,.5,-.4,.49,.16,.025);
  for(const a of [-1,1]){cube(c,glass,a*.283,.49,-.08,.025,.15,.44);for(const z of [-.36,.36]){const w=mesh(c,wheelGeo,tire,a*.33,.14,z,1,1,1);w.rotation.z=Math.PI/2;}cube(c,lamp,a*.19,.27,.61,.15,.10,.025);}
 }
 function person(x:number,z:number,i:number){
  const root=group(world,x,.12,z),head=group(root,0,1.18,0),arms:T.Group[]=[],legs:T.Group[]=[];
  const skin=material([0xc88f64,0xe5b282,0x9d674e][i%3]),shirt=colors[i%4],hair=material(0x252335);
  ball(root,shirt,0,.77,0,.23,.32,.16);ball(head,skin,0,0,0,.25,.27,.23);ball(head,hair,0,.16,-.04,.25,.14,.22);
  for(const a of [-1,1]){ball(head,dark,a*.08,.035,.206,.026,.033,.018);ball(head,skin,a*.23,0,0,.055,.075,.045);const arm=group(root,a*.23,.94,0);ball(arm,shirt,0,-.15,0,.072,.20,.072);ball(arm,skin,0,-.32,0,.059,.075,.059);arms.push(arm);const leg=group(root,a*.1,.52,0);cube(leg,dark,0,-.18,0,.14,.36,.15);ball(leg,tire,0,-.37,.04,.09,.075,.16);legs.push(leg);}
  ball(head,skin,0,-.035,.23,.045,.045,.04);ball(head,dark,0,-.115,.211,.043,.022,.017);
  root.scale.setScalar(.86+(i%3)*.08);walkers.push({root,head,arms,legs,x,z});
 }
 if(id===0){person(1.85,5.4,0);person(-1.88,4.7,1);person(1.87,1.7,2);person(-1.86,-.4,3);}
 if(id===2){person(1.85,4.7,1);person(-1.86,3.9,2);}
 // On the flood climax, no pedestrians are shown in deep water.
 const cloudMat=new T.MeshStandardMaterial({color:0xb9c9df,transparent:true,opacity:.34,roughness:1,depthWrite:false});
 for(let i=0;i<4;i++){const c=group(world,-7+i*5,7.2+(i%2)*1.4,-12-i*2);clouds.push(c);for(let j=0;j<4;j++)ball(c,cloudMat,j*.58,Math.sin(j)*.13,0,.7,.26,.38)}
 const foamMat=new T.MeshBasicMaterial({color:0xd0f6ff,transparent:true,opacity:.66,depthWrite:false});if(id!==0)for(let i=0;i<30;i++){const m=ball(world,foamMat,0,0,0,.15,.014,.035);foam.push(m);}
 function animate(t:number,q:number){
  trees.forEach((g,i)=>{g.rotation.z=.035*Math.sin(t*1.7+i*.63)*(id===0?1:2.2);g.rotation.x=.02*Math.cos(t*1.3+i)});
  cars.forEach((c,i)=>{const dir=i%2===0?1:-1;c.position.set(dir*.77,id===3?Math.max(.03,.22+q*2.5-.23):.03,((t*(1.05+i*.11)+i*4.1)%18-11)*dir);c.rotation.y=dir===1?0:Math.PI;c.rotation.z=id===3?.12*Math.sin(t*1.7+i)*q:0;});
  walkers.forEach((w,i)=>{const stop=id===0?Math.min(1,t/2.3):Math.min(1,t/1.3);const walk=1-Math.min(1,Math.max(0,(t-1.1)/1.2));const a=Math.sin(t*7.2+i)*walk;w.root.position.z=w.z-.52*(1-Math.exp(-t));w.root.position.y=.12+.025*Math.abs(a);w.root.rotation.y=i%2===0?Math.PI*.8:Math.PI*1.15;w.head.rotation.x=-.36*stop;w.legs[0].rotation.x=a*.5;w.legs[1].rotation.x=-a*.5;w.arms[0].rotation.x=-a*.35;w.arms[1].rotation.x=a*.35-1.65*stop;});
  clouds.forEach((c,i)=>c.position.x=-7+i*5+t*.15);
  foam.forEach((m,i)=>{const x=(i*1.71%11)-5.5,z=(i*2.29+t*.85)%17-10;const level=id===2?-.25+q*.55:.22+q*2.5;m.position.set(x,level+.16*Math.sin(x*1.5+t*3)+(.10+q*.13)*Math.sin(z*.9+t*2.1)+.035,z);m.scale.x=.08+.12*(.5+.5*Math.sin(t*2+i));});
 }
 return {animate};
}
