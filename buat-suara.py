import asyncio, pathlib, subprocess, tempfile
import edge_tts
lines=["Pernah kepikiran, gimana caranya tulang yang patah bisa menyatu lagi? Yuk, kita lihat.","Pertama, dokter memeriksa pasien dan hasil rontgen, untuk menentukan penanganan yang tepat.","Sadurunge operasi, pasien dipersiapkan. Tim medis memberikan anestesi sesuai kebutuhan.","Dokter kemudian menyelaraskan bagian tulang yang patah, agar posisinya kembali sesuai.","Bila diperlukan, plat dan sekrup dipasang untuk menjaga tulang tetap stabil selama penyembuhan.","Setelah luka ditutup, pasien menjalani kontrol dan rehabilitasi sesuai arahan dokter.","Alon-alon, tulang akan pulih. Waktunya berbeda pada setiap pasien. Tetap ikuti arahan dokter, nggih."]
async def main():
    root=pathlib.Path(__file__).resolve().parent
    (root/'public').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        paths=[]
        for i,line in enumerate(lines):
            raw=f'{tmp}/{i}.mp3'; out=f'{tmp}/{i}.wav'
            await edge_tts.Communicate(line,'id-ID-GadisNeural',rate='+5%',pitch='-2Hz').save(raw)
            duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',raw]))
            speed=max(1,duration/7.5)
            subprocess.run(['ffmpeg','-y','-i',raw,'-af',f'atempo={speed},apad','-t','8','-ar','44100','-ac','1',out],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            paths.append(out)
        listing=pathlib.Path(tmp)/'list.txt'; listing.write_text(''.join(f"file '{p}'\n" for p in paths))
        subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(listing),'-c:a','libmp3lame',str(root/'public/narasi.mp3')],check=True)
asyncio.run(main())
