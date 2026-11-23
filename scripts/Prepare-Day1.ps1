# Start once during Lab 1 in the course-window terminal.
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$tools = Join-Path $root 'tools'
New-Item -ItemType Directory -Force $tools | Out-Null
$lock = $null
$oldProgress = $ProgressPreference
try {
    try {
        $lock = [IO.File]::Open((Join-Path $tools 'day1-setup.lock'),
            [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
    } catch {
        throw 'Cannot acquire setup lock. Check for another running setup or a tools-folder access error. Do not start parallel installations.'
    }
    $ProgressPreference = 'SilentlyContinue'
    Write-Host '[1/4] Preparing Node and Azure Functions Core Tools.'
    Write-Host 'Complete any Windows installer prompts. Keep this terminal open until preparation finishes.'
    & (Join-Path $PSScriptRoot 'Prepare-Node.ps1')

    Write-Host '[2/4] Installing the Microsoft Azure Functions extension.'
    & code.cmd --install-extension ms-azuretools.vscode-azurefunctions
    if ($LASTEXITCODE -ne 0) { throw 'Azure Functions extension installation failed.' }
    $extensions = & code.cmd --list-extensions
    if ($LASTEXITCODE -ne 0 -or $extensions -notcontains 'ms-azuretools.vscode-azurefunctions') {
        throw 'Azure Functions extension could not be verified.'
    }

    Write-Host '[3/4] Installing and building the Lab 3 connector dependencies.'
    . (Join-Path $PSScriptRoot 'Use-Node.ps1') -Version 22
    Push-Location (Join-Path $root 'Day1\Lab3-CopilotConnector\connector')
    try {
        & npm.cmd ci --ignore-scripts --no-audit --no-fund
        if ($LASTEXITCODE -ne 0) { throw 'Connector dependency installation failed.' }
        & npm.cmd run build
        if ($LASTEXITCODE -ne 0) { throw 'Connector build failed.' }
    } finally {
        Pop-Location
    }

    Write-Host '[4/4] Preparing WIQD 1.0.0.'
    . (Join-Path $PSScriptRoot 'Use-Node.ps1') -Version 24
    $wiqdFolder = Join-Path $tools 'wiqd-1.0.0'
    $wiqd = Join-Path $wiqdFolder 'node_modules\.bin\wiqd.cmd'
    if (-not (Test-Path -LiteralPath $wiqd)) {
        & npm.cmd install --prefix $wiqdFolder --save-exact @microsoft/wiqd@1.0.0 --no-audit --no-fund
        if ($LASTEXITCODE -ne 0) { throw 'WIQD installation failed.' }
    }
    $version = (& $wiqd --version | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or $version -ne '1.0.0') {
        throw "Expected WIQD 1.0.0; received '$version'. Ask the instructor before changing versions."
    }
    Write-Host 'DAY 1 PREPARATION COMPLETE'
    Write-Host 'Before Lab 3, save your work, close ALL VS Code windows and reopen the app from Start.'
    Write-Host 'Do not rerun the installs unless preparation failed. New manual npm terminals still need Use-Node.ps1.'
} finally {
    $ProgressPreference = $oldProgress
    if ($lock) { $lock.Dispose() }
}
