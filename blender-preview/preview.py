import bpy, math, random, pathlib, subprocess, json
from mathutils import Vector
from math import sin,cos,pi
R=random.Random(44)
out=pathlib.Path(__file__).resolve().parent/'out'
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
    return m
skin=material('Sage dinosaur skin',(.20,.42,.25),noise=True);belly=material('Cream belly',(.65,.63,.34),noise=True)
dark=material('Deep green',(.09,.24,.15));black=material('Eyes',(.012,.018,.015),.19);ivory=material('Ivory',(.85,.79,.57));white=material('Eye whites',(.96,.9,.73),.3)
sand=material('Warm sand',(.78,.59,.32),noise=True);grass=material('Coastal green',(.30,.48,.12),noise=True);sea=material('Turquoise water',(.025,.44,.57),.26)
wood=material('Palm bark',(.32,.18,.075),noise=True);leaf=material('Palm leaves',(.12,.38,.10));leaf2=material('Light palm leaves',(.29,.55,.12))
road=material('Footpath',(.38,.36,.32));yellow=material('Hoodie',(.95,.53,.035));blue=material('Jeans',(.07,.18,.37));flesh=material('Face',(.61,.35,.19));hair=material('Hair',(.028,.02,.014))
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
box('Sea',(0,17,-.24),(65,15,.1),sea)
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
    for f in range(1,151,5):
        crown.rotation_euler=(.028*sin(f*.06+i),.037*cos(f*.05+i),0);crown.keyframe_insert(data_path='rotation_euler',frame=f)
# Main dinosaur, continuous neck and tail with articulated segments.
root=empty('Brachiosaurus root',(-2.8,0,0))
torso=empty('Body',(0,0,2.6),root)
sphere('Torso',(0,0,0),(1.65,.82,1.06),skin,torso,40)
sphere('Belly',(.08,0,-.48),(1.43,.73,.57),belly,torso,32)
neck=empty('Neck pivot',(.95,0,.45),torso)
tube('Continuous neck',[(0,0,0),(.45,0,.5),(.78,0,1.2),(.97,0,2.0),(1.05,0,2.75),(1.18,0,3.28)],[.56,.50,.38,.28,.22,.25],skin,neck,22,2)
head=empty('Head',(1.18,0,3.28),neck)
sphere('Skull',(.16,0,.07),(.52,.31,.30),skin,head,32)
sphere('Muzzle',(.43,0,-.04),(.36,.29,.18),belly,head)
jaw=empty('Jaw',(.10,0,-.16),head);sphere('Lower jaw',(.26,0,0),(.39,.26,.09),skin,jaw)
for side in [-1,1]:
    sphere('Eye white',(.13,side*.272,.14),(.135,.065,.125),white,head)
    sphere('Pupil',(.16,side*.32,.14),(.068,.035,.085),black,head)
    sphere('Eye glint',(.18,side*.35,.17),(.023,.012,.024),white,head,12)
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
# Human scale reference wearing signature yellow hoodie.
hero=empty('Hero',(-.8,-2.45,0))
sphere('Hoodie torso',(0,0,.99),(.24,.17,.34),yellow,hero)
sphere('Hood',(0,.12,1.25),(.19,.12,.15),yellow,hero)
sphere('Face',(0,0,1.51),(.21,.19,.24),flesh,hero)
sphere('Hair',(0,0,1.65),(.22,.2,.12),hair,hero)
for a in [-1,1]:
    sphere('Jeans leg',(a*.105,0,.45),(.095,.1,.39),blue,hero)
    sphere('Sneaker',(a*.105,-.06,.11),(.11,.17,.085),white,hero)
    arm=sphere('Sleeve',(a*.27,0,1.0),(.08,.08,.27),yellow,hero);arm.rotation_euler.y=a*.22
    sphere('Hand',(a*.32,0,.76),(.075,.07,.09),flesh,hero)
    sphere('Eye',(a*.075,-.169,1.55),(.043,.029,.049),white,hero)
    sphere('Pupil',(a*.075,-.191,1.55),(.021,.012,.026),black,hero)
