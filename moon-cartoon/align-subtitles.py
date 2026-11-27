import json, pathlib, subprocess, tempfile, re
from faster_whisper import WhisperModel
import numpy as np
import wave
ROOT=pathlib.Path(__file__).resolve().parent
scenes=json.loads((ROOT/'narasi.json').read_text())
voice=ROOT/'public/moon-voice.mp3'
if not voice.exists(): raise SystemExit('Locked narration file not found')
model=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=4)
all_words=[]; offset=0
with tempfile.TemporaryDirectory() as tmp:
    for i,scene in enumerate(scenes):
        clip=pathlib.Path(tmp)/f'{i}.wav'
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(voice),'-ss',str(offset),'-t',str(scene['sec']),'-ac','1','-ar','16000','-c:a','pcm_s16le',str(clip)],check=True)
        with wave.open(str(clip),'rb') as wav:
            assert wav.getframerate()==16000 and wav.getnchannels()==1 and wav.getsampwidth()==2
            audio=np.frombuffer(wav.readframes(wav.getnframes()),dtype='<i2').astype(np.float32)/32768.0
        segments,_=model.transcribe(audio,language='id',word_timestamps=True,beam_size=5,condition_on_previous_text=False,initial_prompt=scene['line'],vad_filter=False)
        words=[]
        for seg in segments:
            for w in seg.words or []:
                text=w.word.strip()
                start=max(0,min(float(w.start),scene['sec']))
                end=max(start,min(float(w.end),scene['sec']))
                if text and end>start:
                    words.append({'text':text,'start':round(start,3),'end':round(end,3)})
        if not words: raise SystemExit(f'No subtitle timings for scene {i+1}')
        print(f'Scene {i+1}: {len(words)} timestamped words')
        all_words.append(words)
        offset+=scene['sec']
(ROOT/'src/subtitle-timing.json').write_text(json.dumps(all_words,ensure_ascii=False,indent=2))
(ROOT/'public/subtitle-timing.json').write_text(json.dumps(all_words,ensure_ascii=False,indent=2))
