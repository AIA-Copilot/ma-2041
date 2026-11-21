# Instructor preflight — outside student lab time

This is a rehearsal/testing candidate, not security clearance or live acceptance. Prepare only the assigned VM and authorized training tenant. Hold notices below override executable examples. No consent, provisioning, installation or runtime is authorized by this document alone.

## Day 1: WIQD preparation


The provider prepares the VM, not learners' personal computers:

- Obtain the instructor-confirmed release using the [repository setup](../README.md) **inside the VM**. Clone only into an unused `C:\ma-2041`, or extract the approved ZIP there; never overwrite an existing workspace. Confirm `Day1\Lab1-WIQD` and `Day2\AI3026` exist. Open `C:\ma-2041` in VS Code, then follow the project-specific steps below.
- VS Code is already installed in MS-4018. Prepare **PowerShell 7 or later** and Node.js **24.15.0 or later**. Confirm both `node` and `npm.cmd` work from the same PowerShell terminal. The older Node used for other labs may not meet WIQD's requirement.
- Pin **@microsoft/wiqd@1.0.0** in the course-local folder below. Do not install globally or silently change to `latest`/`alpha`. The plugin command interface is itself alpha; this is a reproducibility pin, not a stability guarantee.
- Review WIQD terms with the authorized human. The isolated course-build approval does not consent on behalf of all learners or downstream tools. If consent is absent, stop before creation and use the supplied files for inspection only. Never copy another person's consent store.
- Confirm the assigned account has access to Microsoft 365 Copilot and the tenant's permitted custom-agent/plugin creation and installation route. Tenant policy must allow the lab's registration/upload and access. Obtain any required admin consent before class; learners must not grant themselves roles or disable policy. This instruction-only scenario needs no Graph data permissions, connector, Azure resources or API credentials of its own; the lifecycle tooling still needs the tenant-authorized registration/upload permissions.
- Rehearse provision, package, validation and the returned Chat install/test link on **this pin and VM**. Prepare approved developer identity, website, privacy and terms values for the root manifest. Generated `example.com` values are placeholders, not course legal policies; they may cause service findings. Do not invent replacement URLs. Store no passwords in these files.
- Reserve a unique project name per learner if the tenant has collisions. Keep one explicit `dev` environment throughout. Inspect `env\.env.dev`: the actual 1.0.0 scaffold has `AGENT_SCOPE=shared`; do not assume that the name `local` makes another environment personal. This lab does not share or publish to a catalog.

Provider PowerShell commands, run only in the approved VM preparation window:

```powershell
node --version
npm.cmd --version
New-Item -ItemType Directory -Force C:\ma-2041\tools\wiqd-1.0.0
npm.cmd install --prefix C:\ma-2041\tools\wiqd-1.0.0 --save-exact @microsoft/wiqd@1.0.0
if ($LASTEXITCODE -ne 0) { throw 'WIQD installation failed' }
$wiqd = 'C:\ma-2041\tools\wiqd-1.0.0\node_modules\.bin\wiqd.cmd'
& $wiqd --version
```

Expected version: `1.0.0`. Only after an authorized human reviews and chooses to accept the WIQD terms, that human runs the interactive command:

```powershell
& $wiqd eula accept wiqd
& $wiqd eula status --json
```

Inspect the WIQD host row for `accepted`, current terms and CLI version. A separate unresolved Work IQ binary can cause status exit 2; it does not mean host consent failed. Do not accept downstream terms as a workaround. This lab does not use Work IQ commands.

Sign in **before class** in a real, unredirected PowerShell terminal:

```powershell
& $wiqd auth login --interactive
& $wiqd auth status
```

Skip optional Marketplace publisher setup if offered. Confirm the lifecycle provider's actual account and intended training tenant, not just any signed-in row. Do not pipe or redirect interactive login. Never proceed in a personal/customer tenant accidentally. If provider consent, policy or licensing fails, the instructor resolves it; timebox troubleshooting and retain a blocked result.


