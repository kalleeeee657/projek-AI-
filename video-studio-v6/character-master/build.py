import bpy, math, json, pathlib, sys
from mathutils import Vector
from math import sin,cos,pi
OUT=pathlib.Path(sys.argv[sys.argv.index('--')+1]).resolve()
OUT.mkdir(parents=True,exist_ok=True)
def mat(n,c,r=.75):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True
 b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*c,1);b.inputs['Roughness'].default_value=r
 return m
def loft(name,rings,material,rig,weights,seg=48,cap=True):
 # rings: center xyz, transverse x/y radii; closed quad surface with smooth normals
 verts=[];faces=[]
 for x,y,z,rx,ry in rings:
  for j in range(seg):
   a=2*pi*j/seg;verts.append((x+rx*cos(a),y+ry*sin(a),z))
 for i in range(len(rings)-1):
  for j in range(seg):a=i*seg+j;b=i*seg+(j+1)%seg;faces.append((a,b,b+seg,a+seg))
 if cap:faces.extend([tuple(reversed(range(seg))),tuple((len(rings)-1)*seg+j for j in range(seg))])
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
 o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(material)
 for f in me.polygons:f.use_smooth=True
 bind(o,rig,[(i*seg+j,weights[i]) for i in range(len(rings)) for j in range(seg)])
 return o
def bind(o,rig,weights):
 groups={}
 for i,ws in weights:
  for name,w in ws.items():
   if w<=0:continue
   if name not in groups:groups[name]=o.vertex_groups.new(name=name)
   groups[name].add([i],w,'REPLACE')
 mod=o.modifiers.new('Smooth skeletal deformation','ARMATURE');mod.object=rig
 o.parent=rig
def rigid(o,rig,bone,m):
 o.data.materials.append(m)
 for f in o.data.polygons:f.use_smooth=True
 bind(o,rig,[(i,{bone:1}) for i in range(len(o.data.vertices))]);return o
def oval(n,p,s,m,rig,bone):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,location=p)
 o=bpy.context.object;o.name=n;o.scale=s;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);return rigid(o,rig,bone,m)
def strand(n,pts,radii,m,rig,bone,depth=.72):
 # A tapered, curved strand surface along a Catmull-Rom path, no disconnected ball joints.
 from mathutils.geometry import interpolate_bezier
 ps=[Vector(p) for p in pts];vv=[];ff=[];steps=24;seg=12
 for k in range(steps+1):
  u=k/steps*(len(ps)-1);i=min(len(ps)-2,int(u));t=u-i;p0=ps[max(0,i-1)];p1=ps[i];p2=ps[i+1];p3=ps[min(len(ps)-1,i+2)]
  p=.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)
  v=.5*((-p0+p2)+2*(2*p0-5*p1+4*p2-p3)*t+3*(-p0+3*p1-3*p2+p3)*t*t);v.normalize()
  ref=Vector((0,1,0)) if abs(v.y)<.95 else Vector((1,0,0));a=v.cross(ref).normalized();b=v.cross(a).normalized();rr=radii[i]*(1-t)+radii[i+1]*t
  for j in range(seg):th=2*pi*j/seg;vv.append(p+rr*cos(th)*a+rr*depth*sin(th)*b)
 for k in range(steps):
  for j in range(seg):a=k*seg+j;b=k*seg+(j+1)%seg;ff.append((a,b,b+seg,a+seg))
 ff.extend([tuple(reversed(range(seg))),tuple(steps*seg+j for j in range(seg))]);me=bpy.data.meshes.new(n);me.from_pydata(vv,[],ff);me.update();o=bpy.data.objects.new(n,me);bpy.context.collection.objects.link(o);return rigid(o,rig,bone,m)
