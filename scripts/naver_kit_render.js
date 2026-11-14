// naver_kit.py가 만든 jobs.json([{html, out, width}])을 읽어 각 html 조각을 모바일 폭 PNG로 렌더한다.
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 390, height: 800 }, deviceScaleFactor: 2.5 });
  const css = `
  *{box-sizing:border-box}
  body{margin:0;background:#fff;color:#111;font-family:'Malgun Gothic','Apple SD Gothic Neo','WenQuanYi Zen Hei','Noto Sans CJK KR',sans-serif;line-height:1.55}
  #box{width:390px;padding:14px 12px;background:#fff}
  table{width:100%;border-collapse:collapse;font-size:14px;margin:0}
  th,td{border:1px solid #cfcfcf;padding:8px 7px;text-align:left;vertical-align:top;word-break:keep-all;overflow-wrap:anywhere}
  th{background:#f3f3f3;font-weight:800}
  b{font-weight:800}
  .stat{border:1.5px solid #111;padding:14px 14px;margin:0 0 10px;background:#fff}
  .stat p{margin:0}
  .stat p:first-child{font-size:13px;color:#555}
  .stat .price{font-size:27px;font-weight:800;margin:3px 0}
  .stat p:last-child{font-size:14px;font-weight:800}
  .grid{display:block}
  `;
  const page = await ctx.newPage();
  for (const j of jobs) {
    await page.setContent(`<!doctype html><meta charset="utf-8"><style>${css}</style><div id="box">${j.html}</div>`);
    await page.waitForTimeout(80);
    await (await page.$('#box')).screenshot({ path: j.out });
  }
  await b.close();
})();
