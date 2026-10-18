const puppeteer = require('puppeteer-core');
const [,, html, which, outdir] = process.argv;
(async () => {
  const b = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: 'new', args: ['--force-color-profile=srgb'] });
  const p = await b.newPage();
  await p.setViewport({ width: 1080, height: 1350 });
  await p.goto('file://' + html + '#' + which, { waitUntil: 'load' });
  await p.evaluate(() => document.fonts.ready);
  const n = await p.evaluate(() => window.__n);
  for (let i = 0; i < n; i++)
    await p.screenshot({ path: `${outdir}/${which}-${String(i+1).padStart(2,'0')}.png`, clip: { x: i*1080, y: 0, width: 1080, height: 1350 }, captureBeyondViewport: true });
  console.log(which, n);
  await b.close();
})();
