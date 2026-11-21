# Day 2 · Lab 3 — Implement and test the C# Foundry bridge

**Workspace:** use VS Code and PowerShell 7 inside the provided AI3026 VM. “Local” means this VM. One-time preparation: [course setup](../README.md).

**Outcome:** trace a real Microsoft 365 Agents SDK host, change its logic, test the modern REST contract locally, and invoke the **same grounded agent** from C#. Allow 60–90 minutes after dependencies are ready.

## Compatibility gate: read before running

The official Microsoft ProxyAgent-CSharp revision uses `PersistentAgentsClient`, classic assistant IDs and Agent Framework threads. AI3026 now creates named/versioned agents and invokes Responses. They are not interchangeable. This course’s C# adaptation retains the SDK host and Toolkit pattern but replaces only the Foundry boundary with documented modern REST. See `COMPATIBILITY.md`.

**Acceptance gate:** offline tests do not prove live Azure or channel behavior. The live probe in section 5 must pass before Lab 4; never substitute a classic agent or bare model.

## 1. Build and run offline tests

With provider-prepared dependencies, run in the VS Code **PowerShell 7** terminal:

```powershell
Set-Location C:\ma-2041\Day2\AI3026
dotnet build .\Proxy\Proxy.csproj --no-restore
dotnet build .\Probe\Probe.csproj --no-restore
dotnet run --project .\Tests\Tests.csproj
dotnet run --project .\Probe\Probe.csproj
```

The test executable prints named **PASS** lines and a summary; a failure returns a nonzero exit code. The supplied baseline has 18 offline tests. The final command prints that no network call is made without `--live`. It does not log in or invent an answer.

If a dependency or SDK is missing, record the first error and ask the instructor to complete preflight. Do not delete lockfiles or upgrade packages. An SDK error is not an Azure permissions error.

**Checkpoint:** Record offline PASS/failure output and the probe’s no-network message.

## 2. Trace the code path

Open these files in order and annotate your evidence:

1. **`Proxy\Program.cs`** — `AddCloudAdapter`, SDK agent registration, authentication middleware, and `/api/messages`. Notice `.RequireAuthorization()` is unconditional. Development does not mean anonymous chat access.
2. **`Proxy\PolicyAgent.cs`** — receives Activity messages; handles `/help` locally; forwards policy questions to `FoundryGateway.AskAsync`; returns a generic chat error rather than raw service exceptions.
3. **`Gateway\FoundryGateway.cs`** — validates the project endpoint and agent identity, obtains a token, creates an HTTP request, checks status and extracts text/file citations.
4. **`Probe\Program.cs`** — calls the same gateway directly, without Teams or Toolkit. This separates a Foundry problem from a channel problem.
5. **`M365Agent\m365agents.local.yml`** — Toolkit creates identities/Bot resource and runtime configuration during provision; builds/validates/updates the app package during deploy. These are external actions, not local unit tests.

Find the request body builder. It sends:

```json
{
  "input": "the learner's question",
  "store": false,
  "stream": false,
  "agent_reference": {
    "type": "agent_reference",
    "name": "your existing agent name",
    "version": "your grounded saved version"
  }
}
```

No model, instructions or tools are sent to replace your saved agent. The endpoint is `{projectEndpoint}/openai/v1/responses`. A named/versioned reference preserves your portal configuration. `store:false` does not guarantee that all platform telemetry or retention is disabled.

This bounded implementation is **single-turn**: it supplies no conversation or previous-response ID. Ask self-contained questions. It renders text and source filenames, not rich interactive citations, generated images or files. A client-side `function_call` response fails explicitly because no custom function execution loop exists here.

**Checkpoint:** Explain the exact agent_reference request and its single-turn limits.

## 3. Make a deliberate code change and test the boundary

You will change input handling, not merely run the supplied code.

1. Open `Gateway\FoundryGateway.cs`. In `BuildBody`, change the maximum input length from **4000** to **2000**, including the user-facing error message.
2. Save and run `dotnet run --project .\Tests\Tests.csproj` again.
3. The existing **4000 character boundary accepted** test must now fail. This is an intentional mismatch between the changed behavior and the old test. Record the actual failure.
4. In `Tests\Program.cs`, update the two length tests: accept **2000** characters, reject **2001**, and update their display names. Do not remove validation or weaken unrelated assertions.
5. Run the test executable again. All tests should pass. If they do not, fix your implementation before proceeding.
6. In `Proxy\PolicyAgent.cs`, edit `HelpText` to state your agent’s purpose and the new **2000-character** limit. Preserve its no-ticket/no-history limitations.
7. Run `dotnet build .\Proxy\Proxy.csproj` to verify the host still compiles.

