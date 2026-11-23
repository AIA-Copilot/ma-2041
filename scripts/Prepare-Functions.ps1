# Prepare Azure Functions Core Tools v4 for the Windows x64 training VM.
$ErrorActionPreference = 'Stop'

function Get-CourseFunctionsVersion {
    $command = Get-Command func -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $command) { return $null }
    $version = (& $command.Source --version | Out-String).Trim()
    if ($LASTEXITCODE -ne 0 -or $version -notmatch '^4\.\d+\.\d+') {
        throw "An existing func command is not working Core Tools v4: $($command.Source). Ask the instructor before replacing it."
    }
    return $version
}

function Update-CourseProcessPath {
    # Refresh only this process. Do not write persistent PATH settings.
    $combined = $env:Path + ';' + [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')
    $env:Path = (($combined -split ';' | Where-Object { $_ } | Select-Object -Unique) -join ';')
}

Update-CourseProcessPath
$version = Get-CourseFunctionsVersion
if ($version) {
    Write-Host "Azure Functions Core Tools already available: $version"
    return
}
if (-not [Environment]::Is64BitOperatingSystem) {
    throw 'This course requires a Windows x64 VM.'
}
$tools = Join-Path (Split-Path $PSScriptRoot -Parent) 'tools'
New-Item -ItemType Directory -Force $tools | Out-Null
$msi = Join-Path $tools 'func-cli-4.16.1-x64.msi'
$expected = 'a1f7afdc4422f10988604d1ad004cac18123e6339856e3efafc446bc93d63838'
if (-not (Test-Path -LiteralPath $msi)) {
    Write-Host 'Downloading Azure Functions Core Tools (about 474 MB). Please wait.'
    Invoke-WebRequest 'https://github.com/Azure/azure-functions-core-tools/releases/download/4.16.1/func-cli-4.16.1-x64.msi' -UseBasicParsing -OutFile $msi
}
if ((Get-FileHash -LiteralPath $msi -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expected) {
    throw "Core Tools checksum mismatch. Do not run $msi. Ask the instructor to replace the download."
}
$signature = Get-AuthenticodeSignature -LiteralPath $msi
if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch '(^|,\s*)CN=Microsoft Corporation(,|$)') {
    throw 'Core Tools installer does not have a valid Microsoft Corporation signature.'
}
Write-Host 'Complete the Windows installer, including its license and administrator prompts. Do not close this terminal.'
$process = Start-Process -FilePath 'msiexec.exe' -ArgumentList @('/i', ('"' + $msi + '"'), '/norestart') -Wait -PassThru
if ($process.ExitCode -eq 3010) {
    throw 'Core Tools installation requires a VM restart. Save your work, restart the VM and run this preparation again.'
}
if ($process.ExitCode -ne 0) {
    throw "Core Tools installation did not complete (exit $($process.ExitCode)). Complete installation before debugging."
}
Update-CourseProcessPath
$version = Get-CourseFunctionsVersion
if (-not $version) {
    throw 'Core Tools is still unavailable. Save your work, close all VS Code windows, reopen and run func --version before debugging.'
}
Write-Host "Azure Functions Core Tools available: $version"
Write-Host 'Save your work, close all VS Code windows and reopen them before debugging so they receive the updated PATH.'
