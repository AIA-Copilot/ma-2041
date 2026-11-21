# Day 2 · Lab 4 — Connect through Toolkit and test in Teams/Copilot

**Workspace:** use VS Code and PowerShell 7 inside the provided AI3026 VM. “Local” means this VM. One-time preparation: [course setup](../README.md).

**Outcome:** use Microsoft 365 Agents Toolkit to register/package the C# custom engine agent, expose the local host through an approved tunnel, and test the same Foundry agent from Teams and Copilot. Allow 60–90 minutes **after** permission and tenant setup; provisioning/admin approval may require additional time.

## Mandatory gates — do not skip

**Toolkit dependency HOLD:** the fresh audit of the pinned CLI lock reports **5 affected packages (2 high, 3 moderate)**, including MSAL authorization-code disclosure and glob/minimatch advisories. Do not install/rebuild the credential module, run Toolkit CLI, authenticate, provision or deploy this candidate until a tested supported remediation passes independent security review. Inspect the files only while blocked. Script-disabled builder installation and C# tests are not runtime approval. No waiver is supplied.

The live route below is conditional. Continue only after security release and these permission gates:

- Lab 3’s **live C# probe** invoked the same grounded modern agent and produced a policy-supported answer.
- Provider authorizes the selected Azure subscription/resource group, app registration creation, Azure Bot Service and development tunnel.
- Your Azure identity can deploy Bot Service in that group; your Entra permissions/policy allow a single-tenant app registration with a client secret. Tenant policy may require an administrator.
- Your Microsoft 365 tenant/account supports Teams custom app installation and the requested Microsoft 365 extension workflow. Ask the provider to verify app policies and any admin approval requirement.
- Copilot access/licensing and custom engine agent availability are confirmed for your account. If Copilot is unavailable, record that slice **blocked**, not passed through Teams alone.
- Only fictional files and your personal lab installation are used. The proxy accesses Foundry as the **developer Azure CLI identity**, not the chatting Teams user. Do not deploy this developer-identity design for other users or real company data.

If any gate fails, complete the local architecture/manifest review but stop before external provisioning. Preserve your exact blocker. Portal publishing is a different route and must not be presented as successful SDK integration.

## Current route — read-only while Toolkit is on HOLD

1. Read the lifecycle and manifest in section 1. Do not edit them yet.
2. Identify the Bot ID shared by the bot and custom-engine agent, and distinguish it from the Foundry agent name/version.
3. Trace where the lifecycle would create the app, secret, Bot resource and local settings.
4. Record **architecture review complete; Toolkit provisioning, Teams and Copilot blocked**.

**STOP before section 2 while HOLD remains.** Do not run the Toolkit CLI, credential rebuild, sign-in, tunnel, provision, deploy or host commands. Sections 2–6 are retained for a later security-released rehearsal, not authorized by this walkthrough.

## 1. Inspect what Toolkit will do

1. In VS Code open `C:\ma-2041\Day2\AI3026\M365Agent\m365agents.local.yml`.

| Stage | External or local effect |
|---|---|
| `teamsApp/create` | Creates the app record in your M365 tenant |
| `aadApp/create` | Creates a single-tenant bot app, service principal and 7-day client secret |
| `arm/deploy` | Creates Azure Bot Service and Teams channel using `infra\bot.bicep` |
| `file/createOrUpdateJsonFile` | Writes ignored local runtime settings, including the generated bot secret |
| `teamsApp/validateManifest` / ZIP actions | Validates and packages manifest/icons |
| `teamsApp/update` | Updates the tenant’s app record |
| `teamsApp/extendToM365` | Extends the app to Microsoft 365; tenant availability/policy gates still apply |

No App Service, search service, managed identity or SSO app is created by this reduced lifecycle. **Hosting stays on the VM.** “Deploy” here updates the app package; it does not move C# compute into Azure.

2. Open `appPackage\manifest.json`. Find `bots[].botId` and `copilotAgents.customEngineAgents[].id`: both use the same `${{BOT_ID}}`, not the Foundry name. Find the `personal` and `copilot` scopes. **After security release only**, change the short/full descriptions to describe your policy assistant accurately; retain placeholder identifiers and icon names. Do not add team/group scope or promise ticket execution.

Publisher URLs are sample `example.com` placeholders for a private lab package. Organization/public distribution needs approved real publisher/legal URLs and separate review. Do not submit this lab to a public store.

**Checkpoint:** Identify shared Bot ID and external lifecycle effects; while HOLD remains, stop here.

## 2. Configure the approved live route

**STOP:** the instructor must confirm tested remediation, independent security review, prepared tools and Lab 3 live-probe acceptance before you continue. Installation and credential-module preparation belong to [instructor preflight](INSTRUCTOR-PREFLIGHT.md), not this lab.

