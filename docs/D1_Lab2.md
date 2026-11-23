# Day 1 · Lab 2 — Zava Currency Converter: API, Adaptive Cards and MCP

## Outcome

Build the Zava Currency Converter to help employees estimate costs for international travel using current and historical reference exchange rates. Test its answers in Microsoft 365 Copilot, add an Adaptive Card to display the rate and effective date, and verify that the agent handles unsupported currencies and cannot transfer money. Finally, switch the same agent from its REST action to Frankfurter MCP and test rate lookups and amount conversions.

## 1. Check the public API

1. Open the **Terminal** in VS Code.
2. Paste and run these commands to request a USD-to-CAD rate:

```powershell
$rate = Invoke-RestMethod 'https://api.frankfurter.dev/v2/rate/USD/CAD'
$rate | Format-List
```

3. Find `base`, `quote`, `rate` and `date` in the response.
4. Read the result as: **1 unit of base currency equals rate units of quote currency, effective on date.** The date can be earlier than today. Do not compare a changing rate with a fixed value in an instructor screenshot.
5. Paste and run this command to request a historical rate:

```powershell
Invoke-RestMethod 'https://api.frankfurter.dev/v2/rate/USD/CAD?date=2024-01-02'
```

6. Paste and run these commands to check the error for an invalid currency:

```powershell
try {
    Invoke-RestMethod 'https://api.frankfurter.dev/v2/rate/USD/ZZZ' -ErrorAction Stop
    throw 'Unexpected success for invalid currency; ask the instructor.'
} catch {
    if ($null -eq $_.Exception.Response) { throw }
    $status = [int]$_.Exception.Response.StatusCode
    Write-Host "HTTP status: $status"
    if ($status -ne 422) { throw }
}
```

**Checkpoint:** Valid requests return a rate object. Invalid `ZZZ` returns HTTP 422.

## 2. Create the Zava Currency Converter

Keep your Lab 1 travel assistant unchanged. This second Zava agent helps employees estimate international travel costs; Lab 3 will return to the travel assistant.

1. Open **Microsoft 365 Agents Toolkit** in VS Code.
2. Choose **Create a New Agent/App** (the wording can vary by Toolkit version).
3. Choose **Declarative Agent**, then **No Action**.
4. Use the default project folder: `C:\Users\Admin\AgentsToolkitProjects`.
5. Name the project **CurrencyAssistant**. Open the generated project in VS Code.
6. In Toolkit **Accounts**, confirm your assigned Microsoft 365 account and tenant.
7. Open `appPackage/declarativeAgent.json`. Change its display `name` to `Zava Currency Converter` and its `description` to `Estimate international travel costs using currency reference rates and effective dates.` Preserve the generated schema version and other fields.

**Checkpoint:** The project contains `appPackage/declarativeAgent.json`, `appPackage/manifest.json` and `m365agents.yml`. If your template proposes Azure hosting or starts a tunnel, you selected the wrong project type. Stop and return to the declarative-agent **No Action** template.

## 3. Add the supplied OpenAPI contract and plugin

You will wire the supplied files directly so each connection is visible. Do not generate an OpenAPI file in Postman, and do not use the Add Action wizard as well as these steps.

1. Open a terminal in the generated project.
2. Paste and run these commands to copy the prepared files:

```powershell
Set-Location 'C:\Users\Admin\AgentsToolkitProjects\CurrencyAssistant'
$assets = 'C:\Users\Admin\ma-2041\Day1\Lab2-CurrencyConverter'
New-Item -ItemType Directory -Force '.\appPackage\apiSpecificationFile' | Out-Null
Copy-Item "$assets\frankfurter.openapi.yaml" '.\appPackage\apiSpecificationFile\frankfurter.openapi.yaml'
Copy-Item "$assets\currency-plugin.no-card.json" '.\appPackage\currency-plugin.json'
Copy-Item "$assets\currency-instructions.txt" '.\appPackage\instruction.txt'
```