Keep a small before/after diff or screenshots of just these code changes, with no credentials. Explain why input validation must happen **before** token acquisition or an HTTP request.

**Checkpoint:** Retain intentional red test, repaired green test and compiling help change.

## 4. Configure the existing modern agent

1. Confirm provider approval for model invocation. In PowerShell set non-secret configuration using your actual project/name from Labs 1–2:

```powershell
$env:FOUNDRY_PROJECT_ENDPOINT = 'https://YOUR-RESOURCE.services.ai.azure.com/api/projects/YOUR-PROJECT'
$env:FOUNDRY_AGENT_NAME = 'it-support-agent'
az login
az account show --query '{subscription:name,tenant:tenantId}' -o json
```

Use the assigned Azure identity/directory. If the subscription is not the approved one, select the provider-specified subscription with `az account set --subscription 'YOUR-APPROVED-SUBSCRIPTION-ID'`. Do not expose or copy access tokens.

2. If you already recorded the grounded saved version, assign it explicitly:

```powershell
$env:FOUNDRY_AGENT_VERSION = 'YOUR-GROUNDED-VERSION'
```

3. If the portal did not expose it, read the agent metadata with the documented REST operation:

```powershell
$agentUrl = "$($env:FOUNDRY_PROJECT_ENDPOINT)/agents/$($env:FOUNDRY_AGENT_NAME)?api-version=v1"
az rest --method get --url $agentUrl --resource https://ai.azure.com --query '{name:name,version:versions.latest.version}' -o json
```

Read the returned name/version. Compare the name with your evidence and assign the returned version only if it is the grounded version you just evaluated. A missing result or 404 is a blocker, not permission to guess. CLI metadata access is a live read, not local test output.

The developer identity needs the Foundry project data-plane permission appropriate to invoking the agent, typically the provider-assigned **Azure AI User** role or equivalent permitted custom role. A subscription management role does not automatically establish all data-plane rights. Ask the provider rather than granting broader roles yourself.

**Checkpoint:** Confirm approved account, project endpoint, exact agent name and grounded version.

## 5. Invoke the exact agent with C#

1. Run the live probe and enter the question below. This invokes the model using your approved Azure identity.

```powershell
dotnet run --project .\Probe\Probe.csproj -- --live
```

The probe prints the selected agent name/version and asks for one question. Enter **“How do I request custom software?”** The code obtains an Azure CLI credential for `https://ai.azure.com/.default`; you must not paste a bearer token into a file.

2. Compare the actual answer with Section 2 of `IT_Policy.txt` and the Lab 2 result. Look for approval/security-review steps and grounded source evidence. The gateway appends **Source files** when Foundry returns structured file citations with filenames. If the model merely types a filename but no annotation appears, do not call structured citation extraction verified.

3. Run the command again for **“What is the lunar-office allowance?”** The answer should state that it is not documented. Each invocation is a new, self-contained request. A success response with the wrong policy is still a failed grounding test.

**Mandatory gate:** retain a real C# answer, correct identity/version, and comparison with the policy. If invocation or grounding fails, Lab 4 is blocked until resolved. No local fixture can satisfy this gate.

**Checkpoint:** Retain a real policy-supported C# answer; otherwise Lab 4 is blocked.

## Recovery

| Symptom | Diagnose |
|---|---|
| `asst_` rejected | You supplied a classic ID; use the original modern agent name, not a renamed ID |
| Endpoint rejected | Copy the project endpoint; public Azure only in this exercise |
| Credential error / 401 | Check Azure CLI account, directory and login; never copy tokens manually |
| HTTP 403 | Ask provider to verify project data-plane roles and policy restrictions |
| HTTP 404 | Check project, exact agent name and saved version |
| HTTP 429 | Stop repeated requests; follow provider quota/rate-limit guidance |
| Function/no text/incomplete error | Check unintended tools, model capacity and run trace; do not fabricate output |
| Different answer than portal | Compare saved versions, file attachment, new conversation and actual source facts |

**Private evidence:** restore/build result, intentional red/green boundary test, help edit, actual same-agent probe answers and source checks. Do not delete the agent or files yet.

**Sources:** [official ProxyAgent-CSharp revision](https://github.com/OfficeDev/microsoft-365-agents-toolkit-samples/tree/16f3562e64e6df20da4b736e9c499708d7f86070/ProxyAgent-CSharp); [Foundry runtime components](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/runtime-components); [REST v1 reference](https://learn.microsoft.com/rest/api/microsoft-foundry/aiproject); [Agents SDK](https://learn.microsoft.com/en-us/microsoft-365/agents-sdk/agent-application). See `SOURCES.md` for modifications and licenses.
