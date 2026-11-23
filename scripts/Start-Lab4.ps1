# Prepare the Lab 4 project. Prerequisites must already be installed.
$ErrorActionPreference = 'Stop'
$utf8 = New-Object Text.UTF8Encoding($false)
$root = Split-Path $PSScriptRoot -Parent
$project = Join-Path $env:USERPROFILE 'AgentsToolkitProjects\ZavaTravelWIQD'
$lab1 = Join-Path $env:USERPROFILE 'AgentsToolkitProjects\ZavaLab1\appPackage\declarativeAgent.json'
$assets = Join-Path $root 'Day1\Lab4-WIQD\assets'
$currency = Join-Path $root 'Day1\Lab2-CurrencyConverter\currency-plugin.mcp.json'
$wiqd = Join-Path $root 'tools\wiqd-1.0.0\node_modules\.bin\wiqd.cmd'

if (-not (Test-Path -LiteralPath $wiqd)) { throw 'Complete Prepare-Day1.ps1 before starting Lab 4.' }
. (Join-Path $PSScriptRoot 'Use-Node.ps1') -Version 24
$version = (& $wiqd --version | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or $version -ne '1.0.0') { throw 'This lab requires the prepared WIQD 1.0.0 installation.' }
$code = Get-Command code.cmd -CommandType Application -ErrorAction Stop | Select-Object -First 1
if (-not (Test-Path -LiteralPath $lab1)) { throw 'Open your working ZavaLab1 project and complete Lab 3 first.' }
$sourceAgent = Get-Content -LiteralPath $lab1 -Raw | ConvertFrom-Json
$connections = @($sourceAgent.capabilities | Where-Object { $_.name -eq 'GraphConnectors' } | ForEach-Object { $_.connections })
if ($connections.Count -ne 1) { throw 'Expected one GraphConnectors connection in the working ZavaLab1 agent.' }
$connectionId = [string]$connections[0].connection_id
if ($connectionId -notmatch '^[A-Za-z0-9]{3,32}$' -or $connectionId -match '^REPLACE') {
    throw 'Replace the connection placeholder in ZavaLab1 and verify Lab 3 before continuing.'
}
foreach ($file in @((Join-Path $assets 'declarativeAgent.json'), (Join-Path $assets 'instruction.txt'), $currency)) {
    if (-not (Test-Path -LiteralPath $file)) { throw "Required course asset is missing: $file" }
}

if (Test-Path -LiteralPath $project) {
    # Reopen a completed setup without replacing learner edits or generated IDs.
    $existingFile = Join-Path $project 'appPackage\declarativeAgent.json'
    if (-not (Test-Path -LiteralPath $existingFile)) { throw 'Existing ZavaTravelWIQD folder is incomplete. Leave it intact and ask the instructor.' }
    $existing = Get-Content -LiteralPath $existingFile -Raw | ConvertFrom-Json
    $existingIds = @($existing.capabilities | Where-Object { $_.name -eq 'GraphConnectors' } | ForEach-Object { $_.connections } | ForEach-Object { $_.connection_id })
    if ($existing.name -ne 'Zava Travel Assistant' -or $existingIds.Count -ne 1 -or $existingIds[0] -ne $connectionId -or
        -not (Test-Path -LiteralPath (Join-Path $project 'appPackage\currency-plugin.mcp.json')) -or
        -not (Test-Path -LiteralPath (Join-Path $project 'm365agents.yml'))) {
        throw 'Existing project does not match the completed Zava lab setup. No files were changed; ask the instructor.'
    }
    Write-Host 'Reusing the existing ZavaTravelWIQD project without changing its files.'
} else {
    Write-Host 'Review the WIQD licence: https://aka.ms/wiqd/eula'
    $consent = Read-Host 'If you agree and are authorized to accept it, type ACCEPT. Any other response stops setup'
    if ($consent -cne 'ACCEPT') { throw 'Licence not accepted. No project was created.' }
    & $wiqd eula accept wiqd
    if ($LASTEXITCODE -ne 0) { throw 'WIQD licence acceptance did not complete.' }
}

Write-Host 'Sign in with the same Microsoft 365 lab account used in Labs 1-3.'
& $wiqd auth login --interactive
if ($LASTEXITCODE -ne 0) { throw 'WIQD sign-in failed.' }
& $wiqd auth status
if ($LASTEXITCODE -ne 0) { throw 'Could not confirm the WIQD sign-in session.' }

if (-not (Test-Path -LiteralPath $project)) {
    $parent = Split-Path $project -Parent
    & $wiqd plugin create --name 'ZavaTravelWIQD' --output $parent
    if ($LASTEXITCODE -ne 0) { throw 'Project creation failed. Do not continue to provisioning.' }
    Push-Location $project
    try {
        & $wiqd plugin add agent --name 'Zava Travel Assistant'
        if ($LASTEXITCODE -ne 0) { throw 'Agent creation failed. Leave the generated folder intact and ask the instructor.' }
        $manifestPath = Join-Path $project 'appPackage\manifest.json'
        $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
        if (@($manifest.copilotAgents.declarativeAgents).Count -ne 1 -or
            $manifest.copilotAgents.declarativeAgents[0].file -ne 'declarativeAgent.json') {
            throw 'Unexpected generated agent reference. No supplied files were copied; ask the instructor.'
        }
        $agent = Get-Content -LiteralPath (Join-Path $assets 'declarativeAgent.json') -Raw | ConvertFrom-Json
        ($agent.capabilities | Where-Object { $_.name -eq 'GraphConnectors' }).connections[0].connection_id = $connectionId
        [IO.File]::WriteAllText((Join-Path $project 'appPackage\declarativeAgent.json'), ($agent | ConvertTo-Json -Depth 100), $utf8)
        Copy-Item -LiteralPath (Join-Path $assets 'instruction.txt') -Destination (Join-Path $project 'appPackage\instruction.txt')
        Copy-Item -LiteralPath $currency -Destination (Join-Path $project 'appPackage\currency-plugin.mcp.json')
        $manifest.name.short = 'Zava Travel Assistant${{APP_NAME_SUFFIX}}'
        $manifest.name.full = 'Zava Travel Assistant'
        $manifest.description.short = 'Zava travel guidance, official transport info and currency estimates.'
        $manifest.description.full = $manifest.description.short
        $domains = @($manifest.validDomains | Where-Object { $_ })
        $manifest | Add-Member -NotePropertyName validDomains -NotePropertyValue @($domains + 'mcp.frankfurter.dev' | Select-Object -Unique) -Force
        [IO.File]::WriteAllText($manifestPath, ($manifest | ConvertTo-Json -Depth 100), $utf8)
    } finally { Pop-Location }
}
Write-Host "Using the working Lab 3 connection: $connectionId"
& $code.Source -n $project
if ($LASTEXITCODE -ne 0) { throw "Project is prepared, but VS Code did not open. Open $project manually in a new window." }
Write-Host 'LAB 4 PROJECT PREPARED. Place the new window on the right; keep the instructions on the left.'
Write-Host 'Continue with Inspect the combined agent. No provisioning or tenant-wide sharing was performed.'
