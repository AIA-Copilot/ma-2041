# Optional connector setup

This exercise is separate from the four required Day 1 labs. Follow [Optional connector exercise](../../docs/D1_Optional_Connector.md).

In the course-window Terminal:

```powershell
Set-Location C:\Users\Admin\ma-2041
.\scripts\Prepare-Day1.ps1 -Target Connector
```

Complete the Windows installer prompts. Wait for `OPTIONAL CONNECTOR PREPARATION COMPLETE`, close all VS Code windows and reopen them. Core Tools `func --version` must report `4.x`. Use Node 22 for this connector, not the Node 24 used by TypeSpec and WIQD.

The exercise needs an authorized administrator to grant Microsoft Graph application permissions for synthetic Zava policy ingestion. Have Microsoft Authenticator available for lab-account registration if prompted. Remove only that lab account entry after all exercises and sign-ins are finished. Do not remove existing personal/work entries.

Use the **local** environment and **Run and Debug > Debug Connector > F5**, not Toolkit Deploy. No Azure subscription or public tunnel is required. Keep upstream-reference files as provenance, not executable instructions. Retain resources until the instructor authorizes cleanup.
