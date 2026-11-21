// Course launcher: never downloads tools or resolves npm/PATH shims.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { spawnSync } = require('node:child_process');
function approvedHost(env = process.env, platform = process.platform) {
  if (platform !== 'win32') throw new Error('Core Tools runtime requires the provider-approved MS4018 Windows VM.');
  const exe = env.DAY1_FUNC_EXE;
  const hash = env.DAY1_FUNC_SHA256;
  if (!exe || !path.win32.isAbsolute(exe) || !/\\func\.exe$/i.test(exe) || /(?:node_modules|devTools)/i.test(exe))
    throw new Error('Provider must set DAY1_FUNC_EXE to the approved MSI-installed func.exe; npm/devTools/PATH launchers are forbidden.');
  if (!/^[a-f0-9]{64}$/i.test(hash || '')) throw new Error('Provider must set DAY1_FUNC_SHA256 after verifying the MSI installation.');
  if (crypto.createHash('sha256').update(fs.readFileSync(exe)).digest('hex') !== hash.toLowerCase())
    throw new Error('Approved Core Tools executable hash mismatch. Stop for provider review.');
  return exe;
}
function main() {
  const exe = approvedHost();
  const version = spawnSync(exe, ['--version'], { encoding: 'utf8', shell: false });
  if (version.status !== 0 || version.stdout.trim() !== '4.16.1') throw new Error('Approved Core Tools must report exactly 4.16.1.');
  const args = process.argv.slice(2);
  if (args.length === 1 && args[0] === '--version') { console.log(version.stdout.trim()); return; }
  const result = spawnSync(exe, args, { stdio: 'inherit', shell: false });
  if (result.error) throw result.error;
  process.exitCode = result.status === null ? 1 : result.status;
}
module.exports = { approvedHost };
if (require.main === module) { try { main(); } catch (error) { console.error(error.message); process.exitCode = 1; } }
