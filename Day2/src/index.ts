import {readConfig,PolicyAgent} from './core';
import {createAzureTransport} from './model';
import {startHost} from './host';
try{
 const config=readConfig(process.env);
 startHost(new PolicyAgent(createAzureTransport(config.endpoint),config.model),config.mode);
}catch{console.error('STARTUP BLOCKED: configure PROJECT_ENDPOINT, MODEL_DEPLOYMENT_NAME and HOST_MODE; production also requires approved channel credentials. No fallback model exists.');process.exitCode=1;}
