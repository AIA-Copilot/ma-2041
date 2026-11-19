# D2_Lab2 — Ground the same agent in a new policy passage



## Learning outcome

Extend the fictional security policy to cover phishing, prove retrieval happens before the Azure request, and distinguish a supported answer from a no-result path. Continue Go Deploy **1. Build AI agents with portal and VS Code**; use the same launch if provider rules permit. This adapts exercise 01's grounding concept, not its hosted File Search implementation. No new Azure AI Search service is required.

**Diagram in prose:** Playground message → SDK activity handler → `retrieve(text)` tokenizes and scores local passages → at most two selected passages become model instructions/data → real Azure Responses call → application checks bracketed citation IDs → SDK reply. Toolkit owns local lifecycle; `src/policy.ts` owns bounded lexical selection; Azure generates wording. None of these steps supplies SharePoint permissions, vector search or tenant ACL trimming.

## Prerequisite prior state

D2_Lab1 code changes retained, Lab 1 checkpoint GREEN, default tests/build GREEN, approved Azure model reply observed, and the same-OS CLI identity still valid. Use Node.js **22** in the VM. If changing launches, carry only sanitized source and notes; repeat setup, `az login` in the Node runtime's OS, and the two nonsecret configuration files from D2_Lab1. Never carry tokens or login caches. Setup and resource switching are outside the timer.

In VS Code **File > Open Folder**, reopen the continuing `C:\ma-2041\Day2` folder. **Terminal > New Terminal > PowerShell**:

```powershell
Set-Location 'C:\ma-2041\Day2'
node --version
npm run preflight
npx tsx --test checkpoints/lab1.test.ts
npm test
```

STOP if configuration or prior edits are missing. Local work can continue under CONDITIONAL GO if Azure is blocked, but this does not complete the live lab.

## Keep a short lab record

Use your own notes file in the working copy. Record the lab name, changed files, commands, observed outputs/exit codes, positive and negative checks, restored state, and any blocker. Save only fictional data and sanitized screenshots. Never include tokens, keys, passwords, login caches or runtime configuration files. Expected output in this handout is a target to compare against, not proof that your run succeeded.

## Planned core — 42 minutes after setup

| Stage | Minutes | Observable checkpoint |
|---|---:|---|
| Predict retrieval and capture RED | 6 | Explain why phishing currently misses |
| Edit the bounded policy | 9 | One passage changed; checkpoint GREEN |
| Inspect selected context | 9 | P1 present before model request |
| Compare live positive/negative behavior | 11 | Cited phishing answer; no-result diagnostic |
| Record evidence and limitations | 7 | Retrieval and model claims separated |

## 1. Predict and capture the gap — 6 minutes

Open `src/policy.ts`. Find P1, **Lost device and security**. The reference has device/security keywords but not `phishing`. Token matching is exact lowercase alphanumeric matching, not semantic synonym search. `MAX_PASSAGES` remains **2**; do not change it despite its generic edit-point comment. The exact checkpoint contract calls for a keyword/text change.

Run:

```powershell
npx tsx --test checkpoints/lab2.test.ts
```

Expected RED before the change. Read its assertion: a query consisting of `phishing` should select P1; unrelated text must still return no passages. Do not modify the checkpoint to make it pass.

## 2. Add one bounded policy fact — 9 minutes

In the **P1 entry only**, add `'phishing'` to `keywords`. Append this sentence to its existing `text` string, before the closing quote:

```text
 Report suspected phishing to Security; do not open links or share verification codes.
```

Keep the existing lost-device and draft-only wording. Do not add the keyword to every passage or alter the other IDs. Save, then run:

```powershell
npx tsx --test checkpoints/lab2.test.ts
npx tsx --test checkpoints/lab1.test.ts
npm run build
npm test
```

Expected GREEN. The checkpoint verifies retrieval, not the newly written sentence's meaning; inspect the saved P1 text yourself. This distinction prevents a keyword-only edit being mistaken for grounded content.

## 3. Inspect the selected context — 9 minutes

