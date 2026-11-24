# Zava Travel Connector

Indexes five explicitly fictional Zava documents from `content/`: arrival/office, hotels, ground transport reimbursement, accessibility and support. Follow the [course learner guide](../../../docs/D1_Lab3.md) and [one-time setup](../SETUP.md), not upstream deployment instructions.

The connector remains local-only, with app-only Graph write permissions and tenant-wide `everyone` item ACLs. Use only synthetic public data. After authorized ingestion, add its actual connection ID to the existing Lab 1 ZavaLab1 agent alongside WebSearch. No new agent, Azure deployment, public tunnel or content server is needed.

Each student uses a separate tenant. Use `CONNECTOR_ID=zavatravel` and `CONNECTOR_NAME=Zava Travel`; the actual connection ID is `zavatravellocal`. Metadata is `id`, `title`, `lastModified`, `owner`, `abstract`; the parser constructs `url` from the public course base plus the ID and `.md`. `owner` is mapped through the item model, adapter, schema and search card. Existing feedback schemas/cards are not migrated automatically. CF IDs are retained as stable filenames, not customer-feedback semantics.

Offline check after dependencies are prepared: `npm run build` then `node scripts/verify-offline.cjs`. This executes the real parser/adapter with Graph blocked and does not prove tenant ingestion or Copilot behavior. Package name and dependency metadata retain upstream identity; see [provenance](../PROVENANCE.md) and [license](../LICENSE).

## Credit

Thanks to authors of the the Policies Copilot Connector sample which is the bootstrap project for this connector for Trey Research scenario. [https://github.com/pnp/graph-connectors-samples/tree/main/samples/nodejs-typescript-policies](https://github.com/pnp/graph-connectors-samples/tree/main/samples/nodejs-typescript-policies) 

## Disclaimer

**THIS CODE IS PROVIDED *AS IS* WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING ANY IMPLIED WARRANTIES OF FITNESS FOR A PARTICULAR PURPOSE, MERCHANTABILITY, OR NON-INFRINGEMENT.**
