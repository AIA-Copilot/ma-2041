# Required setup: Node 24, TypeSpec and WIQD. Connector tools are opt-in.
param([ValidateSet('All','Lab3','Lab4','Connector')][string]$Target = 'All')
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$tools = Join-Path $root 'tools'
$lock = $null
$oldProgress = $ProgressPreference
$stage = 'setup lock'
try {
    New-Item -ItemType Directory -Force $tools | Out-Null
    try {
        $lock = [IO.File]::Open((Join-Path $tools 'day1-setup.lock'),
            [IO.FileMode]::OpenOrCreate, [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
    } catch {
        throw 'Another setup is running, or the tools folder is not writable. Do not run parallel installations.'
    }
    $ProgressPreference = 'SilentlyContinue'
    if ($Target -eq 'Connector') {
        $stage = 'optional Node 22 and Azure Functions Core Tools'
        Write-Host "Preparing $stage. Complete any Windows installer prompts."
        & (Join-Path $PSScriptRoot 'Prepare-Node.ps1') -Runtime 22 -IncludeFunctions
        $stage = 'optional Azure Functions VS Code extension'
        & code.cmd --install-extension ms-azuretools.vscode-azurefunctions
        if ($LASTEXITCODE -ne 0) { throw 'Azure Functions extension installation failed.' }
        $extensions = & code.cmd --list-extensions
        if ($LASTEXITCODE -ne 0 -or $extensions -notcontains 'ms-azuretools.vscode-azurefunctions') {
            throw 'Azure Functions extension could not be verified.'
        }
        . (Join-Path $PSScriptRoot 'Use-Node.ps1') -Version 22
        $stage = 'optional connector dependencies and build'
        Push-Location (Join-Path $root 'Day1\Optional-Connector\connector')
        try {
            & npm.cmd ci --include=dev --bin-links=true --ignore-scripts --no-audit --no-fund
            if ($LASTEXITCODE -ne 0) { throw 'Connector dependency installation failed.' }
            & npm.cmd run build
            if ($LASTEXITCODE -ne 0) { throw 'Connector build failed.' }
        } finally { Pop-Location }
    } else {
        $stage = 'Node 24'
        Write-Host 'Preparing Node 24. Keep this terminal open.'
        & (Join-Path $PSScriptRoot 'Prepare-Node.ps1') -Runtime 24
        . (Join-Path $PSScriptRoot 'Use-Node.ps1') -Version 24
        if ($Target -in @('All','Lab3')) {
            $stage = 'Lab3 TypeSpec dependencies and compile'
            Push-Location (Join-Path $root 'Day1\Lab3-TypeSpec')
            try {
                & npm.cmd ci --include=dev --bin-links=true --ignore-scripts --no-audit --no-fund
                if ($LASTEXITCODE -ne 0) { throw 'TypeSpec dependency installation failed.' }
                & npm.cmd run build
                if ($LASTEXITCODE -ne 0) { throw 'TypeSpec compile failed.' }
            } finally { Pop-Location }
        }
        if ($Target -in @('All','Lab4')) {
            $stage = 'Lab4 WIQD installation'
            $wiqdFolder = Join-Path $tools 'wiqd-1.0.0'
            $wiqd = Join-Path $wiqdFolder 'node_modules\.bin\wiqd.cmd'
            if (-not (Test-Path -LiteralPath $wiqd)) {
                & npm.cmd install --prefix $wiqdFolder --save-exact @microsoft/wiqd@1.0.0 --bin-links=true --no-audit --no-fund
                if ($LASTEXITCODE -ne 0) { throw 'WIQD installation failed.' }
            }
        }
    }
    $stage = 'local tool checks'
    & (Join-Path $PSScriptRoot 'Test-Day1.ps1') -Target $Target
    if ($Target -eq 'Connector') {
        Write-Host 'OPTIONAL CONNECTOR PREPARATION COMPLETE'
        Write-Host 'Save your work, close ALL VS Code windows, then reopen them before debugging.'
    } else {
        Write-Host "DAY 1 PREPARATION COMPLETE ($Target)"
    }
} catch {
    Write-Host "PREPARATION FAILED [$stage]: $($_.Exception.Message)"
    Write-Host "After resolving the error, retry from the course root: .\scripts\Prepare-Day1.ps1 -Target $Target"
    throw
} finally {
    $ProgressPreference = $oldProgress
    if ($lock) { $lock.Dispose() }
}
