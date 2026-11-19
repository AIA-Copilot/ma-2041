# D2_Lab1 — Configure and change the Toolkit agent



## Learning outcome

Configure the supplied Toolkit custom-engine reference, change its behavior, and demonstrate an Entra-authenticated Azure response in Microsoft 365 Agents Playground. Explain which layer owns each action. This is an adaptation of a supplied Toolkit template, not a claim that you generated or tested a fresh wizard scaffold.

Launch Go Deploy **AI-3026 Develop AI Agents on Azure (Cloud Share)**, **1. Build AI agents with portal and VS Code**. Follow provider instructions for approved project/model access only; do not replace this app with their Foundry playground agent. If the title or entitlement is absent, stop and ask the provider rather than purchasing another allocation.

**Diagram in prose:** VS Code + Agents Toolkit → local build/configuration/debug lifecycle → Playground sends an activity → Agents SDK handles the activity → `PolicyAgent` retrieves fictional policy and constructs a Responses request → Foundry serves the Azure model → the application validates citation IDs → SDK returns an activity. Toolkit is not the model; Foundry is not the channel adapter. Your instructions do not create account permissions.

## Prepare the Day 2 working copy — outside the timer

1. Use the assigned AI-3026 virtual machine. Confirm the provider's selected exercise, tenant/subscription scope, existing Foundry project, expiry/save rules and approved resource-use limits before signing in. If access, quota, roles or required software are missing, ask the provider; do not create replacement resources or use production credentials.
2. Acquire the repository using the instructions below; the project root is `C:\ma-2041\Day2`.
3. Keep an untouched source copy for recovery. Across all four Day 2 labs, edit the **same TypeScript project**. Do not mix in Day 1 Python files. The course code includes all checkpoint files; no separate setup or answer document is required.
4. Confirm permission for local dependency downloads, loopback HTTP callbacks and approved Azure model requests. Required software is listed below. Missing tools must be installed through the provider-approved process; do not disable policy. Foundry Toolkit, if present, is not Microsoft 365 Agents Toolkit.
5. The existing deployment must support Responses and strict function tools with the assigned account's Entra access. The code accepts a Foundry project endpoint under `https://...services.ai.azure.com/api/projects/...`, not an Azure OpenAI resource root. Model access is mandatory for Labs 1–3 and Lab 4 live debugging. If Azure is blocked, code inspection and local tests may continue, but record the live portion as **BLOCKED**, not complete. There is no fixture fallback.
6. Day 2 ends with local debug and validation-only packaging. No upload, Provision, Publish, cloud deployment, tunnel or bot/host resource creation is authorized by these handouts. An Azure model does not provide Teams hosting or app permissions.

### Get the student repository (once per VM)

Start in the provided **MS-4018 VM for Day 1** or **AI-3026 VM for Day 2**, not your personal computer. Cloning downloads files only; it does not install Python, Node.js, extensions or Azure CLI. Use the provider-approved software process if a required tool is missing. Open PowerShell.

If `C:\ma-2041` already contains your work, reuse it and skip acquisition; do not clone, extract or reset over it. Otherwise choose **one** method below.

**Option A — Git clone** (Git must already be installed):