## Day 1: Functions, extensions and tenant preparation



**Do not install on a student's physical PC.** Provider approval applies to VM tool changes and tenant operations; course files do not override it.

- **Lab 1 runtime:** Node.js 24.15.0 (or a separately tested newer version), npm, PowerShell 7+, VS Code and course-local WIQD **1.0.0**. Use the WIQD preparation section above. An authorized human reviews the terms. The isolated build consent does not accept terms for learners.
- **Labs 2–4 runtime:** Node.js **22.22.2**, the tested Functions runtime line. The provider must prepare a supported way to select the correct Node version inside the VM. Do not assume the WIQD Node 24 session is validated for these Functions labs. Before Session 2, switch with the provider's approved mechanism, restart VS Code, and verify `node --version` is `v22.22.2`. No particular version manager or unverified switch command is prescribed.
- **Functions host:** use the provider-approved **4.16.1 x64 MSI** and the executable receipt specified in each project's `PROVIDER-PREFLIGHT.md`. The MSI download/hash was verified; signature trust, installation and native host execution remain VM checks. Do not install Core Tools from npm or enable a Toolkit downloader. Set the two documented host-receipt environment variables before launching VS Code; tasks verify them before side effects.
- **Node dependencies:** preserve the lockfiles and `npm.cmd ci --ignore-scripts` procedure. Do not use `npm audit fix --force`, disable strict type checking, or reinstall dependencies while hosts/Azurite are running.
- **VS Code extensions for Labs 2–4:** Microsoft 365 Agents Toolkit (`TeamsDevApp.ms-teams-vscode-extension`), Azure Functions (`ms-azuretools.vscode-azurefunctions`), and Adaptive Card Previewer for Lab 3. Record installed versions. Historical `teamsfx` identifiers remain valid internal names; do not rename them globally.
- **Tenant:** assigned Copilot account; permitted agent/plugin custom-app upload; approved developer/legal metadata for WIQD's root manifest; administrator availability for connector permissions. Sign-in alone does not prove these permissions.
- **API tunnel:** authorize only the synthetic restaurant service on port 7071. Never expose a private service, debugger or storage emulator.
- **Connector:** approve unique ownership/naming and the Graph application permissions `ExternalConnection.ReadWrite.OwnedBy` and `ExternalItem.ReadWrite.OwnedBy`. All sample items use an everyone-in-tenant ACL; no private content. Provision/consent must not be confused with completed ingestion.

[API provider preflight](../Day1/Lab2-RestaurantAPI/PROVIDER-PREFLIGHT.md) · [Cards preflight](../Day1/Lab3-AdaptiveCards/PROVIDER-PREFLIGHT.md) · [Connector preflight](../Day1/Lab4-CopilotConnector/connector/PROVIDER-PREFLIGHT.md)

## Dependency-security gate

The retained npm scans report **zero findings for Labs 2 and 3** after removing the npm Core Tools installer. This is not a full system security certification.

**Lab 4 runtime remains on HOLD:** nine moderate affected package entries across two unique advisories remain in the connector's identity/storage dependencies: uuid buffer handling and HTTP instrumentation. Telemetry is disabled and inspected call paths have constrained exposure, but the packages are not remediated. A named provider/security owner must disposition the exact residuals before emulator/Functions runtime or F5. See the connector preflight. No instructor or learner should treat VM isolation as approval. A build/inspection fallback cannot be claimed as live ingestion.

## Evidence and boundaries

- WIQD source generation and pass/fail/restore validation ran in an isolated builder. Its declarative-agent package is **not** supported by the offline packager; use the approved provisioned environment, normal package command and explicit uploading package validation.
- F5 for Labs 2–4 can create applications, a tunnel or Graph content. It is not an offline test. Read each lifecycle and confirm authorization first.
- Cards do not authenticate an API. Session 3 teaches API-key and OAuth request/configuration concepts; the restaurant remains anonymous synthetic data. Learners do not implement API-key/OAuth authentication in these four labs.
- Preserve redacted evidence. Never share generated secrets, populated user environment files, token caches or full consent logs. Stop hosts, tasks, tunnels and Azurite after use. Tenant cleanup belongs to the authorized owner of the exact resources.
- Original licenses and upstream readmes are retained for attribution. Current guides govern setup. Successful local tests do not establish Copilot behavior, tenant access or indexing readiness.

