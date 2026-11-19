import {test} from 'node:test';import assert from 'node:assert/strict';import {WELCOME,INSTRUCTIONS} from '../src/core';
test('Lab 1 learner edit: welcome and concise explanation style',()=>{assert.match(WELCOME,/Northstar lab support/);assert.match(INSTRUCTIONS,/Use at most three sentences/);});
