# AI Video Studio V5 — Production preparation
Use the canonical STICKMAN_001 SVG as a deterministic Remotion overlay, preserving the exact existing 2D design. Three.js semi-realistic backgrounds and GLB supporting objects are planned; no approved 3D STICKMAN_001 model yet.
- project.example.json: six-second opening reveal, a planning example only.
- plan.mjs: checks the locked identity, fingerprint, poses, native 1080x1920 at 60fps, audio quota guard, and scene durations. It explicitly reports renderReady:false until integration is complete.
- character-lock/LockedCharacter.jsx: proposed Remotion overlay, not yet visually tested or connected to a composition.
- test.mjs: negative and positive plan checks.
Run node video-studio-v5/character-lock/test.mjs; node video-studio-v5/test.mjs; node video-studio-v5/plan.mjs.
Next: create Three.js environment/dinosaur asset integration (reuse existing asset sources, bake procedural textures when exporting GLB), test camera, shadow and overlay alignment, benchmark actual native frames, confirm Gemini free quota before voice requests, align subtitles, approve 6-second preview, then produce remaining scenes and validate final MP4. This push does not trigger video rendering or restart V2/V3/V4.
