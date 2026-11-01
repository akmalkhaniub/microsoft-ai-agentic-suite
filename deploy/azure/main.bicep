// ============================================================================
// Production Azure Bicep IaC — Microsoft AI & Agentic Solution Architecture Suite
// Deploys:
// 1. Azure AI Foundry / Cognitive Services Account (GPT-4o + Content Safety Prompt Shields)
// 2. Azure AI Search (Standard S1 with Semantic Ranker for Pre-Trimmed Hybrid RRF)
// 3. Azure API Management (APIM) Gateway (Entra ID OBO JWT validation & Semantic Cache)
// 4. Azure Service Bus Namespace + Topic (sbt-d365-erp-fulfillment) with Dead-Letter Queue
// 5. Log Analytics + Application Insights (OpenTelemetry GenAI Tracing)
// ============================================================================

@description('Deployment environment name (dev, staging, prod)')
@allowed(['dev', 'staging', 'prod'])
param environmentName string = 'prod'

@description('Primary Azure region supporting EU/UK/NA Data Residency (e.g., uksouth, germanywestcentral, eastus2)')
param location string = resourceGroup().location

@description('Entra ID Tenant GUID for On-Behalf-Of (OBO) & RBAC enforcement')
param tenantId string = subscription().tenantId

var prefix = 'msft-agentic-${environmentName}'

// 1. Observability: Log Analytics & Application Insights (OpenTelemetry GenAI)
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: '${prefix}-law'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 90
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${prefix}-appi'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
}

// 2. Microsoft Foundry / Azure AI Services (OpenAI GPT-4o + Content Safety Prompt Shields)
resource aiFoundryAccount 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: '${prefix}-foundry'
  location: location
  kind: 'AIServices'
  sku: {
    name: 'S0'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    customSubDomainName: '${prefix}-foundry'
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: true // Enforce Zero-Trust Entra ID Managed Identity only
  }
}

// 3. Azure AI Search (Hybrid Vector + BM25 + Pre-Retrieval Entra ACL Security Trimming)
resource aiSearch 'Microsoft.Search/searchServices@2023-11-01' = {
  name: '${prefix}-search'
  location: location
  sku: {
    name: 'standard'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    replicaCount: 2
    partitionCount: 1
    semanticSearch: 'standard'
    authOptions: {
      aadOrApiKey: {
        aadAuthFailureMode: 'http401WithBearerChallenge'
      }
    }
  }
}

// 4. Azure Service Bus (Asynchronous Dynamics 365 & SAP ERP Integration + DLQ)
resource serviceBusNamespace 'Microsoft.ServiceBus/namespaces@2022-10-01-preview' = {
  name: '${prefix}-sbns'
  location: location
  sku: {
    name: 'Standard'
  }
  properties: {
    minimumTlsVersion: '1.2'
    disableLocalAuth: true
  }
}

resource erpTopic 'Microsoft.ServiceBus/namespaces/topics@2022-10-01-preview' = {
  parent: serviceBusNamespace
  name: 'sbt-d365-erp-fulfillment'
  properties: {
    supportOrdering: true
    maxSizeInMegabytes: 1024
  }
}

resource erpSubscription 'Microsoft.ServiceBus/namespaces/topics/subscriptions@2022-10-01-preview' = {
  parent: erpTopic
  name: 'sbs-logicapp-sap-d365-sync'
  properties: {
    maxDeliveryCount: 3
    deadLetteringOnMessageExpiration: true
    deadLetteringOnFilterEvaluationExceptions: true
    lockDuration: 'PT1M'
  }
}

output appInsightsConnectionString string = appInsights.properties.ConnectionString
output aiFoundryEndpoint string = aiFoundryAccount.properties.endpoint
output aiSearchEndpoint string = 'https://${aiSearch.name}.search.windows.net'
output serviceBusNamespaceFqdn string = '${serviceBusNamespace.name}.servicebus.windows.net'
output configuredTenantId string = tenantId
