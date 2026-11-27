import assert from "node:assert/strict";
import {MASTER,verifyMaster,characterSVG,MOTIONS,EXPRESSIONS,CHARACTER_ID} from "./STICKMAN_001.mjs";
assert.equal(verifyMaster(),true);
assert.throws(()=>characterSVG({id:"YELLOW_HOODIE"}));
assert.throws(()=>characterSVG({motion:"random"}));
for(const motion of MOTIONS)for(const expression of EXPRESSIONS)for(const frame of [0,30,75,180,359]){
 const s=characterSVG({motion,expression,frame});
 assert.equal(s,characterSVG({motion,expression,frame}));
 assert.ok(s.includes('data-character="'+CHARACTER_ID+'"'));
 for(const c of ['#242424','#547ba0','#81a0b9','#181818','rx="47" ry="49"','M-48 -8Q-58 -32'])assert.ok(s.includes(c),c);
 assert.equal((s.match(/<g\b/g)||[]).length,(MASTER.match(/<g\b/g)||[]).length);
}
console.log("Character Lock: 120 pose checks passed");
