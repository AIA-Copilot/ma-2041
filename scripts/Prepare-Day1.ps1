# Start once during Lab 1; use -Target Lab3 or Lab4 for isolated recovery.
param([ValidateSet('All','Lab3','Lab4')][string]$Target = 'All')
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
        throw 'Cannot acquire setup lock. Check for another running setup or a tools-folder access error. Do not start parallel installations.'
    }
    $ProgressPreference = 'SilentlyContinue'
    $stage = 'Node runtimes'
    if ($Target -ne 'Lab4') { $stage = 'Node and Azure Functions Core Tools' }
    Write-Host "Preparing $stage. Keep this terminal open and complete any Windows installer prompts."
    & (Join-Path $PSScriptRoot 'Prepare-Node.ps1') -SkipFunctions:($Target -eq 'Lab4')

    if ($Target -in @('All','Lab3')) {
        $stage = 'Azure Functions VS Code extension'
        Write-Host "Preparing $stage."
        & code.cmd --install-extension ms-azuretools.vscode-azurefunctions
        if ($LASTEXITCODE -ne 0) { throw 'Azure Functions extension installation failed.' }
        $extensions = & code.cmd --list-extensions
        if ($LASTEXITCODE -ne 0 -or $extensions -notcontains 'ms-azuretools.vscode-azurefunctions') {
            throw 'Azure Functions extension could not be verified.'
        }

        $stage = 'Lab3 connector dependencies'
        . (Join-Path $PSScriptRoot 'Use-Node.ps1') -Version 22
        Push-Location (Join-Path $root 'Day1\Lab3-CopilotConnector\connector')
        try {
            & npm.cmd ci --include=dev --bin-links=true --ignore-scripts --no-audit --no-fund
            if ($LASTEXITCODE -ne 0) { throw 'Connector dependency installation failed.' }
            $stage = 'Lab3 local executable checks'
            & (Join-Path $PSScriptRoot 'Test-Day1.ps1') -Target Lab3
            $stage = 'Lab3 connector build'
            & npm.cmd run build
            if ($LASTEXITCODE -ne 0) { throw 'Connector build failed.' }
        } finally { Pop-Location }
    }

    if ($Target -in @('All','Lab4')) {
        $stage = 'Lab4 WIQD installation'
        . (Join-Path $PSScriptRoot 'Use-Node.ps1') -Version 24
        $wiqdFolder = Join-Path $tools 'wiqd-1.0.0'
        $wiqd = Join-Path $wiqdFolder 'node_modules\.bin\wiqd.cmd'
        if (-not (Test-Path -LiteralPath $wiqd)) {
            & npm.cmd install --prefix $wiqdFolder --save-exact @microsoft/wiqd@1.0.0 --bin-links=true --no-audit --no-fund
            if ($LASTEXITCODE -ne 0) { throw 'WIQD installation failed.' }
        }
        $stage = 'Lab4 local executable checks'
        & (Join-Path $PSScriptRoot 'Test-Day1.ps1') -Target Lab4
    }
    Write-Host "DAY 1 PREPARATION COMPLETE ($Target)"
    if ($Target -ne 'Lab4') { Write-Host 'Before Lab 3, save your work, close ALL VS Code windows and reopen the app from Start.' }
    Write-Host 'Do not rerun the installs unless preparation failed. New manual npm terminals still need Use-Node.ps1.'
} catch {
    Write-Host "DAY 1 PREPARATION FAILED [$stage]: $($_.Exception.Message)"
    Write-Host "After resolving the error, retry from the course root: .\scripts\Prepare-Day1.ps1 -Target $Target"
    throw
} finally {
    $ProgressPreference = $oldProgress
    if ($lock) { $lock.Dispose() }
}
