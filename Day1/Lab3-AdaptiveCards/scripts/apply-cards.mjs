import fs from 'node:fs';
const path='appPackage/ai-plugin.json';
const plugin=JSON.parse(fs.readFileSync(path));
for (const [name,file] of [['getDishes','dish'],['placeOrder','order']]) {
 const fn=plugin.functions.find(f=>f.name===name);
 if(!fn) throw Error(`Missing function ${name}`);
 fn.capabilities.response_semantics.static_template=JSON.parse(fs.readFileSync(`cards/${file}.json`));
}
fs.writeFileSync(path,JSON.stringify(plugin,null,2)+'\n');
console.log('Embedded both cards locally. Rebuild/provision via local debugging to test in Copilot.');