3. Open `appPackage/apiSpecificationFile/frankfurter.openapi.yaml`. Find:
   - Server: `https://api.frankfurter.dev/v2`.
   - Operation: `GET /rate/{base}/{quote}`.
   - Operation ID: `getExchangeRate`.
   - Required path parameters: `base` and `quote`.
   - Optional query parameter: `date`.
   - Response fields: `date`, `base`, `quote`, `rate`.
4. Open `appPackage/currency-plugin.json`. Verify the function name matches `getExchangeRate`, runtime is `OpenApi`, authentication is `None`, and `spec.url` points to the copied YAML.
5. Open `appPackage/declarativeAgent.json` and add this top-level `actions` property inside the JSON object. Add a comma after the preceding property. If an empty `actions` property already exists, replace it rather than adding a duplicate.

```json
"actions": [
  {
    "id": "currencyAction",
    "file": "currency-plugin.json"
  }
]
```

6. Replace the template's example conversation starters with these, using the existing `conversation_starters` property or adding it once:

```json
"conversation_starters": [
  { "title": "Latest rate", "text": "Get the latest available USD to CAD reference rate and its effective date." },
  { "title": "Historical rate", "text": "Get the USD to CAD reference rate for January 2, 2024." }
]
```

7. In `appPackage/manifest.json`, add `api.frankfurter.dev` to `validDomains`. Preserve any existing entries. If the array is empty, the result is:

```json
"validDomains": ["api.frankfurter.dev"]
```

8. Save all files. Fix any JSON syntax errors shown by VS Code before continuing.

**Checkpoint:** Explain the chain: declarative agent → plugin → OpenAPI operation → public HTTPS service. The VM has not become an API server. The sample has no create/update/delete operation.

## 4. Provision and test the action without a custom card

1. Use the **dev** environment configuration for this lab.
2. In Toolkit, select **Provision** for the dev environment. Follow sign-in prompts for the assigned training account. This registers/packages the agent in Microsoft 365, not in Azure.
3. If validation reports a missing file or invalid JSON, correct that file and retry. If tenant policy refuses upload or requires admin approval, ask the instructor. Do not change deployment scope to bypass the refusal.
4. Open `https://m365.cloud.microsoft/chat` in the VM browser. Sign in with the same training account. Open the agent list/conversation drawer and select the newly provisioned agent, following Microsoft's Toolkit test route.
5. Start a new conversation with **Zava Currency Converter**. The picker may instead show the generated application name **CurrencyAssistant** with a dev suffix. Do not use ordinary Copilot or your section 1 agent.
6. Enter `-developer on` in the agent chat and send it to enable developer mode.
7. Enter:

```text
Get the latest available USD to CAD reference rate and its effective date. Use the currency action.
```

8. When Copilot asks to connect to **Currency Reference Rates**, select **Allow**.
9. Expand **Agent debug info** in the response. Under **Actions**, find **Currency Reference Rates** and check whether `getExchangeRate` is **Matched** and **Selected**. These statuses show function selection, not proof of a successful API response. Inspect the action result and compare its rate and date with a fresh API request from step 1.
10. Enter the historical prompt from the starter. Verify both the requested historical date and the returned effective date.

**Checkpoint:** The agent actually invokes the currency action and reports the returned rate and date.

## 5. Add the Adaptive Card

1. In the project terminal, paste and run these commands to copy the card into your project and replace the no-card plugin with the with-card plugin:

```powershell
$assets = 'C:\Users\Admin\ma-2041\Day1\Lab2-CurrencyConverter'
Copy-Item "$assets\currency-card.json" '.\appPackage\currency-card.json'
Copy-Item "$assets\currency-plugin.with-card.json" '.\appPackage\currency-plugin.json'
```

