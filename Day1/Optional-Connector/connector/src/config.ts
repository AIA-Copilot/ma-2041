import { InvocationContext } from '@azure/functions';
import schema from './references/schema.json';
import template from './references/template.json';
import { Config } from './models/Config';
import { ExternalConnectors } from '@microsoft/microsoft-graph-types';

/**
 * Builds the configuration object based on environment variables.
 */
export function initConfig(context: InvocationContext): Config {
  const config = {
    context: context,
    clientId: process.env.AZURE_CLIENT_ID,
    connector: {
      id: `${process.env.CONNECTOR_ID}${process.env.TEAMSFX_ENV}`,
      name: process.env.CONNECTOR_NAME,
      description: process.env.CONNECTOR_DESCRIPTION,
      schema: schema as ExternalConnectors.Schema,
      baseUrl: process.env.CONNECTOR_BASE_URL,
      template: template
    }
  };

  if (!/^[A-Za-z0-9]{1,32}$/.test(config.connector.id)) {
    throw new Error("Combined CONNECTOR_ID + TEAMSFX_ENV must be 1-32 alphanumeric characters.");
  }
  return config;
}
