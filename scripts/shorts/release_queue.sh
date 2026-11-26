#!/usr/bin/env bash
# 예약 업로드: shorts-queue 브랜치의 queue/<날짜>/ 묶음을 main의 shorts-upload/<YYYY-MM>/로 옮기고 README에 섹션을 붙여 push한다.
#   bash scripts/shorts/release_queue.sh 2026-11-27
set -euo pipefail
D="$1"; M="${D:0:7}"; cd "$(git rev-parse --show-toplevel)"
git checkout -q main && git pull -q --ff-only
git fetch -q origin +shorts-queue:refs/remotes/origin/shorts-queue
mkdir -p "shorts-upload/$M"
for f in $(git ls-tree --name-only "origin/shorts-queue:queue/$D"); do
  [ "$f" = "README-section.md" ] && continue
  git show "origin/shorts-queue:queue/$D/$f" > "shorts-upload/$M/$f"
done
git show "origin/shorts-queue:queue/$D/README-section.md" >> "shorts-upload/$M/README.md"
git add "shorts-upload/$M"
git commit -q -m "Release queued shorts for $D (3/day schedule)" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_018qhGmtPmAEzCU8qCiBxkdv"
git fetch -q && git merge -q --no-edit origin/main 2>/dev/null || true
git push -q origin main && git log --oneline -1
