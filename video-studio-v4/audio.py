import os,json,pathlib,urllib.request,urllib.error,base64,wave,time,subprocess,tempfile
import numpy as np
from faster_whisper import WhisperModel
from difflib import SequenceMatcher
import re
ROOT=pathlib.Path(__file__).resolve().parent
PUBLIC=ROOT/'public'
PUBLIC.mkdir(exist_ok=True)
SCENES=json.loads((ROOT/'project.json').read_text())['scenes']
(ROOT/'src').mkdir(exist_ok=True)
SR=44100
KEY=os.environ.get('GEMINI_API_KEY','').strip()
MODEL='gemini-2.5-flash-preview-tts'
VOICE='Zubenelgenubi'
PROFILE='Read only the exact Indonesian transcript. Original adult male storyteller, subtle Central Javanese accent, relaxed warm conversational delivery, clear diction, moderate pace, consistent pitch and timbre. Express surprise and humor naturally, never change speaker. No imitation of a real person. No extra words.'
def run(args): subprocess.run(args,check=True)
def wavwrite(path,data,sr):
    with wave.open(str(path),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(data)
def read_pcm(path):
    with wave.open(str(path),'rb') as w:
        return np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32)/32768
def gen(line,path):
    if not KEY: raise SystemExit('GEMINI_API_KEY missing')
    body={'contents':[{'parts':[{'text':PROFILE+'\nTranscript:\n'+line}]}],'generationConfig':{'responseModalities':['AUDIO'],'speechConfig':{'voiceConfig':{'prebuiltVoiceConfig':{'voiceName':VOICE}}}}}
    req=urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','x-goog-api-key':KEY})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req,timeout=180) as res: data=json.load(res)
            p=next(p['inlineData'] for c in data.get('candidates',[]) for p in c.get('content',{}).get('parts',[]) if p.get('inlineData',{}).get('data'))
            wavwrite(path,base64.b64decode(p['data']),24000)
            return
        except urllib.error.HTTPError as e:
            print('Gemini HTTP',e.code,flush=True)
            if e.code not in (429,500,502,503,504) or attempt==4: raise SystemExit('Gemini TTS failed')
        except Exception:
            if attempt==4: raise SystemExit('Gemini audio unavailable')
        time.sleep(min(90,15*2**attempt))
def norm(s): return re.sub(r'[^\w]','',s.lower())
def match_words(text,heard,limit):
    target=text.split()
    sm=SequenceMatcher(None,[norm(x) for x in target],[norm(x['text']) for x in heard],autojunk=False)
    out=[None]*len(target)
    for tag,a,b,c,d in sm.get_opcodes():
        if tag=='equal':
            for k in range(b-a): out[a+k]=(heard[c+k]['start'],heard[c+k]['end'])
        elif tag=='replace' and b>a and d>c:
            lo=heard[c]['start'];hi=heard[d-1]['end']
            for k in range(b-a):out[a+k]=(lo+(hi-lo)*k/(b-a),lo+(hi-lo)*(k+1)/(b-a))
    i=0
    while i<len(out):
        if out[i] is not None:i+=1;continue
        j=i
        while j<len(out) and out[j] is None:j+=1
        lo=out[i-1][1] if i else 0
        hi=out[j][0] if j<len(out) else min(limit,heard[-1]['end']+.25)
        hi=max(lo,hi)
        for k in range(i,j):out[k]=(lo+(hi-lo)*(k-i)/(j-i),lo+(hi-lo)*(k-i+1)/(j-i))
        i=j
    result=[]
    for i,(a,b) in enumerate(out):
        a=max(0,min(limit,a));b=max(a,min(limit,b))
        result.append({'text':target[i],'start':round(a,3),'end':round(b,3)})
    return result,round(sm.ratio(),3)
def transcribe(model,path,script,limit):
    audio=read_pcm(path)
    segs,_=model.transcribe(audio,language='id',word_timestamps=True,beam_size=5,condition_on_previous_text=False,initial_prompt=script,vad_filter=False)
    heard=[{'text':w.word.strip(),'start':float(w.start),'end':float(w.end)} for s in segs for w in (s.words or []) if w.word.strip() and w.end>w.start]
    if not heard:raise SystemExit('No speech timing')
    return match_words(script,heard,limit)
