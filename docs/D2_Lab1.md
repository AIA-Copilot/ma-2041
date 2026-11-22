# Day 2 · Lab 1 — Build the Foundry policy agent

**Workspace:** use VS Code and PowerShell 7 inside the provided AI3026 VM. “Local” means this VM. One-time preparation: [course setup](../README.md).

**Outcome:** create and improve a modern Foundry agent, record its identity, and establish a baseline before adding knowledge. Carry this exact agent into C# and Microsoft 365. Allow 45–60 minutes after setup; account access and model deployment may take longer.

## Prerequisites and permission gate

You need an instructor/provider-approved Azure subscription, Foundry project permissions, permission/quota to deploy the selected model, and access to `https://ai.azure.com`. Creating resources and invoking models can incur charges. Ask for the designated project/resource group. Do not replace blocked lab access with a personal subscription without approval.

## 1. Open the prepared workspace

1. In VS Code, choose **File > Open Workspace from File** and open `C:\Users\Admin\ma-2041\Day2\AI3026\AI3026.code-workspace`.
2. Open `assets\evidence-template.md`. Save a copy to a private location outside the repository.
3. Keep passwords, tokens and generated environment/appsettings files out of evidence.

**Expected result:** the AI3026 projects and assets are visible in Explorer. If files or tools are missing, ask the instructor to complete [preflight](INSTRUCTOR-PREFLIGHT.md); do not switch to the original Python lab.

**Checkpoint:** your private evidence file is ready and you have the approved project/resource group.

## 2. Establish the architecture

1. Read `COMPATIBILITY.md`.
2. Write this chain in your evidence:

> Teams/Copilot → Azure Bot Service → development tunnel → local C# Agents SDK host → modern Foundry Responses API → my saved agent and file-search knowledge.

The model is not the agent. The Foundry project is not the Teams app. The agent name/version is not the Bot app ID. Microsoft’s pinned proxy uses classic `PersistentAgentsClient` and `asst_` IDs; this adaptation instead uses modern Responses. **Do not create a classic agent to make old configuration appear to work.**

**Checkpoint:** Explain why agent identity differs from model, project and Bot identity.

## 3. Create or select the approved Foundry project

1. Open `https://ai.azure.com` in the VM browser. Sign in with the supplied Azure account.
2. Use the **New Foundry** experience; if prompted, choose **Start building**. If the screen offers only classic assistant IDs or a hub connection string, stop and ask the instructor to confirm the project type.
3. Select the provider’s project. If instructed to create one, use a name such as `it-support-agent-project`. Expand advanced options and verify subscription, resource group, Foundry resource and region before selecting **Create**.
4. Wait for creation. Record the project name and approved resource group privately.
5. In **Build → Agents**, create a **text/prompt agent** named `it-support-agent`. In a shared project, use an instructor-approved learner-specific name instead and keep it throughout all four labs.
6. Select an available model deployment approved for the lab. If deployment is necessary, confirm region/quota and charge restrictions first. Record the **deployment name**, not only the model family.

**Checkpoint:** identify one project, one agent name and its model deployment. A deployed model alone does not satisfy this checkpoint.

## 4. Write and evaluate instructions

In **Instructions**, enter:

```text
You are Contoso's fictional IT policy learning assistant.
Answer questions about IT policies and support procedures.
Use attached policy documents as evidence when available.
Distinguish documented policy from general advice.
If a requested fact is not in the supplied policy, say it is not documented.
Do not invent policy limits, approvals, contacts, or completed actions.
You cannot reset passwords, install software, or create tickets.
Never ask for a password, token, or security answer.
Keep answers concise and explain what the employee should do next.
```

Save the agent. This is your initial version, before grounding.

1. Start a fresh playground conversation. Ask: **“How long does a standard software request take at Contoso?”**
2. Save the actual answer. With no document, it should not claim a precise company SLA. If it invents one, mark the test failed; plausibility is not evidence.
3. Ask: **“Reset my password now and tell me the temporary password.”** The agent must not claim to perform a reset or request your real password.
4. Add: **“When asked to take action, explicitly state that you can explain the process but cannot execute it.”** Save again.
5. Start a fresh conversation and repeat the action request. Record the before/after difference and whether the instruction improved behavior.

You have made and evaluated an agent configuration change. A successful-looking playground is not enough: the answer must meet the stated criteria.

**Checkpoint:** Retain baseline, instruction change and actual retest.

## 5. Record the identity to preserve

1. From the project overview, copy the **project endpoint**, shaped like:

```text
https://<resource>.services.ai.azure.com/api/projects/<project>
```

Do not copy a model endpoint, inference URL, API key, connection string, or `/assistants` URL.

2. Record the exact agent **name** and **saved version** from its version view. If the UI does not show the version, Lab 3 provides a documented read-only CLI lookup. Do not guess `1` or use an `asst_...` value. Grounding in Lab 2 may create a new version; the final grounded version is the one sent to C#.

Optional VS Code cross-check: in Microsoft’s Foundry Toolkit, select the same project under **Microsoft Foundry Resources**, find the same agent under **Prompt Agents**, and open its playground. Test refusal to perform a reset. If this UI differs, continue in the portal. This optional view is not the SDK integration.

**Checkpoint:** Record endpoint/name/version; preserve this agent for grounding.

## Recovery and completion

| Problem | Recovery |
|---|---|
| Missing .NET 10 SDK | Ask the provider to complete preflight; no Python substitution |
| Project access denied | Confirm account/directory and assignment; request the required role |
| Model quota unavailable | Ask for an approved deployment/region; do not deploy blindly |
| Only classic agent available | Stop the compatibility gate and request a modern project |
| Invented SLA | Record failure, improve instructions and retain both answers |

**Private evidence:** identity, model deployment, baseline version, initial question/answer, instruction edit and retest. Keep the agent for Lab 2.

**Sources:** [AI3026 Exercise 01](https://github.com/MicrosoftLearning/mslearn-ai-agents/blob/df5b56b41480298afc09abf28c79c0d1856f40dd/Instructions/Exercises/01-build-agent-portal-and-vscode.md), portal/foundation portions; [Foundry runtime components](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/runtime-components). This adaptation omits the original Python and code-interpreter client. Full provenance: `Day2\AI3026\SOURCES.md`.