In `src/core.ts`, set a breakpoint on the line starting `const instructions=INSTRUCTIONS`. Choose **Run and Debug > Debug in Microsoft 365 Agents Playground**, press **F5**, and start a new conversation. Send:

```text
Explain phishing policy
```

At the breakpoint inspect `selected` in **Variables > Local**, or evaluate `selected` in the **Debug Console**. It should contain P1 with the new sentence. Inspect `text` to confirm the incoming question. Step over the instructions assignment once with **F10** and inspect `instructions`: it includes the retained safety rules and `[P1]` text. This is the actual context sent to the model, not every passage in the file.

Press **Continue (F5)** quickly. Keep debugger pauses short: live requests and Playground delivery can time out. If a timeout occurs, preserve that outcome, restart your owned app and retry a fresh conversation; a timeout is not proof of model refusal.

## 4. Test supported and unsupported questions — 11 minutes

Observe the real Azure answer to the phishing question. Expected content: report to Security, avoid opening links/sharing verification codes, cite `[P1]`, no claim of tenant access or automatic containment. Exact wording is nondeterministic. Read the cited source and compare meaning; the code only validates that a citation ID belongs to the selected set. It does not prove semantic entailment.

Remove/disable the instructions breakpoint and put one on `this.transport.create(...)`. Send:

```text
banana astrophysics
```

Expected exact diagnostic:

```text
I found no relevant policy passage. Ask about access, lost devices, service outages or equipment purchases. No model answer was generated.
```

The model breakpoint must not be reached for this request. That is a negative retrieval outcome by design, not a fabricated Azure answer. Then send:

```text
Explain equipment purchase reimbursement policy
```

Expected selected source P4, a real Azure answer citing `[P4]`, and referral to Procurement without invented limits or spending approval. Continue promptly if the model breakpoint pauses. This checks that your new security keyword did not swallow other topics.

## 5. Acceptance evidence and debrief — 7 minutes

Record in your lab notes: changed `src/policy.ts`; before/after checkpoint result; selected ID and new sentence; actual phishing reply/citation; P4 regression result; no-result diagnostic and absence of a transport breakpoint hit; remaining blockers. Keep only sanitized screenshots or text. Do not log runtime configuration files or authentication data.

**Acceptance:** P1 is retrieved before a real Azure response; the response uses the supplied fact with an allowed citation; unsupported text does not call the model; Lab 1 remains intact. A unit-test pass without a live cited reply is **BLOCKED live acceptance**, not completed grounding.

Explain to a partner: “Our application selects up to two lexical passages. The model writes an answer. Citation IDs are checked, but content truth and prompt-injection resistance are not proven.” A prior conversation may carry bounded history; new conversations reduce that confound during these comparisons.

## Troubleshooting and recovery

- Still RED: check spelling and array punctuation; the keyword must be exactly `'phishing'` in P1. Do not change `MAX_PASSAGES` or the test.
- New keyword but old answer: verify the P1 sentence, rebuild, stop/restart the local debug tasks and use a new conversation. This project is not a hot-reload promise.
- Hollow breakpoint: check `npm run build` and workspace root. The supplied attach target maps `lib/**/*.js` to TypeScript; do not attach to a different app/port.
- Citation validation failure: preserve the observed failure; inspect selected passages and generated reply in a short debug attempt. Do not disable validation or assert a reply was delivered when it was rejected.
- Azure failure: use the same-OS/configuration recovery in D2_Lab1 and ask the provider about role/quota/model. No fixture fallback.
- To reset this lab, restore only `src/policy.ts` from your untouched reference, then reapply the P1 edit. At this point Lab 3 has not changed P3; after Lab 3, preserve/reapply its P3 threshold change too.


## Completion checklist

- [ ] P1 includes the phishing keyword and sentence; Lab 1 and Lab 2 checkpoints pass.
- [ ] You observe selected P1 before a real Azure answer citing the supplied policy.
- [ ] The unrelated query skips the model and the P4 regression remains grounded.

Stop your own local servers and debug tasks when finished. Keep your edited source for the next lab. Follow provider save/expiry instructions; do not delete shared resources.
