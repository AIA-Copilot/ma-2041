"""Source-grounded R1-R6 regressions; offline implementation evidence only."""
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def load(relative, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_r1_starter_cli_consumes_learner_payloads(monkeypatch, capsys):
    mod = load('starters/lab5/connector_client.py', 'starter_regression')
    monkeypatch.setattr(mod, 'schema_payload', lambda: {'properties': []})
    monkeypatch.setattr(mod, 'transform', lambda a: {'id': 'LEARNER_SENTINEL', 'acl': [{'value': 'OnlyLearnerGroup'}]})
    assert mod.main(['plan']) == 0
    assert 'LEARNER_SENTINEL' in capsys.readouterr().out
    assert mod.main(['ingest']) == 0
    output = capsys.readouterr().out
    assert 'LEARNER_SENTINEL' in output and '[DRY RUN] not sent' in output
    monkeypatch.setattr(mod, 'schema_payload', lambda: {'properties': [], 'learnerSchema': 'SCHEMA_SENTINEL'})
    mod.main(['register-schema'])
    assert 'SCHEMA_SENTINEL' in capsys.readouterr().out
    monkeypatch.setattr(mod, 'connection_payload', lambda: {'id': 'LEARNER_CONNECTION'})
    mod.main(['create-connection'])
    assert 'LEARNER_CONNECTION' in capsys.readouterr().out


def test_r2_graph_schema_method_and_acl(capsys):
    mod = load('solutions/lab5/connector_client.py', 'connector_regression')
    mod.cmd_register_schema(False)
    assert 'PATCH https://graph.microsoft.com/v1.0/external/connections/' in capsys.readouterr().out
    acl = mod.build_acl({'acl': ['hr-confidential']})
    assert acl == [{'type': 'externalGroup', 'value': 'contosohrconfidential', 'accessType': 'grant'}]
    assert mod.build_acl({'acl': []}) == []
    for item in mod.items_to_ingest():
        for entry in item['acl']:
            assert entry['value'].isascii() and entry['value'].isalnum()
            assert set(entry) == {'type', 'value', 'accessType'}
            assert entry['type'] == 'externalGroup'



def test_r4_apikey_list_public_only_and_openapi_parity(monkeypatch):
    mod = load('solutions/lab4/app.py', 'api_regression')
    monkeypatch.setattr(mod, 'API_KEY', 'synthetic-test-key')
    client = mod.app.test_client()
    path = '/secure/apikey/tickets'
    assert client.get(path).status_code == 401
    assert client.get(path, headers={'X-API-Key': 'wrong'}).status_code == 401
    response = client.get(path, headers={'X-API-Key': 'synthetic-test-key'})
    assert response.status_code == 200
    body = response.get_json()
    assert {r['id'] for r in body['value']} == {r['id'] for r in mod.load_tickets() if not r.get('restricted')}
    assert body['count'] == len(body['value'])
    for mode in ('apikey', 'oauth'):
        doc = json.loads((ROOT / f'solutions/lab4/appPackage/openapi.{mode}.json').read_text())
        for route, operations in doc['paths'].items():
            import re
            flask_route = re.sub(r'\{[^}]+\}', '<ticket_id>', route)
            rules = [r for r in mod.app.url_map.iter_rules() if r.rule == flask_route]
            assert rules, route
            for method in operations.keys() & {'get', 'post', 'patch', 'delete', 'put'}:
                assert method.upper() in rules[0].methods


def test_r5_channel_claims_never_grant_human_identity(monkeypatch):
    from common import principals as p
    monkeypatch.setenv(p.IDENTITY_MODE_ENV, 'channel')
    for claims in ({'sub': 'dave.hr'}, {'preferred_username': 'dave.hr', 'groups': ['hr-confidential']}, {'appid': 'bot', 'aud': 'channel'}):
        ctx = SimpleNamespace(identity=SimpleNamespace(claims=claims), activity=SimpleNamespace(channel_data={p.INJECTED_PRINCIPAL_KEY: 'dave.hr'}))
        principal = p.resolve_principal(ctx)
        assert principal == p.ANONYMOUS
        assert not p.authorize_article(principal, {'acl': ['hr-confidential']})
        assert p.principal_from_verified_claims(claims) == p.ANONYMOUS


def test_r6_lab4_loads_common_env(monkeypatch, tmp_path):
    from common import config
    env = tmp_path / '.env'
    env.write_text('ENTRA_ISSUER=https://synthetic.invalid/\nENTRA_AUDIENCE=synthetic-audience\nLAB4_API_KEY=synthetic-only\n')
    monkeypatch.setattr(config, 'ENV_FILE', env)
    monkeypatch.setattr(config, '_loaded', False)
    for key in ('ENTRA_ISSUER', 'ENTRA_AUDIENCE', 'LAB4_API_KEY'):
        monkeypatch.delenv(key, raising=False)
    mod = load('solutions/lab4/token_validation.py', 'token_regression')
    assert mod.expected_issuer() == 'https://synthetic.invalid/'
    assert mod.expected_audience() == 'synthetic-audience'
    app = load('solutions/lab4/app.py', 'config_app_regression')
    assert app.API_KEY == 'synthetic-only'


def test_connector_unknown_group_fails_closed():
    import pytest
    mod = load('solutions/lab5/connector_client.py', 'unknown_group_regression')
    with pytest.raises(KeyError):
        mod.build_acl({'acl': ['unapproved-group']})
    with pytest.raises(TypeError):
        mod.EXTERNAL_GROUP_IDS['hr-confidential'] = 'contosopublic'


def test_node_minimum_matches_locked_compiler(monkeypatch):
    import subprocess
    import shutil
    mod = load('starters/lab0/preflight.py', 'preflight_regression')
    lock = json.loads((ROOT/'starters/lab1/package-lock.json').read_text())
    assert lock['packages']['node_modules/@typespec/compiler']['engines']['node'] == '>=22.0.0'
    monkeypatch.setattr(shutil, 'which', lambda _: 'synthetic-node')
    for version, expected in [('v20.19.0', 'FAIL'), ('v22.0.0', 'PASS'), ('v24.0.0', 'PASS'), ('unknown', 'FAIL')]:
        monkeypatch.setattr(subprocess, 'run', lambda *a, v=version, **kw: SimpleNamespace(stdout=v, stderr='', returncode=0))
        assert mod.check_cmd_version('Node.js', ['node', '--version'])['status'] == expected
