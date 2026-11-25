// usage: node render.js <width> <out.mp4> [workers] [audio]
const { chromium } = require('playwright');
const { spawn, execFileSync } = require('child_process');
const fs = require('fs');
(async () => {
  const [w, out, nw = '4', audio] = process.argv.slice(2);
  const b = await chromium.launch();
  const probe = await b.newPage(); await probe.goto(`http://127.0.0.1:8765/film.html?w=${w}`);
  const dur = await probe.evaluate(() => CUES.duration); await probe.close();
  const total = Math.round(dur * 30), W = +nw, per = Math.ceil(total / W);
  const t0 = Date.now();
  await Promise.all([...Array(W)].map(async (_, k) => {
    const a = k * per, e = Math.min(total, a + per);
    const p = await b.newPage(); p.on('pageerror', er => console.log('ERR', er.message));
    await p.goto(`http://127.0.0.1:8765/film.html?w=${w}`); await p.evaluate(() => window.ready);
    const ff = spawn('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-pix_fmt', 'yuv420p', '-r', '30', `seg${k}.mp4`]);
    ff.stderr.on('data', d => console.log('ffmpeg', String(d)));
    for (let f = a; f < e; f++) {
      const d = await p.evaluate(f => { window.renderFrame(f / 30, f); return document.querySelector('canvas').toDataURL('image/jpeg', 0.96); }, f);
      const buf = Buffer.from(d.slice(d.indexOf(',') + 1), 'base64');
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (k === 0 && f % 30 === 0) console.log(`worker0 ${f - a}/${e - a}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }));
  await b.close();
  fs.writeFileSync('segs.txt', [...Array(W)].map((_, k) => `file seg${k}.mp4`).join('\n'));
  const args = ['-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', 'segs.txt'];
  if (audio) args.push('-i', audio, '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '256k', '-af', 'apad', '-t', String(total / 30));
  args.push('-c:v', 'copy', '-movflags', '+faststart', out);
  execFileSync('ffmpeg', args, { stdio: 'inherit' });
  console.log('done', out, ((Date.now() - t0) / 1000).toFixed(0) + 's');
})();
