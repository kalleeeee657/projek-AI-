import asyncio, json, pathlib, subprocess, tempfile, wave
import numpy as np
import edge_tts

ROOT=pathlib.Path(__file__).resolve().parent
PUBLIC=ROOT/'public'
SR=44100
SCENES=json.loads((ROOT/'narasi.json').read_text())
def run(args):
    subprocess.run(args,check=True)
async def main():
    PUBLIC.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp=pathlib.Path(tmp)
        paths=[]
        for i,scene in enumerate(SCENES):
            raw=tmp/f'{i}.mp3'; out=tmp/f'{i}.wav'
            await edge_tts.Communicate(scene['line'],'id-ID-ArdiNeural',rate='-3%',pitch='-3Hz').save(str(raw))
            duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(raw)]))
            speed=max(1,duration/(scene['sec']-.4))
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
        run(['ffmpeg','-loglevel','error','-y','-i',str(voice),'-i',str(bed),'-filter_complex','[0:a]volume=0.95[v];[1:a]volume=0.8[b];[v][b]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]','-map','[a]','-c:a','libmp3lame','-b:a','160k',str(PUBLIC/'moon-mix.mp3')])
        run(['ffmpeg','-loglevel','error','-y','-i',str(voice),'-c:a','libmp3lame','-b:a','128k',str(PUBLIC/'moon-voice.mp3')])
asyncio.run(main())
