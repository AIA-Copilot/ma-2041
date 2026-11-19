import {AIProjectClient} from '@azure/ai-projects';
import {AzureCliCredential} from '@azure/identity';
import {Transport} from './core';
// Actual @azure/ai-projects 2.11.0 API. No Foundry agent resource is created.
// Responses requests use the project /openai/v1 endpoint and https://ai.azure.com/.default.
export function createAzureTransport(endpoint:string, credential?:ConstructorParameters<typeof AIProjectClient>[1]):Transport{
 const project=new AIProjectClient(endpoint,credential??new AzureCliCredential());
 const client=project.getOpenAIClient({timeout:45000,maxRetries:0});
 return {create:async(request)=>client.responses.create(request)};
}
