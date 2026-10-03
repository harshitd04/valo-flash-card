// Usage: PAGE=yoru|neon node render-gif.mjs [full|inset|both] [--still t1,t2]
// Renders yoru.html frame by frame (window.renderAt) and encodes GIFs into ./out
// Reuses puppeteer + ffmpeg-static installed in ../3d-card-gif
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const req = createRequire(path.join(ROOT, '..', '3d-card-gif', 'package.json'));
const puppeteer = req('puppeteer');
const ffmpeg = req('ffmpeg-static');

const which = process.argv[2] && !process.argv[2].startsWith('--') ? process.argv[2] : 'both';
const stillIdx = process.argv.indexOf('--still');
const PAGE = process.env.PAGE || 'yoru';
const FPS = 20, PORT = 4174;
const MODES = which === 'both' ? ['full', 'inset'] : [which];
const INSET = process.env.INSET || '0.82';

const types = { '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png', '.json': 'application/json' };
const server = http.createServer((rq, res) => {
  const url = decodeURIComponent(rq.url.split('?')[0]);
  const file = path.join(ROOT, url === '/' ? PAGE + '.html' : url);
  fs.readFile(file, (err, buf) => {
    if (err) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { 'content-type': types[path.extname(file)] || 'application/octet-stream' });
    res.end(buf);
  });
});
await new Promise(r => server.listen(PORT, r));

const browser = await puppeteer.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const out = path.join(ROOT, 'out');
fs.mkdirSync(out, { recursive: true });

for (const mode of MODES) {
  const page = await browser.newPage();
  page.on('pageerror', e => console.log('[page error]', e.message));
  await page.setViewport({ width: 540, height: 960, deviceScaleFactor: 1 });
  await page.goto(`http://localhost:${PORT}/${PAGE}.html?fit=${mode}&inset=${INSET}&t=0`, { waitUntil: 'networkidle0' });
  await page.waitForFunction('document.body.dataset.ready === "1"', { timeout: 60000 });
  const L = await page.evaluate(() => window.LOOP);
  const N = Math.round(L * FPS);

  if (stillIdx > -1) {
    for (const t of process.argv[stillIdx + 1].split(',').map(Number)) {
      await page.evaluate(t => window.renderAt(t), t);
      await page.screenshot({ path: path.join(out, `still-${PAGE}-${mode}-${t}.png`) });
    }
    await page.close(); continue;
  }

  const dir = path.join(out, `frames-${PAGE}-${mode}`);
  fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
  for (let i = 0; i < N; i++) {
    await page.evaluate(t => window.renderAt(t), (i / N) * L);
    await page.screenshot({ path: path.join(dir, `f${String(i).padStart(4, '0')}.png`) });
    if (i % 40 === 0) console.log(`${mode}: frame ${i}/${N}`);
  }
  const gif = path.join(out, `${PAGE}-card-${mode}.gif`);
  const r = spawnSync(ffmpeg, ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', path.join(dir, 'f%04d.png'),
    '-vf', 'split[a][b];[a]palettegen=max_colors=200:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle',
    '-loop', '0', gif], { stdio: 'inherit' });
  if (r.status) throw new Error('ffmpeg failed');
  console.log(`done: ${gif} (${(fs.statSync(gif).size / 1048576).toFixed(1)} MB)`);
  await page.close();
}
await browser.close();
server.close();
