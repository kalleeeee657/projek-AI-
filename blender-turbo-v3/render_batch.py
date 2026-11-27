"""Render one checkpoint batch from the immutable V2 scene without changing quality."""
import bpy, pathlib, os, sys, struct, zlib, time
def valid_png(path):
    try:
        with path.open('rb') as f:
            if f.read(8)!=b'\x89PNG\r\n\x1a\n':return False
            first=True; idat=False
            while True:
                head=f.read(8)
                if len(head)!=8:return False
                n,kind=struct.unpack('>I4s',head)
                if n>64*1024*1024:return False
                data=f.read(n);crc=f.read(4)
                if len(data)!=n or len(crc)!=4:return False
                if zlib.crc32(kind+data)&0xffffffff!=struct.unpack('>I',crc)[0]:return False
                if first:
                    if kind!=b'IHDR' or n!=13 or struct.unpack('>II',data[:8])!=(1080,1920):return False
                    first=False
                if kind==b'IDAT':idat=True
                if kind==b'IEND':return n==0 and idat and f.read(1)==b''
    except (OSError,ValueError,struct.error):return False
def main():
    args=sys.argv[sys.argv.index('--')+1:]
    first,last=map(int,args[:2]);out=pathlib.Path(args[2]).resolve()
    assert 1<=first<=last<=300
    out.mkdir(parents=True,exist_ok=True)
    s=bpy.context.scene
    assert bpy.app.version[:3]==(4,5,3),bpy.app.version_string
    assert s.render.engine=='CYCLES' and s.cycles.device=='CPU'
    assert (s.render.resolution_x,s.render.resolution_y,s.render.resolution_percentage)==(1080,1920,100)
    assert s.render.fps==60 and s.render.fps_base==1
    assert s.cycles.samples==128 and s.cycles.use_denoising and s.cycles.denoiser=='OPENIMAGEDENOISE'
    assert s.cycles.use_adaptive_sampling and abs(s.cycles.adaptive_threshold-.09)<.0001
    assert s.cycles.adaptive_min_samples==12 and s.cycles.max_bounces==5
    assert s.render.use_motion_blur and abs(s.render.motion_blur_shutter-.35)<.0001
    assert s.render.image_settings.file_format=='PNG'
    assert s.world and s.world.use_nodes and any(n.type=='TEX_ENVIRONMENT' and n.image and n.image.packed_file for n in s.world.node_tree.nodes)
    s.render.use_persistent_data=True
    s.render.threads_mode='AUTO'
    s.render.use_file_extension=True
    temp=out.parent/('temporary-'+out.name)
    temp.mkdir(exist_ok=True)
    for f in range(first,last+1):
        dest=out/f'frame-{f:04d}.png'
        if valid_png(dest):
            print(f'CHECKPOINT_REUSED {f}',flush=True);continue
        dest.unlink(missing_ok=True)
        tmp=temp/f'frame-{f:04d}.png';tmp.unlink(missing_ok=True)
        s.frame_set(f);s.render.filepath=str(tmp)
        t=time.monotonic()
        result=bpy.ops.render.render(write_still=True)
        assert 'FINISHED' in result and valid_png(tmp),f'Frame {f} incomplete'
        os.replace(tmp,dest)
        print(f'FRAME_COMPLETE {f} seconds={time.monotonic()-t:.2f}',flush=True)
    assert all(valid_png(out/f'frame-{f:04d}.png') for f in range(first,last+1))
if __name__=='__main__':main()
