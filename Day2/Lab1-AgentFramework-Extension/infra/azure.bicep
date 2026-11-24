param webAppName string
param planName string
param location string = resourceGroup().location
param botName string
param botId string
param tenantId string
@secure()
param botPassword string
param projectEndpoint string
param modelDeploymentName string
param foundrySubscriptionId string
param foundryResourceGroup string
param foundryAccountName string
param foundryProjectName string

resource plan 'Microsoft.Web/serverfarms@2024-04-01' = {
  name: planName
  location: location
  kind: 'linux'
  sku: { name: 'F1', tier: 'Free' }
  properties: { reserved: true }
}
resource site 'Microsoft.Web/sites@2024-04-01' = {
  name: webAppName
  location: location
  kind: 'app,linux'
  identity: { type: 'SystemAssigned' }
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.13'
      appCommandLine: 'python host.py'
      alwaysOn: false
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      appSettings: [
        { name: 'SCM_DO_BUILD_DURING_DEPLOYMENT', value: '1' }
        { name: 'PORT', value: '8000' }
        { name: 'BOT_ID', value: botId }
        { name: 'BOT_TENANT_ID', value: tenantId }
        { name: 'BOT_PASSWORD', value: botPassword }
        { name: 'PROJECT_ENDPOINT', value: projectEndpoint }
        { name: 'MODEL_DEPLOYMENT_NAME', value: modelDeploymentName }
      ]
    }
  }
}
resource scm 'Microsoft.Web/sites/basicPublishingCredentialsPolicies@2024-04-01' = {
  parent: site
  name: 'scm'
  properties: { allow: false }
}
resource ftp 'Microsoft.Web/sites/basicPublishingCredentialsPolicies@2024-04-01' = {
  parent: site
  name: 'ftp'
  properties: { allow: false }
}
resource easyAuth 'Microsoft.Web/sites/config@2024-04-01' = {
  parent: site
  name: 'authsettingsV2'
  properties: { platform: { enabled: false } }
}
module bot './bot.bicep' = {
  name: 'expense-bot'
  params: {
    botName: botName
    botId: botId
    tenantId: tenantId
    botEndpoint: 'https://${site.properties.defaultHostName}'
  }
}
module modelRole './model-role.bicep' = {
  name: 'expense-model-role'
  scope: resourceGroup(foundrySubscriptionId, foundryResourceGroup)
  params: {
    accountName: foundryAccountName
    projectName: foundryProjectName
    principalId: site.identity.principalId
  }
}
output WEBAPP_RESOURCE_ID string = site.id
output BOT_ENDPOINT string = 'https://${site.properties.defaultHostName}'
