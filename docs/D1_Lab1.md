# D1_Lab1 — Compile a scoped declarative agent

**Learning outcome:** Write policy instructions and a conversation starter in TypeSpec, compile them, and trace the emitted agent JSON. The project scaffold and capabilities are supplied. Compilation checks structure; it does not prove model behavior or publish a Copilot agent.

**Planned practice:** 40 minutes, excluding setup and provider support.

## Setup — complete before the lab timer

### Setup task 1

Use the virtual lab environment provided for this training. For all Day 1 labs, use the **MS-4018 lab environment**. Complete the steps inside that virtual machine using the supplied learner account.
### Setup task 2

### Get the student repository (once per VM)

Start in the provided **MS-4018 VM for Day 1** or **AI-3026 VM for Day 2**, not your personal computer. Cloning downloads files only; it does not install Python, Node.js, extensions or Azure CLI. Use the provider-approved software process if a required tool is missing. Open PowerShell.

If `C:\ma-2041` already contains your work, reuse it and skip acquisition; do not clone, extract or reset over it. Otherwise choose **one** method below.

**Option A — Git clone** (Git must already be installed):

```powershell
git --version
if (Test-Path 'C:\ma-2041') { throw 'STOP: preserve existing work' }
git clone https://github.com/AIA-Copilot/ma-2041.git C:\ma-2041
if ($LASTEXITCODE -ne 0) { throw 'STOP: clone failed' }
```

**Option B — Download ZIP** (no Git needed): run this guarded download/extraction in PowerShell. GitHub wraps its ZIP in `ma-2041-main`; the final rename below removes that wrapper so the code roots match the clone exactly. Do not use Extract All into `C:\ma-2041`.

```powershell
if (Test-Path 'C:\ma-2041') { throw 'STOP: preserve existing work' }
$stage = Join-Path $env:TEMP ('ma2041-' + [guid]::NewGuid())
New-Item -ItemType Directory -Path $stage | Out-Null
$url = 'https://github.com/AIA-Copilot/ma-2041/archive/refs/heads/main.zip'
Invoke-WebRequest $url -OutFile (Join-Path $stage 'source.zip')
Expand-Archive (Join-Path $stage 'source.zip') (Join-Path $stage 'unpacked')
$root = Join-Path $stage 'unpacked\ma-2041-main'
if (-not (Test-Path "$root\Day1\requirements.txt")) {
    throw 'STOP: unexpected archive layout'
}
if (-not (Test-Path "$root\Day2\package.json")) {
    throw 'STOP: incomplete archive'
}
if (Test-Path 'C:\ma-2041') { throw 'STOP: destination now exists' }
Move-Item -LiteralPath $root -Destination 'C:\ma-2041'
```

Confirm both `C:\ma-2041\Day1\requirements.txt` and `C:\ma-2041\Day2\package.json` exist. The eight handouts are in `C:\ma-2041\Labs`. No manual code-folder copy is needed after clone or this extraction. Keep the same working folder throughout each day's four labs. Preserve your edits before any recovery; do not use a whole-project reset.


### Setup task 3

In VS Code choose **File > Open Folder** and open `C:\ma-2041\Day1`. Explorer must show `starters`, `solutions`, `tests`, `fixtures` and `requirements.txt` directly. The `solutions` folder is the supplied code reference used to prepare these exercises, not a separate instructor download. Choose **Terminal > New Terminal**, then select **PowerShell** from the terminal profile dropdown.
### Setup task 4

Check software. Required: Python 3.11, Node.js 22 or later, npm, Git (clone option only), VS Code, Microsoft Python and Python Debugger extensions. Microsoft 365 Agents Toolkit is required only for a separately authorized live declarative-agent activity; it does not grant tenant permissions.

```powershell
Set-Location 'C:\ma-2041\Day1'
py -3.11 --version
node --version
npm --version
code --version
```

### Setup task 5