2. In Explorer, open `appPackage/currency-card.json`. Find the expressions `${base}`, `${quote}`, `${rate}` and `${date}`. They bind to fields in the API response.
3. Open `appPackage/currency-plugin.json`. Find `functions[0].capabilities.response_semantics`.
4. Notice that `data_path` is `$` because the rate response is one object at the root. The `static_template` contains the complete card. It is intentionally embedded, not a separate deployed file reference.
5. Open `appPackage/manifest.json`. Increase the top-level `version` to a higher app version, for example `1.0.0` to `1.0.1`. Do not edit the generated `manifest.dev.json`, `manifestVersion`, or the declarative agent's schema version.
6. Save all files. Run Toolkit **Provision** again for the same dev environment. Reload `https://m365.cloud.microsoft/chat`, select your agent, and start a fresh conversation.
7. Ask for the USD-to-CAD rate again.
8. Open the action result's source/citation. Microsoft 365 can display this card within the citation rather than directly in the main answer.
9. Verify the card shows the currency pair, rate, effective date and reference-rate disclaimer. Narrow the Copilot pane and check that the text still fits.

**Checkpoint:** The real API response populates the custom card. A screenshot of a locally rendered sample is useful for layout checking but does not satisfy this Copilot checkpoint.

## 6. Check boundaries

1. Ask: `Get the USD to ZZZ exchange rate.` The agent must report an unsupported code or a failed request, not invent a rate. It may ask you to correct the code instead of calling the API; the direct HTTP test in step 1 separately checks service error handling.
2. Ask: `Transfer 100 USD into CAD for me.` The agent must explain that it cannot transfer money. There is no payment operation in the contract.
3. Optional: ask `Estimate how many CAD 100 USD would buy at that reference rate, excluding fees.` Check the multiplication yourself:

```powershell
$rate = Invoke-RestMethod 'https://api.frankfurter.dev/v2/rate/USD/CAD'
[math]::Round(100 * $rate.rate, 2)
```

The amount is multiplied locally. The API returns a rate, not a converted amount. A bank's rate and fees may differ. The card continues to display the reference rate, not this optional calculation.

## 7. Switch the same agent from REST to MCP

Replace the REST action with Frankfurter's hosted MCP server. Keep the same agent and business task; change how it calls the service. No API key, local server or new project is needed. MCP still uses HTTPS, but exposes named tools instead of the OpenAPI operation used earlier.

1. In the project terminal, paste and run:

```powershell
Set-Location 'C:\Users\Admin\AgentsToolkitProjects\CurrencyAssistant'
$assets = 'C:\Users\Admin\ma-2041\Day1\Lab2-CurrencyConverter'
Copy-Item "$assets\currency-plugin.mcp.json" '.\appPackage\currency-plugin.mcp.json'
Copy-Item "$assets\currency-instructions.mcp.txt" '.\appPackage\instruction.txt'
```

2. Open `appPackage/currency-plugin.mcp.json`. Find:
   - Runtime: `RemoteMCPServer`, replacing `OpenApi`.
   - Server URL: `https://mcp.frankfurter.dev/`, replacing the OpenAPI file reference.
   - Authentication: `None`.
   - Tools: `get_rates` for rate lookups and `convert` for amount conversions.
   - `mcp_tool_description.tools`: supplied tool names and input schemas from the server. This lab pins these two tools rather than discovering every tool dynamically.
3. Open `appPackage/instruction.txt`. Notice that rate requests now use `get_rates`, and amount conversions use `convert` with `details: true` to return the rate and effective date.
4. In `appPackage/declarativeAgent.json`, replace the existing `actions` array with this one. Do not add a second `actions` property. Preserve the other properties and any separating comma after the array.

```json
"actions": [
  {
    "id": "currencyAction",
    "file": "currency-plugin.mcp.json"
  }
]
```

5. In `appPackage/manifest.json`, add `mcp.frankfurter.dev` to `validDomains`. Keep the existing entries. With the earlier REST domain, the array is:

```json
"validDomains": ["api.frankfurter.dev", "mcp.frankfurter.dev"]
```

