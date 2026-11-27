import assert from 'node:assert/strict';
import {createCharacter,IDS} from './characters.mjs';
assert.throws(()=>createCharacter('OTHER'));
for(const id of IDS){const a=createCharacter(id);assert.equal(a.identity,id);const names=[];a.root.traverse(o=>{if(o.name)names.push(o.name)});for(const n of ['head','spine','hipL','hipR','kneeL','kneeR','shoulderL','shoulderR','elbowL','elbowR'])assert.ok(names.includes(n),n);
const identity=()=>{const v=[];a.root.traverse(o=>{if(o.isMesh)v.push([o.geometry.uuid,o.material.color.getHex()])});return JSON.stringify(v)};
const before=identity();
for(const motion of ['idle','walk','wave','talk',...(id==='AMI_001'?['phone']:[])])for(const frame of [0,30,120,359]){a.pose({frame,motion,expression:'surprised'});assert.equal(identity(),before);a.root.updateMatrixWorld(true);a.root.traverse(o=>assert.ok(o.matrixWorld.elements.every(Number.isFinite)))}
}
console.log('Both locked character prototypes passed identity, pose and finite transform checks');
