# Day 1 · Lab 4 — Build Zava Travel Assistant with WIQD

## Outcome

Create a new **Zava Travel Assistant** that combines the official travel web sources from Lab 1, the currency MCP action from Lab 2 and the indexed Zava policies from Lab 3. Use WIQD to create, validate and deploy it, then test all three capabilities in Microsoft 365 Copilot.

This reuses your Lab 3 connection. It does not ingest the documents again or change your earlier agents.

## 1. Create the new project

1. Open the **Terminal** in VS Code. Paste and run:

```powershell
. C:\Users\Admin\ma-2041\scripts\Use-Node.ps1 -Version 24
$wiqd = 'C:\Users\Admin\ma-2041\tools\wiqd-1.0.0\node_modules\.bin\wiqd.cmd'
$lab = 'C:\Users\Admin\ma-2041\Day1\Lab1-WIQD'
$project = 'C:\Users\Admin\AgentsToolkitProjects\ZavaTravelWIQD'
& $wiqd --version
& $wiqd auth status
```

2. Use the supplied **WIQD 1.0.0** installation. If sign-in is needed, run `& $wiqd auth login --interactive` and use your assigned training account. If WIQD requires terms acceptance, review the terms. If you agree and are authorized to accept them, run `& $wiqd eula accept wiqd`. This exercise does not use Work IQ or Marketplace publishing.
3. Create the project and its declarative agent:

```powershell
& $wiqd plugin create --name 'ZavaTravelWIQD' --output 'C:\Users\Admin\AgentsToolkitProjects'
if ($LASTEXITCODE -ne 0) { throw 'Project creation failed' }
Set-Location $project
& $wiqd plugin add agent --name 'Zava Travel Assistant'
if ($LASTEXITCODE -ne 0) { throw 'Agent creation failed' }
code .
```

4. In the new project window, open a terminal and set the variables again:

```powershell
. C:\Users\Admin\ma-2041\scripts\Use-Node.ps1 -Version 24
$wiqd = 'C:\Users\Admin\ma-2041\tools\wiqd-1.0.0\node_modules\.bin\wiqd.cmd'
$lab = 'C:\Users\Admin\ma-2041\Day1\Lab1-WIQD'
Set-Location 'C:\Users\Admin\AgentsToolkitProjects\ZavaTravelWIQD'
```

5. In Explorer, open **m365agents.yml**, then **appPackage/manifest.json**. WIQD will run this project's lifecycle using the **dev** environment. Use the terminal commands below, not F5.

## 2. Combine the Zava capabilities

1. Copy the supplied agent definition and instructions, plus the MCP plugin used in Lab 2:

```powershell
Copy-Item "$lab\assets\declarativeAgent.json" '.\appPackage\declarativeAgent.json'
Copy-Item "$lab\assets\instruction.txt" '.\appPackage\instruction.txt'
Copy-Item 'C:\Users\Admin\ma-2041\Day1\Section2-Currency\currency-plugin.mcp.json' '.\appPackage\currency-plugin.mcp.json'
```

2. Open **appPackage/declarativeAgent.json**. Replace `REPLACE_WITH_ACTUAL_CONNECTION_ID` with the exact connection ID you verified in Lab 3.
3. Review the three parts of the file:
   - **WebSearch** uses Port of Seattle and Sound Transit for public transport information.
   - **GraphConnectors** retrieves the fictional company documents already indexed in Lab 3.
   - **actions** loads **currency-plugin.mcp.json**, which calls Frankfurter's MCP server.
4. Open **appPackage/instruction.txt**. Notice how it directs company questions, public travel questions and currency requests to different sources. Review the three conversation starters in **declarativeAgent.json**.
5. In **appPackage/manifest.json**, set `name.short` to `Zava Travel Assistant${{APP_NAME_SUFFIX}}`. Set `name.full` to `Zava Travel Assistant`. Set both description values to `Zava travel guidance, official transport info and currency estimates.`. Add `mcp.frankfurter.dev` to `validDomains`:

```json
"validDomains": ["mcp.frankfurter.dev"]
```

6. Keep the new project's generated identity and its `copilotAgents` reference. Save all files. This is a new app; do not copy the IDs or populated environment files from your earlier agents.

**Checkpoint:** one new agent references your existing Zava connection, two public web sources and the Frankfurter MCP action.

## 3. Validate and deploy with WIQD

1. Run source validation:

```powershell
& $wiqd plugin validate --mode source --env dev
if ($LASTEXITCODE -ne 0) { throw 'Fix the source validation errors before continuing' }
```

2. Read any findings and correct the source files. Once validation passes, provision the new agent:

```powershell
& $wiqd plugin provision --env dev
if ($LASTEXITCODE -ne 0) { throw 'Provisioning failed' }
```

3. Wait for the complete lifecycle to succeed. Keep the returned **Chat install/test link** for the next section.
4. Build the app package:

```powershell
& $wiqd plugin package --env dev
if ($LASTEXITCODE -ne 0) { throw 'Packaging failed' }
```

5. Open **appPackage/build** and inspect the generated ZIP. It should include the agent definition, its resolved instructions and the currency MCP plugin. The Zava policies stay in the Microsoft 365 index; they are not embedded in this ZIP.

**Checkpoint:** WIQD has provisioned the new agent and generated its package. Source validation checks the definition; the following tests check actual behavior.

## 4. Test the combined assistant

1. Open the **Chat install/test link** returned by WIQD using your training account. Add the app if prompted, then open **Zava Travel Assistant** in Microsoft 365 Copilot.
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

If you edit the agent after provisioning, increase the source **appPackage/manifest.json** app `version`, run source validation and provision again in **dev**. Rebuild the package and test in a fresh conversation. Do not edit **manifest.dev.json**.

## Summary

You used WIQD to deploy a new agent that combines company knowledge, public web information and an MCP action. WIQD manages the project lifecycle; Microsoft 365 Copilot runs the agent. The existing connection continues to supply the Zava documents without embedding them in the package.

Keep the project and Lab 3 connection available for the course demonstration. Cleanup follows the instructor's instructions.
