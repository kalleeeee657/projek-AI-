import json,subprocess,pathlib,os
p=pathlib.Path('out/mandalika-scene-1-v5.mp4')
r=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)]))
v=next(s for s in r['streams'] if s['codec_type']=='video')
assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_read_frames']))==(1080,1920,'60/1',360),v
assert abs(float(r['format']['duration'])-6)<.10
assert any(s['codec_type']=='audio' for s in r['streams'])
subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(p),'-f','null','-'],check=True)
t=int(pathlib.Path('out/render-seconds.txt').read_text())
report={'character':'STICKMAN_001','fingerprint':'4f963f7b','engine':'Three.js + Remotion software WebGL swangle','video':r,'render_seconds':t,'v4_total_workflow_seconds':2550,'notes':'V4 total time is not a render-only comparison. V5 workflow elapsed must be read from GitHub. No voice; original ambient sound, manually timed captions. Original Blender model simplified PBR, not identical lighting.'}
pathlib.Path('out/report.json').write_text(json.dumps(report,indent=2))
