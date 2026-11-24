// Offline regression: capture the actual compiled Graph request. No network.
const assert = require('node:assert/strict');
const Module = require('node:module');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const originalLoad = Module._load;
let calls = [];
Module._load = function(request, parent, isMain) {
  if (request.endsWith('graphClient')) return { getClient: () => ({
    api: endpoint => ({
      get: async () => { calls.push({method:'GET', endpoint}); return {}; },
      patch: async body => { calls.push({method:'PATCH', endpoint, body}); },
      post: async () => { throw new Error('Unexpected connection creation'); }
    })
  }) };
  return originalLoad.call(this, request, parent, isMain);
};
const {setSearchSettings} = require(path.join(root, 'dist/src/connection.js'));
const template = require(path.join(root, 'src/references/template.json'));
(async () => {
  for (const id of ['zavatravellocal', 'zavatravellocallocal', 'z'.repeat(32)]) {
    calls = [];
    await setSearchSettings({context:{log(){}}, connector:{id,template}});
    assert.deepEqual(calls.map(c=>c.method), ['GET','PATCH']);
    for (const call of calls) assert.equal(call.endpoint, '/external/connections/' + id);
    const card = calls[1].body.searchSettings.searchResultTemplates[0];
    assert.equal(card.id, 'zavatravel');
    assert.match(card.id, /^[A-Za-z0-9]{1,16}$/);
    assert.equal(card.layout, template);
    assert.equal(card.priority, 1);
  }
  console.log('PASS: 3 connection lengths keep their own endpoint and use a valid independent display-template ID. No network.');
})().catch(e=>{console.error(e);process.exitCode=1;});
