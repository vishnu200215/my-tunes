const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const [w, dir, ...views] = process.argv.slice(2); fs.mkdirSync(dir, { recursive: true });
  const b = await chromium.launch(); const p = await b.newPage();
  p.on('pageerror', e => console.log('ERR', e.message)); p.on('console', m => { if (!/GPU stall|GL Driver/.test(m.text())) console.log('page:', m.text()); });
  await p.goto(`http://127.0.0.1:8765/scene3d.html?w=${w}`); 
  let t0 = Date.now(); await p.evaluate(() => window.ready); console.log('init', Date.now() - t0);
  for (const v of views) { t0 = Date.now();
    const d = await p.evaluate(v => { window.views[v](); return document.querySelector('canvas').toDataURL('image/jpeg', 0.92); }, v);
    fs.writeFileSync(`${dir}/${v}.jpg`, Buffer.from(d.split(',')[1], 'base64')); console.log(v, Date.now() - t0, 'ms'); }
  await b.close();
})();
