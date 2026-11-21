const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { LongRunningOperationMiddleware } = require('../dist/src/longRunningOperationMiddleware');

// Only external boundaries are replaced. Schema, invocation and middleware below
// execute the actual freshly compiled modules; no network/Functions host starts.
function load(relative, overrides) {
  const filename = require.resolve(relative);
  const module = { exports: {} };
  const localRequire = id => Object.hasOwn(overrides, id) ? overrides[id] : require(require.resolve(id, { paths: [path.dirname(filename)] }));
  vm.runInNewContext(fs.readFileSync(filename, 'utf8'), { require: localRequire, module, exports: module.exports, process, console, Date }, { filename });
  return module.exports;
}
function operation(statuses, http = 200, timeout = 50, slow = false) {
  const middleware = new LongRunningOperationMiddleware(1, timeout);
  let calls = 0;
  middleware.setNext({ async execute(context) {
    if (++calls === 1) context.response = new Response(null, { status: 202, headers: { Location: 'https://offline.invalid/operations/1' } });
    else {
      if (slow) await new Promise(resolve => setTimeout(resolve, 40));
      const status = statuses[Math.min(calls - 2, statuses.length - 1)];
      context.response = new Response(JSON.stringify({ status }), { status: http });
    }
  }});
  return () => middleware.execute({ request: 'https://offline.invalid/schema', options: { method: 'POST', body: '{}' } });
}
for (const status of ['failed', 'unknownFutureValue', 'unspecified', 'succeeded', undefined]) {
  test(`operation rejects non-success status ${status}`, async () => {
    await assert.rejects(operation([status]), /operation|status/i);
  });
}
test('only completed succeeds, including inprogress first', async () => {
  await operation(['inprogress', 'completed'])();
});
test('bad polling HTTP fails', async () => {
  await assert.rejects(operation(['completed'], 503), /HTTP.*503/i);
});
test('deadline bounds repeated inprogress', async () => {
  // Finite transport sequence also lets the unfixed implementation fail cleanly.
  await assert.rejects(operation([...Array(30).fill('inprogress'), 'completed'], 200, 8), /timed out/i);
});
test('deadline bounds slow polling HTTP', async () => {
  await assert.rejects(operation(['completed'], 200, 8, true), /timed out/i);
});

