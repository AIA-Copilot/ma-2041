# Microsoft 365 agent development — start here

This repository contains **all eight lab guides and their required course files**. Work inside the provided **MS-4018 VM for Day 1** and **AI3026 VM for Day 2**, not on your physical PC. VS Code is already installed in MS-4018.

**Current Day 1 order:** first declarative agent → currency API and Adaptive Card → synced connector → WIQD. The old restaurant/tunnel exercises are not assigned. The existing `Lab1-WIQD` source-folder name is retained, but its current guide is **Lab 4**.

**Readiness:** these are instructor-rehearsal materials, not a claim that your VM or tenant has passed. Day 1 uses no Azure hosting or public development tunnel. Day 2 Labs 1–3 need the provided Foundry/Azure resources. **Day 2 Lab 4 is a read-only architecture exercise, not live Teams/Copilot deployment.** Its dependency and tunnel requirements remain unresolved.

## 1. Clone once in a fresh VM

Open a terminal in the VM. Check `git --version`. If Git is missing, install it through the VM's permitted process (`winget install --id Git.Git --exact --source winget`), then open a fresh terminal.

```powershell
if (Test-Path C:\ma-2041) { throw 'Folder already exists. Use the safe-update instructions below; do not overwrite it.' }
git clone https://github.com/AIA-Copilot/ma-2041.git C:\ma-2041
if ($LASTEXITCODE -ne 0) { throw 'Clone failed' }
Set-Location C:\ma-2041
code .
```

In VS Code, trust this repository only after confirming the publisher and location. Open this `README.md` and press **Ctrl+Shift+V** to preview it.

**Existing clone:** save your work and stop running debug/tasks. Run `git status --short` and `git branch --show-current`. Only on `main`, with no tracked-file changes or conflicting untracked files, run `git pull --ff-only origin main`. Untracked `tools/` and `work/` folders from preparation are expected. Stop on conflicts or divergence. Do not reset, clean, force, or overwrite your existing environment files.

## 2. Prepare the Day 1 VM once

Use the VM's permitted installation process. If PowerShell 7 is missing:

```powershell
winget install --id Microsoft.PowerShell --exact --source winget
```

Close **all VS Code windows**, reopen VS Code from Start, and choose **PowerShell 7** in **Terminal > Select Default Profile**. Open a new terminal. If it is not discovered, save your work and sign out of and back into the VM. Verify:

```powershell
$PSVersionTable.PSVersion
```

The major version must be 7 or later. Do not weaken execution policy to run blocked scripts; ask the VM administrator if policy blocks the course files.

### Extensions

Install these Microsoft extensions in the VM's VS Code Extensions view:
- **Microsoft 365 Agents Toolkit** (`TeamsDevApp.ms-teams-vscode-extension`) for Labs 1–3.
- **Azure Functions** (`ms-azuretools.vscode-azurefunctions`) for Lab 3 only.

Record the installed Toolkit version during rehearsal. The course supplies JSON OpenAPI/card files; an Adaptive Card Previewer extension is optional, not a prerequisite for the currency lab. No GitHub Copilot subscription, Postman or Python is needed.

### Pinned Node runtimes

The connector needs Node 22; WIQD needs Node 24.15 or later. The supplied script downloads **22.22.2 and 24.15.0**, verifies each official ZIP checksum, and extracts them under `tools/`. It does not replace any system-wide Node installation.

```powershell
Set-Location C:\ma-2041
.\scripts\Prepare-Node.ps1
. .\scripts\Use-Node.ps1 -Version 22
node --version
npm.cmd --version
```

Expected Node: `v22.22.2`. The leading `. ` on **Use-Node.ps1** selects Node in the current terminal. Repeat it in a new terminal when a lab asks. Lab 3's supplied VS Code tasks also select the course Node 22 path; they do not rely on a prior terminal's environment.

### Connector tools and dependencies

Complete [the local connector setup](Day1/Lab3-CopilotConnector/SETUP.md) now. It includes Core Tools, locked dependencies and the required training-tenant permissions. It does not require an Azure subscription or a public tunnel. Do not start ingestion during tool preparation.

### WIQD pin

Switch this terminal to Node 24 and install the course-local WIQD version:

```powershell
Set-Location C:\ma-2041
. .\scripts\Use-Node.ps1 -Version 24
npm.cmd install --prefix C:\ma-2041\tools\wiqd-1.0.0 --save-exact @microsoft/wiqd@1.0.0
if ($LASTEXITCODE -ne 0) { throw 'WIQD installation failed' }
$wiqd = 'C:\ma-2041\tools\wiqd-1.0.0\node_modules\.bin\wiqd.cmd'
& $wiqd --version
```

Expected WIQD: `1.0.0`. Do not install global/latest/alpha as a workaround. An authorized human reviews WIQD terms and signs into the assigned tenant in Lab 4. Installation does not accept terms or provide tenant permissions.

### Tenant check

In Toolkit **Accounts**, sign into the assigned training Microsoft 365 account. Confirm custom-app upload and Copilot access. Labs 1 and 2 use declarative-agent provisioning, not Azure resource deployment. Lab 3 additionally needs an authorized administrator for Graph application permissions and an owned, uniquely named external connection. Review [instructor preflight](docs/INSTRUCTOR-PREFLIGHT.md) before the run.

## 3. Run the labs in this order

Open each local guide and use **Ctrl+Shift+V**. Do not follow an older source project's README instead of the guide.

### Day 1 — MS-4018 VM

1. [Lab 1 — First declarative agent](docs/D1_Lab1.md): Camp-based instructions and supplied Zava knowledge document.
2. [Lab 2 — Currency API and Adaptive Card](docs/D1_Lab2.md): real public reference rates, provided OpenAPI and card, no authentication/backend/tunnel.
3. [Lab 3 — Synced Copilot connector](docs/D1_Lab3.md): Camp-based synthetic feedback ingestion into Graph, then cited retrieval by an agent.
4. [Lab 4 — WIQD Briefing Coach](docs/D1_Lab4.md): create, edit, validate, provision and test with the pinned CLI.

### Day 2 — AI3026 VM

Prepare this separate VM using [Day 2 setup](docs/INSTRUCTOR-PREFLIGHT.md#day-2-preparation).

1. [Lab 1 — Foundry agent](docs/D2_Lab1.md).
2. [Lab 2 — Grounding and evaluation](docs/D2_Lab2.md).
3. [Lab 3 — C# bridge](docs/D2_Lab3.md).
4. [Lab 4 — Microsoft 365 integration architecture](docs/D2_Lab4.md), **read-only**.

The same eight guides are supplied as PDFs in `Labs/`. Use Markdown or `docs/commands/` for copying commands; PDF line wrapping can alter clipboard text. Day 1 sample files and code are already in this repository. Reference links are for further reading, not required downloads during the exercises.

## Boundaries and cleanup

Use supplied synthetic content, public currency codes and assigned training accounts. Never commit passwords, tokens, populated environment files or private tenant data. Do not publish agents to a catalog, expose a local service, or delete shared tenant resources. Follow each guide's exact test and cleanup steps. Copilot answers, indexing, tenant permissions and elapsed lab times must be checked in the actual VM; a source/schema/build pass does not prove them.

Original sample licenses and provenance are retained alongside the source. Old `Lab2-RestaurantAPI`, `Lab3-AdaptiveCards` and `Lab4-CopilotConnector` folders are retained only as earlier source checkpoints and are not part of this route.
