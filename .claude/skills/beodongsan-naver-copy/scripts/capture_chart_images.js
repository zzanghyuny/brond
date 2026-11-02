// 브동산 포스팅의 .map-wrap / .radar-wrap / .bridge-wrap SVG 차트를 실제 PNG 파일로 캡처한다.
// 사용법: node capture_chart_images.js <repo-root> <slug>
// 예:     node capture_chart_images.js /home/user/brond mokdong-yunseulxi
//
// 결과: <repo-root>/posts/images/<slug>/chart-map.png (있는 것만, 없으면 건너뜀)
//                                      chart-radar.png
//                                      chart-bridge.png
//
// Playwright/Chromium 경로는 이 환경(Claude Code 세션) 기준 고정 경로를 그대로 쓴다.
// 다른 환경에서 재사용할 경우 PLAYWRIGHT_MODULE / CHROMIUM_PATH를 바꿀 것.

const path = require('path');
const fs = require('fs');

const PLAYWRIGHT_MODULE = process.env.PLAYWRIGHT_MODULE || '/opt/node22/lib/node_modules/playwright';
const CHROMIUM_PATH = process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';

const [, , repoRoot, slug] = process.argv;
if (!repoRoot || !slug) {
  console.error('사용법: node capture_chart_images.js <repo-root> <slug>');
  process.exit(1);
}

const postPath = path.join(repoRoot, 'posts', `${slug}.html`);
const outDir = path.join(repoRoot, 'posts', 'images', slug);

if (!fs.existsSync(postPath)) {
  console.error('포스팅 파일을 찾을 수 없음:', postPath);
  process.exit(1);
}
fs.mkdirSync(outDir, { recursive: true });

const { chromium } = require(PLAYWRIGHT_MODULE);

const TARGETS = [
  { sel: '.map-wrap', file: 'chart-map.png' },
  { sel: '.radar-wrap', file: 'chart-radar.png' },
  { sel: '.bridge-wrap', file: 'chart-bridge.png' },
];

(async () => {
  const browser = await chromium.launch({ executablePath: CHROMIUM_PATH });
  // deviceScaleFactor 2로 캡처해 네이버에 올렸을 때도 선명하게 보이도록 한다.
  const page = await browser.newPage({ viewport: { width: 720, height: 1200 }, deviceScaleFactor: 2 });
  await page.goto('file://' + postPath, { waitUntil: 'networkidle' });

  const saved = [];
  for (const t of TARGETS) {
    const el = await page.$(t.sel);
    if (!el) {
      console.log(`(없음, 건너뜀) ${t.sel}`);
      continue;
    }
    const outPath = path.join(outDir, t.file);
    await el.screenshot({ path: outPath });
    saved.push(outPath);
    console.log('저장됨:', outPath);
  }

  await browser.close();

  if (saved.length === 0) {
    console.log('저장된 차트가 없습니다 — 이 포스팅에는 map-wrap/radar-wrap/bridge-wrap이 없을 수 있습니다.');
  } else {
    console.log(`\n${saved.length}개 차트 이미지 저장 완료. 이 파일들을 커밋·push한 뒤(신규 파일만 추가되는 안전한 변경),`);
    console.log('https://www.brandongsan.com/posts/images/' + slug + '/<파일명> 으로 200이 뜨는지 확인하고 나서 복사용 HTML에 사용하세요.');
  }
})();
