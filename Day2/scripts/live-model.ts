// LIVE Azure gate: never injects fixtures. Run only after provider approval and az login.
import {readConfig,PolicyAgent} from '../src/core';
import {createAzureTransport} from '../src/model';
async function main(){
 const c=readConfig(process.env);
 const engine=new PolicyAgent(createAzureTransport(c.endpoint),c.model);
 console.log(await engine.reply('live-verification-synthetic','Explain the policy for a lost laptop.'));
 console.log(await engine.reply('live-verification-synthetic-tool','Assess a draft support request: category outage, impact department, affectedUsers 30, dataRisk false, summary Department service unavailable.'));
 console.log('LIVE model returned validated citations. Inspect real model/tool trace in debugger; this log alone does not prove a function was selected.');
}main().catch(()=>{console.error('LIVE MODEL GATE FAILED: configuration, Entra login, project role, model capability or response validation. No fallback.');process.exitCode=1;});
