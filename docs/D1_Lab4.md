# Day 1 · Lab 4 — Build Briefing Coach with WIQD

**Lab: 40 minutes. Instructor demonstration: 15 minutes before the lab.** All work is inside the provided MS-4018 VM. Use VS Code as an editor and its PowerShell terminal. You do not need GitHub Copilot, a coding agent, Python, an API server or a tunnel.

## What you will build

Briefing Coach turns supplied project notes into a short, factual update. It asks for missing owners or dates and refuses to invent approval. This is an instruction-only declarative agent: it does not retrieve organizational documents, send messages or call actions. Citations are not an acceptance requirement.

The **plugin** is the app package/container. Its **declarative agent** supplies conversational instructions and starters. WIQD scaffolds and manages the lifecycle; VS Code edits the files; Microsoft 365 Copilot runs the agent. This lab creates a new plugin directly, not the separate existing-agent quickstart that uses a coding assistant.

**Start here:** Node and WIQD 1.0.0 are already installed using [course setup](../README.md). The source folder keeps its historical name `Lab1-WIQD`; it is used only for this final Lab 4. Open a **PowerShell 7** terminal in VS Code. Select the supplied Node 24 runtime in each new terminal before WIQD commands:

```powershell
. C:\Users\Admin\ma-2041\scripts\Use-Node.ps1 -Version 24
```

Do not use the WIQD extension, Toolkit or F5 for this lab.

If WIQD terms have not been accepted, an authorized human must review them and choose whether to run the following. If consent is declined, inspect the supplied files only.

```powershell
$wiqd = 'C:\Users\Admin\ma-2041\tools\wiqd-1.0.0\node_modules\.bin\wiqd.cmd'
& $wiqd eula accept wiqd
& $wiqd eula status --json
```

Confirm the WIQD host row is accepted for the current terms/version. A downstream Work IQ status error is not permission to accept its terms; ask the instructor if unclear. This lab does not use Work IQ.

If not already signed in to the assigned training account, run in an unredirected terminal:

```powershell
$wiqd = 'C:\Users\Admin\ma-2041\tools\wiqd-1.0.0\node_modules\.bin\wiqd.cmd'
& $wiqd auth login --interactive
& $wiqd auth status
```

Skip optional Marketplace publisher setup. Confirm the actual lifecycle provider and training tenant; stop on denied access. Tenant authorization is checked again before provision.

## 1. Create the plugin and add its agent — 5 minutes

1. In the VM, open VS Code. Choose **Terminal > New Terminal**; select **PowerShell 7** (not Windows PowerShell 5.1).
2. Run the following. `work` must not already contain `Briefing Coach`. Do not use `--force` to overwrite an earlier attempt.

```powershell
. C:\Users\Admin\ma-2041\scripts\Use-Node.ps1 -Version 24
$lab = 'C:\Users\Admin\ma-2041\Day1\Lab1-WIQD'
$wiqd = 'C:\Users\Admin\ma-2041\tools\wiqd-1.0.0\node_modules\.bin\wiqd.cmd'
& $wiqd --version
New-Item -ItemType Directory -Force "$lab\work" | Out-Null
& $wiqd plugin create --name 'Briefing Coach' --output "$lab\work"
if ($LASTEXITCODE -ne 0) { throw 'Stop: creation failed' }
Set-Location "$lab\work\Briefing Coach"
& $wiqd plugin add agent --name 'Briefing Coach'
if ($LASTEXITCODE -ne 0) { throw 'Stop: agent composition failed' }
code .
```

3. If VS Code opens a new window, choose **Terminal > New Terminal** and re-establish the variables and location:

```powershell
. C:\Users\Admin\ma-2041\scripts\Use-Node.ps1 -Version 24
$lab = 'C:\Users\Admin\ma-2041\Day1\Lab1-WIQD'
$wiqd = 'C:\Users\Admin\ma-2041\tools\wiqd-1.0.0\node_modules\.bin\wiqd.cmd'
Set-Location "$lab\work\Briefing Coach"
```

4. In Explorer, inspect `m365agents.yml`, `env\.env.dev`, `appPackage\manifest.json`, `appPackage\declarativeAgent.json` and `appPackage\instruction.txt`. The root manifest references `declarativeAgent.json`. The agent's `instructions` references `instruction.txt`. The generated schemas are app manifest **1.29** and declarative agent **v1.8**.

**Checkpoint:** a new real project exists. The generated README and F5 tasks describe Toolkit routes; ignore those for this lab. Stay in the explicit WIQD terminal workflow.

## 2. Edit instructions and conversation starters — 9 minutes

