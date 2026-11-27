# Bagaimana jika Bulan mendekati Bumi?
Original 3D cartoon educational short. 1080x1920, 60fps, 60 seconds, 8 scenes. Three.js procedural meshes, animated water, particles, camera and stylized materials; no external visual assets.

Voice: id-ID-ArdiNeural, original synthetic male Indonesian voice with Javanese expressions, not a clone of any public figure. Original synthesized background and sound effects. Captions highlight words using estimated timing, not forced alignment.

## Run
From this folder:
```bash
npm install
python -m pip install edge-tts numpy
python buat-audio.py
npm run dev
npm run render
```
FFmpeg and ffprobe required. Output: out/moon-cartoon.mp4. GitHub Actions automates the same steps. GPU software fallback uses Remotion --gl=swangle.

## Science
Average Earth–Moon distance 384,400 km; lunar recession about 3.8 cm/year. The tidal forcing approximation scales as inverse distance cubed; actual water height is not multiplied directly. Flooding, deformation, breakup and rings are conceptual hypothetical illustrations, not forecasts or simulations. Distances and planet sizes are not to scale.
Sources: https://science.nasa.gov/moon/by-the-numbers/ and https://science.nasa.gov/solar-system/moon/10-things-what-we-learn-about-earth-by-studying-the-moon/
