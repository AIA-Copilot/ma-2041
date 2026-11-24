# Microsoft 365 agent development — start here

Use the provided MS-4018 virtual lab machines for Day 1, and AI-3026 virtual labs for Day 2.

## Before class

Use the Microsoft 365 account supplied with your lab. Sign-in requirements depend on the tenant's policy. The optional connector exercise includes its own administrator-permission and Microsoft Authenticator preparation.

## Quick start — start the VM and open Lab 1

1. Start the VM lab.
2. In the VM, open **Visual Studio Code**.
3. Select **View > Command Palette**.
4. Type **Git Clone** and select **Git: Clone**.
5. Paste `https://github.com/AIA-Copilot/ma-2041.git` into the repository URL box.
6. Select **Clone from URL** and press **Enter**. **Do not select Clone from GitHub.**
7. In the folder-selection dialog, stay in the **Admin** folder that opens (`C:\Users\Admin`).
8. Select **Select as Repository Destination**. Do not create a new folder; Git will create the `ma-2041` folder for you.
9. Wait for cloning to finish. When VS Code asks whether to open the repository, select **Open**.
10. In the **Restricted Mode** banner, select **Manage**.
11. In **Workspace Trust**, select **Trust** for this course repository. Confirm that the page says **You trust this folder**, then close the Workspace Trust tab or dialog.
12. Ignore or close any other VS Code notifications.
13. Close the **Welcome** page and any other open editor tabs.
14. In Explorer, expand the **docs** folder.
15. Right-click **D1_Lab1.md** and select **Open in Preview**.
16. Follow the lab instructions in the preview.

**Checkpoint:** the course repository is open and trusted, and you can read this lab in VS Code Preview. Git creates one `ma-2041` folder directly inside **Admin**. The course repository is `C:\Users\Admin\ma-2041` on the supplied VM.

**Continue in Lab 1.** Follow its Toolkit installation, start the shared Day 1 preparation script, and continue the Copilot access steps while preparation runs.

## Check Day 1 setup

After the Lab 1 preparation finishes, run `.\scripts\Test-Day1.ps1` in the course-window Terminal. It must report **DAY 1 LOCAL TOOL CHECKS PASSED (All)**. This checks the local TypeSpec compiler and WIQD, not tenant permissions or agent responses. The required setup does not install Azure Functions or Azurite.

If a check fails, use `.\scripts\Prepare-Day1.ps1 -Target Lab3` or `-Target Lab4` for that lab. Wait for completion before retrying. Do not run preparation scripts in parallel.

## Lab guides

In VS Code, right-click a guide and select **Open in Preview**.

### Day 1 — MS-4018 virtual lab machines

1. [Lab 1 — First declarative agent](docs/D1_Lab1.md)
2. [Lab 2 — Zava Currency Converter: API, card and MCP](docs/D1_Lab2.md)
3. [Lab 3 — Author an agent with TypeSpec](docs/D1_Lab3.md)
4. [Lab 4 — Build an agent with an editable WIQD script](docs/D1_Lab4.md)

**Optional:** [Index Zava policies with a connector](docs/D1_Optional_Connector.md). This separate exercise installs its own tools and needs administrator consent. It is not a prerequisite for Labs 3 or 4.

### Day 2 — AI-3026 virtual labs

Complete Microsoft's **AI-3026 Agent Framework lab** first and defer its cleanup. Then follow the single [Python agent extension — Teams and Copilot](docs/D2_Lab1.md).

For PDF copies, open the **Labs** folder.
