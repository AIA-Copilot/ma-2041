# Day 2 · Lab 4 — Trace the Microsoft 365 integration

**Current route: read-only architecture practice.** Allow 25–35 minutes after Lab 3 (estimate). Use the AI3026 VM and the supplied files. You will explain how the same grounded Foundry agent would be reached from Teams/Copilot through the C# host and Agents Toolkit.

This lab does **not** deploy or test a live Teams/Copilot channel. The retained Toolkit CLI dependencies have unresolved findings, and the old channel route needs a public development tunnel. This course does not authorize that tunnel. A successful Lab 3 probe does not clear either limitation.

**Do not run Toolkit CLI, install its credential module, provision, deploy, start a tunnel or start the Proxy for this exercise.** No Azure or tenant changes are needed for the read-only outcome.

[Course setup](../README.md) · [Previous: C# bridge](D2_Lab3.md)

## 1. Open the integration files

1. In VS Code open `C:\ma-2041\Day2\AI3026`.
2. Read `M365Agent\m365agents.local.yml` and `M365Agent\appPackage\manifest.json`. Do not run the lifecycle.
3. Find `teamsApp/create`, `aadApp/create`, `arm/deploy`, the local settings write, app-package validation and Microsoft 365 extension actions.
4. Classify each as an app-registration action, Azure resource action, local file action or package action.

**Checkpoint:** Explain why a command named Provision is not merely a local build. In this particular lifecycle it can create an Entra app, secret and Azure Bot resource. This differs from Day 1's no-backend declarative-agent workflow.

## 2. Trace identity and transport

1. In the app manifest, find `bots[].botId` and `copilotAgents.customEngineAgents[].id`.
2. Confirm both refer to the same `${{BOT_ID}}` placeholder. This is not the Foundry agent's name/version.
3. Read `M365Agent\infra\bot.bicep`. Find the messaging endpoint and the Teams channel configuration.
4. Read `Proxy\Program.cs`. Find the route `/api/messages` and its authorization requirement.
5. Explain why a cloud channel cannot call `localhost` inside your VM. The previous live sample used a tunnel; you are not starting one.

**Checkpoint:** Draw: Teams/Copilot → channel/Bot service → authenticated C# endpoint → Foundry agent. Label the Bot app ID, Foundry project endpoint, agent name and version separately.

## 3. Trace the same grounded agent

1. Open `Gateway\FoundryGateway.cs` and `Proxy\PolicyAgent.cs`.
2. Identify how the host selects the Foundry project, agent name and grounded version used in Labs 1–3.
3. Locate the developer Azure CLI credential path. Explain why it is not the chatting user's identity.
4. Compare the `/help`, unsupported-policy and action-boundary behaviors with the tests you ran in Lab 3.

**Checkpoint:** Explain why a correct channel reply must be attributed to this code and the same grounded agent. A response from the portal alone is not evidence that a Teams/Copilot integration works.

## 4. Inspect the acceptance tests without running the host

Read the following proposed checks and state what each proves:

- A local health response: process availability only; not a Foundry or channel reply.
- An unauthenticated POST to `/api/messages` rejected with 401: the route does not accept an anonymous caller; not a complete authentication audit.
- A `/help` response in Teams matching your edited C# text: evidence that the channel reached this host.
- A policy-supported answer using the same grounded version: end-to-end retrieval behavior.
- A separate observed reply in Copilot: Copilot availability is distinct from Teams installation.

**Checkpoint:** Mark the actual evidence from your course run. Do not mark the proposed channel checks as passed; they have not been executed in this exercise.

## 5. Record your result

Write a short explanation containing:

1. The request path and purpose of each component.
2. The difference between the Bot app ID and Foundry agent name/version.
3. The reason developer-identity access is unsuitable as-is for a multi-user production service.
4. The checks needed before anyone could claim a working Teams and Copilot deployment.
5. The current limitations: unresolved Toolkit dependency review, no approved reachable hosting route without a public development tunnel, and no live channel acceptance.

**Complete means:** you can explain the supplied integration and its missing deployment evidence. It does not mean a Microsoft 365 custom engine agent was deployed.

No cleanup is required for this read-only lab because it created no resources. Preserve Lab 3 evidence and follow the provider's cleanup instructions for resources created in earlier labs. Do not delete shared resources.

## References

- [Custom engine agents](https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/overview-custom-engine-agent)
- [Local source provenance](../Day2/AI3026/SOURCES.md)
- [Compatibility and identity distinctions](../Day2/AI3026/COMPATIBILITY.md)
