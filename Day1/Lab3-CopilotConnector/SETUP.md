# One-time preparation — Day 1 Lab 3

Run before class, after the root course setup. Learners do not clone or install again in the lab.

## Windows VM prerequisites

- VS Code, Microsoft 365 Agents Toolkit (`TeamsDevApp.ms-teams-vscode-extension`) and Azure Functions extension (`ms-azuretools.vscode-azurefunctions`).
- Portable Node **22.22.2** at `C:\Users\Admin\ma-2041\tools\node-v22.22.2-win-x64` and the course `scripts/Use-Node.ps1`. Node 24 is for WIQD, not this connector.
- Azure Functions **Core Tools v4 x64**, installed once with Microsoft's Windows installer; use the [official Core Tools installation instructions](https://learn.microsoft.com/azure/azure-functions/functions-run-local#install-the-azure-functions-core-tools). This lab deliberately removes the project npm `azure-functions-core-tools` dependency. Do not use `npx func` to download a substitute. A local Functions host is not Azure cloud hosting.
- Microsoft 365 training tenant, licensed Copilot account able to use declarative agents, custom-app upload allowed, app-registration permission, and an assigned administrator who can grant Microsoft Graph **application** permissions. No Azure subscription is required. Microsoft 365 service/network access is required; this is not an offline tenant lab.
- Administrator approval to ingest the five **synthetic public** Zava travel/arrival/policy documents with the sample's tenant-wide `everyone` ACL. Never replace them with confidential material.

### Prepare the Day 1 tools once

Start `scripts/Prepare-Day1.ps1` from the course repository during Lab 1. It prepares the pinned Node runtimes, verified interactive Core Tools v4 installer, Azure Functions extension, connector dependencies/build, and WIQD 1.0.0. See [Start Day 1 preparation](../../docs/D1_Lab1.md#start-day-1-preparation).

Complete normal installer prompts and wait for `DAY 1 PREPARATION COMPLETE`. Before Lab 3, close all VS Code windows and reopen the app. Verify `func --version` reports `4.x`. The connector uses Node 22; WIQD uses Node 24. New manual npm terminals must select their runtime with `scripts/Use-Node.ps1`.

The connector install retains `npm ci --ignore-scripts --no-audit --no-fund`. Do not run `npm audit fix` or refresh dependencies during class. No tenant provisioning, authentication, terms acceptance or Functions host startup occurs in preparation. Open the `connector` folder itself in the right window when starting Lab 3.

## Delivery boundary

Use only `m365agents.local.yml` / the **local** environment. The active general lifecycle is also local-only to avoid accidental ARM deployment. Original `teamsapp*.yml` are preserved under `../upstream-reference` for provenance, not execution. Preserved `infra/` and `.env.dev` are upstream reference assets and are not lesson steps. Do not open the upstream-reference folder as a Toolkit project. The course guide and this setup file control this adaptation. The continuing agent project is Lab 1’s `C:\Users\Admin\AgentsToolkitProjects\ZavaLab1`; do not create a third agent. Each student has a separate tenant; use the supplied `zavatravel` base ID (`zavatravellocal` after the environment suffix). Existing feedback schemas/search cards are not migrated. Publish all five course content files before testing citation reachability.
