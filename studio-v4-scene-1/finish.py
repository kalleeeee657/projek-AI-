import pathlib,subprocess,math,wave,array,random,json
out=pathlib.Path('final');out.mkdir(exist_ok=True)
def run(args):subprocess.run(args,check=True)
# Original, nonlicensed synthetic coast ambience and gentle low cinematic pulses.
sr=44100;r=random.Random(29);buf=array.array('h');low=0
for n in range(sr*6):
    t=n/sr;low=.97*low+.03*r.uniform(-1,1)
    sea=.13*low*(.65+.35*math.sin(2*math.pi*.3*t))
    fade=min(1,t/.3,(6-t)/.35)
    bed=.035*math.sin(2*math.pi*110*t)+.022*math.sin(2*math.pi*164.81*t)
    foot=0
    for k in (1.25,2.7,4.15,5.5):
        dt=t-k
        if 0<=dt<.6:foot+=.12*math.sin(2*math.pi*42*dt)*math.exp(-8*dt)
    value=(sea+bed+foot)*max(0,fade)
    buf.append(int(max(-1,min(1,value))*32767))
with wave.open(str(out/'ambience.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(buf.tobytes())
srt='''1
00:00:00,250 --> 00:00:02,000
Bayangkan kamu lagi santai

2
00:00:02,000 --> 00:00:03,550
di Mandalika... lalu tiba-tiba,

3
00:00:03,550 --> 00:00:04,850
yang muncul di depanmu

4
00:00:04,850 --> 00:00:06,000
adalah dinosaurus raksasa!
'''
(out/'scene-1.srt').write_text(srt,encoding='utf-8')
pathlib.Path('parts/list.txt').write_text(''.join(f"file 'part-{i:02}.mkv'\n" for i in range(15)))
run(['ffmpeg','-v','error','-xerror','-y','-f','concat','-safe','0','-i','parts/list.txt','-i',str(out/'ambience.wav'),'-vf',"subtitles=final/scene-1.srt:force_style='FontName=DejaVu Sans,FontSize=15,Bold=1,Outline=2,Shadow=1,Alignment=2,MarginV=28'",'-map','0:v','-map','1:a','-c:v','libx264','-preset','fast','-crf','16','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-frames:v','360','-t','6','-movflags','+faststart',str(out/'mandalika-scene-1-v4.mp4')])
report=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out/'mandalika-scene-1-v4.mp4')]))
v=next(s for s in report['streams'] if s['codec_type']=='video')
assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1080,1920,'60/1',360),v
assert abs(float(report['format']['duration'])-6)<.05
assert any(s['codec_type']=='audio' for s in report['streams'])
run(['ffmpeg','-v','error','-xerror','-i',str(out/'mandalika-scene-1-v4.mp4'),'-f','null','-'])
(out/'report.json').write_text(json.dumps(report,indent=2))
