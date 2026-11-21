# API compatibility decision

> **Required working environment: the provided AI3026 Day 2 lab VM.** Perform every clone/download, dependency check or installation, VS Code action, terminal command, file edit and browser/Teams/Copilot test **inside that VM**. Your physical PC is only for accessing the VM. In this guide, “local” hosting/debugging means **local to the VM**, never your physical PC. Install or change tools only with the lab provider’s permission.

## Verified source mismatch — not a configuration typo

AI3026 `01-build-agent-portal-and-vscode.md` at `df5b56b41480298afc09abf28c79c0d1856f40dd` requires the **New** Foundry experience. Its client retrieves `project_client.agents.get(agent_name=agent_name)` and sends `openai_client.responses.create(... extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}} ...)`. The current documentation identifies saved agents by name/version.

Microsoft ProxyAgent-CSharp at `16f3562e64e6df20da4b736e9c499708d7f86070` instead imports `Azure.AI.Agents.Persistent`, instantiates `PersistentAgentsClient`, retrieves `Administration.GetAgentAsync(_agentId)` and obtains an Agent Framework `AgentThread`. Its configuration is `AIServices:AgentID` / `AGENT_ID`; its README illustrates `asst_...`. Its project targets net9.0 with Agents SDK 1.3.176, Persistent 1.2.0-beta.8 and Agent Framework 1.0.0-preview.260108.1. A modern name/version is **not** a classic persistent assistant ID. Renaming the environment variable cannot reconcile those protocols.

## Chosen bridge

- Keep the original modern Foundry project, agent name, saved version, instructions and attached file search.
- Invoke `POST {projectEndpoint}/openai/v1/responses` with `agent_reference: {type:"agent_reference", name, version}` and `input`.
- Use Azure.Identity 1.17.1 / AzureCliCredential with `https://ai.azure.com/.default`; Microsoft 365 Agents SDK 1.3.176 handles Activity protocol independently of the Foundry REST boundary.
- Target .NET 10; no Agent Framework preview or Persistent SDK is required. Toolkit CLI is pinned to 1.1.19 and Bicep to v0.38.33.
- Do not create a new agent in code, override its model/instructions, recreate tools, or convert it to classic. Invalid `asst_` identifiers fail locally before credential acquisition.
- Do not claim that a Python function tool runs inside this C# proxy. File search is service-managed; custom function calls require a separate client execution loop and are explicitly rejected here.

## Evidence boundary

The package restores/builds and its offline request, response, error, citation, identity and host-authentication checks run locally. This establishes compilation and REST contract conformance to cited docs; **it does not establish a successful live modern-agent invocation or a tenant-compatible deployment**. The C# live probe in Lab 3 is a mandatory same-agent acceptance gate. Lab 4 is gated on that proof plus tenant/provider permission. If either gate fails, preserve the existing agent and report that slice blocked. Do not silently fall back to the classic sample, a bare model, portal publishing, or fabricated responses.

The student workflow deliberately uses local hosting + tunnel + Azure Bot, not the original sample’s larger SSO/App Service deployment. The Bicep compiles and the Toolkit/manifest configuration can be checked locally, but Entra application creation, Bot provisioning, M365 extension and actual channel behavior remain live acceptance work. Portal publish is a separate supported workflow, not evidence that the SDK proxy worked.