## Connector registration — HOLD until security disposition

**Do not execute while HOLD is unresolved.** open the connector project, verify the Core Tools receipt, then run **Terminal > Run Task > Provision** (the supplied task targets `env: local`). Do not run `TTK`, `Start Azurite emulator`, the Functions host or F5 during this registration-only step. Review/grant the two OwnedBy permissions on that exact app in Entra and retain the receipt. This creates identity/settings, not a connection or ingested items. With runtime HOLD unresolved, do not perform even this tenant preparation; inspect files only.


## Day 2: VM dependencies

Open **Terminal → New Terminal**, select PowerShell, and run:

```powershell
$PSVersionTable.PSVersion
git --version
dotnet --list-sdks
node --version
az version
```

Required: PowerShell 7, .NET **10 SDK**, Node.js **22.12 or later**, Git and Azure CLI. Install VS Code’s **C# Dev Kit** and **Microsoft 365 Agents Toolkit** extensions from Microsoft. The optional **Foundry Toolkit** extension provides a project/agent view; it is a different extension from Microsoft 365 Agents Toolkit.

If a dependency is missing, use the provider’s approved installer process. Do not install Python or follow the Python setup from the original Microsoft lab. Reopen the terminal after installation. The runtime alone is insufficient: `dotnet --list-sdks` must show a 10.0 SDK.


Complete locked NuGet restore for Proxy and Probe before Lab 3; use the exact `dotnet restore ... --locked-mode` commands retained below. Cache the Tests dependencies as well. Preserve lockfiles; no random upgrades.

```powershell
Set-Location C:\ma-2041\Day2\AI3026
dotnet restore .\Proxy\Proxy.csproj --locked-mode
dotnet restore .\Probe\Probe.csproj --locked-mode
```

## Day 2: Toolkit dependency HOLD

The retained audit reports 5 affected packages (2 high, 3 moderate), including MSAL authorization-code disclosure and glob/minimatch advisories. No waiver is supplied. Do not execute the following installation/rebuild/version checks until tested supported remediation passes independent security review. Script-disabled installation or C# tests do not release this gate.


In PowerShell:

```powershell
Set-Location C:\ma-2041\Day2\AI3026\M365Agent
npm.cmd ci --ignore-scripts --no-audit --no-fund
npm.cmd rebuild keytar --ignore-scripts=false
node -e "require('keytar'); console.log('Credential module loads')"
npx.cmd --no-install atk --version
devtunnel --version
```

Toolkit CLI is pinned to **1.1.19**. Node must be 22.12+ for this package. The first install suppresses package lifecycle scripts; the targeted rebuild enables only the native credential-store dependency. It does not sign in or read credentials. If that rebuild requests a native compiler or Python instead of obtaining a compatible prebuilt module, stop and ask the VM provider to supply the approved dependency; Python is not a student prerequisite. The CLI’s upstream postinstall modifies a global shim, so it is intentionally not run here. If Dev Tunnels is absent, install it through the approved VM process and reopen your terminal. Do not install an unapproved global Toolkit version to work around a dependency error.


## Evidence boundary

WIQD 1.0.0 generated the supplied scaffold and passed source validation, including invalid-field failure/repair, in an isolated Linux build. Native Windows, tenant provisioning, installable ZIP and Copilot behavior remain rehearsal gates. Day 2 compilation and synthetic offline tests establish local contract checks only; native VM, live Foundry and channels remain separate gates. The Day 2 lifecycle was inspected and Bicep compiled, not provisioned or tenant-tested by the builder. Rehearse the exact candidate before teaching; preserve actual failures.
