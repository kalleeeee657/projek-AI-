import * as T from 'three';
export const seed=n=>{let x=Math.sin(n*127.1+311.7)*43758.5453;return x-Math.floor(x)};
const colors=[0x6f5050,0x384e64,0x9a7041,0x526858,0x686070,0x495260,0xa88b69];
const skins=[0xbd8965,0x9f704e,0xd9a781,0xe2b796,0x855b42];
const sphere=new T.SphereGeometry(1,12,9), cyl=new T.CylinderGeometry(1,1,1,10),box=new T.BoxGeometry(1,1,1);
const mats=new Map();function material(c){if(!mats.has(c))mats.set(c,new T.MeshStandardMaterial({color:c,roughness:.87}));return mats.get(c)}
function mesh(p,g,c,x,y,z,sx,sy,sz){const m=new T.Mesh(g,material(c));m.position.set(x,y,z);m.scale.set(sx,sy,sz);p.add(m);return m}
function joint(p,x,y,z){const g=new T.Group();g.position.set(x,y,z);p.add(g);return g}
export function createNPC(i,role){
 const root=new T.Group(),skin=skins[i%skins.length],coat=colors[(i*3)%colors.length],hair=i%7===0?0x77736e:0x242125;
 const h=role==='child'?.72:.91+seed(i+19)*.18,w=.9+seed(i+27)*.22;
 root.scale.set(w,h,w);root.name='NPC-'+i;root.userData.role=role;
 const body=joint(root,0,.79,0);
 mesh(body,sphere,coat,0,.21,0,.225,.32,.145);
 mesh(body,cyl,0x3e4145,0,.015,0,.17,.10,.12);
 const head=joint(body,0,.64,0);
 mesh(head,sphere,skin,0,0,0,.163,.205,.145);
 mesh(head,sphere,hair,0,.08,-.027,.169,.14,.15);
 for(const s of [-1,1]){mesh(head,sphere,skin,s*.158,-.01,0,.027,.045,.028);mesh(head,sphere,0x282222,s*.061,.015,.135,.015,.025,.012)}
 mesh(head,sphere,skin,0,-.025,.14,.025,.034,.029);
 mesh(head,sphere,0x603e37,0,-.086,.132,.039,.009,.011);
 if(role==='elder'){mesh(head,cyl,0x67543a,0,.145,0,.176,.075,.158);mesh(head,box,0x9c7448,-.12,.17,0,.12,.11,.12);}
 if(role==='farmer'){mesh(head,cyl,0x96764c,0,.14,0,.25,.035,.25);mesh(head,sphere,0xab8c5e,0,.18,0,.16,.09,.16)}
 if(role==='tourist'){mesh(body,box,0x5d4436,0,.2,-.17,.27,.37,.14)}
 const legs=[],arms=[];
 for(const s of [-1,1]){
  const leg=joint(root,s*.102,.78,0);mesh(leg,cyl,0x42484e,0,-.185,0,.08,.37,.08);
  const knee=joint(leg,0,-.37,0);mesh(knee,cyl,0x42484e,0,-.16,0,.066,.34,.068);
  const ankle=joint(knee,0,-.34,0);mesh(ankle,sphere,0x363130,0,-.025,.05,.086,.06,.13);legs.push({leg,knee,ankle,s});
  const shoulder=joint(body,s*.228,.38,0);mesh(shoulder,cyl,coat,0,-.118,0,.065,.24,.07);
  const elbow=joint(shoulder,0,-.24,0);mesh(elbow,cyl,coat,0,-.10,0,.055,.20,.058);mesh(elbow,sphere,skin,0,-.22,.008,.052,.066,.04);arms.push({shoulder,elbow,s});
 }
 function pose(t,behavior){const ph=t*5.4+i*1.71,walk=behavior==='walk',cold=behavior==='cold',look=behavior==='look';
  body.rotation.z=cold?.018*Math.sin(t*23+i):.02*Math.sin(ph);head.rotation.x=look?-.21:0;head.rotation.y=.18*Math.sin(t*1.2+i);
  for(const a of arms){a.shoulder.rotation.set(walk?a.s*.25*Math.sin(ph):cold?-.7:look&&a.s===1?-1.1:0,0,a.s*.12);a.elbow.rotation.x=cold?-1.1:look&&a.s===1?-1.0:-.16}
  for(const l of legs){l.leg.rotation.x=walk?l.s*.22*Math.sin(ph):0;l.knee.rotation.x=walk?Math.max(0,-l.s*Math.cos(ph))*.35:0;l.ankle.rotation.x=-l.leg.rotation.x-l.knee.rotation.x}
 }
 return {root,pose,role};
}
export function populate(scene,count,seedOffset=0){const roles=['elder','local','tourist','child','farmer','local'];const people=[];
 for(let i=0;i<count;i++){const n=i+seedOffset,person=createNPC(n,roles[i%roles.length]);const row=Math.floor(i/6),col=i%6;const x=(col-2.5)*1.55+(seed(n+111)-.5)*.24,z=-1.3-row*2.05+(seed(n+91)-.5)*.35;person.root.position.set(x,0,z);scene.add(person.root);people.push({...person,x,z,n,behavior:i%3===0?'walk':i%3===1?'cold':'look'})}
 return {people,draw(t){for(const p of people){const walk=p.behavior==='walk',d=walk?.45*Math.sin(t*.65+p.n):0;p.root.position.x=p.x+d;p.root.rotation.y=walk?(Math.cos(t*.65+p.n)>0?Math.PI/2:-Math.PI/2):.22*Math.sin(t*.6+p.n);p.pose(t,p.behavior)}}};
}
