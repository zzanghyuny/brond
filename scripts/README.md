# scripts/ — 포스팅 운영 자동화

| 파일 | 역할 |
|---|---|
| `build-manifest.ps1` | `posts-data.js` + `naver-html/*.html` → `posts-manifest.json` 생성/갱신 (기존 발행 기록 보존) |
| `build-feed.ps1` | `posts-data.js` → `feed.xml` (RSS 2.0, 최신 30개, 서치어드바이저·서치콘솔 제출용). 새 글을 추가할 때마다 실행 |
| `sync-workflow.ps1` | 운영 문서·스킬·manifest **변경분만** GitHub에 커밋·push (변경 없으면 아무것도 안 함) |

## sync-workflow.ps1 동작
- 대상: `CLAUDE.md`, `.claude/skills/`, `docs/`, `templates/`(있으면), `posts-manifest.json`
- 대상 파일에 변경이 **없으면 아무 작업도 하지 않고** 로그만 남긴다. 웹사이트 소스·배포 설정은 건드리지 않는다.
- 변경이 있으면: 비밀 패턴 검사 → `docs/skill-changelog.md`에 날짜·변경 요약 추가 → 대상 경로만 커밋(`chore: sync publishing workflow YYYY-MM-DD`) → push.
- `main` 브랜치에서만 동작. 로그: `scripts/sync-workflow.log`(git 제외).
- 미리보기: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\sync-workflow.ps1 -DryRun`

> GitHub Actions는 내 PC의 로컬 변경사항을 읽을 수 없어서, 로컬 동기화는 **Windows 작업 스케줄러** 기준이다.

## Windows 작업 스케줄러 등록 (매일 오전 8시)
관리자 권한 없이 사용자 계정으로 등록한다. PowerShell에서:
```powershell
$repo   = 'D:\Paul Kim\브동산'
$script = Join-Path $repo 'scripts\sync-workflow.ps1'
$action = New-ScheduledTaskAction -Execute 'powershell.exe' `
  -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$script`"" -WorkingDirectory $repo
$trigger  = New-ScheduledTaskTrigger -Daily -At 8:00AM
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName 'BrondSyncWorkflow' -Action $action -Trigger $trigger -Settings $settings `
  -Description 'brond publishing workflow sync (08:00 daily)'
```
- `-StartWhenAvailable`: 8시에 PC가 꺼져 있었다면 켜진 직후 실행한다.
- 확인: `Get-ScheduledTask BrondSyncWorkflow | Get-ScheduledTaskInfo`
- 즉시 테스트: `Start-ScheduledTask BrondSyncWorkflow` 후 `scripts\sync-workflow.log` 확인
- 삭제: `Unregister-ScheduledTask BrondSyncWorkflow -Confirm:$false`

GUI로 등록하려면: 작업 스케줄러 → 기본 작업 만들기 → 매일 08:00 → "프로그램 시작" → 프로그램 `powershell.exe`, 인수 `-NoProfile -ExecutionPolicy Bypass -File "D:\Paul Kim\브동산\scripts\sync-workflow.ps1"`, 시작 위치 `D:\Paul Kim\브동산` → 속성의 설정 탭에서 "예약된 시간에 시작하지 못한 경우 가능한 한 빨리 작업 시작"을 체크.

## 사전 조건
- 이 PC의 git이 GitHub에 push 가능해야 한다(자격 증명은 Git Credential Manager가 보관 — 저장소에는 넣지 않는다).
- 자동 동기화는 Claude Code가 작업 중인 미커밋 사이트 파일(`posts/` 등)은 커밋하지 않는다(대상 경로만 커밋).
