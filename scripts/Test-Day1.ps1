# Non-installing version checks. No login, consent or tenant calls.
param([ValidateSet('All','Lab3','Lab4','Connector')][string]$Target = 'All')
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$stage = 'runtime selection'
try {
    if ($Target -eq 'Connector') {
        . (Join-Path $PSScriptRoot 'Use-Node.ps1') -Version 22
        $connector = Join-Path $root 'Day1\Optional-Connector\connector'
        foreach ($tool in @('tsc','azurite')) {
            $stage = "optional connector $tool"
            $command = Join-Path $connector "node_modules\.bin\$tool.cmd"
            if (-not (Test-Path -LiteralPath $command)) { throw "Missing local executable: $command" }
            $toolVersion = (& $command --version | Out-String).Trim()
            if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($toolVersion)) { throw "$tool version check failed." }
            Write-Host "${tool}: $toolVersion"
        }
        $stage = 'optional Azure Functions Core Tools'
        $func = Get-Command func -CommandType Application -ErrorAction Stop | Select-Object -First 1
        $funcVersion = (& $func.Source --version | Out-String).Trim()
        if ($LASTEXITCODE -ne 0 -or $funcVersion -notmatch '^4\.') { throw 'Azure Functions Core Tools v4 is required for the optional exercise.' }
    } else {
        . (Join-Path $PSScriptRoot 'Use-Node.ps1') -Version 24
        if ($Target -in @('All','Lab3')) {
            $stage = 'Lab3 TypeSpec compiler'
            $tsp = Join-Path $root 'Day1\Lab3-TypeSpec\node_modules\.bin\tsp.cmd'
            if (-not (Test-Path -LiteralPath $tsp)) { throw 'Missing local TypeSpec compiler.' }
            $tspVersion = (& $tsp --version | Out-String).Trim()
            if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($tspVersion)) { throw 'TypeSpec compiler check failed.' }
            Write-Host "TypeSpec: $tspVersion"
        }
        if ($Target -in @('All','Lab4')) {
            $stage = 'Lab4 WIQD'
            $wiqd = Join-Path $root 'tools\wiqd-1.0.0\node_modules\.bin\wiqd.cmd'
            if (-not (Test-Path -LiteralPath $wiqd)) { throw 'Missing local WIQD executable.' }
            $wiqdVersion = (& $wiqd --version | Out-String).Trim()
            if ($LASTEXITCODE -ne 0 -or $wiqdVersion -ne '1.0.0') { throw "Expected WIQD 1.0.0; received '$wiqdVersion'. Ask the instructor before replacing an existing installation." }
            Write-Host "WIQD: $wiqdVersion"
        }
    }
    Write-Host "DAY 1 LOCAL TOOL CHECKS PASSED ($Target)"
} catch {
    Write-Host "DAY 1 CHECK FAILED [$stage]: $($_.Exception.Message)"
    Write-Host "Repair from the course root: .\scripts\Prepare-Day1.ps1 -Target $Target"
    throw
}