Create the local Python environment and install the supplied requirements:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
@'
import flask, jwt, jsonschema, aiohttp
import microsoft_agents.hosting.core
print('deps ok')
'@ | python -
```

Expected: `deps ok`. In VS Code press **Ctrl+Shift+P**, choose **Python: Select Interpreter**, and select `.venv\Scripts\python.exe`. If activation is blocked, do not change execution policy: replace `python` in every command with `.\.venv\Scripts\python.exe` while at the Code root. Stop for provider support if approved dependency downloads are blocked.

### Setup task 6

Use a fresh training shell without real model, Graph or Entra credentials. Do not create a `.env` file for Day 1. Run this guard before local checks:

```powershell
if (Test-Path .env) {
    throw 'STOP: use a clean local training copy without .env'
}
$env:AZURE_OPENAI_ENDPOINT = ''
$env:AZURE_OPENAI_API_KEY = ''
$env:AZURE_OPENAI_DEPLOYMENT = ''
$env:MA2041_ALLOW_LIVE_INGEST = '0'
@'
from common.config import settings
assert not settings.model_endpoint_configured()
print('retrieval-only core confirmed')
'@ | python -
if ($LASTEXITCODE -ne 0) { throw 'STOP: model configuration is active' }
```

Expected: `retrieval-only core confirmed`. If you previously configured real credentials in this shell, close it and obtain a clean provider-approved training environment; do not print or copy secrets to diagnose the problem.

### Setup task 7

Install the pinned TypeSpec dependencies and compile the supplied scaffold:

```powershell
Push-Location starters\lab1
npm ci --ignore-scripts --no-audit --no-fund
npx --no-install tsp compile .
Pop-Location
$env:LAB_IMPL = 'solutions'
python -m pytest tests\lab2_3 tests\lab4 tests\lab5 -q
$env:LAB_IMPL = 'starters'
```

Expected: compilation succeeds and `starters\lab1\appPackage\declarative-agent.json` exists; the Day 1 reference checks pass. These are local checks, not Copilot execution. Untouched starter exercises are intentionally incomplete. Do not fix dependency problems by weakening tests or upgrading packages ad hoc.

**Before timed work:** confirm installation, loopback access and the selected interpreter. No tenant permission is required for these local exercises. Live Copilot work would separately need the assigned account's licence, custom-app upload permission, an approved authenticated HTTPS API and any required consent/connector permissions. A licence label or green shield does not prove these permissions. Live publication is not performed in these four labs.

## Keep a short lab record

Use your own notes file in the working copy. Record the lab name, changed files, commands, observed outputs/exit codes, positive and negative checks, restored state, and any blocker. Save only fictional data and sanitized screenshots. Never include tokens, keys, passwords, login caches or runtime configuration files. Expected output in this handout is a target to compare against, not proof that your run succeeded.

```powershell
Set-Location 'C:\ma-2041\Day1'
$env:LAB_IMPL = 'starters'
```

## Tasks (5 + 12 + 8 + 10 + 5 minutes)

### 1. Establish the supplied starting point (5 min)
```powershell
Copy-Item starters\lab1\main.tsp starters\lab1\main.tsp.before-D1-01 -Force
Copy-Item solutions\lab1\main.tsp starters\lab1\main.tsp -Force
Set-Location starters\lab1
$env:LAB_IMPL = "starters"
.\node_modules\.bin\tsp.cmd compile .
```
Expected: successful compilation and `appPackage\declarative-agent.json`. This calls the installed compiler without an implicit download. `LAB_IMPL` has no effect on TypeSpec; the directory selects the starter. Read `main.tsp` and `tspconfig.yaml`: the emitter is `@microsoft/typespec-m365-copilot`; `output-file` supplies the JSON filename.

### 2. Make a meaningful authoring change (12 min)
In `main.tsp`, replace the full triple-quoted `@instructions` content with your own brief. Require: applicable policy and customer tier; response commitment in **business hours**; a source citation; explicit refusal to invent an unsupported policy and escalation to the duty manager. Keep the string delimiters and decorators intact.
Replace the first conversation starter's title with `Unsupported policy` and text with `Which policy applies when no published policy matches this ticket?`. Keep the other starter. Explain why the compiler cannot prove the model will follow your refusal instruction.

### 3. Trace source to output (8 min)
```powershell
.\node_modules\.bin\tsp.cmd compile .
$d = Get-Content appPackage\declarative-agent.json -Raw | ConvertFrom-Json
$d.version
$d.instructions
$d.conversation_starters | ConvertTo-Json -Depth 10
$d.capabilities | ConvertTo-Json -Depth 10
```
Expected: `v1.5`, your instructions and starter, WebSearch scoped to `https://learn.microsoft.com`, and emitted `GraphConnectors` pointing at `contososupportpolicies`. Compare that ID to `..\..\solutions\lab5\connector_client.py`. TypeSpec calls the capability `CopilotConnectors`; the JSON name differs. Inspect `node_modules\@microsoft\typespec-m365-copilot\lib\da-capabilities.tsp` before changing scope. Omitting the scope is not equivalent to restricting it.

### 4. Prove the compiler rejects a bad value (10 min)
Save your good edit:
```powershell
Copy-Item main.tsp main.tsp.good-D1-01 -Force
```
Change only the first `@conversationStarter(#{` to `@conversationStarter({`, save, and compile. Expected: nonzero exit and a type/value diagnostic. Record the actual diagnostic; stale JSON after a failed compile is not fresh evidence.
```powershell
.\node_modules\.bin\tsp.cmd compile .
$LASTEXITCODE
Copy-Item main.tsp.good-D1-01 main.tsp -Force
.\node_modules\.bin\tsp.cmd compile .
$LASTEXITCODE
```
Expected final exit: zero. Re-read the emitted starter to show it came from restored source. If the initial compile fails, check installed dependencies before investigating your edits.

### 5. Explain and capture (5 min)
Capture compiler output and JSON inspection. State which capability is a future connector dependency and why compile success does not establish Copilot behaviour. Return to Code:
```powershell
Set-Location ..\..
```

## Troubleshooting and recovery
From `Day1`, restart from the original saved exercise:
```powershell
Copy-Item starters\lab1\main.tsp.before-D1-01 starters\lab1\main.tsp -Force
```
For a complete reference recovery (record **assisted**, not independent completion):
```powershell
Copy-Item solutions\lab1\main.tsp starters\lab1\main.tsp -Force
$env:LAB_IMPL = "starters"
Push-Location starters\lab1; .\node_modules\.bin\tsp.cmd compile .; Pop-Location
```
Import failure: stop the clock and use the setup steps in D1_Lab1, not ad-hoc dependency upgrades. Unexpected green before repair: check `$env:LAB_IMPL` and the file you edited. Save files, rerun; do not weaken tests. Close a previous server with Ctrl+C before opening another. Preserve your edited file before taking recovery.

## Record your results
Save the edited file/diff, exact commands, exit codes, negative/red output and final green output. Record elapsed minutes and `independent` or `assisted`, plus your explanation of the decision being tested. Mark `LOCAL VERIFIED` only after observing the checkpoint; otherwise `NOT EXECUTED` or `FAILED`. Use actual test totals, not a prewritten count. A skipped test does not prove its check.


## Completion checklist

- [ ] Your edited instructions and starter appear in freshly emitted JSON.
- [ ] The malformed decorator fails compilation, then the restored source compiles with exit 0.
- [ ] You can explain the connector ID dependency and why compilation is not a Copilot behavior test.

Stop your own local servers and debug tasks when finished. Keep your edited source for the next lab. Follow provider save/expiry instructions; do not delete shared resources.
