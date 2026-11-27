import bpy,sys,pathlib,math,os,time,struct
from mathutils import Vector
first,last=map(int,sys.argv[sys.argv.index('--')+1:sys.argv.index('--')+3])
out=pathlib.Path(sys.argv[sys.argv.index('--')+3]).resolve();out.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene
assert bpy.app.version[:3]==(4,5,3)
assert (s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.render.fps)==(1080,1920,100,60)
assert s.render.engine=='CYCLES' and s.cycles.samples==128 and s.cycles.use_denoising and s.render.use_motion_blur
assert abs(s.cycles.adaptive_threshold-.09)<.0001
s.render.use_persistent_data=True
s.render.image_settings.file_format='PNG';s.render.use_file_extension=True
root=bpy.data.objects.get('Brachiosaurus root')
assert root is not None
# New reveal camera; use original rig and evaluate its 300-frame motion over 360 new native frames.
data=bpy.data.cameras.new('Scene 1 Reveal Lens')
cam=bpy.data.objects.new('Scene 1 Reveal Camera',data);s.collection.objects.link(cam);s.camera=cam
def smooth(x):
    x=max(0,min(1,x));return x*x*(3-2*x)
def valid(p):
    try:
        with p.open('rb') as f:h=f.read(24)
        return h[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',h[16:24])==(1080,1920) and p.stat().st_size>1024
    except (OSError,struct.error):return False
for f in range(first,last+1):
    p=out/f'frame-{f:04d}.png'
    if valid(p):continue
    t=(f-1)/60
    source=1+(f-1)*299/359
    s.frame_set(int(source),subframe=source-int(source))
    q=smooth((t-1.65)/2.75)
    x=root.location.x
    cam.location=(x+3.4+1.8*q,-10.8-5.2*q,1.7+1.65*q)
    target=Vector((x+.4+1.0*q,-.25,1.10+2.30*q))
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    data.lens=50-7*q
    bpy.context.view_layer.update()
    tmp=out/f'tmp-{f:04d}.png'
    s.render.filepath=str(tmp);start=time.monotonic()
    result=bpy.ops.render.render(write_still=True)
    assert 'FINISHED' in result and valid(tmp),f'Invalid frame {f}'
    os.replace(tmp,p)
    print('SCENE1_FRAME',f,'seconds',round(time.monotonic()-start,2),flush=True)
