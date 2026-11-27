import bpy, math, pathlib, json, subprocess
from mathutils import Vector
out=pathlib.Path(__file__).resolve().parent/'out'
out.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
def material(name,c):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*c,1)
    return m
def sphere(name,xyz,scale,m):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=20,location=xyz)
    o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(m)
    for p in o.data.polygons:p.use_smooth=True
    return o
green=material('Jade',(.16,.48,.30)); yellow=material('Sun',(.95,.63,.12));sand=material('Sand',(.70,.52,.31))
bpy.ops.mesh.primitive_plane_add(size=200)
bpy.context.object.data.materials.append(sand)
body=sphere('Motion test', (0,0,1.05),(.8,.6,.85),green)
head=sphere('Head', (0,0,1.85),(.52,.48,.5),yellow)
head.parent=body;head.matrix_parent_inverse=body.matrix_world.inverted()
for f,x,z in [(1,-1,1.05),(15,0,1.35),(30,1,1.05)]:
    body.location=(x,0,z);body.keyframe_insert(data_path='location',frame=f)
for loc,power,size in [((3,-4,7),1700,5),((-4,2,5),1100,4)]:
    bpy.ops.object.light_add(type='AREA',location=loc)
    o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size
    o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(5,-8,4))
cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler()
s=bpy.context.scene;s.camera=cam
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=8;s.cycles.use_denoising=False
s.world.color=(.25,.25,.25)
s.render.resolution_x=360;s.render.resolution_y=640;s.render.resolution_percentage=100
s.render.fps=30;s.frame_start=1;s.frame_end=30
s.render.image_settings.file_format='PNG'
s.frame_set(15);s.render.filepath=str(out/'preview.png')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'test.blend'))
bpy.ops.render.render(write_still=True)
s.render.resolution_percentage=50
s.render.filepath=str(out/'frame-')
bpy.ops.render.render(animation=True)
subprocess.run(['ffmpeg','-v','error','-y','-framerate','30','-i',str(out/'frame-%04d.png'),'-c:v','libx264','-pix_fmt','yuv420p',str(out/'motion.mp4')],check=True)
for p in out.glob('frame-*.png'):p.unlink()
(out/'report.json').write_text(json.dumps({'blender':bpy.app.version_string,'engine':s.render.engine,'frames':30,'fps':30,'purpose':'CPU installation and motion smoke test'},indent=2))
