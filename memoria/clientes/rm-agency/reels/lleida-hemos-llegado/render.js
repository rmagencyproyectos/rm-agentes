const puppeteer = require('puppeteer-core');
const { spawn } = require('child_process');
const [,, html, out, mode, ffmpeg] = process.argv;
(async () => {
  const b = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: 'new', args: ['--hide-scrollbars','--force-color-profile=srgb'] });
  const p = await b.newPage();
  await p.setViewport({ width: 1080, height: 1920, deviceScaleFactor: 1 });
  await p.goto('file://' + html + '#render' + (mode === 'stills-safe' ? '' : ''), { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  if (mode && mode.startsWith('stills')) {
    if (mode === 'stills-safe') await p.evaluate(() => document.body.classList.add('safe'));
    const ts = JSON.parse(process.argv[6]);
    for (const t of ts) { await p.evaluate(t => __render(t), t); await p.screenshot({ path: `${out}/s_${t}.png` }); }
  } else {
    const fps = 30, total = await p.evaluate(() => __total), n = Math.ceil(total / 1000 * fps);
    const ff = spawn(ffmpeg, ['-y','-f','image2pipe','-framerate',String(fps),'-i','-','-c:v','libx264','-pix_fmt','yuv420p','-profile:v','high','-crf','16','-preset','slow','-movflags','+faststart', out], { stdio: ['pipe','ignore','inherit'] });
    for (let f = 0; f < n; f++) {
      await p.evaluate(t => __render(t), f * 1000 / fps);
      const buf = await p.screenshot({ type: 'jpeg', quality: 95 });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
    console.log('frames', n);
  }
  await b.close();
})();
