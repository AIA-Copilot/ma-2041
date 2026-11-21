const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {HttpRequest, InvocationContext} = require('@azure/functions');
const {dishes} = require('../dist/src/functions/dishes.js');
const {placeOrder} = require('../dist/src/functions/placeOrder.js');
const spec = fs.readFileSync(path.join(__dirname, '../appPackage/apiSpecificationFile/ristorante.yml'), 'utf8');
const ctx = new InvocationContext({functionName: 'offline-contract-test'});

// Targeted structural checks for this block-style YAML, not a general YAML or
// OpenAPI validator. Scope each check by indentation to avoid matching another
// operation/property; no new parser dependency or lockfile changes are needed.
function block(text, key, indent) {
  const lines = text.split(/\r?\n/);
  const start = lines.indexOf(' '.repeat(indent) + key + ':');
  assert.notEqual(start, -1, `missing contract block ${key} at indent ${indent}`);
  let end = start + 1;
  while (end < lines.length && (!lines[end].trim() || lines[end].search(/\S/) > indent)) end++;
  return lines.slice(start + 1, end).join('\n');
}
function schemaFor(operation, status) {
  const responses = block(block(block(spec, operation, 2), operation === '/dishes' ? 'get' : 'post', 4), 'responses', 6);
  return block(block(block(block(responses, `'${status}'`, 8), 'content', 10), 'application/json', 12), 'schema', 14);
}
function post(quantity) {
  return new HttpRequest({method: 'POST', url: 'http://localhost/api/orders',
    body: {string: JSON.stringify({dishes: [{name: 'spaghetti', quantity}]})}});
}

test('OpenAPI menu schema describes the actual dishes envelope, including empty results', async () => {
  const schema = schemaFor('/dishes', 200);
  assert.match(schema, /^ {16}type: object$/m);
  assert.match(block(schema, 'required', 16), /^ {18}- dishes$/m);
  const menu = block(block(schema, 'properties', 16), 'dishes', 18);
  assert.match(menu, /^ {20}type: array$/m);
  assert.match(block(menu, 'items', 20), /^ {22}\$ref: '#\/components\/schemas\/Dish'$/m);
  for (const query of ['', '?name=__no_such_menu_item__']) {
    const response = await dishes(new HttpRequest({method: 'GET', url: 'http://localhost/api/dishes' + query}), ctx);
    assert.equal(response.status, 200);
    assert.deepEqual(Object.keys(response.jsonBody), ['dishes']);
    assert.ok(Array.isArray(response.jsonBody.dishes));
    if (query) assert.equal(response.jsonBody.dishes.length, 0);
    else assert.ok(response.jsonBody.dishes.length > 0);
  }
});

test('OpenAPI quantity is an integer from 1 to 100, matching handler boundaries', async () => {
  const order = block(block(spec, '/orders', 2), 'post', 4);
  const request = block(block(block(block(order, 'requestBody', 6), 'content', 8), 'application/json', 10), 'schema', 12);
  const items = block(block(block(request, 'properties', 14), 'dishes', 16), 'items', 18);
  const quantity = block(block(items, 'properties', 20), 'quantity', 22);
  assert.match(quantity, /^ {24}type: integer$/m);
  assert.match(quantity, /^ {24}minimum: 1$/m);
  assert.match(quantity, /^ {24}maximum: 100$/m);
  for (const [value, expected] of [[1, 201], [100, 201], [0, 400], [-1, 400], [101, 400], [1.5, 400], ['1', 400], [null, 400], [undefined, 400]]) {
    const response = await placeOrder(post(value), ctx);
    assert.equal(response.status, expected, `quantity ${JSON.stringify(value)}`);
    if (expected === 400) assert.deepEqual(response.jsonBody, {message: 'Invalid order format'});
  }
});

test('order confirmation remains a single object matching declared property types', async () => {
  const schema = schemaFor('/orders', 201);
  assert.match(schema, /^ {16}type: object$/m);
  const properties = block(schema, 'properties', 16);
  const response = await placeOrder(post(1), ctx);
  assert.equal(response.status, 201);
  assert.deepEqual(Object.keys(response.jsonBody).sort(), ['order_id', 'status', 'total_price']);
  for (const [key, type] of [['order_id', 'integer'], ['status', 'string'], ['total_price', 'number']]) {
    assert.match(block(properties, key, 18), new RegExp(`^ {20}type: ${type}$`, 'm'));
    if (type === 'integer') assert.ok(Number.isInteger(response.jsonBody[key]));
    else assert.equal(typeof response.jsonBody[key], type);
  }
  assert.equal(response.jsonBody.status, 'confirmed');
});
