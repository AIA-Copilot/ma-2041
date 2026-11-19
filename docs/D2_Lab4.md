# D2_Lab4 — Debug and package the same agent



## Learning outcome

Inspect the continuing agent at the model/tool boundary, change its app display name, prove the package check rejects a broken asset, and make a defensible local-versus-channel deployment decision.

Pair with Go Deploy **5. Deploy agents to Microsoft Teams and Copilot**. This allocation is a source of potential channel/resource prerequisites, not proof that our SDK app can be hosted there. The provider's portal publishing flow publishes a different Foundry knowledge agent; completing it is not deployment of this TypeScript application.

**Explicit outcome boundary:** local debug/package work is possible. Live Teams/Copilot hosting and identity remain **BLOCKED** until an approved route exists and is exercised. This lab does not deploy the application to Teams or Copilot. Do not upload the generated ZIP, expose the anonymous local endpoint or improvise a hosting identity.

**Diagram in prose:** Toolkit launch/tasks → compiled Node app + debugger → SDK local activity endpoint → policy/model/tool orchestration → Playground reply. Separately, manifest + icons → local schema/package check → validation-only ZIP. A real Teams/Copilot client would additionally require an approved authenticated HTTPS host, bot/app registration, channel enablement and tenant install permission. The manifest is not the host; packaging is not publishing; a model endpoint is not a bot registration.

## Prerequisite prior state

D2_Lab1–D2_Lab3 edits retained; all three opt-in checkpoints and default tests GREEN; actual model response and function trace captured. Use Node.js **22**, the same `Code` workspace, and approved Azure access. For any provider launch switch, copy sanitized source only, repeat D2_Lab1 configuration creation and `az login` in the same OS as Node. `env/.env.playground` drives F5; `.localConfigs.playground` drives terminal commands. Do not bring old launch credentials.

In VS Code **File > Open Folder**, select the continuing `C:\ma-2041\Day2`; **Terminal > New Terminal > PowerShell**:

```powershell
Set-Location 'C:\ma-2041\Day2'
node --version
npm run preflight
npx tsx --test checkpoints/lab1.test.ts checkpoints/lab2.test.ts checkpoints/lab3.test.ts
npm run build
npm test
```

Without Azure, only manifest/package activities may be marked locally complete. Fixture traces do not meet the live debugger criterion.

## Keep a short lab record

Use your own notes file in the working copy. Record the lab name, changed files, commands, observed outputs/exit codes, positive and negative checks, restored state, and any blocker. Save only fictional data and sanitized screenshots. Never include tokens, keys, passwords, login caches or runtime configuration files. Expected output in this handout is a target to compare against, not proof that your run succeeded.

## Planned core — 43 minutes after setup

| Stage | Minutes | Observable checkpoint |
|---|---:|---|
| Inspect local lifecycle and place breakpoints | 5 | Correct app/target and safe local tasks |
| Debug real request and function | 12 | Request, arguments, result and reply traced |
| Edit display name and package | 8 | New name in validation ZIP |
| Break/restore an icon reference | 8 | Negative then positive package check |
| Channel stop/go assessment and evidence | 10 | Incomplete deployment recorded honestly |

## 1. Select the safe target — 5 minutes

Read `.vscode/launch.json` and `.vscode/tasks.json` again. **Debug in Microsoft 365 Agents Playground** attaches through **Attach to Local Service** on `9239`, with compiled files under `lib`. Its local lifecycle uses `m365agents.playground.yml`. No cloud provision/tunnel task belongs in this route. Stop if your workspace files differ materially.

Open `src/core.ts`. Place breakpoints on `this.transport.create(...)` and `executeTool(...)`. Choose **Run and Debug > Debug in Microsoft 365 Agents Playground**, then **F5**. Start a fresh conversation at `http://127.0.0.1:56150` after the local services are ready.

## 2. Follow the actual request — 12 minutes

Send:

```text
Assess a draft support request: category outage, impact department, affectedUsers 30, dataRisk false, summary Department service unavailable.
```

At the first breakpoint inspect `this.model`, `selected`, `instructions`, and the newest user entry in `input`. Explain why selected passage P3 is relevant. Step/Continue promptly; do not inspect credential objects or headers. At the tool line inspect `call.name`, `call.arguments` and `call.call_id`. Use **F11** into `executeTool`, then **Shift+F11** back; inspect `result` if in scope, otherwise inspect its serialized `function_call_output` in `input` before the next transport call. Confirm the matching call ID.

Expected draft result: P1 priority, Incident Management queue, `DRAFT_ONLY`, human approval required; no ticket created. Continue through the second Azure response and confirm a delivered cited answer. Both invocation and returned result matter; a breakpoint hit before a failed request alone is not completion.

**Short pauses only:** live requests have a timeout and the Playground delivery path can also time out. Resume immediately after a small inspection; preserve any failed attempt and retry a fresh conversation. If the model never emits a function call, record that as incomplete rather than hand-invoking the function in Debug Console.

Stop the debugger and terminate only this workspace's remaining owned local tasks before packaging. No cloud resource was created by that debug run.

## 3. Change the package identity surface — 8 minutes

Open `appPackage/manifest.json`. Set `name.short` to:

```json
"Northstar Lab Support"
```

