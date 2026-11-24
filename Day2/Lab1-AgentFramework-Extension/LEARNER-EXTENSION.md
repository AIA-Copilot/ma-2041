# Day 2 · Lab 1 — Put your Lab07 expense agent in Teams and Copilot

**Target: 25–30 minutes after preparation. This is an estimate, not a timed-VM result.** Complete [official Lab07](https://microsoftlearning.github.io/mslearn-ai-agents/Instructions/Exercises/07-agent-framework.html) first and **defer cleanup**. Keep its completed Python file, Foundry project, model deployment and synthetic `data.txt`.

**Outcome:** the same `ExpenseClaimAgent` prepares an itemized **SIMULATED** claim in Teams and Copilot, hosted on Azure App Service Free F1. You change its expense instructions and redeploy. No real email, payment or claim is sent.

**Before the clock starts:** the instructor prepares Python 3.13, Azure CLI 2.48.1+, Bicep, VS Code and supported Agents Toolkit 6.20, installs this project's pinned Python dependencies and clears Azure/Microsoft 365 account and custom-app permissions. You need an assigned resource group, available Linux F1/Python 3.13 capacity, approved policy URLs and existing Foundry access. Sign in to Azure CLI and Toolkit Azure/Microsoft 365 with the assigned work/school accounts before starting. If you cannot assign the model role, the instructor must complete the same Provision task before class; do not seek subscription-wide grants. Installation, capacity approval and permission troubleshooting are **not** included in 25–30 minutes.

Agent Framework runs the model/tool; Agents SDK validates channel tokens; **Agents Toolkit (ATK) owns Provision, Deploy and the Teams app package**. App Service replaces the VM listener. No DevTunnel, GitHub login, container or paid fallback is used.

## 1. Keep your Lab07 context (3 minutes)

Keep this guide in the left course window. In a right VS Code window, open:

```text
C:\Users\Admin\ma-2041\Day2\Lab1-AgentFramework-Extension
```

Trust the supplied folder; if asked to open the parent repository, select **Never**. Copy your Lab07 `.env` and synthetic `data.txt` here. Keep the original lab code unchanged for comparison. Open `expense_agent.py`: it retains `FoundryChatClient`, the `ExpenseClaimAgent` name and `submit_claim`. Local console calls use your Azure CLI identity; the Azure host uses its own system-assigned managed identity, not your credentials. Tool receipts remain visibly simulated and turn-local, not stored claims.

The instructor supplies `env/.env.dev` from `env/.env.dev.example`. Confirm its assigned resource names and copy **only** your Lab07 `PROJECT_ENDPOINT` and `MODEL_DEPLOYMENT_NAME` into the matching fields. No new model is needed. Do not edit generated bot IDs or secrets, and do not share `.env`, `env/.env.dev.user` or configuration screenshots.

## 2. Provision once through ATK (5 minutes estimated)

Select **Terminal > Run Task > 1 Provision Azure expense agent**. Review the assigned subscription/resource group before approving prompts. The task creates the app identity, Linux Python 3.13 **F1** web app with system identity, F0 Azure Bot/Teams channel, private bot settings and a **Foundry User** role assignment on the existing Foundry **project**. It also builds, validates and updates the Teams app package. If the instructor pre-provisioned this project, confirm that task already passed; retain its generated environment and app identity.

**Checkpoint:** Provision finishes without an error. If quota, tenant policy or role assignment fails, stop for the instructor. Do not choose a paid tier, create another model or enable publishing basic authentication. A web app being created does **not** prove its Python runtime/model works.

## 3. Deploy and test in Teams (8 minutes estimated)

Select **Terminal > Run Task > 2 Deploy Azure expense agent**. ATK runs the supplied scoped Azure CLI deployment helper: it packages only application files, deploys with Microsoft Entra authentication while publishing basic auth stays **disabled**, waits for deployment and checks the hosted endpoint. Azure builds dependencies from the unchanged lock file. Do not start a local host or press F5.

**Checkpoint:** the task reports hosted `/health` **200**, the current instruction-file fingerprint, and unauthenticated `/api/messages` **401**. These checks prove liveness and rejection, **not** model or channel success. Any failed check is a stop, not permission to bypass authentication.

In Teams, use **Apps > Manage your apps > Upload an app > Upload a custom app**. Choose `appPackage/build/appPackage.dev.zip`, then select **Add** and open its personal chat. Labels can vary; absent upload means tenant policy needs instructor help.

Send `/help`, then:

```text
Submit an expense claim
```

**Checkpoint:** `/help` replies without a model call. The claim includes the actual tool receipt: **SIMULATED**, **No email was sent**, recipient `expenses@contoso.com`, subject, itemized expenses and correct total from your Lab07 data. Model prose without the receipt does not pass. If access is newly assigned, allow role propagation and retry with the instructor; do not change identities.

## 4. Use Copilot; change an expense behavior (9 minutes estimated)

Open the installed **ExpenseClaimLab** app details and choose **Open with Copilot**. If needed, select it from the **Agents** list in Microsoft 365 Copilot Chat with the same lab account. This is personal installation, **not tenant-wide publication**. Do not use a separate Publish step.

Send `Submit an expense claim` and verify the same simulated receipt. Teams success alone does not pass Copilot.

Now edit **`expense-instructions.txt`**. Add this instruction without removing the simulation rule:

```text
In the simulated email body, group expenses by category, show a subtotal for each
category and a grand total, and finish with: Review required before reimbursement.
```

Save and rerun **2 Deploy Azure expense agent**. Keep the same bot/app identity; code-only changes need no app reinstall or manifest version change. Send `Submit an expense claim` again in **both Teams and Copilot**.

**Checkpoint:** both actual tool receipts now show category subtotals, the grand total and the review sentence, while still saying no email was sent. Compare against your data and the previous receipt. The deployment fingerprint alone does not prove the model followed the changed instructions. If it did not, stop and review the response with the instructor.

## 5. Finish (2 minutes)

The agent runs in Azure, so closing VS Code does not stop it. Remove your personal Teams/Copilot app when instructed. Have the instructor remove only your assigned web app/plan, bot, Entra app/service principal/short-lived secret and project role assignment under the lab cleanup policy. Never delete a shared resource group. Complete Lab07 cleanup only when its project/model are no longer needed.

**Timing boundary:** the steps budget 27 minutes, but F1 cold starts, two cloud builds, role propagation or tenant policy can exceed it. If the class clock runs out, record the unfinished checkpoint; do not claim completion. This is a training prototype, not production hosting or durable claim storage.
