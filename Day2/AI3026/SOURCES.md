# Sources, versions and licenses

## Pinned source repositories

1. MicrosoftLearning/mslearn-ai-agents, commit `df5b56b41480298afc09abf28c79c0d1856f40dd` (main when acquired).
   - [Exercise 01](https://github.com/MicrosoftLearning/mslearn-ai-agents/blob/df5b56b41480298afc09abf28c79c0d1856f40dd/Instructions/Exercises/01-build-agent-portal-and-vscode.md): modern Foundry foundation, instructions and file search; its Python client is deliberately not distributed or required.
   - [Exercise 02](https://github.com/MicrosoftLearning/mslearn-ai-agents/blob/df5b56b41480298afc09abf28c79c0d1856f40dd/Instructions/Exercises/02-agent-custom-tools.md): conceptual distinction between tool definitions and executing custom function code; not claimed as implemented here.
   - [Exercise 05a](https://github.com/MicrosoftLearning/mslearn-ai-agents/blob/df5b56b41480298afc09abf28c79c0d1856f40dd/Instructions/Exercises/05a-m365-teams-integration.md): Teams/Copilot destination and grounding checks; its portal-publish route is not substituted for the SDK route.
   - Unmodified copied asset: `Labfiles/01-build-agent-portal-and-vscode/IT_Policy.txt` → `assets/IT_Policy.txt`.
   - MIT license retained at `licenses/mslearn-ai-agents-LICENSE.txt`.
2. OfficeDev/microsoft-365-agents-toolkit-samples, commit `16f3562e64e6df20da4b736e9c499708d7f86070` (dev when acquired).
   - [ProxyAgent-CSharp](https://github.com/OfficeDev/microsoft-365-agents-toolkit-samples/tree/16f3562e64e6df20da4b736e9c499708d7f86070/ProxyAgent-CSharp), linked from Microsoft’s `https://aka.ms/aif2m365-procode`.
   - Unmodified copied files: `AzureAgentToM365ATK/AspNetExtensions.cs` → `Proxy/AspNetExtensions.cs`; `M365Agent/infra/modules/azurebot-local.bicep` → `M365Agent/infra/bot.bicep`; `M365Agent/appPackage/color.png` and `outline.png` → same relative paths.
   - Adapted concepts/files: Program hosting pattern; SDK package pins; manifest; local YAML lifecycle. AIA rewrote the modern REST client, handler, tests, probe, local debug files and lab instructions. The upstream full automated tasks (including process-wide termination), SSO, classic client and App Service deployment are not copied.
   - MIT license retained at `licenses/ProxyAgent-CSharp-LICENSE.txt`.

The reduced lifecycle uses schema v1.11 so `aadApp/create` can explicitly set `generateServicePrincipal: true`; the pinned CLI implements this option. It binds `tenantId` output to the bot tenant setting and limits the generated lab secret to seven days. See [official Toolkit actions](https://github.com/OfficeDev/microsoft-365-agents-toolkit/wiki/Available-actions-in-Microsoft-365-Agents-Toolkit). No deployment scripts or extra SSO infrastructure are required for that service-principal creation.

## Microsoft documentation consulted

- [Custom engine agents](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/overview-custom-engine-agent) — SDK/Toolkit + Foundry proxy architecture.
- [Runtime components](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/runtime-components) — named/versioned agents, Responses endpoint and optional conversation history. Acquired page identifies git commit `282b92ea6a5ee34a794fdc387c14a9022bfe00c4`.
- [Foundry REST v1 reference](https://learn.microsoft.com/rest/api/microsoft-foundry/aiproject) — `GET /agents/{agent_name}?api-version=v1`, Responses `agent_reference.name/type/version`, response text and file citations.
- [Agents SDK AgentApplication](https://learn.microsoft.com/en-us/microsoft-365/agents-sdk/agent-application) — Activity routing. Package API compilation is verified against pinned 1.3.176, not assumed identical to latest documentation.
- [Dev tunnels](https://learn.microsoft.com/en-us/azure/developer/dev-tunnels/get-started) — explicit local tunnel lifecycle.

Documentation is cited and paraphrased; complete web documentation is not republished here. The upstream MIT notices cover copied sample material. This course adaptation is not an official Microsoft release. NuGet transitive dependencies are locked in `packages.lock.json`; Toolkit dependencies in `M365Agent/package-lock.json`. No binaries or installed dependencies belong in the student source package.
