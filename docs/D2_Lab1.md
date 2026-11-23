# Day 2 · Lab 1 — Extend your Python agent to Teams and Copilot

Complete this lab immediately after [official Lab07](https://microsoftlearning.github.io/mslearn-ai-agents/Instructions/Exercises/07-agent-framework.html). Keep the original lab resources. Run the channel steps only after the instructor confirms the assigned VM and tenant are prepared.

**Outcome:** the same `ExpenseClaimAgent`, Foundry project/model and synthetic `data.txt` can prepare an itemized claim and visibly return its **SIMULATED** email through Teams, then Microsoft 365 Copilot. No email, payment or real claim is submitted.

**Three responsibilities:** Agent Framework runs the model and `submit_claim`; Agents SDK authenticates and routes channel activities; the installed VS Code Agents Toolkit manages identities, bot registration and app package lifecycle. DevTunnel only transports HTTPS to the VM. It does not replace SDK authentication.

## 1. Keep your Lab07 work; add the supplied host

On the separate AI-3026 VM, first clone and trust the course at `C:\Users\Admin\ma-2041` using the repository README steps 1–12 if it is not already present.

Complete Lab07 first, including its console run. **Defer its cleanup.** Keep your completed `agent-framework.py` unchanged for comparison. Keep these instructions open in the **left course window**. In the **right project window**, select **File > Open Folder** and open:

```text
C:\Users\Admin\ma-2041\Day2\Lab1-AgentFramework-Extension
```

If the right window is closed, select **File > New Window** first. If VS Code asks to open the parent Git repository, select **Never**. Copy your Lab07 `.env` and synthetic `data.txt` here (do not copy credentials into chat or screenshots). Retain `PROJECT_ENDPOINT` and `MODEL_DEPLOYMENT_NAME` exactly; do not create another model.

Compare your completed `process_expenses_data` with `expense_agent.py`: the same `FoundryChatClient`, `AzureCliCredential`, named `Agent`, expense instructions and `submit_claim` tool remain. Console input moves to `console.py`. The tool now returns its simulated email instead of only printing it; the host includes that receipt in its channel response. Instructions explicitly prohibit claiming real email delivery. Each request is independent, as in the original one-shot console lab; this extension does not add shared chat memory.

Open the Terminal in the **right project window**:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.lock.txt
python -m pytest -q
az login
python console.py
```

Select the assigned lab work/school account for Azure, then enter `Submit an expense claim` in the console. If script activation is blocked, use `.\.venv\Scripts\python.exe` directly; do not change machine-wide execution policy.

**Checkpoint:** tests pass without contacting Foundry. Separately, the console uses your actual existing model and shows an itemized **SIMULATED** receipt. A test pass is not proof of model or channel access.

## 2. Prepare the assigned Microsoft identity and tunnel

Use VS Code's installed **Microsoft 365 Agents Toolkit** extension, not a Python creation wizard and not a separately installed Toolkit CLI. Sign in to Azure and Microsoft 365 with the assigned lab accounts. No GitHub account, GitHub Copilot subscription or VS Code Ports/GitHub route is used.

Check DevTunnel in PowerShell:

```powershell
devtunnel --version
devtunnel user login
devtunnel user show
```

Choose the **lab work/school Microsoft account**. If browser sign-in is unavailable, the supported Microsoft device-code alternative is:

```powershell
devtunnel user login -d
```

Never use `-g` (that selects GitHub). Login alone does **not** start a tunnel. If tenant consent or policy blocks sign-in, stop and ask the instructor; do not switch to a personal or GitHub account.

Copy the supplied nonsecret environment template:

```powershell
Copy-Item env/.env.local.example env/.env.local
```

Use the instructor's assigned subscription, resource group, unique bot service name and approved website/privacy/terms URLs. Do not invent policy URLs. Leave generated bot IDs/secrets to Toolkit. Keep `env/.env.local.user` and `.env.channel` private.

**Checkpoint:** instructor confirms the extension supports this supplied v1.12 lifecycle and v1.30 manifest; assigned accounts may create the single-tenant Entra application/service principal, Azure Bot registration and Teams app, and may use custom apps and personal-scope Copilot custom-engine agents. Installation alone is not proof. No extra GitHub entitlement is required; Microsoft 365 tenant availability/permissions still apply.

## 3. Connect the authenticated Python host to Teams

Only after the instructor approves this channel run, choose **Terminal > Run Task** in order:

1. **1 Start approved DevTunnel** — Toolkit writes the HTTPS `BOT_ENDPOINT` and `BOT_DOMAIN` to the local environment. It exposes transport on port 3978; SDK authentication stays enabled.
2. **2 Provision assigned lab resources** — creates the Teams app, single-tenant Entra app and service principal (short-lived secret), F0 Azure Bot plus Teams channel, then builds/validates/updates the app package. It creates no hosted compute or new model. Verify the selected assigned resource group before accepting prompts.
3. **3 Write private channel configuration** — generates `.env.channel`; it does not deploy code to Azure or overwrite your Lab07 `.env`.
4. Use **Python: Select Interpreter** to select this folder's `.venv`. In **Run and Debug**, choose **4 Authenticated Python host** and start it. Alternatively run `python host.py` in the activated terminal.

In a second terminal, check the unauthenticated route:

```powershell
curl.exe -i -X POST http://127.0.0.1:3978/api/messages -H "Content-Type: application/json" -d "{}"
```

**Checkpoint:** HTTP **401**, not a model response. Missing bot configuration must stop startup. Never disable authentication to fix a channel problem.

In Teams, use **Apps > Manage your apps > Upload an app > Upload a custom app** (labels may vary) and select `appPackage/build/appPackage.local.zip`, then select **Add**. Open its personal chat. If upload is unavailable, stop for tenant policy support.

Send `/help`, then:

```text
Submit an expense claim
```

**Checkpoint:** `/help` replies without a model call. The claim response includes **SIMULATED**, **No email was sent**, recipient, subject, itemized expenses and total from the same Lab07 data. A model claim without the actual tool receipt does not pass; stop and inspect with the instructor. Keep the VM host and tunnel running for the next step.

## 4. Use the same agent in Copilot; observe a code change

The supplied package already declares this bot as a custom engine agent. After the Teams checkpoint, open the installed **ExpenseClaimLab** app details and choose **Open with Copilot**. Select **ExpenseClaimLab** in Microsoft 365 Copilot Chat. If needed, open Microsoft 365 Copilot and select it from the **Agents** list using the same lab account. Keep the host and tunnel running.

This is personal app installation, not tenant-wide publication; there is no separate Toolkit Publish step. If the agent is unavailable, ask the instructor to check installation, tenant policy and Copilot access.

Send `/about`, then `Submit an expense claim`. Verify the same visible simulated receipt. In `expense_agent.py`, change `ExpenseClaimAgent v1` to `ExpenseClaimAgent v2`, save, stop and restart **only the Python host**, and send `/about` again in Teams and Copilot.

**Checkpoint:** both channels show `v2`. Python code runs on your VM; this text-only change needs no manifest rebuild. If you alter the manifest instead, increment its app version, rebuild/update the package through Toolkit, and upload/install the updated package.

## 5. Stop and clean up

Stop the Python debug session and terminate the DevTunnel task using **Terminal > Terminate Task**. Confirm the tunnel is no longer reachable. Remove the personal Teams/Copilot app and have the instructor remove the extension's bot registration, Entra app/service principal/secret and assigned lab resources under the lab cleanup policy. Do not delete a shared resource group. Then perform the original Lab07 cleanup when the instructor confirms the model/project are no longer needed.

For production, a stable HTTPS host such as App Service or Azure Container Apps replaces VM + tunnel. Identity, authentication, state retention, secret storage and operational controls still need production design; deploying that host is outside this exercise.
