# Source provenance and change map

Sources retrieved publicly without GitHub sign-in. Pinned upstream commits are listed below. Offline Toolkit fixtures are included under `tests/fixtures/`; full historical evidence stays in the internal course workspace.

| Source | Pinned commit |
|---|---|
| MicrosoftLearning/mslearn-ai-agents | df5b56b41480298afc09abf28c79c0d1856f40dd |
| microsoft/Agents-for-python | c04354279a729a0feff072a776a7c32e0becc2bc |
| OfficeDev/microsoft-365-agents-toolkit | f3d7e73fef7bf22f2290635e34c13351c41ca55f |

Lab07: `Instructions/Exercises/07-agent-framework.md`, `Labfiles/07-agent-framework/python/{agent-framework.py,requirements.txt,.env,data.txt}`. The upstream Python file is a starter, not a completed solution. This candidate implements the completion blocks in the pinned official lesson, then extracts the reusable function; it does not pretend the learner's private file was read. Keep learner-completed original alongside for comparison. Supplied data.txt is byte-identical upstream synthetic data.

Change map: preserve FoundryChatClient + AzureCliCredential, PROJECT_ENDPOINT/MODEL_DEPLOYMENT_NAME, Agent name ExpenseClaimAgent, itemized expense/total objective, submit_claim tool and destination. Move input/print to console.py; return response; turn-local tool closure collects and returns visibly labelled simulation receipts; clarify no email was sent; route via authenticated SDK host. No alternative C# or portal-managed agent is created.

SDK references: `test_samples/app_style/empty_agent.py`, `test_samples/app_style/shared/start_server.py`, aiohttp JWT middleware, MSAL connection settings. Published packages **1.9.0** are the executable API authority; main has newer configuration changes. Actual installed signatures and tests drove the host, not an untested copy of main.

Toolkit references: `templates/vsc/python/basic-custom-engine-agent/{m365agents.local.yml.tpl,m365agents.yml.tpl,.vscode/tasks.json.tpl,src/app.py,appPackage/manifest.json.tpl,infra/botRegistration/azurebot.bicep}`; lifecycle schema `packages/fx-core/resource/yaml-schema/v1.12/yaml.schema.json`; Teams schema `packages/manifest/src/json-schemas/teams/v1.30/MicrosoftTeams.schema.json`. Icons copied from that pinned template. Lifecycle adaptation replaces multi-tenant dev.botframework registration with single-tenant Azure Bot through supported aadApp/create + arm/deploy actions, no compute deployment. R3 uses documented personal package installation and opens Copilot only after Teams succeeds; no Publish lifecycle is needed.

R2 Toolkit dispatch evidence (same pinned commit): `packages/vscode-extension/package.json` is retained verbatim as `tests/fixtures/toolkit-package.json` (SHA-256 `6e0e360f0e5b0252c6e4c4a30b5813bbbc4bcd9fc52f0591a3196e52aa7d8c40`). The regression reads its contributed task command schema; it does not invent an allowed enum. The copied fixture and its upstream commit bind this offline regression; it does not identify the extension installed in your VM.

- [CodeLens dispatch](https://github.com/OfficeDev/microsoft-365-agents-toolkit/blob/f3d7e73fef7bf22f2290635e34c13351c41ca55f/packages/vscode-extension/src/codeLensProvider.ts#L799-L804): `fx-extension.publish`, telemetry only.
- [Publish handler](https://github.com/OfficeDev/microsoft-365-agents-toolkit/blob/f3d7e73fef7bf22f2290635e34c13351c41ca55f/packages/vscode-extension/src/handlers/lifecycleHandlers.ts#L100-L103): default command inputs, no environment argument.
- [Core Publish](https://github.com/OfficeDev/microsoft-365-agents-toolkit/blob/f3d7e73fef7bf22f2290635e34c13351c41ca55f/packages/fx-core/src/core/FxCore.ts#L923-L937): `EnvLoaderMW(false)`.
- [Environment selection](https://github.com/OfficeDev/microsoft-365-agents-toolkit/blob/f3d7e73fef7bf22f2290635e34c13351c41ca55f/packages/fx-core/src/component/middleware/envMW.ts#L58-L70): local exception is declarative-only. This explains the historical R2 local Publish limitation, not a blocker for R3 package installation; assigned-VM execution is NOT RUN.

R3 installation authority: Copilot Camp BMA4 Exercise 2 and Microsoft Learn manual manifest/sideload guidance ([Copilot Camp BMA4](https://microsoft.github.io/copilot-camp/pages/custom-engine/agents-sdk/04-bring-agent-to-copilot/) and [Microsoft Learn](https://learn.microsoft.com/en-us/microsoftteams/platform/teams-sdk/teams/enabling-in-copilot)). The existing manifest already meets the documented same-bot `customEngineAgents` declaration and personal + copilot scope requirements. Removed only the unnecessary local Publish lifecycle; no change to Python, authentication, registration, manifest scopes or Foundry resources.

Primary references:
- https://learn.microsoft.com/azure/developer/dev-tunnels/cli-commands
- https://learn.microsoft.com/en-us/azure/developer/dev-tunnels/get-started
- https://learn.microsoft.com/en-us/azure/templates/microsoft.botservice/2022-09-15/botservices

Dependencies: original core==1.12.1, foundry==1.10.3, identity==1.25.3 retained. requirements.txt pins direct dependencies; requirements.lock.txt records the complete locally installed dependency graph. This is a version lock, not wheel-hash or cross-platform certification. License notices for copied official assets are retained in THIRD_PARTY_NOTICES.md.
