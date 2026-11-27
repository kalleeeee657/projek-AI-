import asyncio, json, pathlib, subprocess, tempfile, wave
import numpy as np
import os, base64, urllib.request, urllib.error, time, random

ROOT=pathlib.Path(__file__).resolve().parent/'moon-cartoon'
PUBLIC=ROOT/'public'
SR=44100
SCENES=json.loads((ROOT/'narasi.json').read_text())
KEY=os.environ.get('GEMINI_API_KEY','').strip()
if not KEY:
    raise SystemExit('GEMINI_API_KEY unavailable.')
MODEL='gemini-2.5-flash-preview-tts'
VOICE='Zubenelgenubi'
MOODS=[
    'Curious, playful opening; surprise at the end. Friendly, natural rhythm.',
    'Informative, relaxed, as if explaining a fun fact to a friend.',
    'Build excitement, emphasize delapan kali, then settle.',
    'Concerned and engaging, not sensational; conversational Lha.',
    'Gently surprised, clear and lightly amused.',
    'Suspenseful and serious, without shouting.',
    'Amazed and lightly humorous; imagine a wonderful planetary ring.',
    'Warm, reassuring, soft smile in the voice; natural nggih.'
]
def synthesize(line, i, output):
    prompt=(
        "Speak only the transcript, exactly as written, in Indonesian. "
        "An original adult male storyteller, relaxed, friendly and expressive, with a subtle Central Javanese accent. "
        "Sound like a science creator chatting with a friend, never a news anchor. "
        "Use natural pauses, clear articulation and an unhurried but lively rhythm. "
        "Keep the same voice identity throughout. Do not imitate any real person. "
        "Keep it within the scene duration of "+str(SCENES[i]['sec'])+" seconds. "
        "Scene delivery: "+MOODS[i]+"\nTranscript:\n"+line
    )
    body={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"responseModalities":["AUDIO"],"speechConfig":{"voiceConfig":{"prebuiltVoiceConfig":{"voiceName":VOICE}}}}}
    req=urllib.request.Request(f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent',data=json.dumps(body).encode(),headers={'Content-Type':'application/json','x-goog-api-key':KEY})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req,timeout=180) as res:
                data=json.load(res)
            part=next((p['inlineData'] for c in data.get('candidates',[]) for p in c.get('content',{}).get('parts',[]) if p.get('inlineData',{}).get('data')),None)
            if not part: raise ValueError('No audio returned')
            pcm=base64.b64decode(part['data'],validate=True)
            if not pcm or len(pcm)%2: raise ValueError('Invalid PCM')
            with wave.open(str(output),'wb') as w:
                w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(pcm)
            print(f'Scene {i+1}: Gemini audio generated',flush=True)
            return
        except urllib.error.HTTPError as e:
            if e.code not in (429,500,502,503,504) or attempt==4:
                raise SystemExit(f'Gemini scene {i+1}: HTTP {e.code}; check access, billing or quota.')
            time.sleep(min(90,15*(2**attempt)))
        except Exception:
            if attempt==4: raise SystemExit(f'Gemini scene {i+1}: no valid audio after retries.')
            time.sleep(min(90,10*(2**attempt)))

def run(args):
    subprocess.run(args,check=True)
async def main():
    PUBLIC.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp=pathlib.Path(tmp)
        paths=[]
        for i,scene in enumerate(SCENES):
            raw=tmp/f'{i}-gemini.wav'; out=tmp/f'{i}.wav'
            synthesize(scene['line'],i,raw)
            if i < len(SCENES)-1: time.sleep(15)
            duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(raw)]))
            speed=max(1,duration/(scene['sec']-.22))
            print(f'Scene {i+1}: raw {duration:.2f}s; tempo {speed:.2f}x',flush=True)
            run(['ffmpeg','-loglevel','error','-y','-i',str(raw),'-af',f'atempo={speed:.6f},apad','-t',str(scene['sec']),'-ar',str(SR),'-ac','1',str(out)])
            paths.append(out)
        listing=tmp/'list.txt'
        listing.write_text(''.join(f"file '{p}'\n" for p in paths))
        voice=tmp/'voice.wav'
        run(['ffmpeg','-loglevel','error','-y','-f','concat','-safe','0','-i',str(listing),'-c:a','pcm_s16le',str(voice)])
        total=sum(s['sec'] for s in SCENES)
        t=np.arange(total*SR,dtype=np.float64)/SR
        music=np.zeros_like(t)
        rng=np.random.default_rng(77)
        cursor=0
        for i,scene in enumerate(SCENES):
            n=scene['sec']*SR; u=np.arange(n)/SR
            envelope=np.minimum(1,u/.8)*np.minimum(1,(scene['sec']-u)/.8)
            root=[55,55,49,49,58.27,49,65.41,65.41][i]
            pad=sum(np.sin(2*np.pi*root*k*u+.25*np.sin(2*np.pi*.23*u)) for k in [1,1.5,2,2.52])/4
            beat=np.sin(2*np.pi*48*u)*np.exp(-8*(u%1.5))
            impact=np.sin(2*np.pi*(42*u+16*(1-np.exp(-u))))*np.exp(-3.4*u)
            noise=rng.normal(0,1,n)
            # Smooth noise for a soft ocean/space whoosh, no licensed audio.
            noise=np.convolve(noise,np.ones(48)/48,mode='same')
            fx=.09*noise*np.sin(np.pi*np.clip(u/scene['sec'],0,1)) if i in [2,3,5] else 0
            music[cursor:cursor+n]=.065*pad*envelope+.023*beat*envelope+.09*impact+fx
            cursor+=n
        music*=np.minimum(1,(total-t)/1.4)
        bed=tmp/'bed.wav'
        with wave.open(str(bed),'wb') as w:
            w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(music,-1,1)*32767).astype('<i2').tobytes())
        run(['ffmpeg','-loglevel','error','-y','-i',str(voice),'-i',str(bed),'-filter_complex','[0:a]volume=0.95,asplit=2[v][key];[1:a]volume=0.8[b];[b][key]sidechaincompress=threshold=0.025:ratio=5:attack=25:release=450[duck];[v][duck]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]','-map','[a]','-c:a','libmp3lame','-b:a','160k',str(PUBLIC/'moon-mix.mp3')])
        run(['ffmpeg','-loglevel','error','-y','-i',str(voice),'-c:a','libmp3lame','-b:a','128k',str(PUBLIC/'moon-voice.mp3')])
asyncio.run(main())
