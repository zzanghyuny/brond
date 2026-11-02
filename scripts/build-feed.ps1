# build-feed.ps1
# posts-data.js  ->  feed.xml (RSS 2.0, newest N posts)
# Run after adding a post to posts-data.js, before commit/push.
# Usage:  powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build-feed.ps1 [-Count 30]
param([string]$RepoPath = (Split-Path -Parent $PSScriptRoot), [int]$Count = 30)
$ErrorActionPreference = 'Stop'
$enc = New-Object System.Text.UTF8Encoding($false)

$dataPath  = Join-Path $RepoPath 'posts-data.js'
$indexPath = Join-Path $RepoPath 'index.html'
$feedPath  = Join-Path $RepoPath 'feed.xml'
$base      = 'https://www.brandongsan.com/'

$catKo = @{ realestate = '청약·분양'; brand = '브랜드이야기'; vietnam = '호치민이야기' }
$inv   = New-Object System.Globalization.CultureInfo('en-US')
$kst   = New-Object TimeSpan(9, 0, 0)

function Esc([string]$s) { return [System.Security.SecurityElement]::Escape($s).Replace('&apos;', "'").Replace('&quot;', '"') }
function Strip-Invalid([string]$s) { return [regex]::Replace($s, '[\x00-\x08\x0B\x0C\x0E-\x1F]', '') }

# a single-line "key: "value"" or a backtick template literal
function Get-Field([string]$block, [string]$name) {
  $m = [regex]::Match($block, '(?m)^\s*' + $name + ':\s*"((?:[^"\\]|\\.)*)"')
  if ($m.Success) { return $m.Groups[1].Value } else { return $null }
}
function Get-Preview([string]$block) {
  $m = [regex]::Match($block, '(?s)preview:\s*`(.*?)`')
  if ($m.Success) { return $m.Groups[1].Value } else { return '' }
}

# channel description = index.html meta description
$idx = [System.IO.File]::ReadAllText($indexPath, $enc)
$dm = [regex]::Match($idx, '<meta\s+name="description"\s+content="([^"]*)"')
if (-not $dm.Success) { throw 'index.html meta description not found' }
$chDesc = [System.Net.WebUtility]::HtmlDecode($dm.Groups[1].Value)

$js = [System.IO.File]::ReadAllText($dataPath, $enc)
$blocks = [regex]::Split($js, '(?m)^  \{\s*$') | Select-Object -Skip 1

$posts = @(); $i = 0
foreach ($b in $blocks) {
  $slug = Get-Field $b 'id'
  if (-not $slug) { continue }
  $i++
  $tag = Get-Field $b 'tag'
  $num = -1
  if ($tag) { $nm = [regex]::Match($tag, 'No\.\s*(\d+)'); if ($nm.Success) { $num = [int]$nm.Groups[1].Value } }
  $posts += [pscustomobject]@{
    Index = $i; Num = $num; Id = $slug
    Category = Get-Field $b 'category'; Region = Get-Field $b 'region'
    Title = Get-Field $b 'title'; Date = Get-Field $b 'date'; Url = Get-Field $b 'url'
    Preview = Get-Preview $b
  }
}
if ($posts.Count -eq 0) { throw 'no posts parsed from posts-data.js' }

$sorted = @($posts | Sort-Object @{Expression = 'Date'; Descending = $true}, @{Expression = 'Num'; Descending = $true}, @{Expression = 'Index'; Descending = $false} | Select-Object -First $Count)

$nl = "`n"
$sb = New-Object System.Text.StringBuilder
[void]$sb.Append('<?xml version="1.0" encoding="UTF-8"?>' + $nl)
[void]$sb.Append('<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">' + $nl)
[void]$sb.Append('  <channel>' + $nl)
[void]$sb.Append('    <title>' + (Esc '브동산 — 브랜드와 부동산 인사이트') + '</title>' + $nl)
[void]$sb.Append('    <link>' + $base + '</link>' + $nl)
[void]$sb.Append('    <description>' + (Esc $chDesc) + '</description>' + $nl)
[void]$sb.Append('    <language>ko</language>' + $nl)
$now = [DateTimeOffset]::UtcNow.ToOffset($kst)
[void]$sb.Append('    <lastBuildDate>' + $now.ToString('ddd, dd MMM yyyy HH:mm:ss', $inv) + ' +0900</lastBuildDate>' + $nl)
[void]$sb.Append('    <atom:link href="' + $base + 'feed.xml" rel="self" type="application/rss+xml"/>' + $nl)

foreach ($p in $sorted) {
  $link = $base + $p.Url
  $d = [DateTimeOffset]::new([datetime]::ParseExact($p.Date, 'yyyy-MM-dd', $inv).AddHours(9), $kst)
  $pub = $d.ToString('ddd, dd MMM yyyy HH:mm:ss', $inv) + ' +0900'
  $txt = [regex]::Replace($p.Preview, '<[^>]+>', ' ')
  $txt = [System.Net.WebUtility]::HtmlDecode($txt)
  $txt = ([regex]::Replace($txt, '\s+', ' ')).Trim()
  if ($txt.Length -gt 200) { $txt = $txt.Substring(0, 200).TrimEnd() + '…' }
  [void]$sb.Append('    <item>' + $nl)
  [void]$sb.Append('      <title>' + (Esc (Strip-Invalid $p.Title)) + '</title>' + $nl)
  [void]$sb.Append('      <link>' + $link + '</link>' + $nl)
  [void]$sb.Append('      <guid isPermaLink="true">' + $link + '</guid>' + $nl)
  [void]$sb.Append('      <pubDate>' + $pub + '</pubDate>' + $nl)
  if ($catKo[$p.Category]) { [void]$sb.Append('      <category>' + (Esc $catKo[$p.Category]) + '</category>' + $nl) }
  if ($p.Category -eq 'realestate' -and $p.Region) { [void]$sb.Append('      <category>' + (Esc $p.Region) + '</category>' + $nl) }
  [void]$sb.Append('      <description>' + (Esc (Strip-Invalid $txt)) + '</description>' + $nl)
  [void]$sb.Append('    </item>' + $nl)
}
[void]$sb.Append('  </channel>' + $nl)
[void]$sb.Append('</rss>' + $nl)

[System.IO.File]::WriteAllText($feedPath, $sb.ToString(), $enc)
Write-Host ("feed.xml written: {0} items (of {1} posts), newest = {2} ({3})" -f $sorted.Count, $posts.Count, $sorted[0].Id, $sorted[0].Date)
