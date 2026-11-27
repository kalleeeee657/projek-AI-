import json,pathlib,subprocess,math
root=pathlib.Path(__file__).resolve().parent
p=json.loads((root/'project.json').read_text())
scenes=p['scenes'];duration=sum(s['sec'] for s in scenes)
out=pathlib.Path('final');out.mkdir(exist_ok=True)
def run(a):subprocess.run(a,check=True)
def ts(v):
    ms=round(v*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'
timing=json.loads(pathlib.Path('audio/subtitle-timing.json').read_text())
assert len(timing)==len(scenes)
lines=[];offset=0
for scene,words in zip(scenes,timing):
    assert len(words)==len(scene['line'].split())
    for i in range(0,len(words),4):
        group=words[i:i+4];start=offset+max(0,group[0]['start']);end=offset+min(scene['sec'],group[-1]['end'])
        if end<=start:continue
        lines.extend([str(len(lines)//4+1),ts(start)+' --> '+ts(end),' '.join(w['text'] for w in group),''])
    offset+=scene['sec']
(out/'subtitles.srt').write_text('\n'.join(lines),encoding='utf-8')
pathlib.Path('scenes/list.txt').write_text(''.join(f"file 'scene-{i}.mkv'\n" for i in range(len(scenes))))
run(['ffmpeg','-v','error','-xerror','-y','-f','concat','-safe','0','-i','scenes/list.txt','-i','audio/mix.mp3','-vf',"subtitles=final/subtitles.srt:force_style='FontName=DejaVu Sans,FontSize=15,Bold=1,Outline=2,Shadow=1,Alignment=2,MarginV=28'",'-map','0:v','-map','1:a','-frames:v',str(duration*60),'-r','60','-c:v','libx264','-preset','fast','-crf','16','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t',str(duration),'-movflags','+faststart',str(out/'studio-v4.mp4')])
r=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out/'studio-v4.mp4')]))
v=next(s for s in r['streams'] if s['codec_type']=='video')
assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1080,1920,'60/1',duration*60)
assert abs(float(r['format']['duration'])-duration)<.15 and any(s['codec_type']=='audio' for s in r['streams'])
run(['ffmpeg','-v','error','-xerror','-i',str(out/'studio-v4.mp4'),'-f','null','-'])
(out/'report.json').write_text(json.dumps(r,indent=2))