function invocation(runOperation, connectionResult = true) {
  const logs = []; let ingested = false; let settings = false;
  const config = { connector: { id: 'offline', schema: [] }, context: { log: x => logs.push(x), error() {} } };
  const client = { api() { return { header() { return this; }, async get() { throw { statusCode: 404 }; }, post: runOperation }; } };
  const schema = load('../dist/src/schema', { './graphClient': { getClient: () => client } });
  const functions = load('../dist/src/functions/connections', {
    '@azure/functions': { app: { timer() {} } },
    '../connection': { ensureConnection: async () => connectionResult, setSearchSettings: async () => { settings = true; } },
    '../schema': schema,
    '../ingest': { ingestContent: async () => { ingested = true; } },
    '../config': { initConfig: () => config }
  });
  return { run: () => functions.deployConnection({}, config.context), logs, touched: () => settings || ingested };
}
for (const [name, run] of [
  ['failed schema', () => operation(['failed'])()],
  ['unknown schema', () => operation(['unknownFutureValue'])()],
  ['HTTP schema error', () => operation(['completed'], 500)()],
  ['schema timeout', () => operation([...Array(30).fill('inprogress'), 'completed'], 200, 8)()]
]) {
  test(`${name} cannot log schema success or reach settings/ingestion`, async () => {
    const app = invocation(run);
    await assert.rejects(app.run);
    assert.equal(app.logs.some(x => x.includes('was created')), false);
    assert.equal(app.touched(), false);
  });
}
test('completed schema reaches success log and ingestion', async () => {
  const app = invocation(operation(['completed']));
  await app.run();
  assert.equal(app.logs.some(x => x.includes('was created')), true);
  assert.equal(app.touched(), true);
});
for (const result of [false, undefined]) {
  test(`connection result ${result} fails invocation before schema/ingestion`, async () => {
    let schemaCalled = false;
    const app = invocation(async () => { schemaCalled = true; }, result);
    // Explicit undefined must not activate invocation helper's default argument.
    if (result === undefined) {
      const functions = load('../dist/src/functions/connections', {
        '@azure/functions': { app: { timer() {} } },
        '../connection': { ensureConnection: async () => undefined },
        '../schema': { ensureSchema: async () => { schemaCalled = true; } },
        '../ingest': {}, '../config': { initConfig: () => ({}) }
      });
      await assert.rejects(() => functions.deployConnection({}, {}), /connection/i);
    } else await assert.rejects(app.run, /connection/i);
    assert.equal(schemaCalled, false);
    assert.equal(app.touched(), false);
  });
}
test('real ensureConnection HTTP failure fails the invocation', async () => {
  const logs = []; let schemaCalled = false; let ingested = false;
  const connection = load('../dist/src/connection', {
    './graphClient': { getClient: () => ({ api: () => ({ get: async () => { throw { statusCode: 500 }; } }) }) }
  });
  const functions = load('../dist/src/functions/connections', {
    '@azure/functions': { app: { timer() {} } }, '../connection': connection,
    '../schema': { ensureSchema: async () => { schemaCalled = true; } },
    '../ingest': { ingestContent: async () => { ingested = true; } },
    '../config': { initConfig: () => ({ connector: { id: 'offline' }, context: { log: x => logs.push(x), error() {} } }) }
  });
  await assert.rejects(() => functions.deployConnection({}, {}), /connection/i);
  assert.equal(schemaCalled, false);
  assert.equal(ingested, false);
  assert.equal(logs.some(x => x.includes('was created')), false);
});
test('valid settings select explicit client-secret credential without token request', () => {
  const keys = ['AZURE_TENANT_ID', 'AZURE_CLIENT_ID', 'AZURE_CLIENT_SECRET'];
  const saved = keys.map(k => process.env[k]);
  let selected = false;
  try {
    keys.forEach(k => { process.env[k] = 'offline-sensitive-sentinel'; });
    const client = load('../dist/src/graphClient', {
      '@azure/identity': { ClientSecretCredential: class { constructor(...values) { selected = true; assert.equal(values.length, 3); assert.ok(values.every(v => v === 'offline-sensitive-sentinel')); } } }
    });
    client.getClient();
    assert.equal(selected, true);
  } finally { keys.forEach((k, i) => { if (saved[i] === undefined) delete process.env[k]; else process.env[k] = saved[i]; }); }
});
test('credential settings fail closed without leaking values', () => {
  const { getClient } = require('../dist/src/graphClient');
  const keys = ['AZURE_TENANT_ID', 'AZURE_CLIENT_ID', 'AZURE_CLIENT_SECRET'];
  const saved = keys.map(k => process.env[k]);
  try {
    for (const missing of keys) {
      keys.forEach(k => { process.env[k] = 'offline-sensitive-sentinel'; });
      process.env[missing] = '   ';
      assert.throws(getClient, e => e.message.includes(missing) && !e.message.includes('offline-sensitive-sentinel'));
    }
  } finally { keys.forEach((k, i) => { if (saved[i] === undefined) delete process.env[k]; else process.env[k] = saved[i]; }); }
});
test('F5 installs once before Azurite, never in host/watch/clean chain', () => {
  const tasks = JSON.parse(fs.readFileSync(path.join(__dirname, '../.vscode/tasks.json'))).tasks;
  const order = [];
  function visit(label) {
    const task = tasks.find(t => t.label === label);
    assert.ok(task, label);
    for (const dep of [task.dependsOn || []].flat()) visit(dep);
    order.push(task);
  }
  visit('TTK'); visit('func: host start');
  assert.equal(order.filter(t => /npm ci/.test(t.command || '')).length, 1);
  assert.ok(order.findIndex(t => t.label === 'Install Dependencies') < order.findIndex(t => t.label === 'Start Azurite emulator'));
  assert.equal(tasks.find(t => t.label === 'TTK').dependsOrder, 'sequence');
  assert.ok(tasks.find(t => t.label === 'Install Dependencies').windows.command.startsWith('npm.cmd'));
});
test('Azurite disables telemetry', () => {
  assert.match(require('../package.json').scripts.storage, /--disableTelemetry\b/);
});