hero.rotation_euler.z=-.45
# Wind-driven surf, sparse vegetation, landmark sign.
for i in range(30):
    x=R.uniform(-20,20);y=R.uniform(3.8,5.1)
    for k in range(3):
        o=sphere('Grass tuft',(x+k*.06,y,.11),(.035,.035,.17),leaf2,seg=10);o.rotation_euler.y=(k-1)*.35
for i in range(5):box('Surf foam',(0,6.1+i*.38,-.075+i*.005),(24,.035,.015),white)
box('Sign base',(5,3,.35),(2.3,.24,.35),road)
bpy.ops.object.text_add(location=(5,2.73,.70),rotation=(pi/2,0,0))
sign=bpy.context.object;sign.data.body='MANDALIKA';sign.data.align_x='CENTER';sign.data.size=.47;sign.data.extrude=.045;sign.data.materials.append(white)
for f in range(1,151):
    t=(f-1)/30;phase=t*2*pi/2.0;speed=.78;root.location.x=-2.8+speed*t;root.keyframe_insert(data_path='location',frame=f)
    torso.location.z=2.6+.045*cos(phase*2);torso.rotation_euler=(.026*sin(phase),.025*cos(phase),0)
    torso.keyframe_insert(data_path='location',frame=f);torso.keyframe_insert(data_path='rotation_euler',frame=f)
    neck.rotation_euler=(.034*sin(phase-.7),.047*sin(phase-1),.065*sin(phase-.6));neck.keyframe_insert(data_path='rotation_euler',frame=f)
    head.rotation_euler.y=.05*sin(phase-1.3);head.keyframe_insert(data_path='rotation_euler',frame=f)
    jaw.rotation_euler.y=.035*(1+sin(t*4));jaw.keyframe_insert(data_path='rotation_euler',frame=f)
    tail.rotation_euler.z=.15*sin(phase-.8);tail.keyframe_insert(data_path='rotation_euler',frame=f)
    for x,side,hip,knee,foot in legs:
        ph=(t/2+(0 if x*side>0 else .5)+(0.1 if x>0 else 0))%1
        # Stance travels backward at root speed, swing returns smoothly.
        step=1.56*.65
        if ph<.65:dx=step/2-step*ph/.65;lift=0
        else:
            u=(ph-.65)/.35;q=u*u*(3-2*u);dx=-step/2+step*q;lift=.28*sin(pi*u)**2
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
# Lighting, camera.
bpy.ops.object.light_add(type='SUN',location=(-5,-7,10))
sun=bpy.context.object;sun.data.energy=2.4;sun.data.angle=.15;sun.rotation_euler=(.48,-.38,-.52)
bpy.ops.object.light_add(type='AREA',location=(1,-5,8))
fill=bpy.context.object;fill.data.energy=1500;fill.data.shape='DISK';fill.data.size=8;fill.rotation_euler=(Vector((0,0,3))-fill.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.lens=42
for f in range(1,151):
    t=(f-1)/30;cam.location=(7.5+.47*t,-15+.26*t,5.2+.08*t);target=Vector((-.3+.60*t,0,3.2));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.keyframe_insert(data_path='location',frame=f);cam.keyframe_insert(data_path='rotation_euler',frame=f)
s=bpy.context.scene;s.camera=cam;s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.40,.65,.86,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=12;s.cycles.use_denoising=False;s.cycles.max_bounces=4
s.render.resolution_x=540;s.render.resolution_y=960;s.render.resolution_percentage=100;s.render.fps=30;s.frame_start=1;s.frame_end=150
s.render.image_settings.file_format='PNG';s.render.filepath=str(out/'frame-');s.frame_set(75)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'mandalika-preview.blend'))
s.render.filepath=str(out/'still.png');bpy.ops.render.render(write_still=True)
s.render.resolution_percentage=67;s.render.filepath=str(out/'frame-')
bpy.ops.render.render(animation=True)
subprocess.run(['ffmpeg','-v','error','-y','-framerate','30','-i',str(out/'frame-%04d.png'),'-vf','scale=540:960:flags=lanczos','-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart',str(out/'mandalika-dinosaur-preview.mp4')],check=True)
for p in out.glob('frame-*.png'):p.unlink()
report=subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(out/'mandalika-dinosaur-preview.mp4')])
(out/'report.json').write_bytes(report)