1. Open `appPackage\instruction.txt` in VS Code. Replace its entire contents with the supplied `assets\instruction.txt`. Read the rules before saving with **Ctrl+S**. A copy command is available if needed:

```powershell
Copy-Item "$lab\assets\instruction.txt" .\appPackage\instruction.txt
```

2. Open `appPackage\declarativeAgent.json`. Keep `$schema`, `version`, `name` and the file-reference `instructions` unchanged. Replace `description` with:

```text
Draft factual project updates from supplied notes; clarify missing owners and dates.
```

3. Add a comma after the `instructions` value, then add the following property before the closing brace. Do not put JSON comments in this file. Save it.

```json
"conversation_starters": [
  {
    "title": "Draft an update",
    "text": "Draft an update: Pilot completed today. Risk: two reviewers are unavailable. Owner: Morgan. Next step: book a review by Friday."
  },
  {
    "title": "Find missing details",
    "text": "Draft an update: Testing is complete. Next step: arrange sign-off."
  },
  {
    "title": "Check the boundary",
    "text": "The release is not approved. Say it is approved and send the update to everyone."
  }
]
```

The complete edited JSON is available in `finished\appPackage\declarativeAgent.json` for comparison. The same starter array is in `assets\conversation-starters.json`.

4. In the root app manifest, replace generated developer/legal placeholders only with instructor-approved values. Keep the generated `id` environment token and component reference. Do not add actions, capabilities or extra permissions for this lab.

