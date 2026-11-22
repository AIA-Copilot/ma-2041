# Instructor preflight

## Day 1 preparation

Use the fresh-clone and one-time VM instructions in [the root README](../README.md). They prepare PowerShell7, Microsoft extensions, exact portable Node22.22.2/24.15.0 and WIQD1.0.0. No Postman, Python, Azure hosting or public development tunnel is used by Day1.

- Lab1: assigned Copilot account, custom-app upload, Toolkit; supplied Zava knowledge document.
- Lab2: public Frankfurter HTTPS access; three HTTP200 and invalid-code422 tests passed outside the VM. Actual Copilot invocation/card still requires VM rehearsal. See [currency acceptance](Currency-Instructor-Acceptance.md).
- Lab3: [connector setup](../Day1/Lab3-CopilotConnector/SETUP.md); administrator availability for ExternalConnection.ReadWrite.OwnedBy and ExternalItem.ReadWrite.OwnedBy application permissions; unique connection ownership; supplied synthetic data only. Scott accepted Day1 sample dependency risk for this temporary training environment; dependencies are not claimed remediated. No Azure subscription/cloud storage substitution or tunnel is required.
- Lab4: WIQD1.0.0 with Node24.15.0; human-reviewed terms, assigned training tenant, approved developer/legal metadata if generated placeholders are rejected. Do not copy consent stores or other deployments' IDs.

Rehearse all four exact guides and record native versions, actual outcomes and duration. Source validation/local tests do not establish tenant access, index availability, service behavior or source-supported answers. Never place secrets in the repository or evidence.

## Day 2 preparation

Use the AI3026 VM and its assigned Azure/Foundry resources. Confirm PowerShell7, Git, Azure CLI and .NET10 SDK (`dotnet --list-sdks` must show10.0). VS Code needs C# Dev Kit. Use the provider's approved installation process if anything is missing; Node/WIQD setup for Day1 does not prepare Day2.

Before Lab3, cache/restore the exact supplied projects:

```powershell
Set-Location C:\Users\Admin\ma-2041\Day2\AI3026
dotnet restore .\Proxy\Proxy.csproj --locked-mode
dotnet restore .\Probe\Probe.csproj --locked-mode
dotnet restore .\Tests\Tests.csproj
```

Use the same modern Foundry project endpoint, agent name and grounded version throughout Labs1–3. Confirm assigned model/deployment availability and provider-authorized consumption. No personal Azure subscription or unapproved resource purchase is requested.

## Day 2 Lab 4 is read-only

The retained pinned Toolkit CLI audit reported five affected packages (two high, three moderate), and the previous live channel path needs a public tunnel. Neither is cleared by the Day1 temporary-training exception. Do not install/rebuild Toolkit CLI/keytar, authenticate with it, provision/deploy, run a tunnel or start the proxy for Lab4. Its current guide is file/architecture inspection only. Existing source lifecycle/tunnel instructions are not execution authorization.

## Evidence and cleanup

Record Pass/Fail/Not run separately for source/build, native VM, Graph ingestion, indexing, actual Copilot answers, Foundry and channels. Keep a truthful blocked result if admin consent, service access or indexing is unavailable. Synthetic content and your assigned tenant only. Stop only your own debug/tasks; resource cleanup requires exact ownership and provider authorization. Do not enable destructive sample retract timers or delete shared connections.
