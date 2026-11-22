// Offline only: no host, credentials, Graph calls or tenant writes.
const assert = require('node:assert/strict');
const Module = require('node:module');
const path = require('node:path');
process.chdir(path.resolve(__dirname, '..'));
const root = process.cwd();
const registered = [];
const originalLoad = Module._load;
Module._load = function(request, parent, isMain) {
  if (request === '@azure/functions') return { app: { timer: (name, settings) => registered.push({name, settings}) } };
  if (request.endsWith('graphClient')) return {getClient: () => ({api: () => {throw new Error('NETWORK FORBIDDEN in offline verification');}})};
  return originalLoad.call(this, request, parent, isMain);
};
process.env.CONNECTOR_ID = 'tfcverify';
process.env.TEAMSFX_ENV = 'local';
process.env.CONNECTOR_BASE_URL = 'https://github.com/microsoft/copilot-camp/blob/937fd5b6af4c705597381dd24d5e8aa7693521ad/src/extend-m365-copilot/path-e-bonus-gc-lab/trey-feedback-connector/content/';
const {initConfig} = require(path.join(root, 'dist/src/config.js'));
const {getAllItems} = require(path.join(root, 'dist/src/services/itemsService.js'));
const {getExternalItemFromItem} = require(path.join(root, 'dist/src/custom/getExternalItemFromItem.js'));
const config = initConfig({log(){},warn(){},error(){}});
assert.equal(config.connector.id, 'tfcverifylocal');
const items = getAllItems(config);
assert.deepEqual(items.map(i=>i.id).sort(), ['CF-001','CF-002','CF-003','CF-004','CF-005']);
for (const item of items) {
  assert.ok(item.title && item.content && item.consultant);
  assert.ok(item.url.endsWith(`${item.id}.md`));
  const external = getExternalItemFromItem(item);
  assert.equal(external.acl[0].type, 'everyone');
  assert.equal(external.content.type, 'text');
  assert.equal(external.properties.url, item.url);
}
process.env.CONNECTOR_ID = 'x'.repeat(28);
assert.throws(()=>initConfig({}), /1-32/);
process.env.CONNECTOR_ID = 'tfc-bad';
assert.throws(()=>initConfig({}), /1-32/);
process.env.CONNECTOR_ID = 'tfcverify';
process.env.AZURE_FUNCTIONS_ENVIRONMENT = 'Development';
require(path.join(root, 'dist/src/functions/connections.js'));
assert.deepEqual(registered.map(t=>t.name), ['deployConnection']);
assert.equal(registered[0].settings.runOnStartup, true);
console.log('PASS: five synthetic records, URL mapping, everyone ACL, ID guard, deploy-only timer registration; no handler invoked or network used.');
