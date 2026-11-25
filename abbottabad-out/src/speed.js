const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('http://127.0.0.1:8765/world.html?w=3840'); await p.evaluate(() => window.ready);
  const r = await p.evaluate(() => { const o = []; for (let f = 0; f < CUES.duration * 30; f++) o.push(camSpeedPx(f / 30)); return o; });
  let line = '';
  for (let f = 0; f < r.length; f += 6) { const t = f / 30; const acc = Math.abs(r[f + 1] - r[f]) ; line += `${t.toFixed(1).padStart(5)} ${r[f].toFixed(1).padStart(6)} ${'#'.repeat(Math.min(80, Math.round(r[f] / 3)))}\n`; }
  console.log(line);
  let maxJerk = 0, at = 0; for (let f = 2; f < r.length; f++) { const j = Math.abs(r[f] - 2 * r[f - 1] + r[f - 2]); if (j > maxJerk) { maxJerk = j; at = f / 30; } }
  console.log('min speed', Math.min(...r).toFixed(2), 'max', Math.max(...r).toFixed(1), 'max 2nd diff', maxJerk.toFixed(2), 'at', at);
  await b.close();
})();
