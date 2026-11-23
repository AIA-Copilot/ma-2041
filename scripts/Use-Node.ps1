# A distinct parameter name avoids attaching ValidateSet to the caller's $version when dot-sourced.
param([Parameter(Mandatory=$true)][Alias('Version')][ValidateSet('22','24')][string]$CourseNodeMajor)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$full = if ($CourseNodeMajor -eq '22') { '22.22.2' } else { '24.15.0' }
$folder = Join-Path $root "tools\node-v$full-win-x64"
if (-not (Test-Path (Join-Path $folder 'node.exe'))) { throw 'Run scripts\Prepare-Node.ps1 during setup first.' }
$env:Path = $folder + [IO.Path]::PathSeparator + $env:Path
$actual = & node --version
if ($LASTEXITCODE -ne 0 -or $actual -ne "v$full") { throw 'Unexpected Node runtime selected.' }
Write-Host "This terminal uses $actual. New terminals must select their runtime again."
