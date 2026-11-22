# Day 1 · Lab 2 — Currency API actions and Adaptive Cards

## Outcome

Build a Currency Assistant that calls a public API for current and historical exchange rates. Test its answers in Microsoft 365 Copilot, add an Adaptive Card to display the rate and effective date, and verify that the agent handles unsupported currencies and cannot transfer money.

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

**Checkpoint:** Valid requests return a rate object. Invalid `ZZZ` returns HTTP 422. If a valid request returns 403, a challenge page, or a network error, stop and show the instructor. Do not bypass network controls. A saved response can support card practice, but is not proof of a live API call.

## 2. Create a separate Currency Assistant

Keep your section 1 agent unchanged. A separate agent avoids its onboarding instructions restricting the new currency task.

1. Open **Microsoft 365 Agents Toolkit** in VS Code.
2. Choose **Create a New Agent/App** (the wording can vary by Toolkit version).
3. Choose **Declarative Agent**, then **No Action**.
4. Select `C:\ma-2041\work` as the parent folder. Create that folder in the picker if needed.
5. Name the project **CurrencyAssistant**. Open the generated project in VS Code.
6. In Toolkit **Accounts**, confirm your assigned Microsoft 365 account and tenant.
7. Open `appPackage/declarativeAgent.json`. Change its display `name` to `Currency Assistant` and its `description` to `Look up currency reference rates and their effective dates.` Preserve the generated schema version and other fields.

The rest of this guide assumes the project is `C:\ma-2041\work\CurrencyAssistant`. If your picker created another location, use that actual path in the next command.

**Checkpoint:** The project contains `appPackage/declarativeAgent.json`, `appPackage/manifest.json` and `m365agents.yml`. If your template proposes Azure hosting or starts a tunnel, you selected the wrong project type. Stop and return to the declarative-agent **No Action** template.

## 3. Add the supplied OpenAPI contract and plugin

You will wire the supplied files directly so each connection is visible. Do not generate an OpenAPI file in Postman, and do not use the Add Action wizard as well as these steps.

1. Open a terminal in the generated project.
2. Paste and run these commands to copy the prepared files:

```powershell
Set-Location 'C:\ma-2041\work\CurrencyAssistant'
$assets = 'C:\ma-2041\Day1\Section2-Currency'
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
5. In `appPackage/declarativeAgent.json`, set the `instructions` property to:

```json
"instructions": "$[file('instruction.txt')]"
```

6. Add this top-level `actions` property inside the same JSON object. Add a comma after the preceding property. If an empty `actions` property already exists, replace it rather than adding a duplicate.

```json
"actions": [
  {
    "id": "currencyAction",
    "file": "currency-plugin.json"
  }
]
```

7. Replace the template's example conversation starters with these, using the existing `conversation_starters` property or adding it once:

```json
"conversation_starters": [
  { "title": "Latest rate", "text": "Get the latest available USD to CAD reference rate and its effective date." },
  { "title": "Historical rate", "text": "Get the USD to CAD reference rate for January 2, 2024." }
]
```

8. In `appPackage/manifest.json`, add `api.frankfurter.dev` to `validDomains`. Preserve any existing entries. If the array is empty, the result is:

```json
"validDomains": ["api.frankfurter.dev"]
```

9. Save all files. Fix any JSON syntax errors shown by VS Code before continuing.

**Checkpoint:** Explain the chain: declarative agent → plugin → OpenAPI operation → public HTTPS service. The VM has not become an API server. The sample has no create/update/delete operation.

## 4. Provision and test the action without a custom card

1. Open `env/.env.dev` if generated by the template. Use this same **dev** environment throughout the exercise. Preserve the template's identity and scope settings; do not copy IDs from another agent.
2. In Toolkit, select **Provision** for the dev environment. Follow sign-in prompts for the assigned training account. This registers/packages the agent in Microsoft 365, not in Azure.
3. If validation reports a missing file or invalid JSON, correct that file and retry. If tenant policy refuses upload or requires admin approval, ask the instructor. Do not change deployment scope to bypass the refusal.
4. Open `https://m365.cloud.microsoft/chat` in the VM browser. Sign in with the same training account. Open the agent list/conversation drawer and select the newly provisioned agent, following Microsoft's Toolkit test route.
5. Start a new conversation with **Currency Assistant**. The picker may instead show the generated application name **CurrencyAssistant** with a dev suffix. Do not use ordinary Copilot or your section 1 agent.
6. Enter:

```text
Get the latest available USD to CAD reference rate and its effective date. Use the currency action.
```

