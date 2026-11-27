import fs from "node:fs";
import assert from "node:assert/strict";
import {fileURLToPath} from "node:url";
import {CHARACTER_ID,VERSION,FINGERPRINT,MOTIONS,EXPRESSIONS,verifyMaster,characterSVG} from "./character-lock/STICKMAN_001.mjs";
export function validate(p){
 verifyMaster();
 assert.ok(typeof p.title==="string"&&p.title.trim());
 assert.deepEqual(p.format,{width:1080,height:1920,fps:60});
 assert.equal(p.character.id,CHARACTER_ID);
 assert.equal(p.character.version,VERSION);
 assert.equal(p.character.fingerprint,FINGERPRINT);
 assert.equal(p.character.representation,"svg-overlay");
 assert.equal(p.visual.renderer,"threejs-remotion");
 assert.equal(p.visual.environmentStyle,"semi-realistic");
 assert.equal(p.audio.narrator,"Zubenelgenubi");
 assert.equal(p.audio.provider,"Gemini");
 assert.ok(typeof p.audio.enabled==="boolean"&&typeof p.audio.freeQuotaConfirmed==="boolean");
 if(p.audio.enabled)assert.equal(p.audio.freeQuotaConfirmed,true,"Confirm free Gemini quota before TTS");
 assert.ok(Array.isArray(p.scenes)&&p.scenes.length);
 const ids=new Set();let start=0;
 const scenes=p.scenes.map(s=>{
  assert.match(s.id,/^[a-z0-9-]+$/);assert.ok(!ids.has(s.id),"Duplicate scene ID");ids.add(s.id);
  assert.ok(Number.isInteger(s.durationFrames)&&s.durationFrames>0);
  assert.equal(s.character.id,CHARACTER_ID);
  assert.ok(MOTIONS.includes(s.character.motion)&&EXPRESSIONS.includes(s.character.expression));
  assert.ok(typeof s.narration==="string"&&s.narration.trim());
  assert.ok(typeof s.environment==="string"&&s.environment.trim());
  assert.ok(Array.isArray(s.assets)&&s.assets.every(a=>typeof a==="string"));
  assert.ok(typeof s.camera==="string"&&s.camera.trim());
  assert.ok(Array.isArray(s.sfx)&&s.sfx.every(a=>typeof a==="string"));
  for(const frame of [0,Math.floor(s.durationFrames/2),s.durationFrames-1])
   characterSVG({...s.character,frame,fps:60});
  const entry={id:s.id,startFrame:start,durationFrames:s.durationFrames,endFrameExclusive:start+s.durationFrames};start+=s.durationFrames;return entry;
 });
 return {title:p.title,format:p.format,character:p.character.id,totalFrames:start,durationSeconds:start/60,scenes,previewOnly:p.previewOnly===true,renderReady:false,missing:["Three.js environment and dinosaur asset integration","Remotion composition and benchmark","Approved 3D character master if required",...(p.audio.enabled?["Generate and align narration"]:["Voice quota confirmation and narration"]) ]};
}
if(process.argv[1]===fileURLToPath(import.meta.url)){
 const p=JSON.parse(fs.readFileSync(process.argv[2]||new URL("./project.example.json",import.meta.url),"utf8"));
 console.log(JSON.stringify(validate(p),null,2));
}
