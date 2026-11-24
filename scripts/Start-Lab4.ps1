# Compatibility entry point. Edit the actual build script before running.
$ErrorActionPreference = 'Stop'
$courseRoot = Split-Path $PSScriptRoot -Parent
& (Join-Path $courseRoot 'Day1\Lab4-WIQD\Build-Agent.ps1')
