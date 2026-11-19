import {test} from 'node:test';
import assert from 'node:assert/strict';
import {once} from 'node:events';
import {startHost} from '../src/host';
import {PolicyAgent} from '../src/core';
test('local SDK host binds loopback and rejects remote callback URLs',async()=>{
 const engine=new PolicyAgent({create:async()=>{throw Error('Must not call');}},'fixture');
 const server=startHost(engine,'local',0);await once(server,'listening');
 try{
 const addr=server.address();assert.ok(addr&&typeof addr==='object');assert.equal(addr.address,'127.0.0.1');
 const result=await fetch(`http://127.0.0.1:${addr.port}/api/messages`,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({serviceUrl:'https://external.example/steal',type:'message',text:'access'})});
 assert.equal(result.status,400);assert.match(await result.text(),/Local Playground/);
 }finally{await new Promise<void>(r=>server.close(()=>r()));}
});
test('approved-channel SDK entrypoint rejects unauthenticated activity',async()=>{
 const names=['NODE_ENV','clientId','tenantId','clientSecret']as const;const saved=Object.fromEntries(names.map(k=>[k,process.env[k]]));
 Object.assign(process.env,{NODE_ENV:'production',clientId:'11111111-1111-4111-8111-111111111111',tenantId:'22222222-2222-4222-8222-222222222222',clientSecret:'SYNTHETIC-NOT-A-SECRET'});
 const engine=new PolicyAgent({create:async()=>{throw Error('Must not call');}},'fixture');
 const server=startHost(engine,'approved-channel',0);await once(server,'listening');
 try{
 const addr=server.address();assert.ok(addr&&typeof addr==='object');
 const result=await fetch(`http://127.0.0.1:${addr.port}/api/messages`,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({type:'message',text:'access'})});
 assert.equal(result.status,401);
 }finally{await new Promise<void>(r=>server.close(()=>r()));for(const k of names){if(saved[k]===undefined)delete process.env[k];else process.env[k]=saved[k];}}
});
