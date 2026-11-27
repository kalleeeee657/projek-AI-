import fs from "node:fs";
import assert from "node:assert/strict";
import {validate} from "./plan.mjs";
const p=JSON.parse(fs.readFileSync(new URL("./project.example.json",import.meta.url),"utf8"));
const report=validate(p);assert.equal(report.totalFrames,360);assert.equal(report.durationSeconds,6);assert.equal(report.renderReady,false);
for(const mutate of [x=>x.scenes[0].character.id="YELLOW_HOODIE",x=>x.format.fps=30,x=>x.scenes[0].durationFrames=0,x=>x.audio.enabled=true,x=>x.character.fingerprint="00000000",x=>x.scenes.push(x.scenes[0])]){
 const copy=structuredClone(p);mutate(copy);assert.throws(()=>validate(copy));
}
console.log("Project preflight checks passed");
