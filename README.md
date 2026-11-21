# Microsoft 365 agent development — two-day labs

Work inside the provided training VM: **MS-4018 for Day 1**, **AI3026 for Day 2**. Your physical computer only accesses the VM. VS Code is already installed in MS-4018. No Python or coding-assistant subscription is required.

## 1. Open the approved course copy

Use the instructor-confirmed release at `C:\ma-2041`. Check that `Day1\Lab1-WIQD` and `Day2\AI3026` exist, then open the folder in VS Code. The older Python/TypeSpec course is not this version.

**Existing Git clone:** stop debugging and save open files. In a terminal at `C:\ma-2041`, run `git status --short` and `git branch --show-current`. Continue only on `main` with no modified, added or deleted tracked files. An untracked `tools/` folder from the WIQD installation is expected and is not part of the course update.

```powershell
Set-Location C:\ma-2041
git pull --ff-only origin main
if ($LASTEXITCODE -ne 0) { throw 'Update stopped. Keep your files and ask the instructor.' }
code .\docs\D1_Lab1.md
```

The update does not reinstall Node or WIQD. If Git reports local changes, conflicting untracked files or diverged history, stop. Do not use reset, clean, force or a ZIP overwrite. Keep source edits, private evidence and populated environment files intact; never upload credentials to resolve a conflict. If the folder was obtained as a ZIP rather than a Git clone, ask the instructor to preserve it and prepare a separate current copy.

**New VM only:** download the instructor-confirmed ZIP and extract its repository root to an unused `C:\ma-2041`. If Git is already available, this is the optional alternative:

```powershell
if (Test-Path C:\ma-2041) { throw 'Workspace exists; preserve it and ask the instructor for the safe update.' }
git clone https://github.com/AIA-Copilot/ma-2041.git C:\ma-2041
if ($LASTEXITCODE -ne 0) { throw 'Clone failed' }
```

Do not proceed with a different release just because a download succeeded.

## 2. Prepare Node and WIQD once — MS-4018

With provider permission, run these in the VM terminal if the tools are not already prepared:

```powershell
winget install --id OpenJS.NodeJS.LTS --exact --source winget
winget install --id Microsoft.PowerShell --exact --source winget
```

Close all VS Code windows and reopen VS Code from the Windows Start menu so it detects the updated PATH and PowerShell 7. A new terminal tab alone is not enough. In the terminal profile menu, select **PowerShell 7 (`pwsh`)**, not Windows PowerShell 5.1. If the tools are still not found, save your work and sign out of and back into the VM. Check:

```powershell
node --version
npm.cmd --version
$PSVersionTable.PSVersion
```

**Expected result:** working Node/npm and PowerShell major version 7 or later. WIQD 1.0.0 requires **Node 24.15.0 or later**. `OpenJS.NodeJS.LTS` floats; verify the installed version rather than assuming it meets this requirement.

Install the course-local WIQD pin:

```powershell
npm.cmd install --prefix C:\ma-2041\tools\wiqd-1.0.0 --save-exact @microsoft/wiqd@1.0.0
if ($LASTEXITCODE -ne 0) { throw 'WIQD installation failed' }
$wiqd = 'C:\ma-2041\tools\wiqd-1.0.0\node_modules\.bin\wiqd.cmd'
& $wiqd --version
```

**Checkpoint:** WIQD reports `1.0.0`. Do not substitute `latest`, `alpha`, a global installation or an extension workflow. Lab 1 includes only conditional terms/sign-in checks before creating the agent. Installation does not supply consent or tenant authorization.

**Before Day 1 Lab 2:** the Functions projects were tested on **Node 22.22.2**, not the floating LTS used above. The provider must supply a tested way to select that version, restart VS Code and verify `node --version` reports `v22.22.2`. No unverified version-switch command is supplied. If this is not prepared, stop; current LTS is not a compatibility clearance.

Other dependencies, account permissions and native tooling belong to [instructor preflight](docs/INSTRUCTOR-PREFLIGHT.md), outside lab time. Day 2 needs its separately prepared AI3026 VM, including .NET 10 SDK; the Node/WIQD steps above do not prepare Day 2.

## 3. Follow the lab guides

| Day | Guide | What you do |
|---|---|---|
| 1 | [Lab 1 — Briefing Coach](docs/D1_Lab1.md) | Create, edit, source-validate and test with WIQD CLI |
| 1 | [Lab 2 — Restaurant API](docs/D1_Lab2.md) | Trace and test API actions |
| 1 | [Lab 3 — Adaptive Cards](docs/D1_Lab3.md) | Bind and verify rich responses |
| 1 | [Lab 4 — Copilot connector](docs/D1_Lab4.md) | Read-only route while runtime HOLD remains |
| 2 | [Lab 1 — Foundry agent](docs/D2_Lab1.md) | Create and evaluate instructions |
| 2 | [Lab 2 — Grounding](docs/D2_Lab2.md) | Attach policy and evaluate evidence |
| 2 | [Lab 3 — C# bridge](docs/D2_Lab3.md) | Change/test code and invoke the same agent |
| 2 | [Lab 4 — Teams/Copilot](docs/D2_Lab4.md) | Read-only route while Toolkit HOLD remains |

[Day 1 session map](Day1/README.md) · [Day 2 starting point](Day2/README.md). Matching student PDFs are `Labs/D1_Lab1.pdf` through `Labs/D1_Lab4.pdf` and `Labs/D2_Lab1.pdf` through `Labs/D2_Lab4.pdf`. Use each guide's project folder, not the repository root, for commands/debugging.

## Release boundaries

This is a **rehearsal/testing package**, not security or live-tenant acceptance. Local builds cannot prove Copilot, Graph ingestion, Foundry or channel behavior.

- **Day 1 Lab 4 runtime HOLD:** nine moderate affected npm packages across two unique advisories. A named provider/security owner must disposition the exact residual risk or a tested remediation before tenant preparation or emulator/Functions runtime. Use the read-only route until then.
- **Day 2 Lab 4 Toolkit HOLD:** five affected packages (two high, three moderate). Do not install/rebuild or run the CLI until tested supported remediation passes independent security review. C# compilation does not clear this hold.
- Use synthetic data and assigned accounts only. Day 1 authentication is an instructor walkthrough, not a completed learner OAuth/API-key implementation. Day 2 hosts C# on the VM, not Azure App Service.
- Do not publish to a catalog, expose private services/data, or delete shared resources. Preserve redacted evidence; never share populated environment files, secrets or token caches. Original licenses and attribution remain in the projects.

Runtime reference: [WIQD installation](https://microsoft.github.io/wiqd/getting-started/installation/) · [pinned package metadata](https://registry.npmjs.org/@microsoft/wiqd/1.0.0).
