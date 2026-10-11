// per-frame tell audit: every white flash (brightness 100) on SPR's clones, its length,
// and how many frames after it starts the next hit/deflect lands (hitstop rising)
module.exports = async (page) => {
  const L = require('./lib.js')(page);
  const [ev, room, secs] = process.env.BOSS.split(',');
  const bc = async m => page.evaluate(m => { vm.runtime.startHats('event_whenbroadcastreceived', {BROADCAST_OPTION: m}); return 0; }, m);
  await L.W(1500); await bc(ev); await L.W(2500);
  for (let i=0;i<4;i++){ await L.W(600); await L.skipDialogue(30);}
  await L.sv('dmg_in', 0);
  for (const kv of (process.env.SET || '').split(';').filter(Boolean)) { const [k, v] = kv.split('='); await L.sv(k, isNaN(+v) ? v : +v); }
  await L.goto(+room, +(process.env.SX || -150), +(process.env.SY || -124)); await L.W(600);
  await page.evaluate((spr) => {
    window.REC = []; let f = 0; let hs = 0;
    const orig = vm.runtime._step.bind(vm.runtime);
    vm.runtime._step = function () {
      orig(); f++;
      const h = +gv('hitstop'); const rise = h > hs && h > 0; hs = h;
      const cl = vm.runtime.targets.filter(t => !t.isOriginal && t.sprite.name === spr && t.visible);
      const fl = cl.filter(t => (t.effects.brightness || 0) >= 100).map(t => { const v = lvars(t); return (v.role || '') + ':' + (v.ck ? v.ck + '/' : '') + (v.role === 'man' ? gv('dm_st') + '@' + gv('dm_t') : v.st + '@' + v.t); });
      window.REC.push({f, fl, rise, mode: gv('mode')});
    };
  }, process.env.SPR);
  if (!process.env.NOBOT) await page.evaluate(()=>{ bot.on=true; });
  if (process.env.NOBOT) { for (let i = 0; i < +secs * 2; i++) { await L.W(500); await L.skipDialogue(2); } } else await L.W(+secs * 1000);
  await page.evaluate(()=>{ bot.on=false; });
  const R = await page.evaluate(() => window.REC);
  // runs
  let run = null; const runs = [];
  for (let i = 0; i < R.length; i++) {
    const on = R[i].fl.length > 0;
    if (on && !run) run = {s: i, first: R[i].fl.join(' ')};
    if (!on && run) { run.e = i - 1; run.last = R[i-1].fl.join(' '); runs.push(run); run = null; }
  }
  const tally = {};
  for (const r of runs) {
    let hit = -1; for (let j = r.s; j < Math.min(R.length, r.s + 40); j++) if (R[j].rise) { hit = j - r.s; break; }
    const len = r.e - r.s + 1;
    const key = r.first.split('@')[0] + ' len ' + len + ' lands+' + hit;
    tally[key] = (tally[key] || 0) + 1;
    if (process.env.V) console.log(r.first, '->', r.last, 'len', len, 'lands', hit);
  }
  for (const k of Object.keys(tally).sort()) console.log(tally[k] + 'x', k);
};
