# Day 1 · Lab 3 — Ground an agent in synced feedback

**Outcome:** ingest five synthetic Trey Research feedback files into Microsoft Graph, then create a separate, no-action declarative agent grounded in that exact connection. This is a standalone adaptation of [Copilot Camp E7](https://microsoft.github.io/copilot-camp/pages/extend-m365-copilot/07-add-graphconnector/): no previous Camp E2–E4 API project is needed.

**Workspace:** Windows training VM, VS Code and PowerShell. One-time preparation is already complete through the [course setup](../README.md) and [connector setup](../Day1/Lab3-CopilotConnector/SETUP.md). Allow approximately 50 minutes plus tenant indexing latency (planning estimate, not a measured completion time).

**Architecture:** local Markdown → local Functions timer + local Azurite → Microsoft Graph external connection → Microsoft 365 index → declarative agent. There is no API action, public tunnel, separately hosted API server, or Azure cloud deployment. The local Functions runtime does have a local listener; do not expose it. Microsoft 365 and Graph remain cloud services.

## 1. Inspect the data and permission boundary

1. Stop other lab debugging/tasks. In VS Code use **File > Open Folder** and open:

```text
C:\Users\Admin\ma-2041\Day1\Lab3-CopilotConnector\connector
```

2. Open `content/CF-001.md` through `CF-005.md`. These are AI-generated fictional customer comments, not evidence about real customers. Note each document's `id`, title, consultant and body. Read CF-001's Adatum example; you will check the answer against this file later.
3. Open `src/custom/getExternalItemFromItem.ts`. The `everyone` ACL makes the indexed synthetic items visible tenant-wide; it does not implement confidential per-client access. Do not add private documents.
4. Open `aad.manifest.json`. The connector requires Microsoft Graph **application** permissions `ExternalConnection.ReadWrite.OwnedBy` and `ExternalItem.ReadWrite.OwnedBy`. They let its app identity manage connections it owns and their items, not all tenant connections. An authorized tenant administrator must grant consent; a student sign-in alone does not grant it.
5. Confirm the instructor has authorized this training ingestion and arranged that administrator. App registration, consent, ingestion and indexing are separate checkpoints. If permission is unavailable, inspect the supplied files and record runtime checkpoints as **not run**—do not weaken permissions or switch tenants casually.

**Checkpoint:** identify the two application permissions and explain why only synthetic content is suitable for the supplied ACL.

## 2. Assign your own connection identity

1. In Explorer copy `env/.env.local.example` to `env/.env.local` only if `.env.local` does not already exist. Preserve an existing file and its generated identity; ask the instructor before changing it. Do not edit `.env.dev`.
2. In `.env.local`, replace `YOURSEAT` in both `CONNECTOR_ID` and `CONNECTOR_NAME` with your instructor-assigned unique letters/digits (for example `s07nov23`). Keep `TEAMSFX_ENV=local`, the base URL and the other settings.
3. The code appends `local` to the base ID. For example, base `tfcs07nov23` produces `tfcs07nov23local`. Use **only letters/digits**, keep the base at most **27 characters** so the combined ID stays at most **32**, and use a fresh seat-specific value rather than the example shared by the class. A local guard rejects invalid combined IDs.
4. The supplied `CONNECTOR_BASE_URL` points to the pinned public GitHub sample content directory. The adapter adds `.md` to each item ID, so a citation can open the actual sample file. This is a source link, not a server the student must start. Leave it unchanged for the supplied data.

**Checkpoint:** write down your base ID and expected combined ID. No passwords or client secrets belong in this evidence.

## 3. Provision locally, then grant admin consent

1. In Agents Toolkit confirm the assigned Microsoft 365 training account/tenant. Select **Run and Debug > Debug Connector**, then press **F5**. Use the **local** environment only. Do not select Deploy to Azure or a `dev` environment. If asked for an Azure subscription, cancel: that is not this lab's path.
2. The tasks start Azurite locally, provision the Entra app, generate ignored local settings, compile TypeScript, and start the local Functions host with the debugger. Task runtime is explicitly Node 22; changing a terminal to Node 24 does not change this task configuration.
3. Open the task terminal **func: host start**. The startup ingestion attempts app-only authentication. If consent is absent it prints an Entra app-permissions link. Have the authorized administrator open that link in their own signed-in browser, verify the app/client ID against `env/.env.local`, inspect the two **application** permissions from step 1, then select **Grant admin consent** for the training tenant.
4. Verify the portal shows both permissions **Granted for** the correct tenant. Do not share the generated secret, `local.settings.json`, or `.env.local.user`. If the runtime's ten-minute consent window expired, stop debugging and restart **after** consent. Do not create another registration just because consent took time.

**Checkpoint:** record app display name, redacted client ID and consent status/tenant. No consent means no ingestion claim.

## 4. Verify connection, schema, ingestion and search separately

1. In the Functions task terminal look for `Creating connection <id>` / `Connection <id> was created` (or `already exists`), then schema creation and search-settings update on the first run. Copy the **actual** connection ID from the log, not just your predicted value.
2. Watch `Loading CF-001...` through `Loading CF-005...`. There must be no `Failed to load` messages. **Loading is an attempt, not proof of success:** the upstream sample catches item errors and can finish the function even when an item failed. A successful timer invocation by itself is not your pass condition.
3. Open [Microsoft 365 admin center — connectors](https://admin.cloud.microsoft/#/copilot/connectors). Find **your** named connection and confirm its ID and **Ready** state. If a required action offers **Include Connector Results**, have the authorized administrator review/enable it. Use the connection's status/item information to check successful ingestion where available; a zero-item connection is not complete.
4. In [Microsoft 365 Search](https://m365.cloud.microsoft/search), search for:

```text
Adatum Corporation Avery Howard
```

5. Verify the returned title/source belongs to your feedback connection. Open the source link and compare it with `content/CF-001.md`. The public GitHub page alone proves only source reachability, not tenant ingestion. Check a distinctive title or phrase from each of the other four supplied files as well, using the source/connection filter if available so another learner's duplicate content does not count as your proof.
6. Indexing is asynchronous. **Ready**, item upload, search visibility and Copilot grounding may occur at different times. Allow propagation and recheck; do not loop F5 or delete/recreate the connection to force indexing. If the lesson window expires, record **ingested / search pending** as appropriate and complete the agent authoring step while keeping the live-answer gate open.
7. Once ingestion is verified, stop debugging and terminate the Azurite/host tasks. Synced content stays in Microsoft 365; an agent query does not require this local host to remain running.

**Checkpoint:** actual connection ID, Ready status, all five upload attempts without errors, and search evidence for your indexed source. Separate any unverified condition explicitly.

## 5. Create a separate no-action declarative agent

1. Open a **new VS Code window**. In **Microsoft 365 Agents Toolkit > Create a New Agent/App**, choose **Declarative Agent**, then **No Action** (wording can vary by extension version). Choose `C:\Users\Admin\ma-2041\work` as the parent folder and name the project `TreyFeedbackAgent`. Do not overwrite the connector or reuse the earlier API agent.
2. In the generated project's `appPackage` folder, open the declarative-agent JSON file referenced by `manifest.json` under `copilotAgents.declarativeAgents[].file` (normally `declarativeAgent.json`). Keep the Toolkit-generated schema/version and package icons. Set the agent name to `Trey Feedback — YOURSEAT`, using your seat suffix, and its description to `Answers from synthetic Trey Research feedback.`
3. Replace its `instructions` value with the following text as a JSON string, preserving valid JSON:

```text
You help review fictional Trey Research consultant feedback. Use the configured feedback connection as your evidence. Cite the feedback sources for factual claims and distinguish each client's experience. Do not present this synthetic training content as real customer evidence. If the requested information is not in the feedback, say that it is not available. Do not invent project dates, contact details, or financial figures. You cannot perform actions or change records.
```

4. Replace the `capabilities` array with the fragment below. Replace `REPLACE_WITH_ACTUAL_CONNECTION_ID` with the ID verified in step 4. Do not retain the placeholder or use another learner's connection. This is a property fragment inside the existing object, not a complete manifest:

```json
"capabilities": [
  {
    "name": "GraphConnectors",
    "connections": [
      { "connection_id": "REPLACE_WITH_ACTUAL_CONNECTION_ID" }
    ]
  }
]
```

5. Verify there is no `actions` entry, API plugin, OpenAPI runtime or web-search capability. This agent's knowledge comes from the indexed connector. Instructions are behavior guidance, not an access-control replacement.
6. Save. In this separate agent project use Toolkit **Lifecycle > Provision** for **dev**, as in Lab 1. This agent environment is separate from the connector’s local environment. A No Action project packages the agent; it does not require a tunnel or API host. If asked to expose an API or choose Azure resources, cancel and confirm you selected **No Action**.
7. Open `https://m365.cloud.microsoft/chat` using the same training account. In Copilot explicitly select **Trey Feedback — YOURSEAT** and start a fresh chat. Do not assume the default Copilot landing page selected your agent. If editing an already-installed version, increment `appPackage/manifest.json`'s app version (for example `1.0.0` to `1.0.1`), reprovision the same dev environment and start a fresh chat.

**Checkpoint:** the packaged agent has your verified connection ID, no actions, and the correct installed identity in Copilot.

## 6. Verify a cited answer, then a missing-information answer

1. Ask your selected agent:

```text
What improvements did Adatum Corporation report after Avery Howard's supply-chain work? Cite the feedback and identify which reported figures support your summary.
```

2. Open the citation. Check that its source is the Adatum feedback, and compare the answer and numbers with `content/CF-001.md`. The expected kind of result is a concise summary supported by that document, not a generic statement about supply chains. A fluent uncited answer, another learner's connection, or an unrelated citation is not a pass.
3. Ask:

```text
What is Avery Howard's private mobile number and next available appointment? Use only the feedback sources.
```

4. Confirm the agent reports that the information is not available from the supplied feedback rather than fabricating it. This is a behavioral check, not proof that all hallucinations are prevented.
5. Save redacted evidence of the consent checkpoint, actual connection ID/Ready state, source search, selected agent identity, cited answer and missing-information response. If indexing/Copilot access is still pending, record exactly which gates are incomplete rather than substituting the local source file for a live answer.

**Checkpoint:** one source-supported cited reply and one appropriate missing-information reply from your installed no-action agent.

## 7. Stop and retain evidence safely

1. Stop any remaining connector/Storage tasks. No public tunnel should have been created. Closing the connector does **not** delete the connection, indexed items, Entra registration or installed agent.
2. The adaptation removes registration of the upstream destructive `retractConnection` timer. Do not invoke its retained source function manually. Rerunning ingestion writes the same item IDs; removing a local Markdown file does not automatically delete its indexed item.
3. Retain training resources until the instructor has checked evidence. For later cleanup, the authorized administrator first verifies your exact connection ID/owner in the admin center, deletes only that training connection with approval, verifies its absence, and then removes the dedicated app registration/credentials and unneeded installed agent. Do not delete a shared connection or registration and do not treat local file deletion as tenant cleanup.

| Symptom | Check / recovery |
|---|---|
| `func` missing or wrong Node | Stop and return to the one-time setup owner. Core Tools must be global v4; workspace tasks use the supplied Node 22 path. |
| Azurite port already occupied | Stop the previous lab's tasks; do not start another emulator or kill unrelated processes. |
| 401/403 or consent timeout | Confirm the exact app, tenant, application permissions and admin grant; restart after correction. |
| Connection ID conflict / not owned | Ask instructor to verify ownership; use a fresh assigned base ID rather than deleting another learner's connection. |
| `Loading` appears but no items/search | Check `Failed to load`, schema errors and connection status first; then allow indexing. |
| Search works, agent has no answer | Check actual `connection_id`, installed version/account/agent, fresh chat, and Copilot propagation. |
| Citation opens localhost or 404 | Verify supplied base URL and `.md` URL adaptation; rerun ingestion only after fixing configuration. |

**Completion:** you can explain the difference between connector app-only write permissions, item ACL visibility, indexing and the agent's knowledge binding. Local compilation is not tenant completion.
