import argparse,base64,hashlib,json,os,pathlib,re,urllib.request,urllib.error,wave
ROOT=pathlib.Path(__file__).resolve().parent
VOICE='Zubenelgenubi'
TEXT_MODEL='gemini-3.5-flash-lite'
TTS_MODEL='gemini-2.5-flash-preview-tts'
IDS={'STICKMAN_001','AMI_001'}
PROFILE='Read only the exact Indonesian transcript. Original adult male storyteller, subtle Central Javanese accent, relaxed warm conversational delivery, clear diction, moderate pace, consistent pitch and timbre. No imitation of a real person. No extra words.'
def require(condition,message):
    if not condition: raise ValueError(message)
def guard():
    require(os.getenv('CONFIRM_FREE_TIER')=='true','Confirm free-tier project and model eligibility before API calls')
    key=os.getenv('GEMINI_API_KEY','').strip()
    require(bool(key),'GEMINI_API_KEY secret is missing')
    return key
def request(model,body):
    key=guard()
    require(model in (TEXT_MODEL,TTS_MODEL),'Model not allowlisted')
    req=urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','x-goog-api-key':key})
    try:
        with urllib.request.urlopen(req,timeout=180) as res:return json.load(res)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'Gemini HTTP {e.code}; stopped without retry or paid fallback') from None
    except urllib.error.URLError:
        raise RuntimeError('Gemini network error; stopped without retry') from None
def validate(d,title,seconds):
    require(isinstance(d,dict) and d.get('title')==title,'Title mismatch')
    scenes=d.get('scenes')
    require(isinstance(scenes,list) and 1<=len(scenes)<=20,'Invalid scene count')
    total=0;seen=set()
    for s in scenes:
        i=s.get('id','')
        require(isinstance(i,str) and bool(re.fullmatch(r'[a-z0-9-]{1,48}',i)) and i not in seen,'Invalid or duplicate scene ID');seen.add(i)
        dur=s.get('seconds')
        require(type(dur) is int and 6<=dur<=8,'Scene must last 6–8 seconds')
        total+=dur
        chars=s.get('characters')
        require(isinstance(chars,list) and all(isinstance(c,str) and c in IDS for c in chars) and len(chars)==len(set(chars)),'Unapproved character')
        for k in ('visual','motion','camera','narration'):
            require(isinstance(s.get(k),str) and 0<len(s[k].strip())<=1000,'Missing or invalid '+k)
        require(len(s['narration'].split())<=dur*3,'Narration too long')
    require(total==seconds,'Incorrect total scene duration')
    return {'title':title,'format':{'width':1080,'height':1920,'fps':60},'totalSeconds':total,'totalFrames':total*60,'narrator':VOICE,'status':'draft-review-required','scenes':[{**s,'durationFrames':s['seconds']*60} for s in scenes]}
def storyboard(title,seconds,out):
    prompt=f'''Create an Indonesian educational entertainment storyboard as ONLY JSON, no markdown. Title exactly {json.dumps(title,ensure_ascii=False)}. Total {seconds} seconds, each scene 6–8 integer seconds. Schema: {{"title":string,"scenes":[{{"id":string,"seconds":integer,"characters":[string],"visual":string,"motion":string,"camera":string,"narration":string}}]}}. Use only character IDs STICKMAN_001 and AMI_001, never redesign hair, clothes or proportions. STICKMAN_001: pale round face, messy black hair, black oversized tee, blue rolled shorts, white sneakers. AMI_001: black messy ponytail, warm tan oval face, charcoal tank top, blue rolled shorts, white sneakers. Smartphone optional. Semi-3D characters and cinematic semi-realistic environments. Indonesian narration max 3 words per second, natural, factually cautious, strong hook. Scene descriptions are a draft, not executable code.'''
    response=request(TEXT_MODEL,{'contents':[{'parts':[{'text':prompt}]}],'generationConfig':{'responseMimeType':'application/json','maxOutputTokens':8192}})
    raw=''.join(p.get('text','') for p in response.get('candidates',[{}])[0].get('content',{}).get('parts',[]) if not p.get('thought'))
    draft=validate(json.loads(raw),title,seconds)
    out.write_text(json.dumps(draft,ensure_ascii=False,indent=2))
def voice(line,out):
    require(isinstance(line,str) and 0<len(line.split())<=24,'Voice preview max 24 words')
    cache=out.with_suffix('.sha256');finger=hashlib.sha256((TTS_MODEL+VOICE+PROFILE+line).encode()).hexdigest()
    if out.exists() and cache.exists() and cache.read_text()==finger:
        with wave.open(str(out),'rb') as w: require(w.getnframes()>0,'Invalid cached voice')
        return
    response=request(TTS_MODEL,{'contents':[{'parts':[{'text':PROFILE+'\nTranscript:\n'+line}]}],'generationConfig':{'responseModalities':['AUDIO'],'speechConfig':{'voiceConfig':{'prebuiltVoiceConfig':{'voiceName':VOICE}}}}})
    part=next((p['inlineData'] for c in response.get('candidates',[]) for p in c.get('content',{}).get('parts',[]) if p.get('inlineData',{}).get('data')),None)
    require(part is not None,'No audio returned')
    mime=part.get('mimeType','').lower()
    require(mime.startswith(('audio/l16','audio/pcm')) and ('rate=24000' in mime or 'rate=' not in mime),'Unexpected PCM audio format')
    data=base64.b64decode(part['data'],validate=True)
    require(len(data)>0 and len(data)%2==0,'Invalid PCM')
    with wave.open(str(out),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(data)
    cache.write_text(finger)
    out.with_suffix('.json').write_text(json.dumps({'model':TTS_MODEL,'voice':VOICE,'seconds':len(data)/48000,'transcript':line,'status':'review-before-render'},ensure_ascii=False,indent=2))
def main():
    p=argparse.ArgumentParser()
    p.add_argument('mode',choices=['storyboard','voice'])
    p.add_argument('--title',default='Bagaimana Jika Dinosaurus Masih Hidup di Lombok? — Mandalika Edition')
    p.add_argument('--seconds',type=int,default=60)
    p.add_argument('--line',default='Bayangkan di Mandalika, dinosaurus raksasa tiba-tiba muncul!')
    a=p.parse_args();out=ROOT/'out';out.mkdir(exist_ok=True)
    if a.mode=='storyboard':
        require(6<=a.seconds<=120 and 1<=len(a.title)<=200,'Invalid storyboard request')
        storyboard(a.title,a.seconds,out/'storyboard.json')
    else:voice(a.line,out/'voice.wav')
if __name__=='__main__':main()
