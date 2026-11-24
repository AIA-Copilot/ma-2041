"""ATK lifecycle helper. No login, secret output, publishing credentials or fallback."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import UUID
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ('host.py', 'expense_agent.py', 'expense-instructions.txt', 'data.txt',
           'requirements.txt', 'requirements.lock.txt')


def package(root=ROOT, dest=None):
    dest = dest or root / '.build/deploy.zip'
    for name in PAYLOAD:
        if not (root / name).is_file() or (root / name).is_symlink():
            raise ValueError('Deployment payload missing or symlink: ' + name)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(dest, 'w', ZIP_DEFLATED) as archive:
        for name in PAYLOAD:
            archive.write(root / name, name)
    return dest


def az(*args):
    executable = shutil.which('az')
    if not executable:
        raise RuntimeError('Instructor prerequisite: Azure CLI is not installed.')
    # Never emit CLI stdout/stderr: failed commands can include private settings.
    result = subprocess.run([executable, *args, '--only-show-errors', '-o', 'json'],
                            capture_output=True, text=True, timeout=900)
    if result.returncode:
        raise RuntimeError('Azure CLI step failed. Stop; instructor checks Azure deployment status privately. No paid or basic-auth fallback.')
    return json.loads(result.stdout) if result.stdout.strip() else None


def settings(env=None):
    env = os.environ if env is None else env
    keys = ('AZURE_SUBSCRIPTION_ID', 'AZURE_RESOURCE_GROUP_NAME', 'WEBAPP_NAME', 'BOT_TENANT_ID')
    cfg = {k: env.get(k, '') for k in keys}
    for key, value in cfg.items():
        if not value or '${{' in value or value.startswith('<'):
            raise ValueError('Missing assigned setting: ' + key)
    UUID(cfg['AZURE_SUBSCRIPTION_ID']); UUID(cfg['BOT_TENANT_ID'])
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{1,58}[a-z0-9]', cfg['WEBAPP_NAME']):
        raise ValueError('Use an assigned lowercase Web App name, 3–60 characters.')
    if not re.fullmatch(r'[A-Za-z0-9_.()-]{1,90}', cfg['AZURE_RESOURCE_GROUP_NAME']):
        raise ValueError('Invalid assigned resource group.')
    return cfg


def preflight(cfg):
    version = tuple(int(x) for x in az('version')['azure-cli'].split('.')[:3])
    if version < (2, 48, 1):
        raise RuntimeError('Instructor prerequisite: Azure CLI 2.48.1+ for Entra deployment.')
    account = az('account', 'show', '--subscription', cfg['AZURE_SUBSCRIPTION_ID'])
    if account['tenantId'].lower() != cfg['BOT_TENANT_ID'].lower():
        raise RuntimeError('Azure CLI tenant differs from the assigned bot tenant. Stop.')
    runtimes = az('webapp', 'list-runtimes', '--os', 'linux')
    if 'PYTHON:3.13' not in runtimes and 'PYTHON|3.13' not in runtimes:
        raise RuntimeError('Python 3.13 is unavailable. Stop; no runtime or paid fallback.')


def verify(endpoint, expected_digest, attempts=24):
    # No redirects: an interactive App Service sign-in page is not bot health.
    from urllib.request import HTTPRedirectHandler, build_opener
    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    opener = build_opener(NoRedirect())
    for attempt in range(attempts):
        try:
            with opener.open(endpoint + '/health', timeout=20) as response:
                body = json.load(response)
                if response.status != 200 or body.get('instructions_sha256') != expected_digest:
                    raise ValueError('Hosted instruction digest does not match this deployment.')
            request = Request(endpoint + '/api/messages', data=b'{}',
                              headers={'Content-Type':'application/json'}, method='POST')
            try:
                opener.open(request, timeout=20)
            except HTTPError as error:
                if error.code == 401:
                    return
                raise ValueError('Expected SDK 401 without redirect.') from None
            raise ValueError('Unauthenticated messages were not rejected.')
        except (HTTPError, URLError, TimeoutError, ValueError):
            if attempt == attempts - 1:
                raise RuntimeError('Hosted health/digest/401 verification failed. No model or channel success claimed.') from None
            time.sleep(10)


def deploy(cfg):
    preflight(cfg)
    sub, rg, name = (cfg[k] for k in ('AZURE_SUBSCRIPTION_ID', 'AZURE_RESOURCE_GROUP_NAME', 'WEBAPP_NAME'))
    resource = f'/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Web/sites/{name}'
    base = 'https://management.azure.com' + resource
    for policy in ('scm', 'ftp'):
        result = az('rest', '--method', 'get', '--url', base + '/basicPublishingCredentialsPolicies/' + policy + '?api-version=2024-04-01')
        if result['properties']['allow'] is not False:
            raise RuntimeError('Publishing basic auth must remain disabled. Stop.')
    app = az('webapp', 'show', '--subscription', sub, '--resource-group', rg, '--name', name)
    if not app.get('identity', {}).get('principalId'):
        raise RuntimeError('App Service system identity missing. Run ATK Provision.')
    plan = az('appservice', 'plan', 'show', '--ids', app['serverFarmId'])
    if plan['sku']['name'] != 'F1':
        raise RuntimeError('Only Free F1 is authorized for this lab.')
    archive = package()
    result = az('webapp', 'deploy', '--subscription', sub, '--resource-group', rg, '--name', name,
                '--src-path', str(archive), '--type', 'zip', '--track-status', 'true', '--timeout', '600000')
    # Guard explicit Kudu/ARM failure results even if a CLI returns exit code zero.
    status = str((result or {}).get('status', '')).lower()
    if status == '3' or 'fail' in status or 'cancel' in status:
        raise RuntimeError('Azure reported a failed deployment. Stop; no channel success claimed.')
    endpoint = 'https://' + app['defaultHostName']
    verify(endpoint, hashlib.sha256((ROOT/'expense-instructions.txt').read_bytes()).hexdigest())
    print('Hosted health + exact instruction digest + unauthenticated 401 passed. Now verify the real model in Teams and Copilot.')


if __name__ == '__main__':
    try:
        command = sys.argv[1] if len(sys.argv) > 1 else ''
        if command == 'package':
            package(); print('Allowlisted deployment ZIP built locally.')
        elif command == 'preflight':
            preflight(settings()); print('Azure account and runtime preflight passed; F1 quota/policy still requires provisioning.')
        elif command == 'deploy':
            deploy(settings())
        else:
            raise ValueError('Choose package, preflight or deploy through the supplied ATK tasks.')
    except Exception as error:
        # Unknown exceptions (including process arguments) are deliberately not printed.
        if isinstance(error, (ValueError, RuntimeError)):
            print(str(error), file=sys.stderr)
        else:
            print('Lab operation failed; instructor diagnosis required. No private output printed.', file=sys.stderr)
        sys.exit(1)