1. Open a PowerShell 7 terminal at `C:\ma-2041\Day2\AI3026\M365Agent`.
2. Copy the configuration template only if `.env.local` does not already exist. If it exists, preserve it and compare it with the template; do not overwrite generated identity or your earlier work.

Copy the configuration template:

```powershell
Copy-Item .\env\.env.local.example .\env\.env.local
code .\env\.env.local
```

3. Fill the blank non-secret values with your approved configuration:

| Variable | Value to supply |
|---|---|
| `AZURE_SUBSCRIPTION_ID` | Approved subscription GUID |
| `AZURE_RESOURCE_GROUP_NAME` | Dedicated/approved lab resource group |
| `BOT_RESOURCE_NAME` | Unique 4–20 character lowercase alphanumeric lab bot name |
| `BOT_TENANT_ID` | Azure/Entra directory GUID used for the bot and assigned M365 lab tenant |
| `FOUNDRY_PROJECT_ENDPOINT` | Exact project endpoint used successfully by the probe |
| `FOUNDRY_AGENT_NAME` | Same agent name |
| `FOUNDRY_AGENT_VERSION` | Same grounded version used successfully by the probe |

Keep `TEAMSFX_ENV=local`. Do not type bot secrets into this template; Toolkit generates them. The v1.11 lifecycle explicitly creates the service principal and writes the bot tenant ID from the authenticated app-creation identity; compare it with the approved tenant before continuing. The lab client secret expires after seven days. Do not upload/share real `.env.local`, `.env.local.user` or `appsettings.Development.json`. If Azure and M365 accounts belong to different tenants, stop for provider-approved alignment rather than guessing identities.

**Checkpoint:** After release only: configuration matches the approved tenant and successful probe.

## 3. Start an explicitly approved tunnel

A public tunnel allows Bot Service to reach the VM. The application’s `/api/messages` endpoint remains JWT-protected; a public tunnel is not permission to disable that authentication.

1. In a dedicated terminal:

```powershell
devtunnel user login
devtunnel create --allow-anonymous
```

2. Copy the returned tunnel ID. Use that exact ID in the next commands; do not use the literal placeholder:

```powershell
devtunnel port create YOUR-TUNNEL-ID -p 5130
devtunnel host YOUR-TUNNEL-ID
```

3. Keep that terminal running. Copy the **HTTPS URL for port 5130** shown by the tool. In `env\.env.local`, set:

```text
BOT_DOMAIN=YOUR-PORT-5130-HOST.devtunnels.ms
BOT_ENDPOINT=https://YOUR-PORT-5130-HOST.devtunnels.ms/api/messages
```

`BOT_DOMAIN` contains just the host, no scheme/path. `BOT_ENDPOINT` includes HTTPS and `/api/messages`. Use actual output rather than inventing a tunnel region or hostname. If provider networking blocks tunnels, this channel slice is blocked. Do not bypass policy with an unrelated relay.

**Checkpoint:** Record the actual port-5130 URL without disabling endpoint authentication.

## 4. Provision with Toolkit, then start the proxy

1. Open a second PowerShell terminal at `M365Agent`. Confirm your Azure CLI login still uses the approved account from Lab 3. The Toolkit command may separately prompt for Azure and Microsoft 365 sign-in; inspect both account/directory selections.

```powershell
Set-Location C:\ma-2041\Day2\AI3026\M365Agent
npx.cmd --no-install atk provision --env local --telemetry false
```

Review the requested subscription/resource group before accepting. If a permission/tenant error occurs, stop and preserve the non-secret error. Do not repeatedly recreate registrations or delete environment files to force retries. Ask the provider to verify the application/service-principal state and permitted resource operations before retrying.

On success, inspect (without screenshotting secrets):

1. Azure Bot resource exists in the intended group.
2. Its Microsoft App ID matches Toolkit’s generated `BOT_ID`.
3. Messaging endpoint exactly equals your tunnel URL plus `/api/messages`.
4. Teams channel is enabled.
5. `Proxy\appsettings.Development.json` contains the same Foundry endpoint/name/version as the successful probe and the generated BotServiceConnection settings.

The generated settings contain a client secret. Keep them private and ignored by Git.

In a third terminal:

```powershell
Set-Location C:\ma-2041\Day2\AI3026
$env:ASPNETCORE_ENVIRONMENT = 'Development'
$env:ASPNETCORE_URLS = 'http://localhost:5130'
dotnet run --project .\Proxy\Proxy.csproj --no-launch-profile
```

Keep the host running. Alternatively use the workspace F5 configuration **Proxy only — NO provisioning** after provision. F5 does not create a tunnel or upload your app.

In another terminal, check the host:

