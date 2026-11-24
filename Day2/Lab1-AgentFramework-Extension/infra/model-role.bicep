param accountName string
param projectName string
param principalId string
resource account 'Microsoft.CognitiveServices/accounts@2025-06-01' existing = {
  name: accountName
}
resource project 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' existing = {
  parent: account
  name: projectName
}
// Foundry User (formerly Azure AI User); verified Microsoft built-in role ID.
var roleId = '53ca6127-db72-4b80-b1b0-d745d6d5456d'
resource role 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(project.id, principalId, roleId)
  scope: project
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleId)
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}
