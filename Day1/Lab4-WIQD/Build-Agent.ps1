# LAB 4: EDIT THIS CONFIGURATION, save, then run this file again.
$ProjectName = 'ZavaScriptAgent' # Keep this folder name unchanged for repeat runs.
$AgentDisplayName = 'Zava Travel Guide'
$Instructions = @'
Help travelers find official Seattle airport and public transport guidance.
Give concise answers with links to the approved official sources. Explain uncertainty.
Do not invent company policies, approve expenses, book travel or make payments.
'@
$ConversationStarters = @(
    @{ title = 'Airport to city'; text = 'Where can I find official SEA airport to downtown light rail guidance?' },
    @{ title = 'Check a source'; text = 'Which official source should I check for current service information?' }
)
$ApprovedWebSearchSites = @('https://www.portseattle.org', 'https://www.soundtransit.org')
# END OF LEARNER CONFIGURATION. Read the numbered build steps below.

$ErrorActionPreference = 'Stop'
$utf8 = New-Object Text.UTF8Encoding($false)

# 1. Check names and ownership BEFORE sign-in or any project writes.
if ($ProjectName -notmatch '^[A-Za-z][A-Za-z0-9-]{2,39}$' -or
    $ProjectName -match '^(CON|PRN|AUX|NUL|COM[0-9]|LPT[0-9])$') {
    throw 'ProjectName must be a safe 3-40 character folder name, not a Windows device name.'
}
if ([string]::IsNullOrWhiteSpace($AgentDisplayName) -or $AgentDisplayName.Length -gt 25) {
    throw 'AgentDisplayName must contain 1-25 characters (room is reserved for the dev suffix).'
}
if ([string]::IsNullOrWhiteSpace($Instructions)) { throw 'Instructions cannot be empty.' }
if ($ApprovedWebSearchSites.Count -lt 1 -or $ApprovedWebSearchSites.Count -gt 4) { throw 'Choose 1-4 approved web sites.' }
foreach ($site in $ApprovedWebSearchSites) {
    $uri = $null
    if (-not [Uri]::TryCreate($site, [UriKind]::Absolute, [ref]$uri) -or
        $uri.Scheme -ne 'https' -or -not $uri.Host -or $uri.UserInfo -or $uri.Query -or $uri.Fragment) {
        throw 'Approved sites must be absolute HTTPS URLs without credentials, queries or fragments.'
    }
}
$project = Join-Path $PSScriptRoot $ProjectName
$markerPath = Join-Path $project '.course-lab4-owned.json'
$manifestPath = Join-Path $project 'appPackage\manifest.json'
# Refuse junctions/symlinks: neither our writes nor WIQD should follow them elsewhere.
$ancestor = Get-Item -LiteralPath $PSScriptRoot
while ($null -ne $ancestor) {
    if ($ancestor.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse-point project paths are not supported.' }
    $ancestor = $ancestor.Parent
}
$existing = Test-Path -LiteralPath $project
if ($existing) {
    $items = @(Get-Item -LiteralPath $project) + @(Get-ChildItem -LiteralPath $project -Force -Recurse)
    if (@($items | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }).Count) { throw 'Reparse-point project paths are not supported.' }
    if (-not (Test-Path -LiteralPath $markerPath)) { throw 'Refusing existing unmarked project. Leave it intact and ask the instructor.' }
    $owner = Get-Content -LiteralPath $markerPath -Raw | ConvertFrom-Json
    if ($owner.course -ne 'MA2041-Day1-Lab4' -or $owner.project -ne $ProjectName) { throw 'Project ownership marker does not match.' }
    foreach ($required in @($manifestPath, (Join-Path $project 'appPackage\declarativeAgent.json'), (Join-Path $project 'm365agents.yml'))) {
        if (-not (Test-Path -LiteralPath $required -PathType Leaf)) { throw 'Owned project is incomplete. Ask the instructor; no automatic reset is performed.' }
    }
    $prior = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    if ($prior.id -ne $owner.manifestId) { throw 'Project identity differs from its ownership marker.' }
    if ($prior.version -notmatch '^\d+\.\d+\.\d+$') { throw 'Source app version must be major.minor.patch.' }
}

# 2. Select Node 24 and check the pinned course CLI (no install or upgrade).
. (Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) 'scripts\Use-Node.ps1') -Version 24
# Use-Node is dot-sourced; derive our own root afterwards, not its $root variable.
$courseRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
& (Join-Path $courseRoot 'scripts\Test-Day1.ps1') -Target Lab4
$wiqd = Join-Path $courseRoot 'tools\wiqd-1.0.0\node_modules\.bin\wiqd.cmd'

