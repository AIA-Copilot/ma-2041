# MA-2041 student labs

Eight student handouts and their code. Day 1 uses the provided **MS-4018** VM; Day 2 uses **AI-3026**.

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

## Open the correct workspace

- Day 1: `C:\ma-2041\Day1`; begin [D1_Lab1](Labs/D1_Lab1.pdf). Requires Python 3.11, Node.js 22+, npm, VS Code and Python/Debugger extensions. Follow the handout for local installs.
- Day 2: `C:\ma-2041\Day2`; begin [D2_Lab1](Labs/D2_Lab1.pdf). Use Node.js 22, npm, VS Code, Microsoft 365 Agents Toolkit and Azure CLI. Live model work needs approved existing Azure access.

- [D1_Lab1](Labs/D1_Lab1.pdf)
- [D1_Lab2](Labs/D1_Lab2.pdf)
- [D1_Lab3](Labs/D1_Lab3.pdf)
- [D1_Lab4](Labs/D1_Lab4.pdf)
- [D2_Lab1](Labs/D2_Lab1.pdf)
- [D2_Lab2](Labs/D2_Lab2.pdf)
- [D2_Lab3](Labs/D2_Lab3.pdf)
- [D2_Lab4](Labs/D2_Lab4.pdf)

Editable handouts are in `docs/`. Reference solutions are student scaffolds used by the guides. Do not commit credentials, edited runtime configuration, generated keys or private data. Local tests do not prove VM/F5/Azure success. Day 2 packaging produces a dummy-ID validation-only ZIP: **do not upload it**. No cloud deployment is part of these labs.
