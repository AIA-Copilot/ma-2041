import { z } from 'zod';
export const MULTI_USER_THRESHOLD = 10; // Lab 3 rule edit point.
const argsSchema=z.object({
 category:z.enum(['access','device','outage']), impact:z.enum(['individual','department']),
 affectedUsers:z.number().int().min(1).max(10000), dataRisk:z.boolean(), summary:z.string().trim().min(4).max(240)
}).strict();
export const supportTool={type:'function' as const,name:'assess_support_request',description:'Assess a support request and return a draft plan only. Ask for all missing facts before calling; never infer dataRisk, category, impact or user count.',strict:true,
 parameters:{type:'object',additionalProperties:false,properties:{category:{type:'string',enum:['access','device','outage']},impact:{type:'string',enum:['individual','department']},affectedUsers:{type:'integer',minimum:1,maximum:10000},dataRisk:{type:'boolean'},summary:{type:'string',minLength:4,maxLength:240}},required:['category','impact','affectedUsers','dataRisk','summary']}};
export function executeTool(name:string, raw:string){
 if(name!==supportTool.name||raw.length>2048)throw Error('Tool denied');
 let parsed;try{parsed=argsSchema.parse(JSON.parse(raw));}catch{throw Error('Tool denied');}
 const a=parsed;
 const major=a.category==='outage'&&a.impact==='department'&&a.affectedUsers>=25;
 const priority=a.dataRisk||major?'P1':a.affectedUsers>=MULTI_USER_THRESHOLD?'P2':'P3';
 const queue=a.dataRisk?'Security':major?'Incident Management':a.category==='access'?'Identity Support':'Service Desk';
 return {status:'DRAFT_ONLY',priority,queue,summary:a.summary,humanApprovalRequired:true,actions:[a.dataRisk?'Notify Security via approved process; do not promise containment.':'Verify requester identity via approved process.', 'Have the service desk review this draft. No ticket was created or changed.']};
}
