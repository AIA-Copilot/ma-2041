import express from 'express';
import {createAgentRequestHandler} from '@microsoft/agents-hosting-express';
import {createAgent} from './agent';
import {PolicyAgent} from './core';
export function startHost(engine:PolicyAgent,mode:string,port=3978){
 const app=express();app.use(express.json({limit:'32kb'}));
 app.get('/health',(_req,res)=>{res.json({status:'ready',model:'configured-not-probed',mode});});
 // Local SDK adapter is deliberately unauthenticated and loopback-only. Do not tunnel it.
 app.use('/api/messages',(req,res,next)=>{
  if(mode==='local'){
   try{const u=new URL(req.body.serviceUrl);if(!['localhost','127.0.0.1','[::1]'].includes(u.hostname)||u.protocol!=='http:'||u.port!=='56150'||u.username||u.password)throw Error();}catch{res.status(400).json({error:'Local Playground serviceUrl required'});return;}
  }next();
 });
 const auth=mode==='local'?{clientId:'',tenantId:'',clientSecret:''}:{clientId:process.env.clientId,tenantId:process.env.tenantId,clientSecret:process.env.clientSecret};
 app.post('/api/messages',createAgentRequestHandler(createAgent(engine,auth),auth));
 app.use((_err:unknown,_req:express.Request,res:express.Response,_next:express.NextFunction)=>{if(!res.headersSent)res.status(500).json({error:'Activity failed safely'});});
 return app.listen(port,mode==='local'?'127.0.0.1':'0.0.0.0',()=>console.log(`Server listening to port ${port} (${mode})`));
}