def make(ami):
 bpy.ops.wm.read_factory_settings(use_empty=True)
 cid='AMI_001' if ami else 'STICKMAN_001'
 skin=mat('Skin',(.59,.32,.19) if ami else (.86,.69,.49),.66);hair=mat('Hair',(.018,.012,.009),.52);hair2=mat('Hair warm highlights',(.034,.024,.018),.59)
 cloth=mat('Charcoal tank' if ami else 'Black cotton',(.06,.065,.075) if ami else (.026,.027,.03),.91)
 jeans=mat('Faded indigo denim',(.075,.15,.235),.95);cuff=mat('Denim cuff',(.16,.25,.34),.92);seam=mat('Denim stitching',(.21,.28,.32),.92)
 white=mat('Canvas sneaker',(.83,.82,.76),.88);rubber=mat('Sole',(.65,.65,.61),.9);ink=mat('Eye pupil',(.012,.008,.006),.48);sclera=mat('Eye white',(.87,.80,.72),.52);iris=mat('Dark brown iris',(.10,.042,.023),.50);lip=mat('Lip',(.37,.13,.10) if ami else (.45,.25,.19),.74)
 # metres, frontal direction is -Y; more adult-like Ami proportions.
 hip=.83 if ami else .69; shoulder=1.31 if ami else 1.11; neck=1.40 if ami else 1.19; hc=1.52 if ami else 1.38; hx=.098 if ami else .193; hy=.087 if ami else .16; hz=.129 if ami else .211
 sx=.157 if ami else .19; lx=.081 if ami else .096; knee=.43 if ami else .35; ankle=.077
 bpy.ops.object.armature_add();rig=bpy.context.object;rig.name=cid+'_Rig';bpy.ops.object.mode_set(mode='EDIT');eb=rig.data.edit_bones;eb.remove(eb[0])
 def bone(n,h,t,parent=None):
  b=eb.new(n);b.head=h;b.tail=t
  if parent:b.parent=eb[parent]
 bone('pelvis',(0,0,hip),(0,0,hip+.12));bone('spine',(0,0,hip+.12),(0,0,shoulder),'pelvis');bone('head',(0,0,neck),(0,0,hc+hz),'spine')
 for s,k in [(-1,'L'),(1,'R')]:
  bone('upper_arm.'+k,(s*sx,0,shoulder),(s*(sx+.085),0,shoulder-.235),'spine')
  bone('forearm.'+k,(s*(sx+.085),0,shoulder-.235),(s*(sx+.12),-.012,shoulder-.465),'upper_arm.'+k)
  bone('hand.'+k,(s*(sx+.12),-.012,shoulder-.465),(s*(sx+.127),-.016,shoulder-.54),'forearm.'+k)
  bone('thigh.'+k,(s*lx,0,hip),(s*lx,0,knee),'pelvis')
  bone('shin.'+k,(s*lx,0,knee),(s*lx,0,ankle),'thigh.'+k)
  bone('foot.'+k,(s*lx,0,ankle),(s*lx,-.11,ankle),'shin.'+k)
 bpy.ops.object.mode_set(mode='OBJECT')
 P={'pelvis':1};S={'spine':1};H={'head':1}
 def torso(name,profile,material):
  rings=[(0,y,z,x,d) for z,x,d,y in profile];ws=[]
  for _,_,z,_,_ in rings:
   t=max(0,min(1,(z-hip-.04)/.18));ws.append({'pelvis':1-t,'spine':t})
  return loft(name,rings,material,rig,ws)
 if ami:
  torso('Upper body skin',[(hip,.127,.08,0),(hip+.1,.11,.073,0),(hip+.24,.129,.084,0),(shoulder-.10,.15,.104,-.01),(shoulder-.025,.148,.075,0),(shoulder+.018,.10,.064,0),(neck,.039,.043,0)],skin)
  top=torso('Tank top tailored mesh',[(hip+.015,.139,.093,0),(hip+.09,.128,.085,0),(hip+.19,.123,.084,0),(shoulder-.14,.149,.105,-.006),(shoulder-.075,.157,.104,-.008),(shoulder-.025,.147,.078,0),(shoulder+.011,.105,.060,0)],cloth)
  # Scoop neckline, taller side straps, separate skin visible beneath.
  for v in top.data.vertices:
   z=v.co.z
   if z>shoulder-.09 and v.co.y<0:
    front=max(0,-v.co.y/max(.001,math.hypot(v.co.x,v.co.y)));v.co.z-=.09*front**4*max(0,min(1,(z-shoulder+.09)/.10))
 else:
  torso('Oversized cotton shirt',[(hip-.04,.175,.10,0),(hip+.015,.19,.105,0),(hip+.14,.183,.104,0),(shoulder-.085,.187,.10,0),(shoulder-.02,.185,.09,0),(shoulder+.025,.12,.075,0),(shoulder+.035,.065,.059,0)],cloth)
  oval('Neck',(0,0,neck-.025),(.06,.055,.077),skin,rig,'spine')
 torso('Denim waist and hips',[(hip-.105,.147 if ami else .18,.095,0),(hip-.045,.163 if ami else .19,.105,0),(hip+.015,.145 if ami else .18,.093,0),(hip+.05,.13 if ami else .177,.091,0)],jeans)
 oval('Waist button',(0,-.10,hip+.022),(.011,.006,.011),seam,rig,'pelvis')
 # Face custom oval/chin/cheek profile; not a sphere.
 profile=[(-1,.18,.33),(-.93,.43,.60),(-.76,.72,.83),(-.48,.91,.96),(-.12,1,1),(.27,.98,.98),(.58,.88,.87),(.83,.65,.66),(.97,.27,.32),(1,.03,.04)]
 loft('Sculpted face',[(0,0,hc+z*hz,hx*w,hy*d) for z,w,d in profile],skin,rig,[H]*len(profile),64)
 for s in [-1,1]:
  oval('Ear',(s*hx*.95,0,hc-.018),(.025 if ami else .033,.021,.042 if ami else .047),skin,rig,'head')
  ex=s*hx*.43;ez=hc+.015;ey=-hy*.89
  if ami:
   oval('Almond eye',(ex,ey,ez),(.033,.013,.017),sclera,rig,'head')
   oval('Iris',(ex,ey-.012,ez),(.014,.006,.014),iris,rig,'head');oval('Pupil',(ex,ey-.017,ez),(.007,.003,.009),ink,rig,'head')
   strand('Upper eyelid',[(ex-.032,ey-.004,ez),(ex,ey-.014,ez+.017),(ex+.032,ey-.004,ez)], [.003,.005,.002],hair,rig,'head')
  else:oval('Black oval eye',(ex,ey-.008,ez),(.027,.014,.041),ink,rig,'head')
  strand('Eyebrow',[(ex-hx*.24,ey+.002,ez+hz*.25),(ex,ey-.005,ez+hz*.29),(ex+hx*.24,ey+.002,ez+hz*.23)],[.003,.006,.002],hair,rig,'head')
 oval('Nose',(0,-hy*.94,hc-hz*.22),(.018 if ami else .022,.022,.026),skin,rig,'head')
 strand('Natural mouth',[(-hx*.31,-hy*.87,hc-hz*.53),(0,-hy*.92,hc-hz*.56),(hx*.31,-hy*.87,hc-hz*.53)],[.002,.006,.002],lip,rig,'head')
 # Hair cap follows skull, front edge lifted to expose face.
 rings=[]
 for i in range(12):
  t=i/11;theta=(pi*.57)*(1-t);rings.append((0,.012,hc+hz*cos(theta)+.018,hx*1.055*sin(theta),hy*1.06*sin(theta)))
 loft('Hair crown',rings,hair,rig,[H]*len(rings),64)
 if ami:
  for s in [-1,1]:
   for j in range(4):
    a=j*.012;strand('Swept hair',[(s*.007,.003,hc+.128),(s*(.058+a*.2),-.069,hc+.102),(s*(.099+a*.12),-.046,hc+.03),(s*(.096-a*.1),-.036,hc-.067)],[.026,.025,.023,.004],hair2 if j==1 else hair,rig,'head')
   strand('Loose face framing hair',[(s*.091,-.036,hc+.06),(s*.105,-.067,hc-.021),(s*.089,-.067,hc-.10)],[.013,.011,.002],hair,rig,'head')
  for j in range(7):
   x=(j-3)*.012;strand('Ponytail sculpted lock',[(x,.07,hc+.055),(x,.15,hc+.045),(x*1.5,.18,hc-.065),(x*1.4,.14,hc-.19)],[.028,.035,.028,.003],hair2 if j in (1,5) else hair,rig,'head')
 else:
  for j in range(15):
   a=j*2.39996;x=cos(a);y=sin(a);strand('Messy sculpted lock',[(x*.07,y*.065,hc+.14),(x*.135,y*.12,hc+.21),(x*.18,y*.155,hc+.22+.037*sin(j)),(x*.21,y*.18,hc+.16+.045*cos(j))],[.044,.049,.035,.003],hair2 if j%5==0 else hair,rig,'head')
  for j in range(5):
   x=(j-2)*.058;strand('Fringe',[(x,-.07,hc+.19),(x+.025,-.14,hc+.14),(x-.012,-.164,hc+.08)],[.04,.035,.003],hair,rig,'head')
 for s,k in [(-1,'L'),(1,'R')]:
  ua='upper_arm.'+k;fa='forearm.'+k;ha='hand.'+k;th='thigh.'+k;sh='shin.'+k;fo='foot.'+k
  # Continuous arm surface, smooth blended elbow weights.
  rs=[];ws=[]
  for t,rx,ry in [(0,.045,.047),(.12,.052,.052),(.28,.044,.045),(.43,.035,.037),(.50,.034,.034),(.57,.039,.037),(.70,.034,.031),(.88,.024,.022),(1,.022,.020)]:
   z=shoulder-.465*t;x=s*(sx+.12*t);a=max(0,min(1,(t-.40)/.20));rs.append((x,-.012*t,z,rx,ry));ws.append({ua:1-a,fa:a})
  loft('Continuous arm '+k,rs,skin,rig,ws)
  if not ami:
   loft('T-shirt sleeve '+k,[(s*(sx+.035),0,shoulder-.15,.074,.071),(s*(sx+.023),0,shoulder-.075,.078,.076),(s*sx,0,shoulder+.03,.059,.064)],cloth,rig,[{ua:1}]*3)
  x=s*(sx+.12);z=shoulder-.465
  oval('Palm '+k,(x,-.015,z-.042),(.037,.022,.048),skin,rig,ha)
  for j in range(4):
   xx=x+(j-1.5)*.014;strand('Finger '+k,[(xx,-.016,z-.063),(xx,-.019,z-.098),(xx,-.026,z-.112+abs(j-1.5)*.005)],[.009,.008,.005],skin,rig,ha)
  strand('Thumb '+k,[(x-s*.026,-.016,z-.034),(x-s*.042,-.025,z-.055),(x-s*.043,-.031,z-.073)],[.012,.010,.006],skin,rig,ha)
  # Continuous leg from ankle to hip, weighted smoothly at knee.
  rs=[];ws=[]
  for z,rx,ry in [(ankle,.029,.033),(ankle+.09,.035,.04),(knee-.11,.052,.056),(knee-.035,.044,.046),(knee,.043,.045),(knee+.045,.051,.05),(hip-.13,.073 if ami else .06,.07),(hip-.025,.079 if ami else .065,.073),(hip,.066,.064)]:
   a=max(0,min(1,(z-knee+.055)/.11));rs.append((s*lx,0,z,rx,ry));ws.append({th:a,sh:1-a})
  loft('Continuous leg '+k,rs,skin,rig,ws)
  hem=hip-(.23 if ami else .25)
  loft('Denim short leg '+k,[(s*lx,0,hem,.079,.074),(s*lx,0,hem+.045,.083,.08),(s*lx,0,hip-.105,.093 if ami else .094,.09),(s*lx,0,hip-.04,.087,.085)],jeans,rig,[{th:1}]*4)
  loft('Rolled cuff '+k,[(s*lx,0,hem-.009,.082,.078),(s*lx,0,hem+.024,.084,.079)],cuff,rig,[{th:1}]*2)
  oval('Sneaker upper '+k,(s*lx,-.045,.060),(.061,.119,.055),white,rig,fo);oval('Sneaker sole '+k,(s*lx,-.05,.022),(.064,.124,.021),rubber,rig,fo)
  for j in range(3):strand('Shoelace '+k,[(s*lx-.036,-.087+j*.025,.094),(s*lx,-.087+j*.025,.105),(s*lx+.036,-.087+j*.025,.094)],[.0025,.003,.0025],white,rig,fo)
 bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.context.scene.objects:o.select_set(True)
 bpy.context.view_layer.objects.active=rig
 path=OUT/(cid+'.glb')
 bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_yup=True,export_animations=False)
 import struct
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);assert g.get('skins') and len(g['skins'][0]['joints'])>=15
 assert any('JOINTS_0' in p['attributes'] and 'WEIGHTS_0' in p['attributes'] for m in g['meshes'] for p in m['primitives'])
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(cid+'.blend')))
 return {'id':cid,'skinCount':len(g['skins']),'jointCount':len(g['skins'][0]['joints']),'meshCount':len(g['meshes']),'bytes':len(raw)}
report=[make(False),make(True)]
(OUT/'asset-report.json').write_text(json.dumps(report,indent=2))
