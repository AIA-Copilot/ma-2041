# Day 1 · Lab 4 — Build an agent with PowerShell and WIQD

## Outcome

Edit **Build-Agent.ps1** to define your own Seattle travel guide, then run its visible create → configure → validate → provision steps. Change the configuration and run again to update the **same agent**. This lab uses **WebSearch only**: no connector, connection ID, previous lab project, MCP service or Azure resource is required.

Use the supplied VM with **Node 24** and **WIQD 1.0.0** prepared. Do not upgrade the tools. Provisioning requires your licensed Microsoft 365 lab account and the tenant's permissions; complete MFA if requested.

## 1. Edit your build script

In the course folder open in **VS Code**, open:

```text
Day1/Lab4-WIQD/Build-Agent.ps1
```

Edit the clearly marked configuration at the top:

- **AgentDisplayName:** give your guide a recognizable name, at most 25 characters.
- **Instructions:** describe its purpose, source requirements and boundaries.
- **ConversationStarters:** write the title and prompt text learners will see.
- **ApprovedWebSearchSites:** choose 1–4 official HTTPS sites. Keep Port of Seattle and Sound Transit for the first build.

Leave **ProjectName = 'ZavaScriptAgent'** unchanged so repeat runs use the same project. Save the file. Read the numbered sections below the configuration: you should be able to find `plugin create`, `plugin add agent`, the JSON writes, source validation and provisioning.

## 2. Run the build

In the **left course-window Terminal**, run:

```powershell
Set-Location C:\Users\Admin\ma-2041
.\Day1\Lab4-WIQD\Build-Agent.ps1
```

The script finds the repository relative to its own location, selects the prepared Node 24 runtime and checks the pinned WIQD installation. If the prerequisite check fails, run the following from the course root, wait for completion, then retry the build:

```powershell
.\scripts\Prepare-Day1.ps1 -Target Lab4
```

Do not run preparation concurrently in another terminal.

1. If the current WIQD licence is not already accepted, review the displayed terms. Type **ACCEPT** only if you agree and are authorized, then complete any further WIQD prompt. Any other response stops the build before sign-in or project creation. Previously accepted current terms do not prompt again.
2. Sign in interactively with your Microsoft 365 lab account. Check the account shown by `auth status`.
3. WIQD creates `Day1/Lab4-WIQD/ZavaScriptAgent` and adds an agent. The script writes your configuration into that generated project.
4. Source validation must succeed before `plugin provision --env dev` runs. Source validation is not deployment or an answer-quality test.
5. Wait for **BUILD COMPLETE**, then open the **Chat install/test link printed by WIQD's successful provisioning result**. If the link is missing, show the instructor the result; do not construct a URL or publish tenant-wide.

This provisions for the lab's personal test. No separate package, organisation catalogue publication or sharing step is required. Do not use F5 for this lab.

## 3. Inspect and test

In the VS Code Explorer, inspect the generated files under `Day1/Lab4-WIQD/ZavaScriptAgent`:

- `appPackage/declarativeAgent.json`: your name, instructions, starters and WebSearch sites.
- `appPackage/manifest.json`: the source app manifest, including its version and generated identity reference.
- `m365agents.yml`: the generated provisioning lifecycle.
- `env/`: generated environment values; do not delete or change the app IDs.

In the agent opened from the returned link, start a fresh conversation:

```text
Where can I find official instructions for taking light rail from SEA
airport into downtown Seattle? Link to the official source and tell me
where to check current service information.
```

Open the source link and compare it with the answer. Then ask:

```text
Will my employer reimburse an airport taxi? Can you approve the expense?
```

The guide should explain that it has no company policy source and cannot approve expenses. These are manual behavior checks, not automated scores or a guarantee that every answer is correct.

## 4. Change and rebuild the same agent

1. Return to **Build-Agent.ps1**, not the generated JSON. Change a starter and add an instruction such as “End travel answers with a reminder to check current service notices.” Save.
2. Run the same command again:

```powershell
Set-Location C:\Users\Admin\ma-2041
.\Day1\Lab4-WIQD\Build-Agent.ps1
```

3. Inspect `appPackage/manifest.json`: the source app patch version increases, while the generated identity and environment IDs are retained. The script skips create/add on repeat runs and validates before provisioning again.
4. Open the returned Chat link and test in a **new conversation**. Check the changed behavior and starter after the service refreshes.

The top configuration is the source of truth: reruns replace those generated agent settings. Never edit `manifest.dev.json`. A failed validation/provision can leave your updated source and increased version in place; fix the error and rerun. Skipped version numbers are harmless.

**Safety:** only the new, marked `ZavaScriptAgent` project is updated. Existing unmarked or incomplete folders stop the script without an automatic reset. Do not delete the ownership marker, rename folders, change IDs or use `--force` to bypass this. Ask the instructor. Existing `ZavaTravelWIQD` and earlier lab projects are not used or modified. Linked/junction project paths are refused; use the supplied local course folder, not a synced or linked folder.

## Optional instructor demonstration

Your instructor may demonstrate evaluation in a separately prepared environment. No Azure judge model, evaluation configuration or extra account is required for this student lab. A prior scorecard must be identified as a prior run; it is not evidence that your agent was evaluated.

## Summary

You authored an agent in an editable PowerShell configuration, followed the WIQD lifecycle, inspected the generated source, and rebuilt the same identity with a higher app version. Keep the script and its generated project for the course; follow the instructor's cleanup instructions.
