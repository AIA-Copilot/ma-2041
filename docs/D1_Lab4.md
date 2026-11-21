# Day 1 · Lab 4 — Ingest policy knowledge and ground an agent

**Workspace:** use VS Code and PowerShell 7 inside the provided MS-4018 VM. “Local” means this VM. One-time preparation: [course setup](../README.md).


**Outcome:** run the official policies Copilot connector, obtain approved Entra application permissions, create an external connection and schema, ingest the supplied synthetic IT policies, then upload an agent grounded in that exact connection and verify a cited answer in Copilot.

**Allow:** 50 minutes of practice after provider/administrator preflight (planning budget, not measured completion), including the official 5–10 minute connection/schema/ingestion window. Admin availability and indexing may add elapsed time. This is not merely a manifest-edit exercise.

**Start gate:** the instructor must confirm [provider preflight](INSTRUCTOR-PREFLIGHT.md) before runtime work. If tools or approval are missing, stop; do not install or bypass policy during this lab.


**Source:** [Microsoft Learn connector exercise](https://learn.microsoft.com/en-us/training/modules/copilot-declarative-agent-graph-connector-vsc/3-exercise-create-declarative-agent-copilot-connector). The exercise downloads [the policies connector](https://aka.ms/learn-gc-ts-policies), then creates a declarative agent with Toolkit. This package includes that pinned PnP TypeScript connector under `connector`, plus the official basic JSON agent scaffold under `agent` so you do not need to download a moving sample during class. It is not a fabricated CSV-only replacement for ingestion.

## Current route — read-only while runtime is on HOLD

The connector retains **nine moderate affected packages across two unique advisories**. A named provider/security owner must disposition the exact residual risk or a tested remediation before runtime. VM isolation and local test success do not release this hold.

1. Open the connector folder in VS Code; do not run terminal commands, tasks or F5.
2. Read the permission/ACL checks in section 1 and the configuration values in section 2 without changing them.
3. Trace the eight files in section 3. Explain how a source file becomes a Graph item and how its ACL differs from its citation URL.
4. Read the separate agent manifest and instruction file named in section 6 without changing or provisioning them.
5. Record **read-only walkthrough complete; ingestion, indexing and Copilot grounding blocked**.

**STOP here while HOLD remains.** Sections 1–7 below are the conditional live route, not instructions to execute now. Do not prepare the tenant, install dependencies, start Azurite/Functions, or run F5 until security disposition and provider preparation are complete.

## 1. Confirm preflight permission and data receipts (3 minutes)

1. Read the [Day1 setup gates](../Day1/README.md). Stop if any of these are unresolved:

- The assigned account has Microsoft 365 Copilot and custom-app upload permission.
- The instructor authorizes creating a lab Entra app registration, its local client secret, a Graph external connection, schema and synthetic external items in the **assigned training tenant**.
- An authorized tenant administrator is available to review/grant **Microsoft Graph application** permissions `ExternalConnection.ReadWrite.OwnedBy` and `ExternalItem.ReadWrite.OwnedBy`. These are not delegated user permissions. Do not use a personal account or bypass admin consent.
- The connector's item ACL is `everyone`: every user in the tenant may access these ingested sample items. Use only the supplied synthetic policy files. This exercise is not a private-document security design.
- The instructor gives you the connection naming rule. `CONNECTOR_ID=policies` plus `TEAMSFX_ENV=local` creates `policieslocal`, exactly as in Learn. In a shared tenant, that ID is not safe for every student's different app: agree unique alphanumeric prefixes before starting.

If consent is unavailable, use read-only inspection; only after runtime security release may the instructor authorize local build/transform checks. Mark **ingestion and Copilot grounding blocked**. Do not treat local test output as a successful external connection.

**Checkpoint:** Record authorization, permissions, synthetic-data ACL and unique ownership, or blocked status.

## 2. Open and check the prepared connector (4 minutes)

1. Only on the security-released live route, open the prepared connector and run its checks.

```powershell
Set-Location C:\ma-2041\Day1\Lab4-CopilotConnector\connector
code .
npm.cmd run build
npm.cmd test
npm.cmd run check:func
```

**Expected result:** build succeeds, the transformation test reads ten real IT policy source files and passes, Core Tools reports 4.16.1. The test deliberately makes **no Graph request** and proves no tenant state.

In VS Code Extensions, verify **Microsoft 365 Agents Toolkit** and **Azure Functions** are enabled inside the VM. The Azure Functions extension provides the Functions background problem matcher. The `func: host start` task explicitly runs the provider-approved, hash-checked MSI Core Tools with the Node debugger on port 9229. This connector also uses Azurite, installed by the lockfile, for the local timer-function storage requirement.

Open `env/.env.local`. Keep:

```dotenv
TEAMSFX_ENV=local
CONNECTOR_SCENARIO=it
```

`it` is the actual folder name under `content`; do not use the outdated `it-policies` value from historical README prose. If your instructor assigned a unique connection prefix, replace **only** the `CONNECTOR_ID` value now. Use an alphanumeric prefix whose final value including `local` is at most 32 characters. Do not change it mid-ingestion or copy another learner's connection ID.

`CONNECTOR_BASE_URL` points at the pinned public upstream IT-policy files. This course corrects the sample's non-working `https://localhost:3000/` citation base and uses each actual Markdown filename. It does not create a new content server or pretend localhost is a usable external source.

**Checkpoint:** Record the final connection prefix/environment and source folder; do not guess another ID.

## 3. Understand what will be sent to Graph (6 minutes)

1. Read the files in this chain before starting:

| File | Responsibility |
|---|---|
| `content/it/acceptable-use-policy.md` | Synthetic policy body and front matter (`id`, title, author, modified date, abstract) |
| `src/services/itemsService.ts` | Reads Markdown files, strips formatting and builds a source URL |
| `src/custom/getExternalItemFromItem.ts` | Maps content/properties and the tenant-wide `everyone` ACL |
| `src/references/schema.json` | Searchable/retrievable properties and semantic labels |
| `src/config.ts` | Forms the final connection ID from prefix + environment |
| `src/functions/connections.ts` | Startup timer calls connection, schema, search settings and ingestion |
| `aad.manifest.json` | The two required Graph application permissions |
| `m365agents.local.yml` | Local Entra provisioning and generated Functions settings |

The connector and agent are separate apps: the connector ingests content; the declarative agent references its connection ID. An agent manifest does not ingest files by itself.

2. Review the schema's `title`, `abstract`, `author`, `lastModified` and `url`. Boolean flags are actual JSON booleans. The item URL is a citation destination; it is not an authorization boundary. The sample content is public/synthetic, and the connector ACL deliberately permits the tenant.

The course disables the upstream scheduled **retract/delete** timer. Cleanup must be an explicit instructor/admin action, not an annual timer that might unexpectedly delete a reused connection.

**Checkpoint:** Explain source → item/schema/ACL → connection → agent reference.

## 4. Confirm pre-provisioned identity and run the connector (5 minutes)

**Outside-class prerequisite:** the provider/admin completes the following registration/consent steps without starting the ingestion host. In the 5-minute learner block, verify the existing identity/consent, then F5 using that same app and connection prefix. A missing receipt is a stop, not an unbudgeted student installation/admin task.

Provider registration/consent details are in [instructor preflight](INSTRUCTOR-PREFLIGHT.md). Verify its receipt; do not perform missing preparation in lab time.

**STOP before F5 if runtime security disposition, app ownership or admin-consent receipts are missing.**

After security release and provider preparation, the learner follows the existing local debug path:

1. In Toolkit > **Accounts**, confirm the assigned training tenant. Do not choose Azure deployment or the main Lifecycle Provision command: use the configured local debugging path.
2. In **Run and Debug**, select **Debug Connector** and press F5.
3. Watch the task sequence: install dependencies; start Azurite; provision the Entra registration for the local environment; compile/watch; start the Functions host; attach the debugger.
4. The local lifecycle writes `local.settings.json` with the generated app ID, tenant ID and secret. **Do not print, screenshot, commit or share this file**. Its presence is not proof that consent succeeded.
5. Open the **Terminal** associated with **func: host start**. When the connector says tenant-wide admin consent is needed, give the authorized administrator the requested application identity through the approved class process. The printed link opens the app's API permissions in Entra; do not copy the full console into a public repository.
6. The administrator checks the app name/tenant and the two OwnedBy application permissions, then selects **Grant admin consent**. A student without the required role must not try to self-elevate.
7. Return to the Functions terminal. The sample retries while waiting for consent. If the ten-minute startup window expires before approval, stop debugging, complete authorized consent, then restart the same project; do not create a new app for each retry.

**Expected evidence:** the correct app registration and consent recorded by the administrator; connector output saying the actual connection was created or already exists. “Already exists” is not enough if it belongs to another learner/app—stop and reconcile ownership.

**Checkpoint:** Record the exact app and consent receipt plus owned connection result.

## 5. Verify connection, schema and items—not just a green host (12 minutes)

1. Allow the official **5–10 minutes** for connection/schema/ingestion, then read the full terminal output. Expect creation/recognition of your connection, successful schema creation, search settings, and item-loading activity for the ten IT documents. A host banner or a single `Loading ...` line is not proof that all items were accepted. Inspect for errors; the course code propagates schema/ingestion failures instead of silently treating them as completion.

2. With the administrator/instructor, open the Microsoft 365 admin center's search/connector data sources experience (the upstream sample uses **Settings > Search & intelligence > Data sources**; portal names can change). Find the **exact connection ID** and verify its status and ingested item information. If **Include Connector Results** is offered as a required action, have the authorized administrator enable it for this lab connection. Do not change another connection.

3. Search Microsoft 365 for:

```text
acceptable use policy
```

When indexed, the policy should appear. Open the source/citation and compare it with the supplied Markdown file. Indexing can lag behind successful API ingestion. Record **ingestion complete, search pending** if that is the actual state; do not repeatedly recreate connections to force indexing.

Once the successful ingestion is recorded, stop debugging and terminate all task terminals, including Azurite. The ingested content remains in Microsoft 365; the connector does not need to run continuously for the following agent test.

**Checkpoint:** Distinguish accepted items from indexing/search readiness.

## 6. Open the separate agent scaffold and bind the real connection (8 minutes)

The official UI route is Toolkit **Create a New App > Agent > Declarative Agent > No plugin**, naming the project `da-it-policies`. The supplied `agent` folder provides that basic JSON scaffold as a pinned course checkpoint. Use it instead of generating a second project with changing template defaults.

```powershell
Set-Location C:\ma-2041\Day1\Lab4-CopilotConnector\agent
code .
```

Confirm VS Code is now rooted at `agent`, not `connector`. Open `appPackage/declarativeAgent.json`: its name is **Contoso IT policies**, description is **Assistant specialized in Contoso IT policies**, and instructions refer to `instruction.txt`.

Read the instruction file. It asks for accurate, helpful responses and says to acknowledge missing information. It does not override permissions or create a connection.

Use the **actual final ID** from the successful connector log/admin record:

```powershell
$connectionId = Read-Host 'Enter the exact external connection ID from your successful ingestion'
node scripts/configure-connection.mjs "$connectionId"
```

This changes local JSON only. It adds a `GraphConnectors` capability containing `connections: [{ "connection_id": your actual ID }]`. With the unmodified official prefix, the value is `policieslocal`; with an instructor-assigned prefix, use that resulting ID instead. Do not paste a sample/dummy ID simply to pass JSON validation.

Review the manifest and exact ID. Then choose Toolkit **Lifecycle > Provision** for this **agent** project. Wait for its app package to be built and uploaded. Inspect the generated agent manifest to confirm the final connection ID and expanded instructions.

**Checkpoint:** The agent manifest uses your actual ingested connection ID.

## 7. Prove grounding in Copilot (9 minutes)

1. Open **Preview in Copilot (Edge)** from this agent project, or navigate inside the VM browser to `https://www.microsoft365.com/chat`. Use the same assigned work account. Choose **Contoso IT policies**, not generic Copilot.

2. Send the official test:

```text
What's the acceptable use policy at Contoso?
```

**Expected result:** an answer grounded in the ingested policy, with references to the external content. Open a reference and verify that the underlying policy supports a specific claim—for example, its use of organizational IT resources. The citation should resolve to the pinned public source file, not localhost. The answer text may vary; source support must not.

3. Run an unsupported-information check:

```text
What is Contoso's approved policy for taking a company laptop to the Moon?
```

**Expected result:** the agent acknowledges that the supplied policy does not establish such approval and does not invent a policy. This is a behavioral probe, not a deterministic proof that the model can never hallucinate. Record and investigate a false assertion.

**Completion evidence:** exact connection identity/ownership; approved permissions; successful schema and item ingestion; index/search observation; installed agent with matching connection ID; cited policy answer with source opened; missing-information behavior. If indexing or consent remains blocked, record the blocked stage explicitly.

**Checkpoint:** Record cited supported answer and unsupported-policy behavior, or the precise blocker.

## Recovery and cleanup (3 minutes)

| Symptom | Check and safe recovery |
|---|---|
| Functions problem matcher unavailable | Enable Azure Functions extension in the VM and reload VS Code. |
| Azurite fails to bind ports | Stop the previous lab's storage task; identify the owning process. Do not kill arbitrary VM processes. |
| 401/403 | Check generated tenant/app identity and actual admin consent. Do not widen permissions to unrelated Graph scopes. |
| Connection already exists but access denied | Instructor checks ID ownership. A shared prefix with separate app registrations causes collisions. Use an approved unused prefix before reprovisioning; never delete another learner's connection. |
| No files or path error | `CONNECTOR_SCENARIO=it` must match `content/it`; run from the connector root. |
| Schema/item failure | Read the first API error; inspect schema/property types and required fields. Do not mark a later host banner as success. |
| Search works but agent cannot cite | Compare exact connection ID, active agent, saved/provisioned manifest and user access; allow indexing/propagation before a fresh chat. |
| Source opens localhost | Inspect `CONNECTOR_BASE_URL` and URL mapping; use the packaged pinned source URLs, then re-ingest through the approved same connection. |

Stop all debugging/tasks. Preserve only redacted results, not generated secrets. The instructor/admin owns removal of **your exact** agent app, connector app registration/secret and external connection after the class. Removing the local folder does not remove tenant items. Do not enable the old retract timer or delete shared resources.

**Additional practice:** [Challenge project — chat with external data](https://learn.microsoft.com/en-us/training/modules/copilot-declarative-agent-challenge-chat-with-external-data/). This is the learning path's separate challenge, not an additional invented core procedure. WIQD was introduced in Session 1; Session 4 is the synced connector ingestion/grounding session.

**Indexing fallback:** if your own ingestion succeeds but indexing exceeds the session, preserve the real schema/item evidence and mark your citation outcome pending. Only with instructor approval may you bind the supplied agent scaffold to a separately identified pre-ingested classroom connection to practise cited answers. Label that evidence **pre-ingested fallback — not my ingestion/indexing acceptance**, record both IDs distinctly, and never overwrite the learner result. If runtime security disposition is absent, use read-only walkthrough only and mark ingestion blocked.
