# D2_Lab3 — Let the model request a validated draft function



## Learning outcome

Change a business threshold and input bound coherently across implementation, policy and tests; then observe the real Azure model choose the function and receive its validated draft result. Pair with Go Deploy **2. Use a custom function in an AI agent**. Continue the existing allocation when approved; otherwise move the same sanitized source project to the new VM and repeat preflight outside the timer. Do not start the provider's separate astronomy-assistant application.

**Diagram in prose:** Toolkit starts the same SDK app → retrieved policy and strict tool schema accompany the Azure request → the model may emit `function_call` → application `executeTool` validates name/JSON/fields and computes routing → `function_call_output` carries the matching call ID back to Azure → a cited answer returns through SDK. The model chooses a request; deterministic code decides the result. This function never creates a ticket or changes an account. `humanApprovalRequired` is a returned flag, not an implemented approval workflow.

## Prerequisite prior state

Keep D2_Lab1 welcome/instructions and D2_Lab2 P1 phishing changes. Both checkpoints, build and default tests should be GREEN. Use Node.js **22**, the same VS Code `Code` workspace, real approved Responses/tool-capable deployment, and Azure CLI identity in the **same OS as Node**. If a new VM requires configuration, follow D2_Lab1's creation of `env/.env.playground` and `.localConfigs.playground`, and run approved `az login` there; do not copy CLI caches or secrets.

In **Terminal > New Terminal > PowerShell**:

```powershell
Set-Location 'C:\ma-2041\Day2'
node --version
npm run preflight
npx tsx --test checkpoints/lab1.test.ts checkpoints/lab2.test.ts
npm test
```

## Keep a short lab record

Use your own notes file in the working copy. Record the lab name, changed files, commands, observed outputs/exit codes, positive and negative checks, restored state, and any blocker. Save only fictional data and sanitized screenshots. Never include tokens, keys, passwords, login caches or runtime configuration files. Expected output in this handout is a target to compare against, not proof that your run succeeded.

## Planned core — 45 minutes after setup

| Stage | Minutes | Observable checkpoint |
|---|---:|---|
| Trace contract and capture RED | 5 | Identify model/server/schema responsibilities |
| Edit threshold, both bounds, policy and test | 12 | Coherent change, checkpoint/default tests GREEN |
| Exercise deterministic positive/negative cases | 8 | Boundary and denial evidence |
| Observe live model-selected function | 13 | Call arguments, draft result and final reply |
| Save evidence and explain limits | 7 | No ticket/approval execution claimed |

## 1. Understand the contract — 5 minutes

Open `src/tool.ts`, `src/policy.ts`, `tests/core.test.ts` and `checkpoints/lab3.test.ts` side by side. The reference uses a multi-user threshold of 10 and summary limit of 240. Our change request is **12 users** and **160 characters**. The department-outage P1 boundary stays 25; Security/data risk still overrides all other routing.

```powershell
npx tsx --test checkpoints/lab3.test.ts
```

Expected RED before edits. Do not weaken this checkpoint. Predict why changing only the policy sentence would not change function results.

## 2. Implement one consistent business change — 12 minutes

In `src/tool.ts`, replace the threshold declaration with:

```typescript
export const MULTI_USER_THRESHOLD = 12;
```

On the server validation schema change only the summary maximum, yielding:

```typescript
summary:z.string().trim().min(4).max(160)
```

In `supportTool.parameters.properties.summary`, change `maxLength:240` to `maxLength:160`. Both the advertised JSON schema and the enforced Zod bound must agree. Preserve `strict:true`, `additionalProperties:false`, `.strict()`, required fields and draft-only return behavior.

In **P3** in `src/policy.ts`, replace `at least 10 affected users` with `at least 12 affected users`. Preserve D2_Lab2's P1 changes. In `tests/core.test.ts`, find the test named **meaningful support routing returns draft only**. Change only its positive P2 boundary input from `affectedUsers:10` to `affectedUsers:12`; keep the expected priority `'P2'`. Do not mass-replace all tens: the checkpoint's 10-user input is deliberately a negative boundary now.

Save all three files:

```powershell
npx tsx --test checkpoints/lab3.test.ts
npm test
npm run build
npx tsx --test checkpoints/lab1.test.ts checkpoints/lab2.test.ts
```

Expected all GREEN. If `npm test` still expects P2 for 10 users, the test has not been reconciled with the new rule; changing its expected answer to P3 alone would lose the existing positive boundary test. The opt-in checkpoint already covers both 10 and 12.

## 3. Positive and negative validator proof — 8 minutes

At the Code root, create a file named `lab3-probe.ts` in VS Code (**File > New Text File**, then **Save As**). Paste the following code and save. This calls the edited function directly; it does not call Azure or create a ticket.

