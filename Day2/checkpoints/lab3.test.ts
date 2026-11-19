import {test} from 'node:test';import assert from 'node:assert/strict';import {executeTool,supportTool} from '../src/tool';
test('Lab 3 learner edit: threshold raised to twelve, summary bounded to 160',()=>{
 const a={category:'access',impact:'department',affectedUsers:10,dataRisk:false,summary:'Access unavailable'};
 const run=(x:object)=>executeTool('assess_support_request',JSON.stringify(x));
 assert.equal(run(a).priority,'P3');assert.equal(run({...a,affectedUsers:12}).priority,'P2');assert.equal(run({...a,dataRisk:true}).queue,'Security');
 assert.equal(supportTool.parameters.properties.summary.maxLength,160);assert.throws(()=>run({...a,summary:'x'.repeat(161)}));
});
