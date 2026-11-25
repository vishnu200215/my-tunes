// usage: node stills.js <width> <outdir> t1 t2 ...
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [w, dir, ...ts] = process.argv.slice(2);
  fs.mkdirSync(dir, { recursive: true });
  const b = await chromium.launch({ args: ['--disable-gpu-vsync'] });
  const p = await b.newPage();
  p.on('console', m => { if (!/GPU stall|GL Driver/.test(m.text())) console.log('page:', m.text()); });
  p.on('pageerror', e => console.log('ERR', e.message));
  await p.goto(`http://127.0.0.1:8765/film.html?w=${w}`);
  await p.evaluate(() => window.ready);
  for (const t of ts) {
    const t0 = Date.now();
    const n = await p.evaluate(t => window.renderFrame(+t, Math.round(t * 30)), t);
    const data = await p.evaluate(() => document.querySelector('canvas').toDataURL('image/jpeg', 0.9));
    fs.writeFileSync(`${dir}/t${(+t).toFixed(2).padStart(6, '0')}.jpg`, Buffer.from(data.split(',')[1], 'base64'));
    console.log(t, 'samples', n, Date.now() - t0, 'ms');
  }
  await b.close();
})();
