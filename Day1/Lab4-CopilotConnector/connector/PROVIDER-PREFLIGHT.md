# Provider preflight — outside taught time, MS4018 VM only

**HOLD:** This is a proposed, locally inspected installation path, not installation approval. The provider/security owner must approve the exact candidate and tool source before any installation/F5. Lab 4 additionally retains nine moderate affected npm package entries (two unique advisories); see the security build report. Do not waive these because the VM is disposable. No personal-PC setup, no Python, no tenant activity is authorized by this document.

## Core Tools: one official MSI path, no npm/Toolkit downloader

Microsoft documents the Windows MSI route at https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local . The verified official release is https://github.com/Azure/azure-functions-core-tools/releases/tag/4.16.1 . Pin **func-cli-4.16.1-x64.msi**, not a floating aka.ms download. Its SHA-256 was checked against the downloaded bytes and GitHub release asset digest:

`a1f7afdc4422f10988604d1ad004cac18123e6339856e3efafc446bc93d63838`

The official tagged `eng/res/msi/funcinstall.wxs` uses an embedded cabinet and the Windows Installer directory `Program Files\Microsoft\Azure Functions Core Tools`; this avoids the npm postinstall/launcher and its extract-zip flow. This source inspection is not a full binary security audit. Windows Authenticode trust and actual native installation remain provider checks.

After provider approval, in the **provided VM**, download and verify (does not install):

```powershell
$msi = Join-Path $env:TEMP 'func-cli-4.16.1-x64.msi'
Invoke-WebRequest 'https://github.com/Azure/azure-functions-core-tools/releases/download/4.16.1/func-cli-4.16.1-x64.msi' -OutFile $msi
$expected = 'a1f7afdc4422f10988604d1ad004cac18123e6339856e3efafc446bc93d63838'
if ((Get-FileHash $msi -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expected) { throw 'MSI digest mismatch; STOP' }
$signature = Get-AuthenticodeSignature $msi
$signature | Format-List Status,StatusMessage,SignerCertificate
if ($signature.Status -ne 'Valid') { throw 'Untrusted MSI signature; STOP' }
```

The provider must inspect the signer certificate and trust chain and confirm **Microsoft Corporation**, record the digest/signature receipt, approve installation privileges and review the license. Only then have the provider install this verified MSI through the normal Windows installer UI. Do not accept terms on someone else's behalf, silently downgrade an existing installation, use npm to install Core Tools, or enable Toolkit `devTool/install`.

After approved installation, verify the installed file location against the provider's receipt. Default path follows the official WiX source; use the actual approved MSI installation directory if customized:

```powershell
$func = Join-Path $env:ProgramFiles 'Microsoft\Azure Functions Core Tools\func.exe'
if (!(Test-Path -LiteralPath $func -PathType Leaf)) { throw 'Approved MSI host missing' }
# Only after the provider has verified this installation:
$env:DAY1_FUNC_EXE = $func
$env:DAY1_FUNC_SHA256 = (Get-FileHash -LiteralPath $func -Algorithm SHA256).Hash.ToLowerInvariant()
node scripts/run-func.cjs --version
```

Expected exactly `4.16.1`. Record the executable hash with the MSI receipt. These environment values are operator configuration, not an authorization or tamper-proof security boundary. Do not hash/bless an arbitrary downloaded executable. Set both variables in the approved VS Code launch environment, fully exit existing VS Code processes, then reopen VS Code from this configured terminal (`code .`) so tasks inherit them. Recheck `npm.cmd run check:func` inside VS Code. A missing/mismatched receipt fails closed before F5's tunnel/provision/install stages. The launcher invokes the absolute hashed executable without shell, npm shim, PATH lookup or download. Native Windows execution still needs provider rehearsal.

## Dependencies and native rehearsal

Stop all hosts, watchers and Azurite before changing node_modules. After exact-candidate security disposition, pre-stage the lockfile dependencies outside class:

```powershell
node --version
npm.cmd ci --ignore-scripts --no-audit --no-fund
npm.cmd run build
npm.cmd test
npm.cmd run check:func
```

Use Node 22.22.2. `--ignore-scripts` is deliberate; do not remove it. No Core Tools npm package remains in the lock. F5 retains a single guarded lockfile install before background processes, using the prewarmed cache; never manually reinstall while Azurite runs. No npm force/major overrides. Avoid cloud deployment commands: only the instructor-approved local lifecycle is taught.

Provider rehearsal must verify task order, native host/debug attach and task shutdown; ports 7071/9229 for APIs, loopback-only Azurite storage for the connector. API tunnels need separate approval. Connector provisioning/admin consent/unique ownership must be completed before class without triggering ingestion early if learners are to demonstrate their own ingestion. Do not start the connector host during preflight merely to check its version: its timer can write Graph resources. No tenant/token/tunnel execution was performed by the remediation builder.

For Lab 4, telemetry is disabled but vulnerable dependencies remain installed: uuid buffer-overload and HTTP-instrumentation advisories require named security disposition. No safe compatible full remedy was demonstrated; the attempted identity 4.14.1 migration failed strict dependency type checking and was not retained. If disposition is absent, stop before connector runtime/F5 and label the live outcomes blocked.
