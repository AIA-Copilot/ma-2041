# Day 2 — carry one Foundry agent into C# and Microsoft 365

Use the provided **AI3026 VM**, VS Code and **PowerShell 7**. Keep the same modern Foundry agent name and saved grounded version across all four labs. No Python is required.

## Start

1. Open `C:\Users\Admin\ma-2041\Day2\AI3026\AI3026.code-workspace` in VS Code.
2. If .NET 10 SDK, Azure CLI or the lab dependencies are missing, ask the instructor to complete the VM setup.
3. Follow the guides in order:

| Guide | Result to carry forward |
|---|---|
| [Lab 1 — Build the agent](../docs/D2_Lab1.md) | Project endpoint, modern agent name, baseline instructions/tests |
| [Lab 2 — Ground and evaluate](../docs/D2_Lab2.md) | Attached policy, evaluation evidence, saved grounded version |
| [Lab 3 — Test the C# bridge](../docs/D2_Lab3.md) | Intentional failing/passing boundary test and actual same-agent live probe |
| [Lab 4 — Teams/Copilot](../docs/D2_Lab4.md) | Read-only architecture review while Toolkit is on HOLD |

**Checkpoint:** your private evidence distinguishes portal behavior, offline tests, live C# invocation, Teams and Copilot. One does not prove another.

## Stop rules

- Resource creation/model invocation needs the provider-approved subscription, project, permissions and spend authority.
- Lab 4's pinned Toolkit lock retains **five affected packages (two high, three moderate)**. Do not install/rebuild or run Toolkit until tested supported remediation passes independent security review. Read-only review is the current route, not channel acceptance.
- Lab 4 is read-only in this release. Do not execute a channel deployment or public tunnel. A future live route would require separate approval and actual Lab 3/tenant/channel acceptance.
- The C# proxy uses the developer's Azure CLI identity, not the Teams user's identity. Use fictional files and your personal lab installation only. Keep `/api/messages` authentication enabled.

This is a C#/.NET 10 adaptation, not the unchanged classic proxy. [Compatibility](AI3026/COMPATIBILITY.md) explains modern name/version versus classic `asst_` IDs; [source/asset provenance](AI3026/SOURCES.md) retains attribution. Local tests are not native-VM or live-tenant acceptance. The source illustrates VM hosting; the current Lab 4 does not expose that host or deploy channel resources.