```typescript
import {executeTool} from './src/tool';
const base = {
  category:'access', impact:'department', affectedUsers:10,
  dataRisk:false, summary:'Access unavailable'
};
const run = (x:any) =>
  executeTool('assess_support_request', JSON.stringify(x));
for (const n of [10,12]) {
  console.log(n, run({...base, affectedUsers:n}));
}
console.log('security', run({...base, dataRisk:true}));
console.log('major', run({...base, category:'outage', affectedUsers:30}));
const bad = [
  ['delete_ticket', '{}'],
  ['assess_support_request', '{bad'],
  ['assess_support_request', '{}'],
  ['assess_support_request', JSON.stringify({...base, approve:true})],
  ['assess_support_request',
    JSON.stringify({...base, summary:'x'.repeat(161)})]
];
for (const [name, raw] of bad) {
  let denied = false;
  try { executeTool(name, raw); }
  catch (e) { denied = (e as Error).message === 'Tool denied'; }
  if (!denied) throw Error('Negative case did not deny');
  console.log('DENIED', name);
}
```

Run it from PowerShell at the Code root:

```powershell
npx tsx lab3-probe.ts
```

Expected: 10 users P3; 12 users P2; data risk Security/P1; department outage 30 Incident Management/P1. Each positive result has `status: 'DRAFT_ONLY'` and `humanApprovalRequired: true`. Five negative cases print `DENIED`: unknown function, malformed JSON, missing fields, extra `approve`, and summary length 161. A 160-character summary remains allowed; trimming happens on server validation. This proof is separate from model behavior.

## 4. Observe the model choose the function — 13 minutes

Open `src/core.ts`. Set a breakpoint on the line `if(calls.length)` and on the `executeTool(...)` line. Choose **Run and Debug > Debug in Microsoft 365 Agents Playground**, press **F5**, and start a new conversation. Send:

```text
Assess a draft support request: category outage, impact department, affectedUsers 30, dataRisk false, summary Department service unavailable.
```

At `if(calls.length)`, inspect `calls`. Required evidence is an actual model-produced `function_call` named `assess_support_request`, with its arguments and call ID. The tool is configured with `tool_choice:'auto'`; the application is not forcing a choice. If `calls` is empty, record **live function selection not demonstrated**, even if the prose answer sounds correct.

At the function line inspect `call.name` and `call.arguments`. To inspect `result` on this compact single line, use **F11 (Step Into)** to enter `executeTool`, then **Shift+F11 (Step Out)**; if VS Code steps beyond the local scope, inspect the appended `function_call_output` in `input` on the next iteration instead. Do not manually invoke `executeTool` in Debug Console and label that a model invocation. The output must carry the original `call_id`.

Expected actual result: `DRAFT_ONLY`, `P1`, `Incident Management`, `humanApprovalRequired:true`, and no-created-ticket action text. Continue promptly through the subsequent Azure call and capture the final cited response. Pauses must be short; live requests/Playground delivery can time out. This app allows at most three model rounds and rejects tool loops; do not disable limits for the demo.

Start a new conversation and send this incomplete request:

```text
Assess a draft support request for an outage.
```

Expected safe behavior: ask for missing impact/user count/data-risk/summary information, not invent it. Inspect whether a call was attempted. A clarification is not validator proof; the deterministic negative checks above are. If the model invents valid-looking facts, report a behavioral failure: schema validation cannot prove facts came from the user.

## 5. Acceptance evidence — 7 minutes

Record edited files and exact values; checkpoint RED/GREEN; default tests; the 10/12 boundary outputs; five denials; actual model call/name/arguments/call ID; validated result; final cited reply; missing-information behavior. Keep synthetic data only in sanitized lab notes.

**GO:** coherent edits, deterministic checks and an observed real Azure function call followed by the validated result and answer. **BLOCKED live acceptance:** fixture pass, hand-called function, plain prose response without function selection, or unavailable Azure. Preserve the distinction even if `npm run verify:azure` prints success: its output explicitly says that log alone does not prove the model selected a function.

## Troubleshooting and recovery

- Test contradiction: reconcile threshold 12, P3 text 12, default positive input 12, Zod max 160 and model maxLength 160 together. Keep checkpoint input 10.
- Syntax failure: check commas/quotes around only the edited properties; do not replace the whole file or lose prior edits.
- Tool not selected: confirm all required facts were sent, model supports strict functions, rebuild/restart, then retry once in a new conversation. Record both results; do not force `tool_choice` to falsify the exercise.
- `Tool denied`: inspect sanitized name and argument shape. Required types include integer users and boolean dataRisk, not string approximations. Never loosen validation to admit an unsafe call.
- Timeout: continue/stop owned debugger and restart; retry with brief pauses. Keep the timeout result.
- Reset Lab 3 as a unit: restore `src/tool.ts` and `tests/core.test.ts` to reference values (10/240/input 10), and restore P3's threshold text to 10 while retaining P1 phishing. Reapply the full change set. No cloud rollback exists because no write occurred.


## Completion checklist

- [ ] Threshold 12 and both 160-character bounds agree with P3 and the positive test input.
- [ ] The 10/12 boundaries and all five denials behave as expected.
- [ ] A real model-generated function call has matching call ID, validated draft result and final cited reply.
- [ ] Missing-information behavior is observed; no ticket creation or approval workflow is claimed.

Stop your own local servers and debug tasks when finished. Keep your edited source for the next lab. Follow provider save/expiry instructions; do not delete shared resources.