# 3. Check licence state. Never accept terms without the learner's explicit consent.
$licenceOutput = & $wiqd eula status --json
if ($LASTEXITCODE -ne 0) { throw 'WIQD licence status failed. Ask the instructor to inspect the CLI output; no acceptance was automated.' }
$licence = ($licenceOutput -join "`n") | ConvertFrom-Json
if ($licence.data.wiqd.state -eq 'unaccepted') {
    Write-Host 'Review https://aka.ms/wiqd/eula before continuing.'
    $consent = Read-Host 'If you agree and are authorized to accept these terms, type ACCEPT. Any other response stops'
    if ($consent -cne 'ACCEPT') { throw 'Licence not accepted. No sign-in or project creation was attempted.' }
    & $wiqd eula accept wiqd
    if ($LASTEXITCODE -ne 0) { throw 'WIQD licence acceptance did not complete.' }
} elseif ($licence.data.wiqd.state -ne 'accepted') { throw 'Could not determine WIQD licence state.' }
Write-Host 'Sign in with your Microsoft 365 lab account. Complete MFA if required.'
& $wiqd auth login --interactive
if ($LASTEXITCODE -ne 0) { throw 'WIQD sign-in failed.' }
& $wiqd auth status
if ($LASTEXITCODE -ne 0) { throw 'Could not confirm WIQD sign-in.' }

# 4. Scaffold ONCE. Never force-create over an existing learner project.
if (-not $existing) {
    & $wiqd plugin create --name $ProjectName --output $PSScriptRoot
    if ($LASTEXITCODE -ne 0) { throw 'WIQD project creation failed. Leave any partial folder intact for instructor review.' }
}
Push-Location $project
try {
    if (-not $existing) {
        & $wiqd plugin add agent --name $AgentDisplayName
        if ($LASTEXITCODE -ne 0) { throw 'WIQD add agent failed. Leave the unmarked folder intact for instructor review.' }
    }

    # 5. Author the generated agent; retain its schema version and generated IDs.
    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    if (@($manifest.copilotAgents.declarativeAgents).Count -ne 1 -or
        $manifest.copilotAgents.declarativeAgents[0].file -ne 'declarativeAgent.json') { throw 'Unexpected generated agent reference.' }
    $agentPath = Join-Path $project 'appPackage\declarativeAgent.json'
    $agent = Get-Content -LiteralPath $agentPath -Raw | ConvertFrom-Json
    $agent.name = $AgentDisplayName
    $agent.description = 'Official Seattle airport and transit guidance.'
    $agent.instructions = $Instructions
    $sites = @($ApprovedWebSearchSites | ForEach-Object { @{ url = $_ } })
    $agent | Add-Member -NotePropertyName capabilities -NotePropertyValue @(@{ name = 'WebSearch'; sites = $sites }) -Force
    $agent | Add-Member -NotePropertyName conversation_starters -NotePropertyValue $ConversationStarters -Force
    $manifest.name.short = $AgentDisplayName + '${{APP_NAME_SUFFIX}}'
    $manifest.name.full = $AgentDisplayName
    $manifest.description.short = $agent.description
    $manifest.description.full = $agent.description
    if ($existing) {
        $parts = $manifest.version.Split('.')
        $manifest.version = '{0}.{1}.{2}' -f $parts[0], $parts[1], ([int]$parts[2] + 1)
    }
    [IO.File]::WriteAllText($agentPath, ($agent | ConvertTo-Json -Depth 100), $utf8)
    [IO.File]::WriteAllText($manifestPath, ($manifest | ConvertTo-Json -Depth 100), $utf8)
    if (-not $existing) {
        $owner = @{ course = 'MA2041-Day1-Lab4'; project = $ProjectName; manifestId = $manifest.id }
        [IO.File]::WriteAllText($markerPath, ($owner | ConvertTo-Json), $utf8)
    }

    # 6. Validate source BEFORE provisioning. Any CLI failure stops the build.
    & $wiqd plugin validate --mode source --env dev
    if ($LASTEXITCODE -ne 0) { throw 'Source validation failed. Fix the configuration before running again.' }
    & $wiqd plugin provision --env dev
    if ($LASTEXITCODE -ne 0) { throw 'Provisioning failed. Inspect the error; do not publish or share to work around it.' }
    # WIQD prints its real Chat install/test link above; we never construct a URL.
    Write-Host "BUILD COMPLETE: $project (source app version $($manifest.version))"
    Write-Host 'Open the Chat install/test link returned by WIQD above. If absent, ask the instructor.'
} finally { Pop-Location }
