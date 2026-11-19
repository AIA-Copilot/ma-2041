"""
Lab 0 preflight check for MA-2041.

Checks what CAN be verified locally. Explicitly refuses to infer tenant
developer permissions (app upload, connector consent, OAuth app registration)
from the mere presence of a Copilot/admin license on this machine - those are
separate, unverifiable-from-here items and are reported as NOT EXECUTED.

Run: python starters\\lab0\\preflight.py
"""
import importlib.util
import json
import shutil
import subprocess
import sys


def check_cmd_version(name, cmd):
    path = shutil.which(cmd[0])
    if not path:
        return {"check": name, "status": "FAIL", "detail": f"'{cmd[0]}' not found on PATH"}
    try:
        # .cmd/.bat shims (npm, tsp, etc.) on Windows need shell=True to execute.
        use_shell = sys.platform == "win32"
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=15, shell=use_shell)
        version = (out.stdout or out.stderr).strip().splitlines()[0] if (out.stdout or out.stderr) else "unknown"
        if out.returncode != 0:
            return {"check": name, "status": "FAIL", "detail": version, "path": path}
        if name == "Node.js":
            import re
            match = re.fullmatch(r"v?(\d+)\.\d+\.\d+.*", version)
            if not match or int(match.group(1)) < 22:
                return {"check": name, "status": "FAIL", "detail": "Node 22+ required; found " + version, "path": path}
        return {"check": name, "status": "PASS", "detail": version, "path": path}
    except Exception as e:
        return {"check": name, "status": "FAIL", "detail": str(e)}


def check_python_module(name, module):
    spec = importlib.util.find_spec(module)
    return {"check": name, "status": "PASS" if spec else "FAIL",
            "detail": "importable" if spec else f"pip install {module} missing"}


def check_vscode():
    path = shutil.which("code")
    return {"check": "VS Code CLI ('code')", "status": "PASS" if path else "WARN",
            "detail": path or "not on PATH - VS Code may still be installed, just not shimmed to PATH"}


def check_agents_toolkit_extension():
    code_path = shutil.which("code")
    if not code_path:
        return {"check": "M365 Agents Toolkit extension", "status": "SKIP", "detail": "VS Code CLI unavailable, cannot query extensions"}
    try:
        out = subprocess.run(["code", "--list-extensions"], capture_output=True, text=True, timeout=20,
                              shell=(sys.platform == "win32"))
        exts = out.stdout.lower()
        found = "teamsdevapp.ms-teams-vscode-extension" in exts or "m365-agents-toolkit" in exts
        return {"check": "M365 Agents Toolkit extension", "status": "PASS" if found else "FAIL",
                "detail": "found in installed extensions" if found else "not found - install 'Microsoft 365 Agents Toolkit' from the VS Code marketplace"}
    except Exception as e:
        return {"check": "M365 Agents Toolkit extension", "status": "WARN", "detail": str(e)}


def unverifiable_tenant_items():
    """
    These CANNOT be checked from a developer workstation and are NOT
    inferred from Copilot/admin license visibility. They require an actual
    sign-in + action attempt against the target tenant.
    """
    return [
        {"check": "Custom app upload permission (Teams admin center / M365 admin)", "status": "NOT EXECUTED",
         "detail": "Requires sign-in to the target tenant and an actual upload attempt. Not inferable from license."},
        {"check": "Declarative agent / plugin registration consent", "status": "NOT EXECUTED",
         "detail": "Requires tenant admin or end-user consent flow to be exercised live."},
        {"check": "Graph connector creation permission", "status": "NOT EXECUTED",
         "detail": "Requires Copilot connector admin role in the target tenant, verified only by attempting creation."},
        {"check": "OAuth app registration in tenant IdP", "status": "NOT EXECUTED",
         "detail": "Requires an actual app registration step in Entra ID or equivalent."},
        {"check": "Dev tunnel / ngrok outbound reachability from tenant", "status": "NOT EXECUTED",
         "detail": "Requires a live tunnel plus an inbound test call from Teams/Copilot."},
        {"check": "Provided MS-4018 lab environment availability", "status": "NOT EXECUTED",
         "detail": "Use the provided MS-4018 virtual lab for Day 1. This local check does not verify provider access."},
    ]


def main():
    results = []
    results.append(check_cmd_version("Python", [sys.executable, "--version"]))
    results.append(check_cmd_version("Node.js", ["node", "--version"]))
    results.append(check_cmd_version("npm", ["npm", "--version"]))
    results.append(check_vscode())
    results.append(check_agents_toolkit_extension())
    results.append(check_python_module("flask importable", "flask"))
    results.append(check_python_module("pytest importable", "pytest"))
    results.append(check_python_module("jwt (pyjwt) importable", "jwt"))

    local_checks = results
    tenant_items = unverifiable_tenant_items()

    print("=== MA-2041 Lab 0 Preflight ===\n")
    print("-- Local workstation checks (actually executed) --")
    for r in local_checks:
        print(f"[{r['status']:4}] {r['check']}: {r['detail']}")

    print("\n-- Tenant/permission items (NOT inferred, NOT executed here) --")
    for r in tenant_items:
        print(f"[{r['status']}] {r['check']}: {r['detail']}")

    report = {"local_checks": local_checks, "tenant_items": tenant_items}
    with open("preflight_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print("\nWrote preflight_report.json")

    hard_fail = any(r["status"] == "FAIL" for r in local_checks if r["check"] in ("Python", "Node.js"))
    sys.exit(1 if hard_fail else 0)


if __name__ == "__main__":
    main()
