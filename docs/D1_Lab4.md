# Day 1 · Lab 4 — Build Zava Travel Assistant with WIQD

## Outcome

Use WIQD to create a new Zava Travel Assistant combining official travel web sources, the currency MCP action and the indexed Zava policies. Follow one workflow: **prepare the project → inspect → validate → provision → test → evaluation demo**. Your earlier agents and indexed documents stay unchanged.

Prerequisites are prepared during Lab 1. Wait for **DAY 1 PREPARATION COMPLETE** before starting. This lab does not repeat those installs.

## 1. Prepare and open the project

1. Keep the instructions in the **left course window**. In its Terminal, run:

```powershell
Set-Location C:\Users\Admin\ma-2041
.\scripts\Start-Lab4.ps1
```

2. For a new project, the script displays the WIQD licence link. Review it. If you agree and are authorized, type **ACCEPT** and complete any further consent prompt. Otherwise, stop.
3. Sign in with the **same Microsoft 365 lab account** used in Labs 1–3. Complete MFA if prompted. Check the account shown by the script.
4. The script creates **ZavaTravelWIQD**, adds the Zava agent files and opens a **new VS Code window**. Place it on the right. Save and close the previous right-hand ZavaLab1 window if it is still open.

**What the script did:** selected Node 24, checked WIQD 1.0.0, copied the working connection ID from your ZavaLab1 agent, added the supplied instructions and currency MCP action, and set the new app's name and MCP domain. It kept the new project's generated identity. It did **not** provision or share the agent. If a completed ZavaTravelWIQD project already exists, it reopens it without replacing your edits; an incomplete or mismatched folder stops setup for instructor review.

The connection ID is copied exactly. For the rehearsed connection this is **`zavatravellocallocal`**; updated Lab 3 defaults produce **`zavatravellocal`**. Do not shorten either value to `zavatravel` or add another suffix.

## 2. Inspect the combined agent

Work in the **new right-hand window** from this point onward.

1. Open **appPackage/declarativeAgent.json**:

    - **WebSearch** uses Port of Seattle and Sound Transit.
    - **GraphConnectors** uses the same full `connection_id` as your working Lab 3 agent. No placeholder should remain.
    - **actions** references **currency-plugin.mcp.json** for Frankfurter.

2. Open **appPackage/instruction.txt**. Notice how company-policy questions, public travel questions and currency requests use different sources.
3. Open **m365agents.yml**. WIQD uses this lifecycle to provision the new app in **dev**. Use the following CLI commands, not F5.
4. Open the Terminal in this project window and run:

```powershell
. C:\Users\Admin\ma-2041\scripts\Use-Node.ps1 -Version 24
$wiqd = 'C:\Users\Admin\ma-2041\tools\wiqd-1.0.0\node_modules\.bin\wiqd.cmd'
Set-Location C:\Users\Admin\AgentsToolkitProjects\ZavaTravelWIQD
```

This selects the runtime for this new terminal. It does not reinstall WIQD. Keep WIQD **1.0.0**; ignore update notices during the lab.

## 3. Validate and provision

1. Check the source definition:

```powershell
& $wiqd plugin validate --mode source --env dev
if ($LASTEXITCODE -ne 0) { throw 'Fix the source validation errors before continuing' }
```

**What this checks:** offline agent-source and project checks. A pass is not a full app-package validation, a successful deployment or an evaluation of agent answers. Correct any reported errors before continuing.

2. Provision the agent:

```powershell
& $wiqd plugin provision --env dev
if ($LASTEXITCODE -ne 0) { throw 'Provisioning failed' }
```

**What this does:** runs the project's provision lifecycle using your lab account. Wait for the entire command to succeed.

3. Open the **Chat install/test link** in that successful provisioning result. Use the lab account and open **Zava Travel Assistant**.

You do not need a separate package, organisation-catalogue publication or tenant-wide share for this personal test. If the Chat link is missing, show the instructor the successful provisioning result; do not invent a link or publish tenant-wide to get past it.

## 4. Test the combined assistant

These are manual behavior checks, not automated evaluations or quality scores.

