// Explicit FIXTURE ONLY. This script is never used by npm start or Toolkit F5.
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {setTimeout as delay} from 'node:timers/promises';
import assert from 'node:assert/strict';
import {PolicyAgent,Transport} from '../src/core';
import {startHost} from '../src/host';
async function main(){
 const requests:unknown[]=[];
 const transport:Transport={create:async r=>{requests.push(r);return {output:[],output_text:'FIXTURE ONLY: verify identity via the service desk [P2]'};}};
 const server=startHost(new PolicyAgent(transport,'FIXTURE-NOT-AZURE'),'local');
 await once(server,'listening');
 const child=spawn(process.execPath,['node_modules/@microsoft/m365agentsplayground/cli.js','start','--app-endpoint','http://127.0.0.1:3978/api/messages','--channel-id','emulator','--host','127.0.0.1','--port','56150','--disable-telemetry'],{env:{...process.env,TEAMSAPPTESTER_BROWSER:'none'},stdio:['ignore','pipe','pipe']});
 let logs='';child.stdout.on('data',d=>{logs+=d;});child.stderr.on('data',d=>{logs+=d;});
 let ws:WebSocket|undefined;
 try{
  let ready=false;for(let i=0;i<60;i++){try{const r=await fetch('http://127.0.0.1:56150/_debug/ping');if(r.ok){ready=true;break;}}catch{} await delay(250);}
  assert.ok(ready,'Playground did not start: '+logs);
  const config:any=await (await fetch('http://127.0.0.1:56150/_internal/v1/config')).json();
  console.log('PLAYGROUND CONFIG',JSON.stringify(config.config));
  const events:string[]=[];
  ws=new WebSocket('ws://127.0.0.1:56150/_ws_conversation/v1/conversations/stream');
  await new Promise<void>((resolve,reject)=>{ws!.onopen=()=>resolve();ws!.onerror=()=>reject(Error('WebSocket failed'));});
  ws.onmessage=e=>events.push(String(e.data));
  const conv=config.config.personalChat;
  assert.ok(conv,'Playground personalChat missing');
  const user=config.config.currentUser;assert.ok(user,'Playground currentUser missing');
  const response=await fetch(`http://127.0.0.1:56150/_conversation/v1/conversations/${conv.id}/messages`,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({from:{id:user.id},text:'How do I recover account access?',textFormat:'plain'})});
  console.log('MESSAGE STATUS',response.status,await response.text());assert.equal(response.status,200);
  for(let i=0;i<60&&!events.some(e=>e.includes('FIXTURE ONLY:'));i++)await delay(250);
  console.log('EVENTS',JSON.stringify(events));assert.ok(events.some(e=>e.includes('FIXTURE ONLY:')),'Reply not observed via Playground WebSocket');assert.equal(requests.length,1);
  console.log('PASS actual Playground 0.2.30 → SDK 1.10.1 HTTP activity → fixture transport → SDK connector → Playground WebSocket. NOT AZURE.');
 }finally{ws?.close();child.kill('SIGTERM');server.close();console.log(logs);}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
