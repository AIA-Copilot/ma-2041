# Toolkit calls this so compilation does not depend on VS Code's inherited PATH.
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot '..\..\scripts\Use-Node.ps1') -Version 24
Push-Location $PSScriptRoot
try {
    $npm = Get-Command npm.cmd -CommandType Application -ErrorAction Stop | Select-Object -First 1
    # PS5.1 may surface piped native stderr as error records. Exit code decides success.
    $savedPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        & $npm.Source run compile
        $compileExit = $LASTEXITCODE
    } finally { $ErrorActionPreference = $savedPreference }
    if ($compileExit -ne 0) { throw 'TypeSpec compilation failed. Fix main.tsp before provisioning.' }
    # Match Toolkit's generated-package layout; source identities stay untouched.
    $manifest = Get-Content .\appPackage\manifest.json -Raw | ConvertFrom-Json
    $manifest.copilotAgents.declarativeAgents[0].file = 'declarativeAgent.json'
    $utf8 = New-Object Text.UTF8Encoding($false)
    [IO.File]::WriteAllText((Join-Path $PSScriptRoot 'appPackage\.generated\manifest.json'), ($manifest | ConvertTo-Json -Depth 100), $utf8)
} finally { Pop-Location }
