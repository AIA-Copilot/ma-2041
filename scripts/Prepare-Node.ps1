# Prepare pinned portable Node runtimes and the Core Tools v4 Windows installer.
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$tools = Join-Path $root 'tools'
New-Item -ItemType Directory -Force $tools | Out-Null
$pins = Get-Content (Join-Path $PSScriptRoot 'node-pins.json') -Raw | ConvertFrom-Json
foreach ($version in @('22.22.2','24.15.0')) {
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
    Invoke-WebRequest "https://nodejs.org/dist/v$version/$($pin.file)" -OutFile $zip
    if ((Get-FileHash $zip -Algorithm SHA256).Hash.ToLowerInvariant() -ne $pin.sha256) {
        throw "Node archive checksum mismatch: $version. Do not extract or execute it."
    }
    Expand-Archive -LiteralPath $zip -DestinationPath $tools
    $actual = & (Join-Path $folder 'node.exe') --version
    if ($LASTEXITCODE -ne 0 -or $actual -ne "v$version") { throw "Node runtime check failed: $version" }
    Write-Host "Prepared: $actual"
}
& (Join-Path $PSScriptRoot 'Prepare-Functions.ps1')
Write-Host 'Use . .\scripts\Use-Node.ps1 -Version 22 for connector setup; -Version 24 for WIQD.'
