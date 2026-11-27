import argparse, array, hashlib, importlib.util, json, math, os, pathlib, random, re, subprocess, sys, wave
from difflib import SequenceMatcher
ROOT=pathlib.Path(__file__).resolve().parent
PROJECT=json.loads((ROOT/'project.json').read_text())
def run(*args):subprocess.run(args,check=True)
def duration(p):return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(p)]))
def write(p,samples,sr=44100):
    with wave.open(str(p),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(samples.tobytes())
def norm(s):return re.sub(r'[^\w]','',s.lower())
def align(script,heard,limit):
    words=script.split();sm=SequenceMatcher(None,[norm(w) for w in words],[norm(w['word']) for w in heard],autojunk=False)
    if sm.ratio()<.75:raise RuntimeError('Speech mismatch below 75%; review narration')
    spans=[None]*len(words)
    for tag,a,b,c,d in sm.get_opcodes():
        if tag=='equal':
            for i in range(b-a):spans[a+i]=(heard[c+i]['start'],heard[c+i]['end'])
        elif tag=='replace' and b>a and d>c:
            lo=heard[c]['start'];hi=heard[d-1]['end']
            for i in range(b-a):spans[a+i]=(lo+(hi-lo)*i/(b-a),lo+(hi-lo)*(i+1)/(b-a))
    i=0
    while i<len(spans):
        if spans[i]:i+=1;continue
        j=i
        while j<len(spans) and not spans[j]:j+=1
        lo=spans[i-1][1] if i else 0;hi=spans[j][0] if j<len(spans) else min(limit,heard[-1]['end']+.2)
        hi=max(hi,lo)
        for k in range(i,j):spans[k]=(lo+(hi-lo)*(k-i)/(j-i),lo+(hi-lo)*(k-i+1)/(j-i))
        i=j
    return [{'word':w,'start':round(max(0,min(limit,a)),3),'end':round(max(0,min(limit,b)),3)} for w,(a,b) in zip(words,spans)],round(sm.ratio(),3)
def stamp(t):
    x=round(t*1000);h,x=divmod(x,3600000);m,x=divmod(x,60000);s,ms=divmod(x,1000);return f'{h:02}:{m:02}:{s:02},{ms:03}'
def main():
    a=argparse.ArgumentParser();a.add_argument('--mode',choices=['preview','full'],default='preview');a.add_argument('--voice',choices=['off','gemini'],default='off');opt=a.parse_args()
    scenes=PROJECT['scenes'] if opt.mode=='full' else PROJECT['scenes'][:2]
    out=ROOT/'audio-out';out.mkdir(exist_ok=True);cache=ROOT/'voice-cache';cache.mkdir(exist_ok=True)
    if opt.voice=='gemini':
        spec=importlib.util.spec_from_file_location('studio',ROOT.parent/'google-ai-studio/studio.py');studio=importlib.util.module_from_spec(spec);spec.loader.exec_module(studio);studio.guard()
        import numpy as np
        from faster_whisper import WhisperModel
        model=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=4)
    report=[];srt=[];time=0;index=0;sr=44100;audio_parts=[]
    for k,s in enumerate(scenes):
        sec=s['seconds'];line=s['line'];n=sec*sr
        # Original synthesized ambience and music, deterministic per scene.
        rng=random.Random(428+k);samples=array.array('h');lo=0
        for i in range(n):
            t=i/sr;lo=.97*lo+.03*rng.uniform(-1,1);v=.11*lo*(.7+.3*math.sin(t*2))+.019*math.sin(t*math.tau*(110 if k<8 else 82.41))+.012*math.sin(t*math.tau*164.81)
            for hit in (1.3,3.6):
                dt=t-hit
                if 0<=dt<.55 and s['type'] in ('reveal','scale','road'):v+=.1*math.sin(dt*math.tau*42)*math.exp(-8*dt)
            v*=max(0,min(1,t/.25,(sec-t)/.35));samples.append(int(max(-1,min(1,v))*32767))
        bed=out/f'bed-{k:02}.wav';write(bed,samples)
        mixed=out/f'mix-{k:02}.wav'
        if opt.voice=='gemini':
            raw=cache/(hashlib.sha256(line.encode()).hexdigest()+'.wav');studio.voice(line,raw)
            length=duration(raw);speed=max(1,length/(sec-.18))
            if speed>1.4:raise RuntimeError('Narration too long for scene; shorten script instead of excessive speedup')
            voice=out/f'voice-{k:02}.wav'
            run('ffmpeg','-v','error','-y','-i',str(raw),'-af',f'atempo={speed:.5f},apad','-t',str(sec),'-ar',str(sr),'-ac','1',str(voice))
            clip=out/f'align-{k:02}.wav';run('ffmpeg','-v','error','-y','-i',str(voice),'-ar','16000','-ac','1','-c:a','pcm_s16le',str(clip))
            with wave.open(str(clip),'rb') as w:pcm=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32)/32768
            segments,_=model.transcribe(pcm,language='id',word_timestamps=True,beam_size=5,condition_on_previous_text=False,initial_prompt=line)
            heard=[{'word':w.word.strip(),'start':float(w.start),'end':float(w.end)} for seg in segments for w in (seg.words or []) if w.word.strip() and w.end>w.start]
            if not heard:raise RuntimeError('No speech detected')
            words,ratio=align(line,heard,sec)
            run('ffmpeg','-v','error','-y','-i',str(voice),'-i',str(bed),'-filter_complex','[0:a]asplit=2[v][key];[1:a][key]sidechaincompress=threshold=0.025:ratio=5:attack=25:release=400[b];[v][b]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95','-t',str(sec),'-ar',str(sr),'-ac','1',str(mixed))
        else:
            words=[{'word':w,'start':.2+i*(sec-.4)/len(line.split()),'end':.2+(i+1)*(sec-.4)/len(line.split())} for i,w in enumerate(line.split())];ratio=None;mixed=bed
        for i in range(0,len(words),4):
            group=words[i:i+4];lo=group[0]['start'];hi=max(lo+.04,group[-1]['end']);hi=min(sec,hi)
            if hi<=lo:continue
            index+=1;srt.append(f'{index}\n{stamp(time+lo)} --> {stamp(time+hi)}\n'+' '.join(w['word'] for w in group)+'\n')
        report.append({'id':s['id'],'seconds':sec,'voice':opt.voice,'alignment_ratio':ratio,'words':words})
        audio_parts.append(mixed);time+=sec
    with wave.open(str(out/'mix.wav'),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
        for p in audio_parts:
            with wave.open(str(p),'rb') as x:w.writeframes(x.readframes(x.getnframes()))
    (out/'subtitles.srt').write_text('\n'.join(srt),encoding='utf8')
    (out/'audio-report.json').write_text(json.dumps({'voice':opt.voice,'subtitleMode':'whisper-aligned' if opt.voice=='gemini' else 'estimated-reading-time','seconds':time,'scenes':report},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
