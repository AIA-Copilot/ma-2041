# Day 1 · Lab 3 — Show API results with Adaptive Cards

**Workspace:** use VS Code and PowerShell 7 inside the provided MS-4018 VM. “Local” means this VM. One-time preparation: [course setup](../README.md).


**Outcome:** build and inspect dish/order card templates, bind them to API response semantics, and verify a dish card in a Copilot citation plus an order card in the response itself.

**Allow:** 50 minutes of practice after Lab 2 and provider preflight (planning budget, not measured completion). Use the same approved anonymous restaurant tunnel and Microsoft 365 account gates.

**Start gate:** the instructor must confirm [provider preflight](INSTRUCTOR-PREFLIGHT.md) before runtime work. If tools or approval are missing, stop; do not install or bypass policy during this lab.

**Official exercise:** [Return rich responses with Adaptive Cards](https://learn.microsoft.com/en-us/training/modules/copilot-declarative-agent-action-api-plugin-adaptive-cards-vsc/3-exercise-return-rich-responses-adaptive-cards). This is the official Cards starter, not a different API or scenario. The complete exercise card files and preview data are supplied under `cards`.

## 1. Switch projects cleanly (3 minutes)

1. Stop Lab 2 debugging and terminate its tunnel/host tasks. Do not run both projects on the same ports.
2. Open and check the prepared Lab 3 project:

```powershell
Set-Location C:\ma-2041\Day1\Lab3-AdaptiveCards
code .
npm.cmd run build
npm.cmd test
npm.cmd run check:func
```

**Expected result:** build and tests succeed. Confirm `appPackage/ai-plugin.json` already contains `getDishes` and `placeOrder`, and `declarativeAgent.json` already references the plugin. The same corrected API contract applies: `GET /dishes` returns `{ "dishes": [...] }`, `POST /orders` is plural, quantities are integers 1–100 inclusive, and multiple excluded allergens use a single comma-separated query value. This is where Lab 2 ended, before cards. The initial plugin deliberately has no `static_template`; you add that now.

Verify **Adaptive Card Previewer** is available; ask the instructor if it is missing. This is a design preview tool, not the Copilot runtime. You still need the live Copilot checks at the end.

**Checkpoint:** Only the Lab 3 project is active; baseline plugin has no cards.

## 2. Inspect and preview the dish card (10 minutes)

1. Open `cards/dish.json` and `cards/dish.data.json` side by side. The data is the official exercise's Caprese Salad sample. The card has `type: AdaptiveCard` and version `1.5`.

2. Use the **Preview Adaptive Card** CodeLens or Command Palette command with `dish.json` active. If the extension asks for a data file, choose the supplied `dish.data.json`. The official flow can also create a file with **Adaptive Card: New Data File**; do not overwrite the prepared data accidentally.

3. Trace these bindings:

| Template expression | Data meaning | What you should see |
|---|---|---|
| `${image_url}` | Dish image URL | Image, if the VM can reach the remote sample asset |
| `${name}` | Dish name | Caprese Salad |
| `${description}` | Dish description | Wrapped descriptive text |
| `${if(count(allergens) > 0, join(allergens, ', '), 'none')}` | List formatting and empty-list behavior | `dairy` for the supplied sample |
| `${formatNumber(price, 2)}` | Two decimal places | Price rendered with two decimals |

The wrapper is a Container, with Image/TextBlock elements inside. `wrap: true` prevents the description being forced onto one line. The preview data is deliberately a **single dish**, not the entire `{dishes:[...]}` API envelope; the plugin's `data_path` selects each dish at runtime.

4. **Make and verify an edit:** change the fixture's `allergens` array to `[]` and save. The preview should show `none`. Restore `["dairy"]` before continuing. This is a formatting test, not an API change. Change the title's weight or spacing, inspect the result, then keep a readable version.

If a binding appears literally as `${name}`, verify that preview data is selected and valid JSON. If only the image is missing, test the image URL in the VM browser; do not diagnose every remote-image failure as a broken card schema. Text/data binding must still be correct.

**Checkpoint:** Record empty-allergen rendering and restore the supplied fixture.

## 3. Inspect and preview the order card (7 minutes)

1. Open `cards/order.json` with `cards/order.data.json`. The fixture contains a fictional order ID, `confirmed` status and total. Use Preview Adaptive Card again.

The FactSet maps these values:

```json
{
  "title": "Order ID:",
  "value": "${order_id} "
}
```

The trailing space after `${order_id}` is intentional in the Learn exercise: it works around number rendering behavior in the preview. Remove the space temporarily and observe whether your current preview reproduces the issue; restore it regardless so the supplied exercise checkpoint remains consistent. Do not silently change the fixture's number into a fabricated live order result.

2. Verify all three facts—ID, status and formatted total—are visible. The fixture's ID and total are preview inputs only; actual Copilot output will use the API's runtime response.

3. **Deliberate broken-binding repair (3 minutes):** in the dish card change `${name}` to `${dish_name}` while leaving the fixture unchanged. Preview the missing title, explain the mismatch, then restore `${name}` and verify the title returns. Do not ship the broken card. This takes the total practice budget to 50 minutes.

**Checkpoint:** both cards preview with resolved text, and long descriptions remain readable. A screenshot of this preview is design evidence only.

## 4. Embed both cards in the API plugin (7 minutes)

1. Open `appPackage/ai-plugin.json`. Find the function object whose `name` is `getDishes`, then its `capabilities.response_semantics`:

```json
{
  "data_path": "$.dishes",
  "properties": {
    "title": "$.name",
    "subtitle": "$.description"
  }
}
```

2. Add a `static_template` property at this same level and make its value the full **object** from `cards/dish.json`, not a filename or quoted JSON string. For `placeOrder`, add the full `cards/order.json` object under that function's response semantics. Keep its `data_path` as `$` because the response is one order object.

For a reproducible edit without brace/copy errors, the supplied utility performs those exact two insertions using your current card files:

```powershell
node scripts/apply-cards.mjs
```

3. Open the resulting plugin and locate both `static_template` objects. Confirm function names, `run_for_functions`, runtime spec path and `auth: None` remain unchanged. The standalone `cards` files are authoring inputs; the **embedded** copies in the plugin are what Copilot receives. If you change a card later, rerun the utility to update those copies before F5.

If your plugin editing fails, `checkpoints/ai-plugin.cards.json` is the complete official-card checkpoint. Copy it only as a deliberate recovery; it overwrites your custom card edits:

```powershell
Copy-Item checkpoints/ai-plugin.cards.json appPackage/ai-plugin.json
```

**Checkpoint:** Both templates are embedded under the correct response semantics.

## 5. Verify the actual Copilot rendering (15 minutes)

1. Recheck the work account in Toolkit. Confirm the instructor's tunnel permission still applies.
2. Select **Run and Debug > Debug in Copilot (Edge)** and press F5. Do not use Preview-only. Wait for the tunnel, local lifecycle, host and browser.
3. Open **Il Ristorante - Lab 3 Cards** in Copilot using the same assigned account (the installed app is named **Il Ristorante Cards**, with the local suffix). This project's distinct name separates it from Lab 2's **Il Ristorante**. F5 opens generic Copilot chat, not an app-specific link: explicitly select the Lab 3 agent before starting a new conversation. If that name is absent or duplicated, stop and have the instructor match the installed app to this project's `TEAMS_APP_ID` in `env/.env.local`; do not guess from the browser tab or conversation age.
4. Start a fresh chat and send:

```text
What's for lunch today?
```

5. Inspect the proposed API request and choose **Allow once** only for the expected read. In the response, open/hover a dish citation. **Expected result:** the citation popup contains your custom dish card with information beyond the title, such as description, allergens and formatted price. Multiple dishes need not appear as a wall of inline cards; the official exercise expects the rich card in the citation popup.
6. Send the official order prompt:

```text
1x spaghetti, 1x iced tea
```

7. Inspect the exact order payload and confirm only the intended fictitious order. **Expected result:** the single order result appears as an inline Adaptive Card with order ID, status and total. Compare its values with the API response/Functions activity. Do not compare the live random ID to `order.data.json`.

**Negative/diagnostic checks:** if the menu answer is fluent but the citation still has only a title, the old/no-card plugin may be installed. Verify the embedded templates in the generated package, stop/restart F5 and use a fresh chat. If a card shows blank facts, compare `data_path` and expression names against the actual API envelope. A local preview cannot detect using `$.dishes` for the order response.

**Checkpoint:** Verify a dish citation card and an inline order card in the selected Lab 3 agent.

## 6. Save evidence and stop tasks (5 minutes)

1. Record a redacted dish citation card and an inline order card from **Copilot**, plus the two preview observations. Note any discrepancy between preview and Copilot. Passing requires the live cards, not simply valid JSON or screenshots supplied with the upstream repository.

2. Stop debugging and terminate all task terminals, including the public tunnel. Confirm no lab process is listening on 7071/9229. Keep the source for class review; do not upload logs or environment files containing secrets.

| Symptom | Recovery |
|---|---|
| Preview command missing | Confirm `.json` card is active; ask the instructor to restore the prepared Previewer extension. |
| Preview shows literal expressions | Select matching data file and inspect syntax/property names. |
| Copilot still has plain responses | Run `apply-cards.mjs` after edits, save, rerun local F5 provisioning, and open the correct agent in a new chat. |
| Menu card works, order card blank | `getDishes` uses `$.dishes`; `placeOrder` uses `$`. Preserve the order-ID trailing space. |
| Host/tunnel fails | Use Lab 2's port, network, account and generated-server checks; do not change working card bindings to fix a network issue. |

**Additional practice:** [Challenge project — chat with your data](https://learn.microsoft.com/en-us/training/modules/copilot-declarative-agent-challenge-chat-with-data/). It follows the API and cards modules and is separate practice, not another mandatory guided block.

**Checkpoint:** Record preview versus Copilot results and confirm tasks/tunnel stopped.

## Session 3 authentication teaching boundary
The instructor separately demonstrates an authenticated request/configuration or explicitly labelled worked walkthrough (15 minutes, outside this 50-minute lab). Trace identity, credential location, token/audience or API-key header, denied request, and least privilege. Do not paste secrets into cards/manifests. This lab keeps anonymous synthetic API actions; learner implementation of OAuth/API-key authentication remains an explicit syllabus gap, not a completed outcome.
