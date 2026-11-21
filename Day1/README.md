# Day 1 — build, act, present, ground

Open the prepared course in VS Code inside the **MS-4018 VM**. Use PowerShell 7, the assigned account and synthetic data. Complete [one-time setup](../README.md) before starting; do not repeat installation in each lab.

## Four sessions and four labs

1. **Foundations + WIQD:** 25-minute foundations, 15-minute CLI demonstration, 40-minute [Lab 1](../docs/D1_Lab1.md), 10-minute debrief. Project: `C:\ma-2041\Day1\Lab1-WIQD`. Build Briefing Coach without a coding assistant.
2. **API actions:** 20-minute teaching, 15-minute request trace, 45-minute [Lab 2](../docs/D1_Lab2.md), 10-minute debrief. Project: `C:\ma-2041\Day1\Lab2-RestaurantAPI`. Copilot calls the real VM-hosted restaurant API through an approved tunnel.
3. **Cards + secure action design:** 15-minute card teaching, 15-minute authentication walkthrough, 50-minute [Lab 3](../docs/D1_Lab3.md), 10-minute debrief. Project: `C:\ma-2041\Day1\Lab3-AdaptiveCards`. Select **Il Ristorante - Lab 3 Cards**, not the prior lab's agent.
4. **Synced connectors:** 20-minute teaching, 10-minute source/ingestion trace, 50-minute [Lab 4](../docs/D1_Lab4.md), 10-minute debrief. Project: `C:\ma-2041\Day1\Lab4-CopilotConnector\connector`, then its separate `agent` folder.

These are planning allocations, not measured completion times. Setup, administrator consent, breaks and delays are outside the six taught hours. A pre-ingested fallback is labelled separately from a learner's ingestion evidence.

## Before you begin

1. Start Lab 1 with installed Node 24.15+ and course-local WIQD 1.0.0. Use CLI commands, not Toolkit/F5.
2. Before Lab 2, have the provider select the tested **Node 22.22.2** Functions environment and restart VS Code. Verify `node --version`; current LTS does not establish compatibility.
3. Confirm provider preparation for Core Tools 4.16.1, cached dependencies, extensions, assigned account and anonymous restaurant tunnel. Detailed installation and receipts: [instructor preflight](../docs/INSTRUCTOR-PREFLIGHT.md).
4. For Lab 4, follow the **read-only route while runtime HOLD remains**. Nine moderate affected packages across two unique advisories require named security disposition before tenant preparation, Azurite, Functions or F5. Local tests are not ingestion acceptance.

**Checkpoint:** you know your project, account and permitted route. If a prerequisite is missing, ask the instructor; do not change package versions, weaken policy or install a workaround.

## Keep the learning evidence separate

- Source validation is not tenant provisioning or behavior testing. WIQD agent packaging needs a provisioned environment; the offline packager does not support this agent.
- Labs 2–4 F5 can create applications, tunnels or Graph content. Obtain the stated approval before side effects.
- Cards do not authenticate APIs. Session 3 includes an instructor authentication walkthrough; the learner API remains anonymous synthetic data.
- Stop only your lab hosts/tasks/tunnels after use. Preserve redacted evidence; exact-resource cleanup belongs to the authorized owner.
