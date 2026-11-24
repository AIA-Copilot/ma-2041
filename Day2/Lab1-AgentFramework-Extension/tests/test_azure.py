import importlib.util
from pathlib import Path
import zipfile
import pytest
from aiohttp.test_utils import TestClient, TestServer
from test_candidate import CONFIG
ROOT = Path(__file__).resolve().parents[1]

def test_cloud_credential_selection(monkeypatch):
    import expense_agent as e
    assert hasattr(e, 'model_credential'), 'Explicit managed identity selection missing'
    monkeypatch.delenv('WEBSITE_INSTANCE_ID', raising=False)
    assert type(e.model_credential()).__name__ == 'AzureCliCredential'
    monkeypatch.setenv('WEBSITE_INSTANCE_ID', 'synthetic')
    assert type(e.model_credential()).__name__ == 'ManagedIdentityCredential'

def test_expense_instructions_are_editable():
    assert (ROOT / 'expense-instructions.txt').exists(), 'Meaningful instruction file missing'
    text = (ROOT / 'expense-instructions.txt').read_text()
    assert 'itemized' in text and 'simulate' in text

@pytest.mark.asyncio
async def test_health_does_not_disable_message_auth():
    from host import create_app
    async with TestClient(TestServer(create_app(CONFIG))) as client:
        assert (await client.get('/health')).status == 200
        assert (await client.post('/api/messages', json={})).status == 401

def test_startup_binding():
    import host
    assert hasattr(host, 'startup_options'), 'App Service startup missing'
    assert host.startup_options({}) == {'host':'0.0.0.0','port':8000,'access_log':None}
    assert host.startup_options({'PORT':'8181'})['port'] == 8181
    with pytest.raises(ValueError): host.startup_options({'PORT':'invalid'})

