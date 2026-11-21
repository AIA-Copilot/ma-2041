import fs from 'node:fs';
const id=process.argv[2];
if(!id || !/^[a-zA-Z0-9]{3,32}$/.test(id)) throw Error('Pass the actual external connection ID from your successful connector log (3–32 alphanumeric characters).');
const path='appPackage/declarativeAgent.json';
const agent=JSON.parse(fs.readFileSync(path));
agent.capabilities=[{name:'GraphConnectors',connections:[{connection_id:id}]}];
fs.writeFileSync(path,JSON.stringify(agent,null,2)+'\n');
console.log('Local manifest updated. Verify connection ownership, then provision separately.');
