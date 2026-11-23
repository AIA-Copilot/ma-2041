// Registration only: no App Service, container, model, or Foundry resource.
param botName string
param botId string
param tenantId string
param botEndpoint string
resource bot 'Microsoft.BotService/botServices@2022-09-15' = {
  name: botName
  location: 'global'
  kind: 'azurebot'
  sku: { name: 'F0' }
  properties: {
    displayName: 'ExpenseClaimLab'
    endpoint: '${botEndpoint}/api/messages'
    msaAppId: botId
    msaAppTenantId: tenantId
    msaAppType: 'SingleTenant'
  }
}
resource teams 'Microsoft.BotService/botServices/channels@2022-09-15' = {
  parent: bot
  name: 'MsTeamsChannel'
  location: 'global'
  properties: {
    channelName: 'MsTeamsChannel'
    properties: { isEnabled: true }
  }
}
