# sync-workflow.ps1
# Daily sync of the publishing-workflow files to GitHub. Commits/pushes ONLY when target files changed.
# Targets: CLAUDE.md, .claude/skills/, docs/, templates/ (if present), posts-manifest.json
# Never touches website sources or deploy settings. Aborts if a secret-like pattern is found.
# Usage:  powershell -NoProfile -ExecutionPolicy Bypass -File scripts\sync-workflow.ps1 [-DryRun]
param([string]$RepoPath = (Split-Path -Parent $PSScriptRoot), [switch]$DryRun)
$ErrorActionPreference = 'Stop'
$enc = New-Object System.Text.UTF8Encoding($false)
Set-Location $RepoPath
$logPath = Join-Path $RepoPath 'scripts\sync-workflow.log'
function Log([string]$m) {
  $line = '{0} {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m
  Add-Content -Path $logPath -Value $line -Encoding UTF8
  Write-Host $line
}
# git writes progress/warnings to stderr; judge success by exit code only.
function Invoke-Git {
  $prev = $ErrorActionPreference
  $ErrorActionPreference = 'Continue'
  try { $out = & git @args 2>&1 | ForEach-Object { "$_" }; $code = $LASTEXITCODE }
  finally { $ErrorActionPreference = $prev }
  return [pscustomobject]@{ Code = $code; Out = @($out) }
}

$targets = @('CLAUDE.md', '.claude/skills', 'docs', 'templates', 'posts-manifest.json') | Where-Object { Test-Path (Join-Path $RepoPath $_) }
if ($targets.Count -eq 0) { Log 'no target paths exist - nothing to do'; exit 0 }

$r = Invoke-Git rev-parse --abbrev-ref HEAD
$branch = ($r.Out -join '').Trim()
if ($branch -ne 'main') { Log "current branch is '$branch' (not main) - skipped"; exit 0 }

$r = Invoke-Git status --porcelain -- @targets
$porcelain = @($r.Out | Where-Object { $_ -match '\S' })
if ($porcelain.Count -eq 0) { Log 'no changes in target files - nothing to do'; exit 0 }

$changed = @()
foreach ($l in $porcelain) { $changed += $l.Substring(3).Trim('"') }

# secret scan (changed text files only)
$strong = '(BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,})'
$assign = '(?i)(api[_-]?key|secret|password|passwd|access[_-]?token|auth[_-]?token)\s*[:=]\s*["'']?[A-Za-z0-9/+_.-]{12,}'
foreach ($f in $changed) {
  $p = Join-Path $RepoPath $f
  if (Test-Path $p -PathType Leaf) {
    $txt = [System.IO.File]::ReadAllText($p, $enc)
    if ($txt -match $strong -or $txt -match $assign) { Log "ABORT: secret-like pattern found in $f - nothing committed"; exit 2 }
  }
}

if ($DryRun) { Log ('DRY RUN - would commit: ' + ($changed -join ', ')); exit 0 }

$date = Get-Date -Format 'yyyy-MM-dd'
$clPath = Join-Path $RepoPath 'docs\skill-changelog.md'
if (-not (Test-Path $clPath)) { [System.IO.File]::WriteAllText($clPath, "# Skill / workflow changelog`n`n", $enc) }
$cl = [System.IO.File]::ReadAllText($clPath, $enc)
$summary = ($changed | Where-Object { $_ -notlike 'docs/skill-changelog.md' } | ForEach-Object { '- ' + $_ }) -join "`n"
if (-not $summary) { $summary = '- (changelog only)' }
$entry = "## $date (auto-sync)`n$summary`n`n"
$m = [regex]::Match($cl, '(?m)^## ')
if ($m.Success) { $cl = $cl.Insert($m.Index, $entry) } else { $cl = $cl.TrimEnd() + "`n`n" + $entry }
[System.IO.File]::WriteAllText($clPath, $cl, $enc)

$r = Invoke-Git add -- @targets
if ($r.Code -ne 0) { Log ('git add failed: ' + ($r.Out -join ' ')); exit 1 }
$r = Invoke-Git commit -m "chore: sync publishing workflow $date" -- @targets
if ($r.Code -ne 0) { Log ('git commit failed: ' + ($r.Out -join ' ')); exit 1 }

$r = Invoke-Git fetch origin
$r = Invoke-Git rev-list --count 'HEAD..origin/main'
$behind = 0
[void][int]::TryParse(($r.Out -join '').Trim(), [ref]$behind)
if ($behind -gt 0) {
  $r = Invoke-Git pull --rebase --autostash origin main
  if ($r.Code -ne 0) { Log ('git pull --rebase failed - resolve manually: ' + ($r.Out -join ' ')); exit 1 }
}
$r = Invoke-Git push origin main
if ($r.Code -ne 0) { Log ('git push failed: ' + ($r.Out -join ' ')); exit 1 }
Log ('synced: ' + ($changed -join ', '))
exit 0
