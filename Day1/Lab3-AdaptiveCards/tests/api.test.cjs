const {test}=require('node:test');
const assert=require('node:assert/strict');
const {HttpRequest,InvocationContext}=require('@azure/functions');
const {dishes}=require('../dist/src/functions/dishes.js');
const {placeOrder}=require('../dist/src/functions/placeOrder.js');
const ctx=new InvocationContext({functionName:'offline-test'});
function post(body){return new HttpRequest({method:'POST',url:'http://localhost/api/orders',body:{string:JSON.stringify(body)}});}
test('known order returns simulated confirmation',async()=>{
 const r=await placeOrder(post({dishes:[{name:'spaghetti',quantity:1},{name:'iced tea',quantity:1}]}),ctx);
 assert.equal(r.status,201);assert.equal(r.jsonBody.status,'confirmed');assert.ok(r.jsonBody.total_price>0);
});
for(const body of [null,{}, {dishes:[]},{dishes:[{name:'spaghetti',quantity:-1}]},{dishes:[{}]},{dishes:[{name:'nonexistent dish',quantity:1}]}]){
 test('reject invalid order '+JSON.stringify(body),async()=>assert.equal((await placeOrder(post(body),ctx)).status,400));
}

test('menu filters course and excludes dairy',async()=>{
 const r=await dishes(new HttpRequest({method:'GET',url:'http://localhost/api/dishes?course=lunch&allergens=dairy'}),ctx);
 assert.equal(r.status,200);assert.ok(r.jsonBody.dishes.length>0);
 assert.ok(r.jsonBody.dishes.every(d=>d.course==='lunch' && !d.allergens.includes('dairy')));
});
