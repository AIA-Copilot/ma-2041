import {readConfig} from '../src/core';
try{readConfig(process.env);console.log('Configuration shape PASS. This does not validate Azure login, roles, model capability or channel credentials.');}catch(e){console.error((e as Error).message);process.exitCode=1;}
