# Operasi tulang patah — Remotion
Video edukasi vertikal 1080×1920, 56 detik, 30 fps. Ilustrasi vektor tanpa darah, contoh fiksasi internal; tidak semua patah tulang perlu operasi.

Di GitHub Codespaces, buka terminal dalam folder proyek:
```bash
npm install
python3 -m venv .venv
source .venv/bin/activate
pip install edge-tts
sudo apt-get update && sudo apt-get install -y ffmpeg
python buat-suara.py
npm run dev
```
Buka port yang tampil di tab Ports. Untuk ekspor MP4: `npm run render`.
Suara memakai id-ID-GadisNeural, suara perempuan Indonesia dengan beberapa ungkapan Jawa; bukan jaminan aksen Jawa asli. Pembuatan audio membutuhkan internet. Audio belum disertakan; jalankan skrip dahulu. Proyek belum diuji render di Codespaces.