def load_ops():
    path = ROOT / 'scripts/azure_lab.py'
    assert path.exists(), 'ATK deployment implementation missing'
    spec = importlib.util.spec_from_file_location('azure_lab', path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module

def test_zip_allowlist_and_missing_file(tmp_path):
    ops = load_ops()
    for name in ops.PAYLOAD:
        (tmp_path/name).write_text('synthetic')
    for name in ['.env', '.env.channel', 'secret.txt']:
        (tmp_path/name).write_text('SECRET')
    (tmp_path/'.venv').mkdir(); (tmp_path/'.venv/secret').write_text('SECRET')
    dest = tmp_path/'deploy.zip'
    ops.package(tmp_path, dest)
    with zipfile.ZipFile(dest) as z:
        assert set(z.namelist()) == set(ops.PAYLOAD)
        assert all(b'SECRET' not in z.read(n) for n in z.namelist())
    (tmp_path/'host.py').unlink()
    with pytest.raises(ValueError): ops.package(tmp_path, dest)

def test_cli_failure_does_not_leak(monkeypatch):
    ops = load_ops()
    from types import SimpleNamespace
    monkeypatch.setattr(ops.shutil, 'which', lambda n: 'az')
    monkeypatch.setattr(ops.subprocess, 'run', lambda *a,**k: SimpleNamespace(returncode=1,stdout='SECRET',stderr='SECRET'))
    with pytest.raises(RuntimeError) as exc: ops.az('webapp','deploy')
    assert 'SECRET' not in str(exc.value)

def test_wiring_and_security():
    import yaml
    lifecycle=yaml.safe_load((ROOT/'m365agents.yml').read_text())
    assert 'provision' in lifecycle, 'Azure provision lifecycle missing'
    assert lifecycle['deploy'][0]['uses']=='script'
    assert 'deploy' in lifecycle['deploy'][0]['with']['run']
    bicep=(ROOT/'infra/azure.bicep').read_text()
    for expected in ['F1','PYTHON|3.13','SystemAssigned','SCM_DO_BUILD_DURING_DEPLOYMENT','python host.py','allow: false','enabled: false']:
        assert expected in bicep
    role=(ROOT/'infra/model-role.bicep').read_text()
    assert '53ca6127-db72-4b80-b1b0-d745d6d5456d' in role
    assert 'scope: project' in role


def config():
    return {'AZURE_SUBSCRIPTION_ID':'11111111-1111-4111-8111-111111111111',
            'BOT_TENANT_ID':'22222222-2222-4222-8222-222222222222',
            'AZURE_RESOURCE_GROUP_NAME':'expense-lab', 'WEBAPP_NAME':'expense-lab-test'}

@pytest.mark.parametrize('field,value', [('WEBAPP_NAME','bad;command'), ('BOT_TENANT_ID','bad'), ('AZURE_RESOURCE_GROUP_NAME','')])
def test_bad_settings_refused(field, value):
    ops = load_ops()
    with pytest.raises(ValueError): ops.settings({**config(), field:value})

@pytest.mark.parametrize('failure', ['version','tenant','runtime'])
def test_preflight_fails_before_deployment(monkeypatch, failure):
    ops=load_ops(); calls=[]
    def fake(*args):
        calls.append(args)
        if args[0]=='version': return {'azure-cli':'2.47.0' if failure=='version' else '2.80.0'}
        if args[0]=='account': return {'tenantId':'wrong' if failure=='tenant' else config()['BOT_TENANT_ID']}
        if args[:2]==('webapp','list-runtimes'): return [] if failure=='runtime' else ['PYTHON:3.13']
        pytest.fail('Unexpected cloud operation')
    monkeypatch.setattr(ops,'az',fake)
    with pytest.raises(RuntimeError): ops.preflight(config())
    assert not any('deploy' in call for call in calls)

@pytest.mark.parametrize('failure', ['basic','identity','paid'])
def test_deploy_guard_refuses_before_upload(monkeypatch, failure):
    ops=load_ops(); calls=[]
    monkeypatch.setattr(ops,'preflight',lambda c: None)
    def fake(*args):
        calls.append(args)
        if args[0]=='rest': return {'properties':{'allow':failure=='basic'}}
        if args[:2]==('webapp','show'):
            return {'identity':{} if failure=='identity' else {'principalId':'synthetic'}, 'serverFarmId':'synthetic'}
        if args[:3]==('appservice','plan','show'): return {'sku':{'name':'B1' if failure=='paid' else 'F1'}}
        pytest.fail('Unexpected upload')
    monkeypatch.setattr(ops,'az',fake)
    with pytest.raises(RuntimeError): ops.deploy(config())
    assert not any(call[:2]==('webapp','deploy') for call in calls)

@pytest.mark.asyncio
async def test_edit_is_read_by_real_agent(monkeypatch, tmp_path):
    import expense_agent as agent
    from test_candidate import MockFoundry
    monkeypatch.setattr(agent, '__file__', str(tmp_path/'expense_agent.py'))
    instruction='Group by category, show subtotals. Review required before reimbursement.'
    (tmp_path/'expense-instructions.txt').write_text(instruction)
    class CaptureOptions(MockFoundry):
        async def _inner_get_response(self, *, messages, stream, options, **kwargs):
            self.last_options = options
            return await super()._inner_get_response(messages=messages, stream=stream, options=options, **kwargs)
    client=CaptureOptions()
    await agent.process_expenses_data('submit', 'synthetic', client=client)
    assert client.last_options['instructions'] == instruction

@pytest.mark.asyncio
@pytest.mark.parametrize('method,path', [('post','/health'),('get','/health/'),('get','/api/messages')])
async def test_health_bypass_is_exact(method,path):
    from host import create_app
    async with TestClient(TestServer(create_app(CONFIG))) as client:
        response=await getattr(client,method)(path)
        assert response.status==401

def test_deploy_exact_scope_and_no_credentials(monkeypatch, tmp_path):
    ops=load_ops(); calls=[]; verified=[]
    monkeypatch.setattr(ops,'preflight',lambda c: None)
    monkeypatch.setattr(ops,'package',lambda: tmp_path/'deploy.zip')
    monkeypatch.setattr(ops,'verify',lambda *a: verified.append(a))
    def fake(*args):
        calls.append(args)
        if args[0]=='rest': return {'properties':{'allow':False}}
        if args[:2]==('webapp','show'):
            return {'identity':{'principalId':'synthetic'}, 'serverFarmId':'synthetic', 'defaultHostName':'synthetic.azurewebsites.net'}
        if args[0]=='appservice': return {'sku':{'name':'F1'}}
        if args[:2]==('webapp','deploy'): return {'status':4}
        pytest.fail('Unexpected command')
    monkeypatch.setattr(ops,'az',fake)
    ops.deploy(config())
    upload=next(args for args in calls if args[:2]==('webapp','deploy'))
    assert upload[upload.index('--subscription')+1]==config()['AZURE_SUBSCRIPTION_ID']
    assert upload[upload.index('--resource-group')+1]=='expense-lab'
    assert '--track-status' in upload and '--src-path' in upload
    assert not any('password' in arg.lower() or 'publishingcredentials/list' in arg.lower() for args in calls for arg in args)
    assert verified[0][0]=='https://synthetic.azurewebsites.net'


def test_cli_nonzero_status_in_success_output_is_refused(monkeypatch, tmp_path):
    ops=load_ops()
    monkeypatch.setattr(ops,'preflight',lambda c: None)
    monkeypatch.setattr(ops,'package',lambda: tmp_path/'deploy.zip')
    monkeypatch.setattr(ops,'verify',lambda *a: pytest.fail('Must not verify/claim a failed deployment'))
    def fake(*args):
        if args[0]=='rest': return {'properties':{'allow':False}}
        if args[:2]==('webapp','show'): return {'identity':{'principalId':'synthetic'},'serverFarmId':'synthetic','defaultHostName':'synthetic.invalid'}
        if args[0]=='appservice': return {'sku':{'name':'F1'}}
        return {'status':3}
    monkeypatch.setattr(ops,'az',fake)
    with pytest.raises(RuntimeError): ops.deploy(config())

@pytest.mark.parametrize('behavior', ['ok','wrong-digest','anonymous','redirect'])
def test_real_http_verifier(behavior):
    import json, threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    ops=load_ops()
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if behavior=='redirect':
                self.send_response(302); self.send_header('Location','/login'); self.end_headers(); return
            self.send_response(200); self.end_headers()
            self.wfile.write(json.dumps({'instructions_sha256':'wrong' if behavior=='wrong-digest' else 'expected'}).encode())
        def do_POST(self):
            self.send_response(200 if behavior=='anonymous' else 401); self.end_headers()
        def log_message(self,*args): pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        endpoint=f'http://127.0.0.1:{server.server_port}'
        if behavior=='ok': ops.verify(endpoint,'expected',attempts=1)
        else:
            with pytest.raises(RuntimeError): ops.verify(endpoint,'expected',attempts=1)
    finally:
        server.shutdown();server.server_close();thread.join()
