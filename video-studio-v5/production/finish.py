import argparse,json,pathlib,subprocess,shutil
R=pathlib.Path(__file__).resolve().parent
def run(*a):subprocess.run(a,check=True)
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)]))
def check(p,n,audio=False):
    j=probe(p);v=next(s for s in j['streams'] if s['codec_type']=='video')
    assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_read_frames']))==(1080,1920,'60/1',n),v
    if audio:assert any(s['codec_type']=='audio' for s in j['streams'])
    assert abs(float(j['format']['duration'])-n/60)<.15
    return j
def main():
    a=argparse.ArgumentParser();a.add_argument('--mode',choices=['preview','full'],required=True);opt=a.parse_args()
    p=json.loads((R/'project.json').read_text());scenes=p['scenes'] if opt.mode=='full' else p['scenes'][:2]
    out=R/'final';out.mkdir(exist_ok=True);audio=R/'audio-out';lines=[];count=0
    for s in scenes:
        clip=R/'parts'/('scene-'+s['id'])/'scene.mp4';n=s['seconds']*60;check(clip,n);count+=n;lines.append("file '"+str(clip)+"'")
    (out/'concat.txt').write_text('\n'.join(lines)+'\n')
    run('ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(out/'concat.txt'),'-c','copy',str(out/'visual.mp4'))
    # Re-encode once to burn subtitle track; audio mixed separately.
    shutil.copy(audio/'subtitles.srt',out/'subtitles.srt')
    shutil.copy(audio/'audio-report.json',out/'audio-report.json')
    shutil.copy(R/'project.json',out/'project.json')
    dest=out/('mandalika-v5-full.mp4' if opt.mode=='full' else 'mandalika-v5-preview.mp4')
    run('ffmpeg','-v','error','-y','-i',str(out/'visual.mp4'),'-i',str(audio/'mix.wav'),'-vf',f"subtitles={out/'subtitles.srt'}:force_style='FontName=DejaVu Sans,FontSize=22,Outline=2,Shadow=1,Alignment=2,MarginV=52'",'-map','0:v','-map','1:a','-c:v','libx264','-preset','fast','-crf','16','-pix_fmt','yuv420p','-r','60','-c:a','aac','-b:a','160k','-t',str(count/60),str(dest))
    j=check(dest,count,True);run('ffmpeg','-v','error','-xerror','-i',str(dest),'-f','null','-')
    (out/'report.json').write_text(json.dumps({'mode':opt.mode,'scenes':[s['id'] for s in scenes],'frames':count,'audio':json.loads((out/'audio-report.json').read_text())['voice'],'probe':j},indent=2))
    (out/'visual.mp4').unlink();(out/'concat.txt').unlink()
if __name__=='__main__':main()