```powershell
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

## Developer setup — outside the timer

Required: approved VM install/download permissions; Node.js **22**; npm; Git (clone option only); Azure CLI; VS Code with **Microsoft 365 Agents Toolkit**, extension ID `TeamsDevApp.ms-teams-vscode-extension`; an existing approved Foundry project and deployment supporting Responses and strict function tools. A VS Code account alone does not authenticate this app.

In VS Code select **File > Open Folder**, choose `C:\ma-2041\Day2`, and confirm Explorer shows `package.json`, `src`, `.vscode` and `m365agents.playground.yml` at the root. Use **Terminal > New Terminal**, then the terminal profile dropdown to select **PowerShell**. These commands assume native Windows PowerShell and Windows Node. Do not switch this workspace into WSL halfway through authentication.

```powershell
Set-Location 'C:\ma-2041\Day2'
node --version
npm --version
az version
code --version
npm ci
npm run build
npm test
npm run package:check
```

Expected: Node major 22; install/build/default tests/package check succeed. Default tests include clearly labeled fixture transports; they prove local contracts only. Preserve an untouched source copy before editing (exclude credentials, generated files and runtime configuration). The opt-in checkpoints intentionally start RED; do not add them to `npm test` or “repair” them before the lesson.

Use the provider-approved account and only its assigned tenant/subscription:

```powershell
az login
```

**Same OS rule:** run `az login` in the OS that runs Node, inside this VM. Windows Azure CLI and WSL Azure CLI have different caches. This implementation uses `AzureCliCredential`, not an API key, the Toolkit sign-in UI, or a hidden fixture fallback. Stop on unapproved tenant selection, missing project role, quota or incompatible model. Never export tokens for troubleshooting.

## Keep a short lab record

Use your own notes file in the working copy. Record the lab name, changed files, commands, observed outputs/exit codes, positive and negative checks, restored state, and any blocker. Save only fictional data and sanitized screenshots. Never include tokens, keys, passwords, login caches or runtime configuration files. Expected output in this handout is a target to compare against, not proof that your run succeeded.

## Planned core — 43 minutes after setup

| Stage | Minutes | Observable checkpoint |
|---|---:|---|
| Trace the layers and inspect lifecycle | 5 | Identify model, SDK and Toolkit responsibilities |
| Configure the project and runtime | 8 | Configuration shape passes without secrets |
| Capture RED and edit behavior | 10 | Lab 1 checkpoint turns GREEN |
| Run the real model in Playground | 13 | Changed welcome plus Azure-backed cited reply |
| Negative evidence and acceptance notes | 7 | Unsupported topic stops before model call |

## 1. Inspect before pressing F5 — 5 minutes

Open `.vscode/launch.json`, `.vscode/tasks.json` and `m365agents.playground.yml`. The compound **Debug in Microsoft 365 Agents Playground** invokes **Start App in Microsoft 365 Agents Playground**, which validates local prerequisites, invokes Toolkit deploy for `playground`, installs/builds, writes runtime configuration and starts the app/Playground. Here “deploy” is local lifecycle work, not an Azure deployment. Check that the inspected file matches this description; stop on unexpected provisioning or tunnel actions.

Ports are loopback app `3978`, Node inspector `9239`, Playground `56150`. Do not expose them publicly. Do not choose a Teams/Copilot cloud target, Provision or Publish.

## 2. Create both configuration surfaces — 8 minutes

Open `env/.env.playground` in Explorer. Enter the actual provider-approved nonsecret endpoint and deployment name. This block shows shape only; replace bracketed descriptions, never run with placeholders:

```dotenv
ENVIRONMENT=playground
PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
MODEL_DEPLOYMENT_NAME=<existing-deployment-name>
```

The endpoint is the Foundry **project endpoint**, not its portal URL and not an Azure OpenAI resource root. The deployment name is not necessarily the model family. No password, token or key belongs here.

Prepare the terminal runtime file as well. If it already exists from this launch, edit it rather than overwriting approved values:

```powershell
if (-not (Test-Path '.localConfigs.playground')) {
    Copy-Item '.localConfigs.playground.example' '.localConfigs.playground'
}
code '.localConfigs.playground'
```

Set `HOST_MODE=local` and the identical `PROJECT_ENDPOINT` and `MODEL_DEPLOYMENT_NAME` values in that file. Save both files. F5 later regenerates `.localConfigs.playground` from `env/.env.playground`; editing only the runtime file will not survive that lifecycle.

```powershell
npm run preflight
```

Expected message starts `Configuration shape PASS`. It does **not** prove login, roles or Azure connectivity. STOP if shape fails. Do not put runtime settings or Azure CLI caches in your source archive.

## 3. Make a genuine behavior edit — 10 minutes

Run the opt-in checkpoint before changes:

```powershell
npx tsx --test checkpoints/lab1.test.ts
```

Expected RED on the untouched reference. In `src/core.ts`, replace only the `WELCOME` declaration with:

```typescript
export const WELCOME=
  'Northstar lab support: I explain fictional policy and draft plans, ' +
  'never change records.';
```

Append this exact sentence **inside** the existing `INSTRUCTIONS` string, immediately before its closing quote. Preserve all existing safety, citation and tool rules:

```text
 Use at most three sentences.
