# Prepare portable Node. Core Tools is opt-in for the optional connector only.
param([ValidateSet('22','24')][string]$Runtime = '24', [switch]$IncludeFunctions)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$tools = Join-Path $root 'tools'
New-Item -ItemType Directory -Force $tools | Out-Null
$pins = Get-Content (Join-Path $PSScriptRoot 'node-pins.json') -Raw | ConvertFrom-Json
$requestedVersion = if ($Runtime -eq '22') { '22.22.2' } else { '24.15.0' }
foreach ($version in @($requestedVersion)) {
    $pin = $pins.PSObject.Properties[$version].Value
    $folder = Join-Path $tools "node-v$version-win-x64"
    if (Test-Path $folder) {
        $exe = Join-Path $folder 'node.exe'
        if (-not (Test-Path $exe)) { throw "Incomplete existing runtime: $folder. Preserve it and ask the instructor." }
        $actual = & $exe --version
        if ($LASTEXITCODE -ne 0 -or $actual -ne "v$version") { throw "Unexpected existing Node in $folder" }
        Write-Host "Already prepared: $actual"
        continue
    }
    $zip = Join-Path $tools $pin.file
    Invoke-WebRequest "https://nodejs.org/dist/v$version/$($pin.file)" -UseBasicParsing -OutFile $zip
    if ((Get-FileHash $zip -Algorithm SHA256).Hash.ToLowerInvariant() -ne $pin.sha256) {
        throw "Node archive checksum mismatch: $version. Do not extract or execute it."
    }
    Expand-Archive -LiteralPath $zip -DestinationPath $tools
    $actual = & (Join-Path $folder 'node.exe') --version
    if ($LASTEXITCODE -ne 0 -or $actual -ne "v$version") { throw "Node runtime check failed: $version" }
    Write-Host "Prepared: $actual"
}
if ($IncludeFunctions) { & (Join-Path $PSScriptRoot 'Prepare-Functions.ps1') }
Write-Host 'Use Node 24 for TypeSpec and WIQD; Node 22 only for the optional connector.'
