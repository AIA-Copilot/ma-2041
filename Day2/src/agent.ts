import {ActivityTypes} from '@microsoft/agents-activity';
import {AgentApplication,MemoryStorage,CloudAdapter,AuthConfiguration} from '@microsoft/agents-hosting';
import {PolicyAgent,WELCOME} from './core';
export function createAgent(engine:PolicyAgent,auth:AuthConfiguration){
 const app=new AgentApplication({storage:new MemoryStorage(),adapter:new CloudAdapter(auth)});
 app.onConversationUpdate('membersAdded',async context=>{await context.sendActivity(WELCOME);});
 app.onActivity(ActivityTypes.Message,async context=>{
  const a=context.activity;
  // A channel conversation is not sufficient isolation for group chats: partition by sender and tenant too.
  const tenant=(a.channelData as {tenant?:{id?:string}}|undefined)?.tenant?.id??'local';
  const key=JSON.stringify([a.channelId,tenant,a.conversation?.id,a.from?.id]);
  try{if(!a.conversation?.id||!a.from?.id)throw Error('identity');await context.sendActivity(await engine.reply(key,a.text??''));}
  catch{await context.sendActivity('Request could not be completed safely. Check configuration, required tool fields and policy scope; retry. No ticket or account change was made.');}
 });return app;
}
