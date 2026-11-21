const {test}=require('node:test');
const assert=require('node:assert/strict');
const {getAllItems}=require('../dist/src/services/itemsService.js');
const {getExternalItemFromItem}=require('../dist/src/custom/getExternalItemFromItem.js');
test('real IT policy files transform to schema and explicit public-in-tenant ACL',()=>{
 const items=getAllItems({connector:{scenario:'it',baseUrl:'https://localhost:3000/'}});
 assert.equal(items.length,10);assert.equal(new Set(items.map(x=>x.id)).size,10);
 for(const item of items){const x=getExternalItemFromItem(item);assert.ok(x.content.value.length>100);assert.ok(x.properties.title);assert.equal(x.acl[0].type,'everyone');assert.ok(x.properties.url.startsWith('https://localhost:3000/'));}
});
