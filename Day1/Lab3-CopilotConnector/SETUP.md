# One-time preparation — Day 1 Lab 3

Run before class, after the root course setup. Learners do not clone or install again in the lab.

## Windows VM prerequisites

- VS Code, Microsoft 365 Agents Toolkit (`TeamsDevApp.ms-teams-vscode-extension`) and Azure Functions extension (`ms-azuretools.vscode-azurefunctions`).
- Portable Node **22.22.2** at `C:\Users\Admin\ma-2041\tools\node-v22.22.2-win-x64` and the course `scripts/Use-Node.ps1`. Node 24 is for WIQD, not this connector.
- Azure Functions **Core Tools v4 x64**, installed once with Microsoft's Windows installer; use the [official Core Tools installation instructions](https://learn.microsoft.com/azure/azure-functions/functions-run-local#install-the-azure-functions-core-tools). This lab deliberately removes the project npm `azure-functions-core-tools` dependency. Do not use `npx func` to download a substitute. A local Functions host is not Azure cloud hosting.
- Microsoft 365 training tenant, licensed Copilot account able to use declarative agents, custom-app upload allowed, app-registration permission, and an assigned administrator who can grant Microsoft Graph **application** permissions. No Azure subscription is required. Microsoft 365 service/network access is required; this is not an offline tenant lab.
- Administrator approval to ingest the five **synthetic public** Zava travel/arrival/policy documents with the sample's tenant-wide `everyone` ACL. Never replace them with confidential material.

### Install the Windows Core Tools host

If `func --version` already reports v4, record the installed version and use it for rehearsal. Otherwise download the pinned Microsoft x64 MSI inside the VM:

```powershell
$msi = Join-Path $env:TEMP 'func-cli-4.16.1-x64.msi'
Invoke-WebRequest 'https://github.com/Azure/azure-functions-core-tools/releases/download/4.16.1/func-cli-4.16.1-x64.msi' -OutFile $msi
$expected = 'a1f7afdc4422f10988604d1ad004cac18123e6339856e3efafc446bc93d63838'
if ((Get-FileHash $msi -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expected) { throw 'Core Tools download checksum mismatch' }
$signature = Get-AuthenticodeSignature $msi
if ($signature.Status -ne 'Valid') { throw 'Core Tools signature is not trusted' }
$signature.SignerCertificate.Subject
```

Confirm the displayed publisher is Microsoft Corporation. Open that verified MSI in the VM, review its license and complete the normal installer with the permitted administrator credentials if requested. Do not install from an unverified download or silently replace another major version. Close all VS Code windows and reopen from Start after installation; if `func` is still missing, sign out of and back into the VM after saving work.

### Prepare dependencies

Run once in PowerShell after Core Tools installation:

```powershell
Set-Location C:\Users\Admin\ma-2041
. .\scripts\Use-Node.ps1 -Version 22
node.exe --version
func --version
code --install-extension TeamsDevApp.ms-teams-vscode-extension
code --install-extension ms-azuretools.vscode-azurefunctions
Set-Location .\Day1\Lab3-CopilotConnector\connector
npm.cmd ci --ignore-scripts --no-audit --no-fund
npm.cmd run build
```

Expected: Node `v22.22.2`, Core Tools `4.x`, TypeScript build exits zero. `--ignore-scripts` is intentional: the retained dependencies compile without lifecycle downloads; Core Tools is supplied globally. Azurite is included in the lockfile and starts locally during the lesson. Do not run `npm audit fix` or refresh dependencies during class. Scott accepted the temporary Day 1 sample dependency risk; this is not a production certification or a waiver for Day 2.

Open **connector**, not its parent folder, as the VS Code workspace. Tasks explicitly prepend `${workspaceFolder}/../../../tools/node-v22.22.2-win-x64` to Windows `Path`; they do not rely on the integrated terminal's selected Node. This relative path resolves to the repository's tools directory.

No tenant provisioning or Functions host startup is part of these preparation commands. The lesson performs the authorized registration/consent/ingestion interactively. Never commit generated `local.settings.json`, `.env.local`, `.env.local.user`, credentials, or `appPackage/build`.

## Delivery boundary

Use only `m365agents.local.yml` / the **local** environment. The active general lifecycle is also local-only to avoid accidental ARM deployment. Original `teamsapp*.yml` are preserved under `../upstream-reference` for provenance, not execution. Preserved `infra/` and `.env.dev` are upstream reference assets and are not lesson steps. Do not open the upstream-reference folder as a Toolkit project. The course guide and this setup file control this adaptation. The continuing agent project is Lab 1’s `C:\Users\Admin\AgentsToolkitProjects\ZavaLab1`; do not create a third agent. Use a fresh seat-specific Zava connection because existing feedback schemas/search cards are not migrated. Publish all five course content files before testing citation reachability.