Keep `name.full` and other descriptions unless deliberately extending later. Preserve `${{TEAMS_APP_ID}}` and both `${{BOT_ID}}` placeholders: the bot and `copilotAgents.customEngineAgents` must reference the same bot identity. Do not invent actual tenant IDs or put secrets in the manifest.

Run:

```powershell
npm run build
npm test
npm run package:check
```

Equivalent VS Code selection: **Terminal > Run Task > Package only (no publish)**. The script checks the bundled official Teams v1.30 schema, icon paths, matching bot ID, lifecycle action allowlist and task references, then writes:

```text
appPackage/build/LOCAL-VALIDATION-ONLY.zip
```

The success message explicitly says dummy IDs, not published or install-tested. Inspect the ZIP's manifest without uploading it:

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem
$path = Resolve-Path 'appPackage/build/LOCAL-VALIDATION-ONLY.zip'
$zip = [System.IO.Compression.ZipFile]::OpenRead($path.Path)
try {
    $zip.Entries | Select-Object FullName, Length
    $entry = $zip.GetEntry('manifest.json')
    $reader = [System.IO.StreamReader]::new($entry.Open())
    try {
        $manifest = $reader.ReadToEnd() | ConvertFrom-Json
    } finally { $reader.Dispose() }
    $manifest.name.short
    $manifest.bots[0].botId
    $manifest.copilotAgents.customEngineAgents[0].id
} finally { $zip.Dispose() }
```

Expected entries `manifest.json`, `color.png`, `outline.png`; short name `Northstar Lab Support`; identical bot/custom-engine dummy IDs. This ZIP contains example developer URLs and dummy identifiers. It is **not tenant-deployable** and **must not be uploaded**.

## 4. Prove a broken package is rejected — 8 minutes

In the source manifest, change only `icons.color` from `color.png` to `missing.png`. Do not rename or delete the actual icon file. Save and run:

```powershell
npm run package:check
$LASTEXITCODE
```

Expected nonzero exit with `Missing/unsafe icon`. The older ZIP may still exist from the previous pass: existence is not proof of a fresh successful package. Record this negative result.

Restore `icons.color` to `color.png`, save, and rerun:

```powershell
npm run package:check
$LASTEXITCODE
```

Expected PASS and exit 0. Reinspect the rebuilt ZIP name/entries using the prior command. Preserve the valid final manifest, not the intentional fault. There is no Lab 4 checkpoint test file; its gates are debugger observation plus the build/default-test/package positive-negative-positive sequence.

## 5. Channel stop/go decision and acceptance evidence — 10 minutes

Use the provider's actual allocation information, not assumptions. A live route for **this same SDK app** needs all of:

- Existing approved bot registration and actual app/bot IDs aligned with the manifest.
- Teams/Microsoft 365 channel enablement and an approved authenticated HTTPS hosting endpoint.
- Runtime identity/secret configuration supplied through approved host secret settings, not source, ZIPs or learner notes.
- Assigned tenant account, app upload/distribution permissions, allowed real developer URLs, and Copilot entitlement if targeting Copilot.
- A deliberately supported model identity on that host. This app uses `AzureCliCredential`; unattended managed-identity adaptation is **not supplied**.

The source exposes `HOST_MODE=approved-channel` with `NODE_ENV=production`, `clientId`, `tenantId` and `clientSecret` requirements and SDK JWT validation. That is a configuration gate, **not** a tested hosting recipe. Do not fill these with production values or switch modes to bypass the local guard. `m365agents.yml` and `m365agents.local.yml` deliberately block provision/publish; their deploy phase builds/packages only. No cloud deployment command is authorized in this lab.

**Current decision:** local debug/package acceptance can be recorded when observed; live channel is **BLOCKED — incomplete deployment outcome**. Do not run Toolkit Provision, Deploy, Publish, tunnel setup, app upload or provider resource creation as part of this lab. A separately approved and verified hosting route is required before a later channel exercise. Completing another Foundry agent's portal publish flow cannot close this gap.

Record in your lab notes: same-project debugger trace, live response/function outcome, manifest name change, first package PASS, missing-icon FAIL, restored PASS, ZIP entries/identity equality, and each missing channel prerequisite. Keep sanitized evidence only. The acceptance claim is “same agent locally debugged and package-only validated,” never “deployed to Teams.”

## Troubleshooting and recovery

- Hollow breakpoint: confirm workspace root, build success, source maps and attach port 9239. Restart the owned F5 target, not a second app.
- Port collision: stop only owned sessions/tasks; do not kill unrelated services. Loopback must remain loopback.
- Timeout: Continue promptly, restart owned app, use a fresh conversation and record retry. Do not remove runtime limits to hide the failure.
- Package error: inspect source manifest JSON punctuation, icon references, and matching bot placeholders. Restore `color.png` before the final check. Do not treat the stale ZIP as success.
- Reset only `appPackage/manifest.json` from the untouched reference if needed, then reapply `name.short`. Keep Labs 1–3 changes. Do not delete provider resources; none were deployed by this lab.


## Completion checklist

- [ ] You trace the same agent through a real Azure request, model-selected function and returned result.
- [ ] The validation ZIP has your short name and the three expected entries.
- [ ] The missing icon fails, restoring color.png passes, and the final ZIP is reinspected.
- [ ] The ZIP remains local and is not uploaded. Teams/Copilot deployment is not completed by this lab.

Stop your own local servers and debug tasks when finished. Keep your edited source for the next lab. Follow provider save/expiry instructions; do not delete shared resources.