```powershell
Invoke-WebRequest http://localhost:5130/health
(Invoke-WebRequest http://localhost:5130/api/messages -Method Post -ContentType 'application/json' -Body '{}' -SkipHttpErrorCheck).StatusCode
```

**Expected result:** HTTP 200 with text stating Foundry/Teams are **not checked**. An unauthenticated POST to `/api/messages` should return **401**. Do not disable `.RequireAuthorization()` to make a manual test message work.

**Checkpoint:** Verify Bot/settings identity, health 200 and unauthenticated message 401.

## 5. Package and register the app, then install it

1. With the host and tunnel still running:

```powershell
Set-Location C:\ma-2041\Day2\AI3026\M365Agent
npx.cmd --no-install atk deploy --env local --telemetry false
```

2. Check all validation/update/extension actions, not just ZIP creation. The generated package is `appPackage\build\appPackage.local.zip`. Inspect the generated manifest: placeholders must be resolved; bot IDs must match; both PNG icons must be in the ZIP root alongside `manifest.json`. Do not manually ZIP the entire project or include credentials/source/build dependencies.

3. In Teams, open **Apps → Manage your apps → Upload an app → Upload a custom app** (labels can vary). Choose that package and install it for yourself. If upload is disabled, ask the tenant administrator; do not treat opening the ZIP as an installation.

**Checkpoint:** Verify generated package, tenant update and personal installation separately.

## 6. Prove the channel uses your C# code and your Foundry agent

1. In the Teams personal chat, send **`/help`**. Verify your edited help text from Lab 3, including the new input limit. This demonstrates the C# route, not only the Foundry portal.
2. Send **“How do I request custom software?”** Compare with the policy, portal and C# probe. Record actual source evidence.
3. Send **“What is the lunar-office allowance?”** Confirm it is not invented.
4. Send **“Create my ticket now.”** Confirm no completed action is claimed.
5. If a reply fails, test the probe again before changing the agent: isolate Foundry from channel transport.

For Copilot, open the Microsoft 365 Copilot app/web experience supplied by your tenant. Find the registered custom engine agent under your available agents/app catalog and open its chat. Depending on policy, an administrator may need to approve or enable it. If absent, inspect the `extendToM365` result and tenant policy with the provider; do not assume Teams installation proves Copilot availability.

Repeat `/help`, the software question and the unsupported-allowance question in Copilot. Record each result separately. **Copilot passes only when an actual reply from this agent is observed**, not when a portal says a package was prepared.

**Checkpoint:** Record actual Teams and Copilot outcomes separately; absence is blocked, not passed.

## Recovery, evidence and cleanup

| Failure | First check |
|---|---|
| Provision denied | Correct account/tenant, app-registration policy, group deployment rights |
| Bot auth/401 from channel | Generated Bot ID/audience, client secret, tenant and Bot settings; keep authentication enabled |
| Bot unreachable | Host running, correct port, tunnel running, Bot messaging endpoint |
| Host returns Foundry error | Rerun probe with same identity/version; inspect provider roles and Foundry run trace |
| ZIP validates but agent absent | Tenant app update/install/approval and Copilot availability; not a build issue |
| Generic/wrong policy reply | Same endpoint/name/version and file attachment; no silent fallback |

Record actual Teams and Copilot replies or exact blocked status. Keep secrets out of screenshots. Your evidence must distinguish **local build**, **live Foundry**, **Toolkit provisioning**, **Teams** and **Copilot** acceptance.

When finished, stop only your host and tunnel terminals with **Ctrl+C** (not a process-wide kill command). With provider approval, delete the specific tunnel using `devtunnel delete YOUR-TUNNEL-ID`, uninstall your personal Teams/Copilot app, and remove only lab-owned Azure Bot/Entra/app records. Delete the Foundry agent/files/project only after all four labs are finished and only if they are yours. Do not delete a shared resource group. Review Azure resources for remaining costs; uninstalling an app does not prove Azure cleanup. Remove local generated secrets according to the provider’s VM reset policy.

**Sources:** [custom engine agent overview](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/overview-custom-engine-agent); [pinned official proxy](https://github.com/OfficeDev/microsoft-365-agents-toolkit-samples/tree/16f3562e64e6df20da4b736e9c499708d7f86070/ProxyAgent-CSharp); [Dev tunnels](https://learn.microsoft.com/en-us/azure/developer/dev-tunnels/get-started); [AI3026 publishing exercise](https://github.com/MicrosoftLearning/mslearn-ai-agents/blob/df5b56b41480298afc09abf28c79c0d1856f40dd/Instructions/Exercises/05a-m365-teams-integration.md). The final source is conceptual context: this lab uses Toolkit/SDK, not its portal-only publish route.