1. In the new **Zava Travel Assistant** opened from the provisioning link, use your lab account. Add the app if prompted.
2. Start a new conversation and enter:

```text
-developer on
```

3. Test company knowledge:

```text
Will Zava reimburse my airport taxi? Cite the Zava guidance and explain
its conditions. What hotel nightly limit applies?
```

Check that the answer cites the indexed Zava document, explains the taxi conditions and does not invent a hotel limit.

4. Test public travel guidance:

```text
Where can I find official instructions for taking light rail from SEA
airport into downtown Seattle? Link to the official source.
```

Open the Port of Seattle or Sound Transit link and compare it with the answer.

5. Test the MCP action:

```text
Estimate 100 USD in CAD using the latest available reference rate.
Show the effective date and explain whether bank fees are included.
```

Choose **Allow** when Copilot asks to contact Frankfurter. Check developer output for the `convert` tool and compare its returned amount, rate and date with the answer.

6. Test the capabilities together:

```text
I am planning a fictional Zava trip to Seattle. Explain the airport-taxi
reimbursement conditions, give me an official airport-to-city transport
link, and estimate 100 USD in CAD for my example budget. Separate company
policy, public guidance and the currency estimate. Do not book or pay
for anything.
```

Check for a Zava policy citation, an official public link and an actual currency tool result. The answer must not claim that an expense was approved or a payment was made.

If you edit the agent after provisioning, increase the source **appPackage/manifest.json** app `version`, run source validation and provision again in **dev**. Test in a fresh conversation. Do not edit **manifest.dev.json**.

## 5. Instructor demo: evaluate the agent

**Watch the instructor; do not run these commands on your lab VM.** The instructor uses a prepared evaluation environment and an approved Azure judge model. Students need no Azure resources, GitHub account or additional installation.

1. Open `Day1/Lab4-WIQD/evals/zava-demo.json` in the **left instructions window**. The four scenarios cover taxi reimbursement, the missing hotel limit, receipt requirements and currency-estimate boundaries. Each has a reference answer and source context.
2. Watch the instructor run the supplied set against the deployed Zava Travel Assistant. From the prepared instructor project's terminal:

```powershell
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$report = ".evals/zava-demo-$stamp.html"
& $wiqd agent eval --env dev --config evals/zava-demo.json `
    --judge-backend azure --concurrency 1 --eval-log-level info `
    --output $report
if ($LASTEXITCODE -ne 0) { throw 'Evaluation did not complete; inspect the error' }
if (-not (Test-Path $report)) { throw 'No scorecard was produced' }
Start-Process $report
```

3. Read one scorecard result together: the prompt, actual answer, reference answer, evaluator score, threshold and explanation. **Relevance** checks the answer addresses the request; **Coherence** checks clarity; **Groundedness** checks support against the reference; **Similarity** checks agreement with it. The configured threshold is **4 out of 5** for each evaluator. A judge score is evidence to inspect, not a guarantee.
4. Compare the actual answer with the source. A wrong answer may need better instructions or grounding. A sign-in, permission or judge error is a failed evaluation run, not proof of a poor agent. Missing scores are not passes.
5. If a genuine agent defect appears, the instructor makes a focused correction, increases the source app version, validates and provisions again, then reruns the **unchanged** evaluation set to compare scorecards. Do not lower thresholds or remove difficult cases to improve the score.

This small demo evaluates answer quality. It does **not** score citation correctness, live exchange-rate accuracy or actual MCP execution. Keep the manual action checks from Step 4. If live evaluation is unavailable, the instructor may show a previously captured real scorecard, clearly labelled as a prior run; do not claim a new run succeeded.

## Summary

You used WIQD to deploy a new agent that combines company knowledge, public web information and an MCP action. WIQD manages the project lifecycle; Microsoft 365 Copilot runs the agent. The instructor demo shows how a repeatable evaluation set supports an inspect, improve and rerun cycle. The existing connection continues to supply the Zava documents without embedding them in the package.

Keep the project and Lab 3 connection available for the course demonstration. Cleanup follows the instructor's instructions.
