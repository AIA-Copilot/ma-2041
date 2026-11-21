# Day 2 — Foundry policy agent to Teams and Copilot

> **Required working environment: the provided AI3026 Day 2 lab VM.** Perform every clone/download, dependency check or installation, VS Code action, terminal command, file edit and browser/Teams/Copilot test **inside that VM**. Your physical PC is only for accessing the VM. In this guide, “local” hosting/debugging means **local to the VM**, never your physical PC. Install or change tools only with the lab provider’s permission.

Open `C:\ma-2041\Day2\AI3026\AI3026.code-workspace` in VS Code. Follow `docs/D2_Lab1.md` through `D2_Lab4.md` at repository root (or the matching PDFs).

**This is an AIA adaptation, not an unchanged Microsoft lab.** It keeps the **same modern Foundry agent name and saved version** across portal, C# probe, and Microsoft 365 Agents SDK proxy. Microsoft’s pinned ProxyAgent-CSharp uses the incompatible classic Persistent Agents API. We retain its SDK hosting/authentication pattern, Bot Service Bicep, icons, and Toolkit lifecycle concepts; replace the classic client with the documented modern Foundry REST Responses API; omit SSO, Agent Framework previews, App Service, and advanced infrastructure. See `COMPATIBILITY.md` and `SOURCES.md`.

## Setup (native Windows inside the provided AI3026 VM)

- Git; VS Code; C# Dev Kit; Microsoft 365 Agents Toolkit; optional Foundry Toolkit.
- .NET **10 SDK**, PowerShell 7, Node.js **22.12+**, Azure CLI. Dev Tunnels CLI is required only for Lab 4.
- Azure/M365 accounts supplied by the lab provider. Permission gates are in each lab. No Python installation or execution.
- This package was built/tested locally in WSL. That is **not** GoDeploy AI3026 VM, Azure, Teams, Copilot, or native-Windows acceptance. The tenant-dependent steps must be verified in your assigned environment.

```powershell
Set-Location C:\ma-2041\Day2\AI3026
dotnet restore .\Proxy\Proxy.csproj --locked-mode
dotnet build .\Proxy\Proxy.csproj --no-restore
dotnet run --project .\Tests\Tests.csproj
dotnet run --project .\Probe\Probe.csproj
```

The tests use **synthetic HTTP fixtures**, not live Azure responses. The probe does nothing online unless `--live` is supplied. F5 builds/starts the local proxy only; it does not provision, start a tunnel, or upload an app. `/api/messages` requires authentication even in Development. `/health` only proves the process is alive.

## Layout

| Path | Purpose |
|---|---|
| `assets/IT_Policy.txt` | Fictional Microsoft Contoso grounding document |
| `Gateway/FoundryGateway.cs` | HTTPS endpoint validation; same-agent request; answer/citation extraction |
| `Probe/` | Explicit live C# diagnostic against the existing Foundry agent |
| `Proxy/` | Microsoft 365 Agents SDK ASP.NET host and message handler |
| `Tests/` | Offline contract tests; executable exits nonzero on failure |
| `M365Agent/` | Pinned Toolkit CLI, local lifecycle, manifest/icons and Bot Service Bicep |
| `.vscode/` | Local-only build/test/debug tasks |
| `licenses/`, `SOURCES.md` | Upstream rights, exact revisions, adaptation record |

## Boundaries

Single-turn text/file-search agent, no client-side functions, ticket creation, chart rendering or multi-turn history. `store:false` is a Responses setting, **not** a guarantee that all service telemetry/data retention is disabled. Foundry runs as the developer’s Azure CLI identity, not the Teams user. Only fictional lab files, one learner’s personal test installation, and a provider-approved subscription/tenant are allowed. This is not a production identity or authorization design.

Lab 4 exposes the local host through an authenticated Bot Service channel over a public tunnel. It provisions a bot app registration and Azure Bot resource and updates a Teams/M365 app. It does **not** deploy compute to Azure App Service. Keep the host and tunnel running while testing; stop both afterwards. Never treat successful ZIP creation or a health response as tenant acceptance.

Generated `.env.*`, app settings, build outputs, credentials, logs and `node_modules` must not be submitted or published. Only `.env.local.example` is a distributable template. Do not paste real tokens or secrets into chat, screenshots, or shared evidence.
