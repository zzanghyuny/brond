# build-manifest.ps1
# posts-data.js + naver-html/*.html  ->  posts-manifest.json
# Existing publish records (naver_published / naver_post_id / published_at) are preserved.
# Usage:  powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build-manifest.ps1
param([string]$RepoPath = (Split-Path -Parent $PSScriptRoot))
$ErrorActionPreference = 'Stop'
$enc = New-Object System.Text.UTF8Encoding($false)

$dataPath     = Join-Path $RepoPath 'posts-data.js'
$manifestPath = Join-Path $RepoPath 'posts-manifest.json'
$naverDir     = Join-Path $RepoPath 'naver-html'
$base         = 'https://www.brandongsan.com/'

$catKo    = @{ realestate = '부동산'; brand = '브랜드'; vietnam = '호치민'; space = '공간' }
$catNaver = @{ realestate = '부동산이야기'; brand = '브랜드이야기'; vietnam = '호치민이야기' }

# previous publish records
$old = @{}
if (Test-Path $manifestPath) {
  $om = [System.IO.File]::ReadAllText($manifestPath, $enc) | ConvertFrom-Json
  foreach ($p in $om.posts) { $old[$p.slug] = $p }
}

function Get-Field([string]$block, [string]$name) {
  $m = [regex]::Match($block, '(?m)^\s*' + $name + ':\s*"((?:[^"\\]|\\.)*)"')
  if ($m.Success) { return $m.Groups[1].Value } else { return $null }
}

$js = [System.IO.File]::ReadAllText($dataPath, $enc)
$blocks = [regex]::Split($js, '(?m)^  \{\s*$') | Select-Object -Skip 1

$posts = @()
foreach ($b in $blocks) {
  $slug = Get-Field $b 'id'
  if (-not $slug) { continue }
  $cat   = Get-Field $b 'category'
  $tag   = Get-Field $b 'tag'
  $title = Get-Field $b 'title'
  $date  = Get-Field $b 'date'
  $url   = Get-Field $b 'url'
  $num = $null
  if ($tag) { $nm = [regex]::Match($tag, 'No\.\s*(\d+)'); if ($nm.Success) { $num = [int]$nm.Groups[1].Value } }

  $naverRel = 'naver-html/' + $slug + '.html'
  $naverAbs = Join-Path $naverDir ($slug + '.html')
  $naverTitle = $null; $naverTags = $null; $covers = $null; $naverCat = $catNaver[$cat]
  $hasNaver = Test-Path $naverAbs
  if ($hasNaver) {
    $html = [System.IO.File]::ReadAllText($naverAbs, $enc)
    $cm = [regex]::Match($html, '(?s)<!--\s*(slug:.*?)-->')
    if ($cm.Success) {
      $meta = $cm.Groups[1].Value
      $t = [regex]::Match($meta, '(?m)^\s*title:\s*(.+?)\s*$');            if ($t.Success)  { $naverTitle = $t.Groups[1].Value }
      $nc = [regex]::Match($meta, '(?m)^\s*naver_category:\s*(.+?)\s*$');  if ($nc.Success) { $naverCat = $nc.Groups[1].Value }
      $tg = [regex]::Match($meta, '(?m)^\s*tags:\s*(.+?)\s*$');            if ($tg.Success) { $naverTags = @($tg.Groups[1].Value -split '\s*,\s*' | Where-Object { $_ }) }
      $cv = [regex]::Match($meta, '(?m)^\s*cover_candidates:\s*(.+?)\s*$')
      if ($cv.Success) { $covers = @($cv.Groups[1].Value -split '\s*,\s*' | Where-Object { $_ } | ForEach-Object { $base + 'posts/images/' + $slug + '/' + $_ }) }
    }
  }

  $prev = $old[$slug]
  $pub = $null; $postId = $null; $pat = $null
  if ($prev) { $pub = $prev.naver_published; $postId = $prev.naver_post_id; $pat = $prev.published_at }
  if ($hasNaver -and $null -eq $pub) { $pub = $false }

  $posts += [pscustomobject][ordered]@{
    slug             = $slug
    number           = $num
    title            = $title
    category         = $catKo[$cat]
    naver_category   = $naverCat
    date             = $date
    site_url         = $base + $url
    naver_html       = $(if ($hasNaver) { $naverRel } else { $null })
    naver_title      = $naverTitle
    naver_tags       = $naverTags
    cover_candidates = $covers
    naver_published  = $pub
    naver_post_id    = $postId
    published_at     = $pat
  }
}

$posts = @($posts | Sort-Object @{Expression = 'date'; Descending = $true}, @{Expression = { if ($null -eq $_.number) { -1 } else { $_.number } }; Descending = $true})

$out = [ordered]@{
  version         = 1
  generated_by    = 'scripts/build-manifest.ps1'
  note            = 'naver_html가 있고 naver_published가 true가 아닌 항목이 발행 대기. naver_published가 null이면 네이버용 HTML이 아직 없는 글. 이미 발행된 글(true)은 중복 발행 금지.'
  category_map    = [ordered]@{ '부동산' = '부동산이야기'; '브랜드' = '브랜드이야기'; '호치민' = '호치민이야기' }
  posts           = $posts
}
$json = $out | ConvertTo-Json -Depth 6
[System.IO.File]::WriteAllText($manifestPath, $json + "`n", $enc)
Write-Host ("posts-manifest.json written: {0} posts, {1} with naver-html" -f $posts.Count, @($posts | Where-Object { $_.naver_html }).Count)