7. If permission is requested, inspect the currency pair, endpoint and read operation. Allow only the expected request.
8. Check the result against a fresh API request from step 1. Look for the action/source indication. A plausible answer without evidence of the action is not a pass.
9. Enter the historical prompt from the starter. Verify both the requested historical date and the returned effective date.

**Checkpoint:** The agent actually invokes the currency action and reports the returned rate and date. If invocation details are unavailable in this UI, matching text alone does not confirm that the action ran. The custom card has not been added yet.

## 5. Add the Adaptive Card

1. Open the supplied `C:\ma-2041\Day1\Section2-Currency\currency-card.json`.
2. Find the expressions `${base}`, `${quote}`, `${rate}` and `${date}`. They bind to fields in the API response.
3. Open `currency-plugin.with-card.json` in the same supplied folder. Find `functions[0].capabilities.response_semantics`.
4. Notice that `data_path` is `$` because the rate response is one object at the root. The `static_template` contains the complete card. It is intentionally embedded, not a separate deployed file reference.
5. In the project terminal, paste and run these commands to replace the no-card plugin:

```powershell
$assets = 'C:\ma-2041\Day1\Section2-Currency'
Copy-Item "$assets\currency-plugin.with-card.json" '.\appPackage\currency-plugin.json'
```

6. Save all files. Run Toolkit **Provision** again for the same dev environment. Reload `https://m365.cloud.microsoft/chat`, select your agent, and start a fresh conversation.
7. Ask for the USD-to-CAD rate again.
8. Open the action result's source/citation. Microsoft 365 can display this card within the citation rather than directly in the main answer.
9. Verify the card shows the currency pair, rate, effective date and reference-rate disclaimer. Narrow the Copilot pane and check that the text still fits.

**Checkpoint:** The real API response populates the custom card. A screenshot of a locally rendered sample is useful for layout checking but does not satisfy this Copilot checkpoint.

**Small change:** In the project's `currency-plugin.json`, change the card heading from `Currency reference rate` to `Travel exchange rate`. Save, reprovision dev and check the updated citation in a new chat. Editing only the supplied standalone `currency-card.json` does not update the embedded card. If the old heading persists, allow time for the update to appear, reload Copilot, and retry.

## 6. Check boundaries

1. Ask: `Get the USD to ZZZ exchange rate.` The agent must report an unsupported code or a failed request, not invent a rate. It may ask you to correct the code instead of calling the API; the direct HTTP test in step 1 separately checks service error handling.
2. Ask: `Transfer 100 USD into CAD for me.` The agent must explain that it cannot transfer money. There is no payment operation in the contract.
3. Optional: ask `Estimate how many CAD 100 USD would buy at that reference rate, excluding fees.` Check the multiplication yourself:

```powershell
$rate = Invoke-RestMethod 'https://api.frankfurter.dev/v2/rate/USD/CAD'
[math]::Round(100 * $rate.rate, 2)
```

The amount is multiplied locally. The API returns a rate, not a converted amount. A bank's rate and fees may differ. The card continues to display the reference rate, not this optional calculation.

## Troubleshooting

- **403 or network failure:** check the same public URL in the VM browser and show the instructor the exact result. Do not bypass a block.
- **429:** wait before retrying. Do not repeatedly submit prompts.
- **API key requested:** the supplied runtime must use `auth.type: None`; Frankfurter's public service does not need a key.
- **Missing operation or spec:** check `actions.file`, `spec.url` and exact `getExchangeRate` spelling.
- **Card missing:** confirm you copied the with-card checkpoint, `data_path` is `$`, provisioning succeeded, and you opened the citation in a fresh chat. Ask the instructor if the card is still absent.
- **Old heading:** edit the embedded template in the project's plugin, then reprovision. The standalone source card is not loaded at runtime. Allow time for the update to appear and reload Copilot before retesting.
- **Older effective date:** this is a reference-rate service, not a live-market feed. Report the returned date.
- **Service unavailable:** use `sample-rate.json` only for offline template inspection. This does not confirm that the live API works.

## Sources and scope

These instructions are original course material. The creation/testing route follows [Microsoft’s Toolkit tutorial](https://learn.microsoft.com/plugins/build-declarative-agents). Runtime behavior follows [Frankfurter v2](https://frankfurter.dev/), the [Microsoft plugin manifest](https://learn.microsoft.com/microsoft-365/copilot/extensibility/plugin-manifest-2.4) and [Microsoft Adaptive Card response templates](https://learn.microsoft.com/plugins/api-plugin-adaptive-cards). All required learner files are supplied locally; these links are references, not extra exercises.
