import asyncio, pathlib, subprocess, tempfile
import edge_tts
lines=["Bayangkan kalau","seluruh air Danau Toba","dipindahkan ke Jakarta.","Air mulai naik.","Gedung bisa terendam.","Tapi ini hanya ilustrasi.","Danau Toba sangat luas.","Di tengahnya ada Samosir.","Alam memang luar biasa, nggih!"]
async def main():
    pathlib.Path("public").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        paths=[]
        for i,line in enumerate(lines):
            raw=f"{tmp}/{i}.mp3"; out=f"{tmp}/{i}.wav"
            await edge_tts.Communicate(line,"id-ID-GadisNeural",rate="+8%").save(raw)
            duration=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",raw]))
            speed=max(1,duration/2.8)
            subprocess.run(["ffmpeg","-y","-i",raw,"-af",f"atempo={speed},apad","-t","3","-ar","44100","-ac","1",out],check=True)
            paths.append(out)
        listing=pathlib.Path(tmp)/"list.txt"
        listing.write_text("".join(f"file '{p}'\n" for p in paths))
        subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(listing),"-c:a","libmp3lame","public/toba.mp3"],check=True)
asyncio.run(main())
