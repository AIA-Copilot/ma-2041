import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createAzureTransport} from '../src/model';
test('FIXTURE HTTP: real AIProjectClient constructs project Responses URL and Entra scope',async()=>{
 const prior=globalThis.fetch;const seen:{url:string,body:any,auth:string|null}[]=[];const scopes:unknown[]=[];
 globalThis.fetch=async(input,init)=>{
  const req=new Request(input,init);seen.push({url:req.url,body:await req.json(),auth:req.headers.get('authorization')});
  return new Response(JSON.stringify({id:'fixture-response',object:'response',created_at:1,status:'completed',output:[{type:'message',id:'fixture-message',status:'completed',role:'assistant',content:[{type:'output_text',text:'Fixture [P2]',annotations:[]}]}]}),{status:200,headers:{'content-type':'application/json'}});
 };
 try{
  assert.equal(createAzureTransport.length,2,'Explicit credential seam is missing');
  const t=createAzureTransport('https://fixture.services.ai.azure.com/api/projects/test',{getToken:async(scope:unknown)=>{scopes.push(scope);return {token:'SYNTHETIC-NOT-A-SECRET',expiresOnTimestamp:Date.now()+60000};}});
  const result=await t.create({model:'fixture-deployment',input:'access',store:false});
  assert.equal(result.output_text,'Fixture [P2]');assert.equal(seen.length,1);
  assert.equal(seen[0].url,'https://fixture.services.ai.azure.com/api/projects/test/openai/v1/responses');
  assert.equal(seen[0].body.model,'fixture-deployment');assert.equal(seen[0].body.store,false);
  assert.equal(seen[0].auth,'Bearer SYNTHETIC-NOT-A-SECRET');assert.match(JSON.stringify(scopes),/https:\/\/ai.azure.com\/\.default/);
 }finally{globalThis.fetch=prior;}
});
