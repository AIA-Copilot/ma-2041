// Synthetic classroom policy. Not tenant content, ACL trimming or hosted file_search.
export const passages = [
 {id:'P1', title:'Lost device and security', keywords:['lost','stolen','laptop','security','incident','data','risk','device'], text:'Report lost or stolen devices and possible data exposure to Security immediately. Do not promise a remote wipe or containment. Prepare a draft escalation only.'},
 {id:'P2', title:'Access recovery', keywords:['access','login','signin','sign','password','account','locked','support'], text:'For access issues, verify identity using the approved service desk process. Never collect passwords, MFA codes or recovery codes. Draft an access support plan; no access changes are made.'},
 {id:'P3', title:'Outage triage', keywords:['outage','department','users','unavailable','service','impact','support'], text:'Department-wide outages affecting at least 25 users are P1 for Incident Management. Other multi-user issues (at least 10 affected users) are P2; individual issues are P3. Security/data-risk incidents override all routing and go to Security as P1.'},
 {id:'P4', title:'Equipment purchase exclusions', keywords:['purchase','reimbursement','expense','equipment','buy'], text:'Purchases and reimbursement are outside this support workflow. Refer to Procurement; do not invent approval limits or approve spending.'}
];
export const MAX_PASSAGES = 2; // Lab 2 edit point; bounded local lexical retrieval.
export function retrieve(query: string) {
 const words=new Set(query.toLowerCase().match(/[a-z0-9]+/g)??[]);
 return passages.map(p=>({p,score:p.keywords.filter(w=>words.has(w)).length}))
  .filter(x=>x.score>0).sort((a,b)=>b.score-a.score||a.p.id.localeCompare(b.p.id)).slice(0,MAX_PASSAGES).map(x=>x.p);
}
