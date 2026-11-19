import { test } from 'node:test';
import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';

test('implementation contract exists', () => assert.ok(existsSync('src/core.ts'), 'Core implementation is not yet present'));
async function core() { return import('../src/core.js'); }
const env = { PROJECT_ENDPOINT:'https://training.services.ai.azure.com/api/projects/class', MODEL_DEPLOYMENT_NAME:'gpt-4.1-mini', HOST_MODE:'local' };
test('configuration is required and endpoint constrained', async () => {
 const {readConfig}=await core(); assert.throws(()=>readConfig({}));
 assert.equal(readConfig(env).model, 'gpt-4.1-mini');
 for(const endpoint of ['http://training.services.ai.azure.com/api/projects/class','https://evil.test/api/projects/class','https://training.services.ai.azure.com/api/projects/class?secret=x']) assert.throws(()=>readConfig({...env,PROJECT_ENDPOINT:endpoint}));
 assert.throws(()=>readConfig({...env,HOST_MODE:'production'}));
 assert.throws(()=>readConfig({...env,NODE_ENV:'production'}));
});
test('retrieval selects passages, rejects unsupported scope', async()=>{
 const {retrieve}=await core(); const p=retrieve('lost stolen laptop security incident');
 assert.ok(p.some(x=>x.id==='P1')); assert.ok(p.length<=2); assert.ok(!p.some(x=>x.id==='P4'));
 assert.deepEqual(retrieve('banana astrophysics recipe'),[]);
});
test('tool schema rejects malformed, extras, unknown names and bounds',async()=>{
 const {executeTool}=await core();
 for(const [n,a] of [['delete_ticket','{}'],['assess_support_request','{bad'],['assess_support_request','{}'],['assess_support_request',JSON.stringify({category:'access',impact:'individual',affectedUsers:0,dataRisk:false,summary:'Help'})],['assess_support_request',JSON.stringify({category:'access',impact:'individual',affectedUsers:1,dataRisk:false,summary:'Help',approve:true})]]) assert.throws(()=>executeTool(n,a));
});
test('meaningful support routing returns draft only',async()=>{
 const {executeTool}=await core(); const call=(a:object)=>executeTool('assess_support_request',JSON.stringify(a));
 const base={category:'access',impact:'individual',affectedUsers:1,dataRisk:false,summary:'Cannot sign in'};
 assert.equal(call(base).priority,'P3'); assert.equal(call({...base,dataRisk:true}).queue,'Security');
 assert.equal(call({...base,category:'outage',impact:'department',affectedUsers:30}).priority,'P1');
 assert.equal(call(base).status,'DRAFT_ONLY'); assert.equal(call({...base,affectedUsers:10}).priority,'P2');
});
test('FIXTURE transport: real orchestration requests Responses tool, grounds before call, follows call_id',async()=>{
 const {PolicyAgent}=await core(); const requests:any[]=[];
 const transport:import('../src/core').Transport={create:async (r:any)=>{requests.push(structuredClone(r)); return requests.length===1?{output:[{type:'function_call',name:'assess_support_request',call_id:'fixture-call',arguments:JSON.stringify({category:'device',impact:'individual',affectedUsers:1,dataRisk:true,summary:'Lost laptop'})}],output_text:''}:{output:[],output_text:'Draft security escalation [P1]'};}};
 const agent=new PolicyAgent(transport,'fixture-deployment'); const reply=await agent.reply('conversation-a','Lost laptop; assess support request');
 assert.match(reply,/Draft/); assert.equal(requests.length,2); assert.equal(requests[0].model,'fixture-deployment');
 assert.equal(requests[0].tools[0].name,'assess_support_request'); assert.equal(requests[0].tool_choice,'auto');
 assert.match(requests[0].instructions,/P1/); assert.doesNotMatch(requests[0].instructions,/P4/);
 assert.ok(requests[1].input.some((x:any)=>x.type==='function_call_output'&&x.call_id==='fixture-call'&&x.output.includes('DRAFT_ONLY')));
 assert.equal(requests[0].store,false);
});
test('FIXTURE transport: conversation isolation and bounded session state',async()=>{
 const {PolicyAgent}=await core(); const requests:any[]=[];
 const agent=new PolicyAgent({create:async(r:any)=>{requests.push(structuredClone(r));return {output:[],output_text:'Approved-policy context [P2]'};}},'fixture');
 await agent.reply('a','access alpha'); await agent.reply('a','access followup'); await agent.reply('b','access beta');
 assert.match(JSON.stringify(requests[1].input),/alpha/); assert.doesNotMatch(JSON.stringify(requests[2].input),/alpha/);
});
test('FIXTURE transport: no grounding fails closed without model call',async()=>{
 const {PolicyAgent}=await core();let count=0;
 const a=new PolicyAgent({create:async()=>{count++;throw Error('should not call');}},'fixture');
 assert.match(await a.reply('x','banana astrophysics'),/no relevant policy/i);assert.equal(count,0);
});
test('FIXTURE transport: service errors never become fabricated answers',async()=>{
 const {PolicyAgent}=await core();const a=new PolicyAgent({create:async()=>{throw Error('secret=supersecret');}},'fixture');
 await assert.rejects(()=>a.reply('x','access issue'),/Model request failed/);
});
test('FIXTURE transport: tool loop bounded and unknown functions denied',async()=>{
 const {PolicyAgent}=await core();let count=0;
 const a=new PolicyAgent({create:async()=>{count++;return {output:[{type:'function_call',name:'assess_support_request',call_id:'f',arguments:JSON.stringify({category:'access',impact:'individual',affectedUsers:1,dataRisk:false,summary:'Locked out'})}],output_text:''};}},'fixture');
 await assert.rejects(()=>a.reply('x','access support'),/Tool loop limit/); assert.equal(count,3);
 const b=new PolicyAgent({create:async()=>({output:[{type:'function_call',name:'delete_everything',call_id:'f',arguments:'{}'}],output_text:''})},'fixture');
 await assert.rejects(()=>b.reply('x','access support'),/Tool denied/);
});
test('FIXTURE transport: citation absent or outside retrieved set is rejected',async()=>{
 const {PolicyAgent}=await core();
 for(const text of ['Do whatever you want','Unsupported [P4]']){
 const a=new PolicyAgent({create:async()=>({output:[],output_text:text})},'fixture');
 await assert.rejects(()=>a.reply('x','stolen laptop'),/Citation validation failed/);
 }
});