6. Increase the top-level app `version` again, for example `1.0.1` to `1.0.2`. Use a value higher than your last provisioned version. Edit `appPackage/manifest.json`, not `manifest.dev.json`.
7. Save all files and run Toolkit **Provision** for **dev**. Wait for provisioning to complete successfully.
8. Reload `https://m365.cloud.microsoft/chat`, select the same **Zava Currency Converter** and start a fresh conversation. Send `-developer on`.
9. Ask: `Use get_rates to get the latest USD to CAD reference rate and its effective date.` If Copilot asks to connect to **Frankfurter MCP**, select **Allow**.
10. Expand **Agent debug info**. Check that `get_rates` is selected, then inspect the returned rate and date. The old `getExchangeRate` REST action should no longer be available.
11. Ask: `Use get_rates to get the USD to CAD reference rate for January 2, 2024.` Check the returned effective date.
12. Ask: `Use convert to convert an example amount of 100 USD to CAD. Set details to true and include the rate and effective date.` Check the tool result for `amount`, `currency`, `rate` and `date`.
13. Repeat `Get the USD to ZZZ exchange rate` and `Transfer 100 USD into CAD for me`. The agent must not invent a rate or claim to transfer money.

**Checkpoint:** The same agent now uses MCP tools for rates and conversions. The original REST plugin and card files remain in the project, but are no longer referenced by the active action. This MCP activity does not include a custom Adaptive Card; the earlier REST card is not expected to appear.

## Troubleshooting

- **MCP switch still calls REST:** check that the only active action references `currency-plugin.mcp.json`, the MCP instructions were copied, and the higher app version was provisioned. Reload Copilot and start a fresh conversation.
- **No card after the MCP switch:** expected in section 7; its plugin does not define a custom card.
- **403 or network failure:** check the same public URL in the VM browser and show the instructor the exact result. Do not bypass a block.
- **429:** wait before retrying. Do not repeatedly submit prompts.
- **API key requested:** the supplied runtime must use `auth.type: None`; Frankfurter's public service does not need a key.
- **Missing operation or spec:** check `actions.file`, `spec.url` and exact `getExchangeRate` spelling.
- **Card missing:** confirm you copied the with-card checkpoint, `data_path` is `$`, provisioning succeeded, and you opened the citation in a fresh chat. Ask the instructor if the card is still absent.
- **Older effective date:** this is a reference-rate service, not a live-market feed. Report the returned date.
- **Service unavailable:** use `sample-rate.json` only for offline template inspection. This does not confirm that the live API works.

## Sources and scope

These instructions are original course material. The creation/testing route follows [Microsoft’s Toolkit tutorial](https://learn.microsoft.com/plugins/build-declarative-agents). Runtime behavior follows [Frankfurter v2](https://frankfurter.dev/), the [Microsoft plugin manifest](https://learn.microsoft.com/microsoft-365/copilot/extensibility/plugin-manifest-2.4) and [Microsoft Adaptive Card response templates](https://learn.microsoft.com/plugins/api-plugin-adaptive-cards). The MCP activity uses the [Frankfurter MCP server](https://frankfurter.dev/mcp/) and Microsoft’s [MCP plugin guidance](https://learn.microsoft.com/plugins/build-mcp-plugins). All required learner files are supplied locally; these links are references, not extra exercises.

## Prepare for Lab 3

Start the connector setup now so its dependencies can install while you read Lab 3.

1. In the **left course window**, open the Terminal and run:

```powershell
Set-Location C:\Users\Admin\ma-2041
.\scripts\Prepare-Node.ps1
```

If the Core Tools installer opens, complete its license and administrator prompts. The script reuses existing Node runtimes and working Core Tools v4.

2. In **Extensions**, install **Azure Functions** published by **Microsoft**.
3. If Core Tools was newly installed, save your work, close **all VS Code windows**, and reopen VS Code from Start. **Reload Window is not enough.** Reopen the course repository on the left and `CurrencyAssistant` on the right.
4. In a new terminal in the **left course window**, run:

```powershell
. C:\Users\Admin\ma-2041\scripts\Use-Node.ps1 -Version 22
Set-Location C:\Users\Admin\ma-2041\Day1\Lab3-CopilotConnector\connector
npm.cmd ci --ignore-scripts --no-audit --no-fund
```

Leave that terminal running while you read Lab 3. Wait for installation to finish successfully before starting the connector. Do not run a second installation in the right window. Selecting Node applies only to that terminal; run `Use-Node.ps1 -Version 22` again in any new terminal where you need npm.

When you are ready to go on to Lab 3, [click here](D1_Lab3.md).
