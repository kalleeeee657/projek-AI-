import bpy,sys,pathlib,json,time,os,math
args=sys.argv[sys.argv.index('--')+1:]
mode=args[0];spec=json.loads(args[1]);out=pathlib.Path(args[2]).resolve();out.mkdir(parents=True,exist_ok=True)
s=bpy.context.scene
assert bpy.app.version[:3]==(4,5,3)
assert (s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage,s.render.fps)==(1080,1920,100,60)
assert s.render.fps_base==1 and s.cycles.samples==128 and s.cycles.use_denoising
assert s.cycles.use_adaptive_sampling and s.cycles.adaptive_min_samples==12 and abs(s.cycles.adaptive_threshold-.09)<.0001
assert s.render.use_motion_blur and abs(s.render.motion_blur_shutter-.35)<.0001
assert s.cycles.max_bounces==5 and s.cycles.denoiser=='OPENIMAGEDENOISE'
engine=spec['engine']
if engine=='CYCLES':s.render.engine='CYCLES';s.cycles.device='CPU'
elif engine=='EEVEE':
    options=s.render.bl_rna.properties['engine'].enum_items.keys()
    choice=next((x for x in ('BLENDER_EEVEE_NEXT','BLENDER_EEVEE') if x in options),None)
    if choice:s.render.engine=choice
    else:
        try:s.render.engine='BLENDER_EEVEE_NEXT'
        except TypeError:s.render.engine='BLENDER_EEVEE'
    if hasattr(s,'eevee') and hasattr(s.eevee,'taa_render_samples'):s.eevee.taa_render_samples=128
else:raise ValueError(engine)
s.render.use_persistent_data=True
s.render.threads_mode='AUTO'
s.render.image_settings.file_format='PNG'
s.render.use_file_extension=True
if spec.get('camera')=='detail':
    s.camera.data.lens*=1.12
frames=spec.get('frames') if mode=='benchmark' else range(spec['first'],spec['first']+spec['sec']*60)
timings=[]
for i,f in enumerate(frames):
    s.frame_set(f)
    target=out/f'frame-{i+1:04d}.png'
    tmp=out/f'tmp-{i+1:04d}.png'
    s.render.filepath=str(tmp)
    started=time.monotonic()
    status=bpy.ops.render.render(write_still=True)
    assert 'FINISHED' in status and tmp.stat().st_size>1024
    os.replace(tmp,target)
    timings.append({'source_frame':f,'seconds':round(time.monotonic()-started,3)})
    print('FRAME',f,timings[-1],flush=True)
(out/'timing.json').write_text(json.dumps({'engine':engine,'actual_engine':s.render.engine,'frames':timings},indent=2))
