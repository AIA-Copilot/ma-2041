"""Offline contract for documented custom-engine personal installation, not tenant proof."""
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_local_lifecycle_packages_without_publish():
    lifecycle = yaml.safe_load((ROOT / 'm365agents.yml').read_text())
    assert 'publish' not in lifecycle, 'Personal package installation does not need Publish'
    steps = lifecycle['provision']
    actions = [s['uses'] for s in steps]
    assert actions[-3:] == ['teamsApp/zipAppPackage', 'teamsApp/validateAppPackage', 'teamsApp/update']
    assert steps[-3]['with']['outputZipPath'] == './appPackage/build/appPackage.${{TEAMSFX_ENV}}.zip'
    assert all('publish' not in s['uses'].lower() for phase in ('provision', 'deploy') for s in lifecycle[phase])


def test_same_bot_is_declared_for_personal_teams_and_copilot():
    manifest = json.loads((ROOT / 'appPackage/manifest.json').read_text())
    bot, = manifest['bots']
    agent, = manifest['copilotAgents']['customEngineAgents']
    assert agent == {'type': 'bot', 'id': bot['botId']}
    assert bot['botId'] == '${{BOT_ID}}'
    assert set(bot['scopes']) == {'personal', 'copilot'}
    assert 'declarativeAgents' not in manifest['copilotAgents']
    assert tuple(map(int, manifest['manifestVersion'].split('.'))) >= (1, 21)


def test_guide_installs_package_then_opens_copilot_without_publish_gate():
    guide = (ROOT / 'LEARNER-EXTENSION.md').read_text()
    assert 'Upload a custom app' in guide and 'select **Add**' in guide
    assert 'appPackage/build/appPackage.dev.zip' in guide
    assert '**Open with Copilot**' in guide
    assert guide.index('## 3.') < guide.index('## 4.') < guide.index('**Open with Copilot**')
    for obsolete in ('copilotAgent/publish', 'Publish CodeLens', 'Known source blocker', 'local Publish selection'):
        assert obsolete not in guide
    assert 'tenant-wide publication' in guide