```

Save, then run:

```powershell
npx tsx --test checkpoints/lab1.test.ts
npm run build
npm test
```

Expected GREEN. This proves the text edit exists, not that the model always obeys it. Explain why deleting the safety instructions to shorten answers would be the wrong fix.

## 4. Observe the same app using real Azure — 13 minutes

Select **Run and Debug** in VS Code's Activity Bar; choose **Debug in Microsoft 365 Agents Playground** in its dropdown, then press **F5**. Do not select a cloud/channel target. Allow local install/build to finish. Open the Playground at `http://127.0.0.1:56150` if it does not open automatically. Start a new conversation; an old conversation may not receive a new welcome event. Confirm the changed welcome.

Send this exact prompt:

```text
Explain access recovery policy
```

Expected: a real model request; an answer grounded in access recovery, normally citing `[P2]`, with no request for passwords/MFA codes and no claim an account was changed. Check the three-sentence instruction as observed behavior, not a guaranteed validator. For request evidence, put a breakpoint on `this.transport.create(...)` in `src/core.ts`, resend, inspect `this.model` and `instructions`, and press **Continue (F5)** promptly. Keep pauses brief: live requests can time out. Do not screenshot authorization values.

After stopping the debugger, the separate live gate is:

```powershell
npm run verify:azure
```

It makes real requests using `.localConfigs.playground`, including a tool-capable assessment prompt. Success prints validated replies and a reminder that this log alone does not prove model tool selection. Save sanitized output; do not claim the Lab 3 function trace yet.

If native F5 cannot run, report that blocker. For diagnostic comparison only, after `npm run build`, run `npm start` in one terminal and `npm run dev:teamsfx:launch-playground` in a second. That can establish model/SDK behavior but cannot be recorded as a successful Toolkit F5 exercise.

## 5. Negative check and acceptance evidence — 7 minutes

Restart the same **Debug in Microsoft 365 Agents Playground** F5 compound after the terminal live gate. Ensure the transport breakpoint is enabled. Send `Explain access recovery policy` once and confirm that it hits the breakpoint; press **Continue (F5)** and wait for the reply. This positive control proves the debugger is attached. Then, in Playground send:

```text
banana astrophysics
```

Expected diagnostic begins `I found no relevant policy passage` and ends `No model answer was generated.` With a breakpoint on the transport call, confirm this request does not reach it. This intentional no-result path is not an outage fallback.

Save a sanitized record in your lab notes: provider title; runtime/Node version; files changed; checkpoint RED then GREEN; build/default-test outcome; actual live prompt/reply and citation; F5 outcome; negative observation; GO/BLOCKED reason. Do not copy credentials, runtime files or tokens into notes.

**Acceptance:** only call the live portion complete when the changed app returns an actual Azure-backed answer. Tests plus a welcome message are insufficient. A denied or unavailable model means CONDITIONAL GO for code work, **BLOCKED** for live acceptance. No fixture substitute is allowed.

## Troubleshooting and recovery

- Startup blocked: compare both configuration files; rerun shape preflight; verify the endpoint shape and same-OS approved CLI login. Do not broaden endpoint validation to hide a mismatch.
- F5 waits/port occupied: stop this app's debug session and its own tasks via **Terminal > Run Task / Terminate Task** as exposed by VS Code; do not kill unrelated services. Retry after the owned processes stop.
- Model gate fails: preserve the sanitized message and ask about assigned role, deployment capability, quota and expiry. No production-account workaround.
- Breakpoint timeout: Continue, stop/restart the owned app, start a fresh conversation and retry once. Keep the failed attempt in evidence.
- Reset only `src/core.ts` from the untouched copy if necessary. Reapply edits, rebuild and restart; never erase the entire workspace or provider allocation.


## Completion checklist

- [ ] The changed welcome and retained instructions pass the Lab 1 checkpoint.
- [ ] Toolkit F5 produces an actual Azure-backed cited reply; the terminal live gate also succeeds.
- [ ] The positive request hits the model breakpoint; the unsupported request does not.
- [ ] Any missing Azure/F5 evidence is recorded as blocked rather than replaced by a fixture pass.

Stop your own local servers and debug tasks when finished. Keep your edited source for the next lab. Follow provider save/expiry instructions; do not delete shared resources.