def main():
    model=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=4)
    timings=[];report=[];parts=[]
    with tempfile.TemporaryDirectory() as temp:
        tmp=pathlib.Path(temp)
        for i,s in enumerate(SCENES):
            raw=PUBLIC/f'voice-scene-{i}.wav'
            if not raw.exists():gen(s['line'],raw);time.sleep(15)
            length=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(raw)]))
            speed=max(1,length/(s['sec']-.20))
            af=[]
            while speed>2:af.append('atempo=2');speed/=2
            af.extend([f'atempo={speed:.6f}','apad'])
            out=tmp/f'{i}.wav'
            run(['ffmpeg','-v','error','-y','-i',str(raw),'-af',','.join(af),'-t',str(s['sec']),'-ar',str(SR),'-ac','1','-c:a','pcm_s16le',str(out)])
            parts.append(read_pcm(out))
            clip=tmp/f'{i}-16k.wav'
            run(['ffmpeg','-v','error','-y','-i',str(out),'-ar','16000','-ac','1','-c:a','pcm_s16le',str(clip)])
            aligned,ratio=transcribe(model,clip,s['line'],s['sec'])
            timings.append(aligned);report.append({'scene':i+1,'script_match_ratio':ratio,'words':len(aligned),'warning':'Interpolated unmatched words; review against audio' if ratio<.95 else None})
            print('Scene',i+1,'match',ratio,flush=True)
        if any(x['script_match_ratio']<.75 for x in report):raise SystemExit('Subtitle alignment below 75%; review speech before delivery')
        v=np.concatenate(parts)
        wavwrite(tmp/'voice.wav',(np.clip(v,-1,1)*32767).astype('<i2').tobytes(),SR)
        t=np.arange(len(v))/SR
        music=np.zeros_like(t)
        rng=np.random.default_rng(42)
        for i,s in enumerate(SCENES):
            off=round(sum(a['sec'] for a in SCENES[:i])*SR);n=round(s['sec']*SR);u=np.arange(n)/SR
            env=np.minimum(u/.4,1)*np.minimum((s['sec']-u)/.5,1)
            melody=np.zeros(n)
            notes=[220,261.63,293.66,329.63,392,329.63,293.66,261.63]
            for k in range(int(s['sec']*2)):
                a=int(k*.5*SR);m=min(n-a,int(.48*SR));z=np.arange(m)/SR
                if m>0:melody[a:a+m]+=.035*(np.sin(2*np.pi*notes[(k+i)%8]*z)+.3*np.sin(4*np.pi*notes[(k+i)%8]*z))*np.exp(-8*z)
            bed=.035*np.sin(2*np.pi*(110 if i<5 else 82.41)*u)+melody
            noise=np.convolve(rng.normal(0,1,n),np.ones(64)/64,mode='same')
            bed+=.045*noise
            if i in (1,6):bed+=.08*np.sin(2*np.pi*45*u)*np.exp(-4*u)
            music[off:off+n]=bed*env
        wavwrite(tmp/'music.wav',(np.clip(music,-1,1)*32767).astype('<i2').tobytes(),SR)
        run(['ffmpeg','-v','error','-y','-i',str(tmp/'voice.wav'),'-i',str(tmp/'music.wav'),'-filter_complex','[0:a]asplit=2[v][key];[1:a][key]sidechaincompress=threshold=0.025:ratio=5:attack=25:release=400[b];[v][b]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]','-map','[a]','-b:a','160k',str(PUBLIC/'mix.mp3')])
        run(['ffmpeg','-v','error','-y','-i',str(tmp/'voice.wav'),'-b:a','128k',str(PUBLIC/'voice.mp3')])
    (ROOT/'src/timing.json').write_text(json.dumps(timings,ensure_ascii=False,indent=2))
    (PUBLIC/'subtitle-timing.json').write_text(json.dumps(timings,ensure_ascii=False,indent=2))
    (PUBLIC/'alignment-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
