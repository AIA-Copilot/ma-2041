# Non-installing local executable checks; no licence acceptance, login or cloud calls.
param([ValidateSet('All','Lab3','Lab4')][string]$Target = 'All')
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$stage = 'runtime selection'
try {
    if ($Target -in @('All','Lab3')) {
        $stage = 'Lab3 Node 22'
        . (Join-Path $PSScriptRoot 'Use-Node.ps1') -Version 22
        $connector = Join-Path $root 'Day1\Lab3-CopilotConnector\connector'
        foreach ($tool in @('tsc','azurite')) {
            $stage = "Lab3 $tool --version"
            $command = Join-Path $connector "node_modules\.bin\$tool.cmd"
            if (-not (Test-Path -LiteralPath $command)) { throw "Missing local executable: $command" }
            $toolVersion = (& $command --version | Out-String).Trim()
            if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($toolVersion)) { throw "$tool did not return a version successfully." }
            Write-Host "${tool}: $toolVersion"
        }
    }
    if ($Target -in @('All','Lab4')) {
        $stage = 'Lab4 Node 24'
        . (Join-Path $PSScriptRoot 'Use-Node.ps1') -Version 24
        $stage = 'Lab4 WIQD --version'
        $wiqd = Join-Path $root 'tools\wiqd-1.0.0\node_modules\.bin\wiqd.cmd'
        if (-not (Test-Path -LiteralPath $wiqd)) { throw 'Missing local WIQD executable.' }
        $wiqdVersion = (& $wiqd --version | Out-String).Trim()
        if ($LASTEXITCODE -ne 0 -or $wiqdVersion -ne '1.0.0') { throw "Expected WIQD 1.0.0; received '$wiqdVersion'. Ask the instructor before changing versions." }
        Write-Host "WIQD: $wiqdVersion"
    }
    Write-Host "DAY 1 LOCAL TOOL CHECKS PASSED ($Target)"
} catch {
    Write-Host "DAY 1 CHECK FAILED [$stage]: $($_.Exception.Message)"
    Write-Host "Repair from the course root: .\scripts\Prepare-Day1.ps1 -Target $Target"
    throw
}
