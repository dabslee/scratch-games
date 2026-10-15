// Serves this folder, opens harness.html in headless Chromium, loads the .sb3 named on the
// command line and runs a test script against it: node shot.js game.sb3 boss_run.js
// CHROME_PATH picks the browser; without it, Playwright's own (npx playwright-core install chromium).
const { chromium } = require('playwright-core');
const http = require('http'); const fs=require('fs'); const path=require('path');
const root = __dirname;
const srv = http.createServer((req,res)=>{ let p = path.join(root, decodeURIComponent(req.url.split('?')[0])); if(!fs.existsSync(p)){res.writeHead(404);res.end();return;} res.writeHead(200,{'Content-Type': p.endsWith('.html')?'text/html':p.endsWith('.js')?'application/javascript':'application/octet-stream'}); fs.createReadStream(p).pipe(res);});
const PORT=+(process.env.PORT||8123); srv.listen(PORT, async ()=>{
  const browser = await chromium.launch({executablePath: process.env.CHROME_PATH || undefined, args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist','--autoplay-policy=no-user-gesture-required']});
  const page = await browser.newPage({viewport:{width:480,height:360}});
  page.on('console', m=>{const t=m.text(); if(!t.includes('audio engine')&&!t.includes('GPU stall')&&!t.includes('404')) console.log('PAGE:', t.slice(0,300));});
  page.on('pageerror', e=>console.log('PAGEERR:', e.message));
  await page.goto('http://localhost:'+PORT+'/' + (process.env.HARNESS||'harness.html'));
  const n = await page.evaluate(u=>boot(u), process.argv[2]);
  console.log('targets', n);
  const script = process.argv[3] ? require(path.resolve(process.argv[3])) : async(page)=>{await page.waitForTimeout(1500); await page.screenshot({path:'out.png'});};
  await script(page);
  await browser.close(); srv.close();
});