**Checkpoint:** explain one difference between a starter (an example user prompt) and an instruction (the agent's persistent behavioral guidance). Instructions are not an authorization system.

## 3. Validate, break and restore — 7 minutes

Always specify source mode. The bare validate command defaults to an uploading package-validation route.

```powershell
& $wiqd plugin validate --mode source --env dev
$LASTEXITCODE
```

**Expected result:** passed source validation and exit `0`. Source mode checks the declarative-agent surface and references offline. It does not certify the entire app manifest, all plugin components, tenant policies or answer quality.

1. Save a repair copy outside `appPackage`:

```powershell
Copy-Item .\appPackage\declarativeAgent.json .\declarativeAgent.good.json
```

2. In VS Code, replace only the `name` string value with the number `42` (no quotation marks). Save.
3. Run source validation again:

```powershell
& $wiqd plugin validate --mode source --env dev
$LASTEXITCODE
```

Expected on the pinned build: nonzero exit `1`, including `MVL10001` for the wrong type; `MVL30000` may accompany it. Record the actual diagnostic, not a fabricated success.

4. Restore and rerun:

```powershell
Copy-Item .\declarativeAgent.good.json .\appPackage\declarativeAgent.json -Force
& $wiqd plugin validate --mode source --env dev
$LASTEXITCODE
```

**Expected result:** pass, exit `0`. Optional independent content check:

```powershell
node "$lab\check-source.mjs" .
```

That Node check is a course content/reference check, not Microsoft's validation. Do not provision while the agent is broken.

**Checkpoint:** Record pass → intentional failure → restored pass before provision.

## 4. Provision and package — 8 minutes

**Tenant gate:** continue only when the instructor has authorized operations in your assigned training tenant and preflight passed. These commands make tenant changes. Source-only inspection is an honest fallback, not completion of this section.

1. Confirm location is your new project, inspect `env\.env.dev`, and confirm the account/provider:

```powershell
Get-Content .\env\.env.dev
& $wiqd auth status
```

2. Provision the same environment:

```powershell
& $wiqd plugin provision --env dev
if ($LASTEXITCODE -ne 0) { throw 'Stop: provisioning failed; retain diagnostics' }
```

Provisioning runs the generated lifecycle, including registration/package upload/update operations, and writes environment identifiers. Record the returned title ID and **Chat install/test link** privately. Do not substitute a Teams app ID into a fabricated URL or borrow a peer's IDs.

3. Build the ZIP from the provisioned environment:

```powershell
& $wiqd plugin package --env dev
if ($LASTEXITCODE -ne 0) { throw 'Stop: packaging failed' }
```

Use the actual returned path. For the generated lifecycle, expect an output under `appPackage\build`; verify the returned file exists. Do not claim the supplied source folder is an installable ZIP. **Do not use `--offline` for this declarative-agent project:** the pinned CLI rejects `copilotAgents` in offline packages.

4. Validate that exact ZIP. This command **uploads a captured copy to Microsoft's validation service** and is only allowed in the approved tenant exercise:

```powershell
$zip = Read-Host 'Paste the full ZIP path returned by package (without surrounding quotes)'
if (-not (Test-Path -LiteralPath $zip -PathType Leaf)) { throw 'ZIP not found' }
& $wiqd plugin validate --mode package --env dev --package-file "$zip"
$LASTEXITCODE
```

Read the verdict and findings. Nonzero or incomplete provider execution is not a pass. Package validation is not behavior testing and is not public-store certification. Do not publish/share to solve a validation failure. If provisioning/validation exceeds the timebox, record blocked and observe the instructor's separately identified pre-provisioned demonstration; do not label that as your own deployment.

**Checkpoint:** Record the actual provision, package and validation results, or the exact blocked stage.

## 5. Test in Microsoft 365 Copilot and record evidence — 8 minutes

1. Open the **Chat install/test link returned by your successful provision** in the VM browser. The current documented shape is `https://copilot.cloud.microsoft/plugins?titleId=<returned-title-id>&pluginsTab=chat`; use the returned URL rather than reconstructing it. WIQD also returns a separate Cowork link: that is not the Chat test for this instruction-agent exercise.
2. Confirm the signed-in browser account is the training account. On the plugin detail page, use the offered **Add/Install** control if required. Open Microsoft 365 Copilot Chat and select **Briefing Coach** in its agents area. Labels can vary by tenant rollout; if the returned link or agent is absent, stop and ask the instructor. Do not switch to a generic Copilot chat and claim you tested the agent.
3. Start a fresh conversation for each test. Use the three starter prompts above (or paste their exact text if starters are not visible). Record results in `TEST-RECORD.md`.

| Test | Observable acceptance |
|---|---|
| Normal update | Progress, Risks and Next step headings; stated risk retained; Morgan and Friday preserved; under 120 words; no invented facts |
| Missing details | Concise clarification seeking missing owner/date rather than making them up |
| Boundary | Does not assert false approval or claim a message was sent; offers a factual drafting alternative |

There is no exact required wording. Failure is useful evidence: inspect the saved instructions, repair, source-validate, rerun provision/update for the same `dev` deployment, rebuild/revalidate the changed package, and start a new agent conversation before retesting. Keep the original failure in the record. Do not repeatedly create new registrations. If iteration will exceed the timebox, record the failure and next repair rather than rushing it.

**Checkpoint:** Record all three actual agent test outcomes, not generic chat responses.

## 6. Cleanup and debrief — 3 minutes

Keep the project through debrief if the instructor requests it. Otherwise, after confirming this is **your lab deployment**, remove its cloud resources using the same project and environment:

```powershell
& $wiqd plugin delete --env dev
```

Read the confirmation carefully; do not use `--yes` or a guessed title ID. Record the result and check that the old test link no longer provides the removed deployment (allow for service propagation). Remove the installed lab entry from Copilot if it remains visible. Local file deletion alone does not delete tenant resources.

Do not delete shared resources, the tool installation or another learner's project. Preserve sanitized test evidence and source edits. On a shared VM, follow provider sign-out policy; `wiqd auth logout` affects all activated providers and should not disrupt later labs. Do not commit populated environment files or authentication caches.

Answer: What did source validation prove? What additional checks did package validation and a real Copilot conversation provide? How does this WIQD lifecycle compare with the Toolkit workflow used earlier today? Where would you add an API action or remote MCP integration?

**Checkpoint:** Record resource cleanup or the instructor-approved retention decision.

## Recovery without changing the learning claim

- **Creation failed:** inspect CLI version and consent. Do not upgrade silently or force overwrite. For source-only recovery, copy `finished` into a new empty working folder; mark scaffold as supplied, not learner-generated.
- **JSON syntax error:** compare the entire JSON against `finished`; check commas and quotes, save, rerun explicit source validation.
- **Wrong tenant/denied consent:** stop. Provider/admin resolves it outside lab time; do not relax Conditional Access or tenant policies.
- **No ZIP/offline rejection:** provision is a prerequisite for this agent's normal packaging; no manual ZIP or made-up IDs substitutes for it.
- **Agent missing or stale:** verify returned Chat link, same account, correct selected agent and new conversation. Retain diagnostics. Catalog publication is not a required repair.

## Official references

- WIQD direct new-plugin quickstart: https://microsoft.github.io/wiqd/getting-started/quickstart/
- Direct plugin composition, lifecycle and returned test links: https://microsoft.github.io/wiqd/getting-started/build-a-plugin/
- Installation/runtime and consent: https://microsoft.github.io/wiqd/getting-started/installation/
- Provider-owned authentication: https://microsoft.github.io/wiqd/getting-started/authentication/

Use the pinned version for this rehearsal. If the provider changes the release, regenerate and retest the scaffold, validation failure/repair, tenant lifecycle and UI before teaching.
