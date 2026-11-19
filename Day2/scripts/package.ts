import fs from 'node:fs';
import path from 'node:path';
import Ajv from 'ajv-draft-04';
import addFormats from 'ajv-formats';
import AdmZip from 'adm-zip';
import YAML from 'yaml';
const raw=fs.readFileSync('appPackage/manifest.json','utf8');
// Local validation IDs only: resulting ZIP is deliberately NOT an uploadable tenant artifact.
const fixture={'TEAMS_APP_ID':'11111111-1111-4111-8111-111111111111','BOT_ID':'22222222-2222-4222-8222-222222222222'};
const text=raw.replace(/\$\{\{(\w+)\}\}/g,(_m,k:string)=>{if(!(k in fixture))throw Error('Unresolved manifest variable '+k);return fixture[k as keyof typeof fixture];});
const manifest=JSON.parse(text),schema=JSON.parse(fs.readFileSync('schemas/MicrosoftTeams.v1.30.schema.json','utf8'));
const ajv=new Ajv({strict:false,allErrors:true});addFormats(ajv);const validate=ajv.compile<{bots:{botId:string}[],copilotAgents:{customEngineAgents:{id:string}[]},icons:Record<string,string>}>(schema);
if(!validate(manifest))throw Error(JSON.stringify(validate.errors));
if(manifest.bots[0].botId!==manifest.copilotAgents.customEngineAgents[0].id)throw Error('Agent identity mismatch');
for(const icon of Object.values(manifest.icons) as string[]){if(path.basename(icon)!==icon||!fs.existsSync('appPackage/'+icon))throw Error('Missing/unsafe icon');}
for(const name of ['m365agents.yml','m365agents.local.yml','m365agents.playground.yml']){
 const y=YAML.parse(fs.readFileSync(name,'utf8'));if(y.version!=='v1.11')throw Error('Unexpected lifecycle version');
 for(const phase of ['provision','deploy','publish'])for(const action of y[phase]??[]){if(!['cli/runNpmCommand','file/createOrUpdateEnvironmentFile'].includes(action.uses))throw Error('Unsafe lifecycle action');}
}
const tasks=JSON.parse(fs.readFileSync('.vscode/tasks.json','utf8')).tasks;
const labels=new Set(tasks.map((t:any)=>t.label));for(const task of tasks)for(const d of task.dependsOn??[])if(!labels.has(d))throw Error('Missing task '+d);
const launch=JSON.parse(fs.readFileSync('.vscode/launch.json','utf8'));for(const c of launch.compounds)if(!labels.has(c.preLaunchTask))throw Error('Missing prelaunch task');
fs.mkdirSync('appPackage/build',{recursive:true});const zip=new AdmZip();zip.addFile('manifest.json',Buffer.from(text));for(const icon of Object.values(manifest.icons)as string[])zip.addLocalFile('appPackage/'+icon);
zip.writeZip('appPackage/build/LOCAL-VALIDATION-ONLY.zip');
console.log('PASS: official Teams v1.30 schema; icons; same bot ID; lifecycle allowlist; task references. LOCAL-VALIDATION-ONLY.zip uses dummy IDs. NOT published or install-tested.');
