import * as T from 'three';
export const IDS=Object.freeze(['STICKMAN_001','AMI_001']);
const palette=Object.freeze({
 STICKMAN_001:Object.freeze({skin:0xf5d9b5,hair:0x18161a,shirt:0x222125,denim:0x345c83,shoe:0xf5f1e8,head:[.268,.302,.246],height:1.56}),
 AMI_001:Object.freeze({skin:0xd7a17b,hair:0x211b1b,shirt:0x3b3d42,denim:0x537491,shoe:0xf5f1e8,head:[.205,.268,.195],height:1.72})
});
const mat=(color,roughness=.78)=>new T.MeshStandardMaterial({color,roughness});
const sph=new T.SphereGeometry(1,32,22);
const smooth=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x)};
function group(parent,x=0,y=0,z=0){const o=new T.Group();o.position.set(x,y,z);parent.add(o);return o}
function ell(p,m,x,y,z,sx,sy,sz){const o=new T.Mesh(sph,m);o.position.set(x,y,z);o.scale.set(sx,sy,sz);o.castShadow=true;o.receiveShadow=true;p.add(o);return o}
function tube(p,m,points,radii,depth=1){
 const path=new T.CatmullRomCurve3(points.map(v=>new T.Vector3(...v)));
 const seg=28,rad=16,frames=path.computeFrenetFrames(seg,false),pos=[],uv=[],idx=[];
 for(let i=0;i<=seg;i++){const a=i/seg,pt=path.getPointAt(a),k=a*(radii.length-1),j=Math.min(radii.length-2,Math.floor(k)),rr=T.MathUtils.lerp(radii[j],radii[j+1],k-j);
 for(let h=0;h<=rad;h++){const th=h/rad*Math.PI*2;const v=pt.clone().addScaledVector(frames.normals[i],rr*Math.cos(th)).addScaledVector(frames.binormals[i],rr*depth*Math.sin(th));pos.push(v.x,v.y,v.z);uv.push(h/rad,a);if(i<seg&&h<rad){let b=i*(rad+1)+h;idx.push(b,b+rad+1,b+1,b+1,b+rad+1,b+rad+2)}}}
 const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(pos,3));g.setAttribute('uv',new T.Float32BufferAttribute(uv,2));g.setIndex(idx);g.computeVertexNormals();const o=new T.Mesh(g,m);o.castShadow=true;o.receiveShadow=true;p.add(o);return o
}
function torso(p,m,ami){
 const pts=(ami?[[.14,0],[.145,.05],[.128,.15],[.145,.24],[.185,.34],[.175,.42],[.10,.47],[.068,.49]]:[[.215,0],[.232,.045],[.219,.14],[.222,.30],[.235,.39],[.195,.45],[.087,.49]]).map(([x,y])=>new T.Vector2(x,y));
 const geo=new T.LatheGeometry(pts,48);
 const a=geo.attributes.position;
 if(ami){ // Open curved neckline at front, retain higher shoulder straps.
   for(let i=0;i<a.count;i++){const y=a.getY(i),x=a.getX(i),z=a.getZ(i);
      if(y>.30){const front=Math.max(0,z/Math.max(.001,Math.hypot(x,z)));
       const center=Math.pow(front,6);a.setY(i,y-.115*center*smooth((y-.30)/.19));}
   }geo.computeVertexNormals();
 }
 const o=new T.Mesh(geo,m);o.scale.z=ami?.74:.67;o.castShadow=o.receiveShadow=true;p.add(o);
}
export function createCharacter(id){
 if(!IDS.includes(id))throw Error('Unknown locked character '+id);
 const c=palette[id],ami=id==='AMI_001',root=new T.Group();root.name=id;root.userData.characterId=id;root.userData.designVersion=ami?'1.0.0':'2.0.0-semi3d';
 const skin=mat(c.skin,.79),hair=mat(c.hair,.55),shirt=mat(c.shirt,.89),denim=mat(c.denim,.91),cuff=mat(ami?0x7893a7:0x6583a0),shoe=mat(c.shoe,.78),sole=mat(0xd6d4cf,.92),ink=mat(0x1a1519,.48),iris=mat(0x38231b,.5),white=mat(0xfff6ed,.45);
 const hipY=ami?.81:.70,body=group(root,0,hipY,0);body.name='pelvis';
 ell(body,denim,0,-.035,0,ami?.155:.205,.135,.125);
 const chest=group(body,0,.045,0);chest.name='spine';if(ami)ell(chest,skin,0,.385,0,.175,.145,.114);torso(chest,shirt,ami);
 ell(chest,skin,0,.49,0,.065,.093,.062);
 const head=group(chest,0,.64,0);head.name='head';ell(head,skin,0,0,0,...c.head);
 const [hx,hy,hz]=c.head;
 for(const s of [-1,1])ell(head,skin,s*(hx-.008),-.035,-.003,.044,.067,.034);
 // Consistent dark hair cap and individually curved locks.
 ell(head,hair,0,.092,-.045,hx*1.045,hy*.82,hz*1.04);
 if(ami){
   for(const s of [-1,1]){
     tube(head,hair,[[s*.015,.244,.067],[s*.125,.214,.145],[s*.203,.10,.100],[s*.203,-.06,.033]],[.052,.075,.052,.004]);
     tube(head,hair,[[s*.14,.12,.12],[s*.177,.012,.17],[s*.149,-.115,.108]],[.024,.022,.003]);
   }
 }else{
   for(let i=0;i<11;i++){let a=i*2.39996,x=Math.cos(a),z=Math.sin(a),rr=.065+.017*(i%3);tube(head,hair,[[x*.09,.17,z*.075],[x*.19,.25,z*.14],[x*.27,.27+.055*Math.sin(i*1.7),z*.20],[x*.245,.22+.085*Math.cos(i),z*.22]],[rr,rr*.98,rr*.52,.007]);}
   for(let i=0;i<5;i++){let x=(i-2)*.082;tube(head,hair,[[x,.24,.09],[x+.03,.207,.205],[x-.016,.13-.02*(i%2),.238]],[.057,.05,.003]);}
 }
 const pony=group(head,0,.105,-hz*.84);pony.name='ponytail';
 if(ami){ell(pony,hair,0,0,-.04,.102,.115,.09);for(let i=0;i<5;i++){let x=(i-2)*.025;tube(pony,hair,[[x,.01,-.04],[x*1.5,-.12,-.17],[x*1.4,-.31,-.18],[x*1.8,-.41,-.095]],[.047,.056,.043,.003])}}
 const eyes=[],brows=[];
 for(const s of [-1,1]){
   const x=s*hx*.43,y=.012,z=hz*.91;
   const eye=group(head,x,y,z);eye.name=s<0?'eyeL':'eyeR';
   if(ami){ell(eye,white,0,0,0,.055,.033,.018);ell(eye,iris,0,0,.016,.025,.028,.014);ell(eye,ink,0,0,.026,.013,.020,.006);ell(eye,white,-.008,.009,.031,.006,.006,.003);}
   else{ell(eye,ink,0,0,.011,.036,.058,.022);ell(eye,white,-.010,.018,.030,.008,.010,.003);}
   eyes.push(eye);
   const brow=group(head,x,.100,z-.005);tube(brow,hair,[[-.043,0,0],[0,.009,.006],[.043,0,0]],[.009,.011,.005]);brows.push(brow);
 }
 ell(head,skin,0,-.062,hz*.93,ami?.034:.027,ami?.039:.027,.029);
 const mouth=group(head,0,-.127,hz*.86);mouth.name='mouth';
 const opening=ell(mouth,ink,0,0,.004,.041,.012,.013);
 const lip=mat(ami?0xb36958:0xbc8b75,.8);
 const smile=tube(mouth,lip,[[-.043,.008,0],[0,-.009,.013],[.043,.008,0]],[.006,.009,.005]);smile.position.z=.008;
 const arms=[],legs=[];
 for(const s of [-1,1]){
   const shoulder=group(chest,s*(ami?.176:.228),.39,0);shoulder.name=s<0?'shoulderL':'shoulderR';
   const a=ami?.235:.207,b=ami?.232:.192;
   ell(shoulder,skin,0,-a*.43,0,ami?.050:.059,a*.68,.057);
   if(!ami)ell(shoulder,shirt,0,-.075,0,.086,.129,.087);
   const elbow=group(shoulder,0,-a,0);elbow.name=s<0?'elbowL':'elbowR';
   ell(elbow,skin,0,-b*.46,0,.045,b*.67,.046);ell(elbow,skin,0,-b-.022,.012,.052,.071,.033);
   ell(elbow,skin,-s*.041,-b-.004,.024,.018,.032,.02);
   arms.push({shoulder,elbow,s});
   const hip=group(body,s*(ami?.084:.108),-.026,0);hip.name=s<0?'hipL':'hipR';
   const l1=ami?.345:.292,l2=ami?.354:.302,rad=ami?.083:.092;
   ell(hip,denim,0,-l1*.43,0,rad,l1*.62,rad*.96);
   ell(hip,cuff,0,-l1*.83,0,rad*1.045,.046,rad*.99);
   const knee=group(hip,0,-l1,0);knee.name=s<0?'kneeL':'kneeR';
   ell(knee,skin,0,-l2*.46,0,ami?.050:.047,l2*.65,.053);
   const ankle=group(knee,0,-l2,0);ankle.name=s<0?'ankleL':'ankleR';
   ell(ankle,shoe,0,-.007,.055,.079,.072,.135);
   ell(ankle,sole,0,-.047,.063,.083,.026,.139);
   for(let i=0;i<3;i++)tube(ankle,white,[[-.037,.043,.02+i*.027],[.037,.044,.02+i*.027]],[.004,.004]);
   legs.push({hip,knee,ankle,s,l1,l2});
 }
 const floor=hipY-.026-legs[0].l1-legs[0].l2-.073;
 root.position.y=-floor;
 const phone=group(arms[1].elbow,0,-(ami?.232:.192)-.018,.075);phone.visible=false;
 if(ami){const box=new T.Mesh(new T.BoxGeometry(.074,.126,.013),mat(0x42434b));phone.add(box);const screen=new T.Mesh(new T.PlaneGeometry(.063,.112),mat(0x233847,.35));screen.position.z=.007;phone.add(screen)}
 function pose({frame=0,fps=60,motion='idle',expression='happy',reaction=0,lookYaw=0}={}){
  if(!['idle','walk','wave','surprised','talk','phone'].includes(motion)||!['happy','neutral','surprised','sad'].includes(expression))throw Error('Unsupported pose');
  if(motion==='phone'&&!ami)throw Error('Phone is Ami optional prop');
  const t=frame/fps,w=motion==='walk',p=t*6.6,amp=w?.34:0;
  reaction=Math.max(0,Math.min(1,reaction));body.position.y=hipY+(w?.013*Math.abs(Math.sin(p)):0);
  chest.rotation.set(.018*Math.sin(t*2),w?.045*Math.sin(p):0,0);
  head.rotation.set(-.36*reaction+(motion==='phone'?.16:.025*Math.sin(t*1.8)),lookYaw+.035*Math.sin(t*1.4),.024*Math.sin(t*1.1));
  pony.rotation.x=.11*Math.sin(t*(w?6:2));
  for(const a of arms){a.shoulder.rotation.set(a.s*amp*Math.sin(p),0,a.s*(.13+.14*reaction));a.elbow.rotation.set(-.12-.38*reaction,0,0);if(motion==='wave'&&a.s===1){a.shoulder.rotation.z=2.28;a.elbow.rotation.z=.65+.25*Math.sin(t*8)}if(motion==='phone'&&a.s===1){a.shoulder.rotation.x=-.72;a.elbow.rotation.x=-1.14}}
  for(const l of legs){l.hip.rotation.x=l.s*amp*Math.sin(p);l.knee.rotation.x=w?Math.max(0,-l.s*Math.cos(p))*.35:0;l.ankle.rotation.x=-l.hip.rotation.x-l.knee.rotation.x}
  const blink=t%4.1>3.96?.06:1;eyes.forEach(e=>e.scale.y=blink*(expression==='surprised'?1.18:1));
  brows.forEach((b,i)=>{b.position.y=expression==='surprised'?.125:.100;b.rotation.z=expression==='sad'?(i===0?.26:-.26):0});
  opening.scale.y=expression==='surprised'?.015+.029*reaction:motion==='talk'?.012+.021*Math.abs(Math.sin(t*13)):.012;
  opening.visible=expression==='surprised'||motion==='talk';smile.visible=!opening.visible;phone.visible=motion==='phone';
 }
 pose();return {root,pose,identity:root.userData.characterId,baseY:-floor};
}
