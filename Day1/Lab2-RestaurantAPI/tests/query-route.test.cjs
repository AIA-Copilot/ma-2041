const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {HttpRequest,InvocationContext}=require('@azure/functions');
const {dishes}=require('../dist/src/functions/dishes.js');
const spec=fs.readFileSync(path.join(__dirname,'../appPackage/apiSpecificationFile/ristorante.yml'),'utf8');
test('allergens explicitly serialize as one comma-separated query parameter',async()=>{
 const parameter=spec.split('          name: allergens\n')[1].split('      responses:')[0];
 assert.match(parameter,/^          style: form$/m);
 assert.match(parameter,/^          explode: false$/m);
 const r=await dishes(new HttpRequest({method:'GET',url:'http://localhost/api/dishes?course=lunch&allergens=dairy,gluten'}),new InvocationContext({functionName:'offline-test'}));
 assert.ok(r.jsonBody.dishes.length>0);
 assert.ok(r.jsonBody.dishes.every(d=>!d.allergens.includes('dairy')&&!d.allergens.includes('gluten')));
});
test('plural orders route agrees with OpenAPI and request examples',()=>{
 const source=fs.readFileSync(path.join(__dirname,'../src/functions/placeOrder.ts'),'utf8');
 assert.match(source,/app\.http\("orders",/);
 assert.match(spec,/^  \/orders:$/m);
 assert.doesNotMatch(spec,/^  \/order:$/m);
});
