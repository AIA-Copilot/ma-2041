import {test} from 'node:test';import assert from 'node:assert/strict';import {retrieve} from '../src/policy';
test('Lab 2 learner edit: phishing is retrieved as security, unknown topics excluded',()=>{assert.equal(retrieve('phishing')[0]?.id,'P1');assert.deepEqual(retrieve('banana astrophysics'),[]);});
