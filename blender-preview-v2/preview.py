import bpy, math, random, pathlib, subprocess, json, os
from mathutils.kdtree import KDTree
from mathutils import Vector
from math import sin,cos,pi
R=random.Random(44)
ROOT=pathlib.Path(__file__).resolve().parent
out=ROOT/'out'
out.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def material(name,c,rough=.75,noise=False):
    m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
    n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough
    if noise:
        tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=32;tex.inputs['Detail'].default_value=2
        bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.19;bump.inputs['Distance'].default_value=.055
        l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal'])
        tc=n.new('ShaderNodeTexCoord')
        macro=n.new('ShaderNodeTexNoise');macro.inputs['Scale'].default_value=4.5;macro.inputs['Detail'].default_value=5
        l.new(tc.outputs['Object'],macro.inputs['Vector'])
        ramp=n.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[0].color=(*[max(0,k*.48) for k in c],1)
        ramp.color_ramp.elements[1].position=.83;ramp.color_ramp.elements[1].color=(*[min(1,k*1.42) for k in c],1)
        l.new(macro.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
    return m
skin=material('Sage dinosaur skin',(.19,.29,.125),noise=True);belly=material('Cream belly',(.42,.39,.20),noise=True)
dark=material('Deep green',(.09,.24,.15));black=material('Eyes',(.012,.018,.015),.19);ivory=material('Ivory',(.85,.79,.57));white=material('Eye whites',(.96,.9,.73),.3)
sand=material('Warm sand',(.78,.59,.32),noise=True);grass=material('Coastal green',(.30,.48,.12),noise=True);sea=material('Turquoise water',(.025,.44,.57),.26)
wood=material('Palm bark',(.32,.18,.075),noise=True);leaf=material('Palm leaves',(.12,.38,.10));leaf2=material('Light palm leaves',(.29,.55,.12))
road=material('Footpath',(.38,.36,.32));yellow=material('Hoodie',(.95,.53,.035));blue=material('Jeans',(.07,.18,.37));flesh=material('Face',(.61,.35,.19));hair=material('Hair',(.028,.02,.014))
# Layered procedural PBR scales with color and wrinkle micro-normal.
n=skin.node_tree.nodes;l=skin.node_tree.links;p=n.get('Principled BSDF')
tc=n.new('ShaderNodeTexCoord');sc=n.new('ShaderNodeTexVoronoi');sc.feature='DISTANCE_TO_EDGE';sc.inputs['Scale'].default_value=42
l.new(tc.outputs['Object'],sc.inputs['Vector'])
ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.025;ramp.color_ramp.elements[0].color=(.08,.08,.08,1);ramp.color_ramp.elements[1].position=.15;ramp.color_ramp.elements[1].color=(.8,.8,.8,1)
l.new(sc.outputs['Distance'],ramp.inputs[0])
fine=n.new('ShaderNodeBump');fine.inputs['Distance'].default_value=.018;fine.inputs['Strength'].default_value=.36;l.new(ramp.outputs[0],fine.inputs['Height'])
old=next((q for q in n if q.type=='BUMP' and q!=fine),None)
if old:l.new(old.outputs['Normal'],fine.inputs['Normal'])
l.new(fine.outputs['Normal'],p.inputs['Normal']);p.inputs['Roughness'].default_value=.58
p.inputs['Subsurface Weight'].default_value=.035
def sphere(name,loc,scale,m,parent=None,seg=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=16)
    o=bpy.context.object;o.name=name;o.parent=parent;o.location=loc;o.scale=scale;o.data.materials.append(m)
    for p in o.data.polygons:p.use_smooth=True
    return o
def empty(name,loc,parent=None):
    o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.parent=parent;o.location=loc;return o
def tube(name,points,radii,mat,parent=None,sides=14,sub=1):
    # Continuous tapered mesh with smooth curved silhouette.
    pts=[Vector(p) for p in points];verts=[];faces=[]
    for j,p in enumerate(pts):
        t=(pts[min(j+1,len(pts)-1)]-pts[max(0,j-1)]).normalized()
        a=t.cross(Vector((0,1,0))).normalized()
        if a.length<.01:a=t.cross(Vector((1,0,0))).normalized()
        b=t.cross(a).normalized()
        for i in range(sides):
            th=2*pi*i/sides;verts.append(p+radii[j]*(cos(th)*a+sin(th)*b))
    for j in range(len(pts)-1):
        for i in range(sides):
            a=j*sides+i;b=j*sides+(i+1)%sides;faces.append((a,b,b+sides,a+sides))
    faces.extend([tuple(reversed(range(sides))),tuple((len(pts)-1)*sides+i for i in range(sides))])
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.parent=parent;o.data.materials.append(mat)
    for f in me.polygons:f.use_smooth=True
    if sub:mod=o.modifiers.new('Smooth surface','SUBSURF');mod.levels=sub;mod.render_levels=sub
    return o
def box(name,loc,scale,m):
    bpy.ops.mesh.primitive_cube_add(size=2,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(m);return o
box('Beach',(0,0,-.16),(24,6,.16),sand)
# Water surface with animated ripples, physically-based reflections.
bpy.ops.mesh.primitive_grid_add(x_subdivisions=90,y_subdivisions=60,size=2,location=(0,17,-.11))
water=bpy.context.object;water.name='Mandalika sea';water.scale=(55,15,1);water.data.materials.append(sea)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
for poly in water.data.polygons:poly.use_smooth=True
for vert in water.data.vertices:vert.co.z=.028*sin(vert.co.x*1.9+vert.co.y*3.2)+.025*cos(vert.co.y*4)
wn=sea.node_tree.nodes;wl=sea.node_tree.links;wp=wn.get('Principled BSDF')
wp.inputs['Metallic'].default_value=.0;wp.inputs['Roughness'].default_value=.19;wp.inputs['IOR'].default_value=1.333
wp.inputs['Transmission Weight'].default_value=.18
wave=wn.new('ShaderNodeTexNoise');wave.inputs['Scale'].default_value=9;wave.inputs['Detail'].default_value=3
coord=wn.new('ShaderNodeTexCoord');mapping=wn.new('ShaderNodeMapping');wl.new(coord.outputs['Object'],mapping.inputs[0]);wl.new(mapping.outputs[0],wave.inputs[0])
bump=wn.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.30;bump.inputs['Distance'].default_value=.045;wl.new(wave.outputs['Fac'],bump.inputs['Height']);wl.new(bump.outputs[0],wp.inputs['Normal'])
for f in [1,300]:
    mapping.inputs['Location'].default_value=(f*.004,f*.007,0);mapping.inputs['Location'].keyframe_insert(data_path='default_value',frame=f)

box('Promenade',(0,-4.2,.015),(24,1.3,.025),road)
for i in range(9):
    sphere('Coastal hill',(-26+i*6,30+R.random()*5,-1),(7,8,3+R.random()*4),grass)
for i in range(17):
    x=-23+i*2.9;y=5.3+R.uniform(-.2,.2)
    if i in (7,8,9):continue
    h=R.uniform(3.4,5.5);root=empty('Coconut palm',(x,y,0))
    tube('Curved palm trunk',[(0,0,0),(.08,0,h*.3),(.23,0,h*.68),(.38,0,h)], [.18,.15,.12,.09],wood,root)
    crown=empty('Crown',(.38,0,h),root)
    for j in range(8):
        a=j*pi/4+R.uniform(-.12,.12)
        pts=[(0,0,0),(.55*cos(a),.55*sin(a),.36),(1.15*cos(a),1.15*sin(a),.26),(1.75*cos(a),1.75*sin(a),-.35)]
        tube('Palm frond',pts,[.04,.18,.13,.012],leaf if j%2 else leaf2,crown,8)
        for k in range(1,5):
            u=k/5;cx=1.65*u*cos(a);cy=1.65*u*sin(a);z=.33-.6*u*u
            for side in [-1,1]:
                tube('Leaflet',[(cx,cy,z),(cx-side*.29*sin(a),cy+side*.29*cos(a),z-.06),(cx+.22*cos(a)-side*.38*sin(a),cy+.22*sin(a)+side*.38*cos(a),z-.25)],[.055,.065,.006],leaf2 if j%2 else leaf,crown,6,0)
    for j in range(3):sphere('Coconut',(.13*cos(j*2.1),.13*sin(j*2.1),-.12),(.13,.13,.17),wood,crown,12)
    for f in range(1,301,5):
        crown.rotation_euler=(.028*sin(f*.03+i),.037*cos(f*.025+i),0);crown.keyframe_insert(data_path='rotation_euler',frame=f)
# Main dinosaur, continuous neck and tail with articulated segments.
root=empty('Brachiosaurus root',(-2.8,0,0))
torso=empty('Body',(0,0,2.6),root)
sphere('Torso',(0,0,0),(1.75,.83,1.0),skin,torso,40)
sphere('Belly',(.08,0,-.38),(1.43,.73,.61),belly,torso,32)
neck=empty('Neck pivot',(.95,0,.45),torso)
tube('Continuous neck',[(0,0,0),(.45,0,.5),(.78,0,1.2),(.97,0,2.0),(1.05,0,2.75),(1.18,0,3.28)],[.56,.50,.38,.28,.22,.25],skin,neck,22,2)
head=empty('Head',(1.18,0,3.28),neck)
sphere('Skull',(.16,0,.07),(.52,.31,.30),skin,head,32)
sphere('Muzzle',(.43,0,-.04),(.36,.29,.18),belly,head)
jaw=empty('Jaw',(.10,0,-.16),head);sphere('Lower jaw',(.26,0,0),(.39,.26,.09),skin,jaw)
for side in [-1,1]:
    sphere('Eye white',(.13,side*.272,.14),(.077,.042,.075),white,head)
    sphere('Pupil',(.16,side*.303,.14),(.048,.023,.054),black,head)
    sphere('Eye glint',(.18,side*.324,.16),(.013,.008,.014),white,head,12)
    sphere('Nostril',(.61,side*.19,.02),(.044,.028,.035),dark,head,12)
tail=empty('Tail pivot',(-1.25,0,.04),torso)
tube('Tapered tail',[(0,0,0),(-.55,0,-.12),(-1.2,0,-.34),(-1.85,0,-.55),(-2.5,0,-.62),(-3.15,0,-.55)],[.5,.39,.27,.17,.09,.02],skin,tail,18,2)
# World-space foot trajectories, ground contact during stance. Deformable jointed legs.
legs=[]
for x in [-1.0,.95]:
    for side in [-1,1]:
        upper=empty('Hip',(x,side*.51,2.47),root)
        sphere('Thigh',(0,0,-.48),(.37,.34,.74),skin,upper)
        knee=empty('Knee',(0,0,-1.06),upper)
        sphere('Shin',(0,0,-.55),(.245,.23,.72),skin,knee)
        foot=empty('Foot',(0,0,-1.22),knee);sphere('Foot pad',(.13,0,-.055),(.35,.27,.18),skin,foot)
        for k in [-1,0,1]:sphere('Toenail',(.35,k*.14,-.07),(.09,.075,.07),ivory,foot,12)
        legs.append((x,side,upper,knee,foot))
# Build a continuous original dinosaur mesh, then bind it to the articulated
# transform rig. Surface samples from the source pieces seed smooth weights.
bpy.context.view_layer.update()
names={'Torso','Belly','Continuous neck','Skull','Muzzle','Lower jaw','Tapered tail','Thigh','Shin','Foot pad'}
sources=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.split('.')[0] in names]
drivers=list(dict.fromkeys(o.parent for o in sources))
vertices=[];faces=[];samples=[];owner=[]
dg=bpy.context.evaluated_depsgraph_get()
for obj in sources:
    ev=obj.evaluated_get(dg);mesh=ev.to_mesh();start=len(vertices);di=drivers.index(obj.parent)
    for vert in mesh.vertices:
        p=ev.matrix_world@vert.co;vertices.append(tuple(p));samples.append(p.copy());owner.append(di)
    faces.extend(tuple(start+i for i in poly.vertices) for poly in mesh.polygons);ev.to_mesh_clear()
mesh=bpy.data.meshes.new('Unified dinosaur skin');mesh.from_pydata(vertices,[],faces);mesh.update()
unified=bpy.data.objects.new('Brachiosaurus continuous skin',mesh);bpy.context.collection.objects.link(unified);mesh.materials.append(skin)
for obj in sources:bpy.data.objects.remove(obj,do_unlink=True)
bpy.ops.object.select_all(action='DESELECT');unified.select_set(True);bpy.context.view_layer.objects.active=unified
unified.data.remesh_voxel_size=.042
bpy.ops.object.voxel_remesh()
mod=unified.modifiers.new('Anatomy smoothing','SMOOTH');mod.factor=.72;mod.iterations=5
bpy.ops.object.modifier_apply(modifier=mod.name)
for poly in unified.data.polygons:poly.use_smooth=True
tree=KDTree(len(samples))
for i,p in enumerate(samples):tree.insert(p,i)
tree.balance()
armdata=bpy.data.armatures.new('Dinosaur skeletal rig');dino_armature=bpy.data.objects.new('Dinosaur skeletal rig',armdata);bpy.context.collection.objects.link(dino_armature)
bpy.ops.object.select_all(action='DESELECT')
bpy.context.view_layer.objects.active=dino_armature;dino_armature.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
bn=[]
for i,driver in enumerate(drivers):
    bone=armdata.edit_bones.new('Motion_%02d'%i);p=driver.matrix_world.translation.copy();bone.head=p;bone.tail=p+Vector((0,.4,0));bn.append(bone.name)
bpy.ops.object.mode_set(mode='OBJECT')
bpy.context.view_layer.update()
assert dino_armature.type=='ARMATURE' and dino_armature.pose is not None, 'Invalid dinosaur armature'
assert len(bn)==len(drivers)==len(dino_armature.pose.bones) and len(bn)>0, 'Missing rig bones'
rest_drivers=[d.matrix_world.copy() for d in drivers]
rest_bones=[dino_armature.data.bones[b].matrix_local.copy() for b in bn]
rest_driver_inv=[m.inverted() for m in rest_drivers]
rest_bone_inv=[m.inverted() for m in rest_bones]
groups=[unified.vertex_groups.new(name=b) for b in bn]
weights=[]
for v in unified.data.vertices:
    w={}
    for _,index,d in tree.find_n(v.co,16):
        i=owner[index];w[i]=w.get(i,0)+1/(d+.045)**2
    tot=sum(w.values());weights.append({i:x/tot for i,x in w.items()})
adj=[[] for _ in weights]
for e in unified.data.edges:
    a,b=e.vertices;adj[a].append(b);adj[b].append(a)
for _ in range(4):
    new=[]
    for i,w in enumerate(weights):
        v={k:x*.55 for k,x in w.items()}
        for j in adj[i]:
            for k,x in weights[j].items():v[k]=v.get(k,0)+.45*x/max(1,len(adj[i]))
        new.append(v)
    weights=new
for i,w in enumerate(weights):
    top=sorted(w.items(),key=lambda p:p[1],reverse=True)[:4];tot=sum(x for _,x in top)
    for k,x in top:groups[k].add([i],x/tot,'REPLACE')
armmod=unified.modifiers.new('Skin deformation','ARMATURE');armmod.object=dino_armature;armmod.use_deform_preserve_volume=True
sub=unified.modifiers.new('Fine surface','SUBSURF');sub.levels=1;sub.render_levels=1
# Human scale reference wearing signature yellow hoodie.
hero=empty('Hero',(-.8,-2.45,0))
sphere('Hoodie torso',(0,0,.99),(.24,.17,.34),yellow,hero)
sphere('Hood',(0,.12,1.25),(.19,.12,.15),yellow,hero)
sphere('Face',(0,0,1.51),(.21,.19,.24),flesh,hero)
sphere('Hair',(0,0,1.65),(.22,.2,.12),hair,hero)
for a in [-1,1]:
    sphere('Jeans leg',(a*.105,0,.45),(.095,.1,.39),blue,hero)
    sphere('Sneaker',(a*.105,-.06,.11),(.11,.17,.085),white,hero)
    sleeve_mesh=sphere('Sleeve',(a*.27,0,1.0),(.08,.08,.27),yellow,hero);sleeve_mesh.rotation_euler.y=a*.22
    sphere('Hand',(a*.32,0,.76),(.075,.07,.09),flesh,hero)
    sphere('Eye',(a*.075,-.169,1.55),(.043,.029,.049),white,hero)
    sphere('Pupil',(a*.075,-.191,1.55),(.021,.012,.026),black,hero)
hero.rotation_euler.z=-.45
# Wind-driven surf, sparse vegetation, landmark sign.
for i in range(30):
    x=R.uniform(-20,20);y=R.uniform(3.8,5.1)
    for k in range(3):
        o=sphere('Grass tuft',(x+k*.06,y,.11),(.035,.035,.17),leaf2,seg=10);o.rotation_euler.y=(k-1)*.35
for i in range(5):
    pts=[(-24+j*1.2,6.1+i*.42+.09*sin(j*.81+i),-.042) for j in range(41)]
    foam=tube('Soft surf crest',pts,[.025+.012*sin(j*.7)**2 for j in range(41)],white,sides=6,sub=1)
    for f in [1,150,300]:
        foam.location.y=.12*sin(f/60+i);foam.keyframe_insert(data_path='location',frame=f)
rock=material('Coastal stones',(.31,.29,.23),noise=True)
for i in range(45):
    x=R.uniform(-22,22);y=R.uniform(4.2,5.8);a=R.uniform(.06,.3)
    o=sphere('Beach stone',(x,y,a*.25),(a,a*.72,a*.45),rock,seg=12)
    o.rotation_euler.z=R.uniform(0,pi)

box('Sign base',(5,3,.35),(2.3,.24,.35),road)
bpy.ops.object.text_add(location=(5,2.73,.70),rotation=(pi/2,0,0))
sign=bpy.context.object;sign.data.body='MANDALIKA';sign.data.align_x='CENTER';sign.data.size=.47;sign.data.extrude=.045;sign.data.materials.append(white)
for f in range(1,301):
    t=(f-1)/60;phase=t*2*pi/2.0;speed=.78;root.location.x=-2.8+speed*t;root.keyframe_insert(data_path='location',frame=f)
    torso.location.z=2.6+.045*cos(phase*2);torso.rotation_euler=(.026*sin(phase),.025*cos(phase),0)
    torso.keyframe_insert(data_path='location',frame=f);torso.keyframe_insert(data_path='rotation_euler',frame=f)
    neck.rotation_euler=(.034*sin(phase-.7),.047*sin(phase-1),.065*sin(phase-.6));neck.keyframe_insert(data_path='rotation_euler',frame=f)
    head.rotation_euler.y=.05*sin(phase-1.3);head.keyframe_insert(data_path='rotation_euler',frame=f)
    jaw.rotation_euler.y=.035*(1+sin(t*4));jaw.keyframe_insert(data_path='rotation_euler',frame=f)
    tail.rotation_euler.z=.15*sin(phase-.8);tail.keyframe_insert(data_path='rotation_euler',frame=f)
    for x,side,hip,knee,foot in legs:
        ph=(t/2.2 + (0.0 if x<0 and side<0 else .25 if x>0 and side<0 else .5 if x<0 else .75))%1
        # Stance travels backward at root speed, swing returns smoothly.
        step=.78*2.2*.73
        if ph<.73:dx=step/2-step*ph/.73;lift=0
        else:
            u=(ph-.73)/.27;q=u*u*(3-2*u);dx=-step/2+step*q;lift=.20*sin(pi*u)**2
        L1=1.06;L2=1.22
        hip.location.z=2.27+.025*cos(phase*2)
        dy=hip.location.z-.23-lift;dist=min(L1+L2-.002,max(.15,math.hypot(dx,dy)))
        # two-link sagittal IK, downward axis
        a=math.atan2(-dx,dy);b=math.acos(max(-1,min(1,(L1*L1+dist*dist-L2*L2)/(2*L1*dist))))
        c=math.acos(max(-1,min(1,(L1*L1+L2*L2-dist*dist)/(2*L1*L2))))
        hip.rotation_euler.y=a-b;knee.rotation_euler.y=pi-c;foot.rotation_euler.y=-(hip.rotation_euler.y+knee.rotation_euler.y)
        for o in [hip,knee,foot]:o.keyframe_insert(data_path='rotation_euler',frame=f)
        hip.keyframe_insert(data_path='location',frame=f)
    hero.rotation_euler.z=-.45+.06*sin(t*1.1);hero.keyframe_insert(data_path='rotation_euler',frame=f)
# Bake independent bones in rest-relative local space; do not rely on stale pose matrices.
assert dino_armature.type=='ARMATURE' and dino_armature.pose is not None
assert armmod.object==dino_armature
assert all(v.groups for v in unified.data.vertices), 'Unweighted skin vertices'
assert all(abs(sum(g.weight for g in v.groups)-1)<.0001 for v in unified.data.vertices), 'Non-normalized weights'
prev_quat={}
for frame in range(1,301):
    bpy.context.scene.frame_set(frame)
    bpy.context.view_layer.update()
    for i,driver in enumerate(drivers):
        pb=dino_armature.pose.bones[bn[i]]
        pb.rotation_mode='QUATERNION'
        basis=rest_bone_inv[i] @ driver.matrix_world @ rest_driver_inv[i] @ rest_bones[i]
        loc,rot,scale=basis.decompose()
        if i in prev_quat and rot.dot(prev_quat[i])<0:rot.negate()
        prev_quat[i]=rot.copy()
        pb.location=loc;pb.rotation_quaternion=rot;pb.scale=scale
        pb.keyframe_insert(data_path='location',frame=frame)
        pb.keyframe_insert(data_path='rotation_quaternion',frame=frame)
        pb.keyframe_insert(data_path='scale',frame=frame)
# Verify animated skin after baking, on actual evaluated mesh.
checks=[]
for frame in (1,75,150,225,300):
    bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get()
    ev=unified.evaluated_get(dg);me=ev.to_mesh()
    try:
        assert len(me.vertices)>0, 'Empty evaluated mesh'
        points=[ev.matrix_world@v.co for v in me.vertices]
        assert all(math.isfinite(c) for p in points for c in p), 'Nonfinite animated skin'
        lo=[min(p[i] for p in points) for i in range(3)]
        hi=[max(p[i] for p in points) for i in range(3)]
        extent=[hi[i]-lo[i] for i in range(3)]
        assert all(.1<e<20 for e in extent), 'Invalid skin bounds'
        checks.append({'frame':frame,'bounds_min':lo,'bounds_max':hi,'vertices':len(points)})
    finally:ev.to_mesh_clear()
assert abs(checks[-1]['bounds_min'][0]-checks[0]['bounds_min'][0])>1, 'Skin did not follow walking root'
(out/'rig-report.json').write_text(json.dumps({'blender':bpy.app.version_string,'bones':len(bn),'weighted_vertices':len(unified.data.vertices),'checked_frames':checks},indent=2))
print('RIG VALIDATED',len(bn),'bones',flush=True)
# Lighting, camera.
bpy.ops.object.light_add(type='SUN',location=(-5,-7,10))
sun=bpy.context.object;sun.data.energy=2.1;sun.data.angle=.10;sun.rotation_euler=(.48,-.38,-.52)
bpy.ops.object.light_add(type='AREA',location=(1,-5,8))
fill=bpy.context.object;fill.data.energy=1500;fill.data.shape='DISK';fill.data.size=8;fill.rotation_euler=(Vector((0,0,3))-fill.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.lens=48
for f in range(1,301):
    t=(f-1)/60;cam.location=(5.6+.60*t,-17+.12*t,4.5+.06*t);target=Vector((-.6+.68*t,0,3.35));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.keyframe_insert(data_path='location',frame=f);cam.keyframe_insert(data_path='rotation_euler',frame=f)
s=bpy.context.scene;s.camera=cam
s.world.use_nodes=True
wn=s.world.node_tree.nodes;wl=s.world.node_tree.links
bg=wn.get('Background');env=wn.new('ShaderNodeTexEnvironment')
env.image=bpy.data.images.load(str(ROOT/'assets/sky.hdr'));env.image.pack()
wl.new(env.outputs['Color'],bg.inputs['Color']);bg.inputs['Strength'].default_value=.65
s.render.engine='CYCLES';s.cycles.device='CPU'
s.cycles.samples=128;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.09;s.cycles.adaptive_min_samples=12
s.cycles.use_denoising=True;s.cycles.denoiser='OPENIMAGEDENOISE';s.cycles.max_bounces=5
s.render.use_motion_blur=True;s.render.motion_blur_shutter=.35
s.render.resolution_x=1080;s.render.resolution_y=1920;s.render.resolution_percentage=100
s.render.fps=60;s.frame_start=1;s.frame_end=300
s.view_settings.view_transform='AgX'
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB'
s.render.image_settings.compression=25;s.render.filepath='//frames/frame-'
s.frame_set(120)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'mandalika-v2.blend'))
print('V2 scene prepared, 300 native Full HD frames',flush=True)
