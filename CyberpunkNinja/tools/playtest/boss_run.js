// generic boss run: BOSS="start_chN,room,deadvar,secs,tag"; logs music, state and the aftermath
module.exports = async (page) => {
  const L = require('./lib.js')(page);
  const [ev, room, dv, secs, tag] = (process.env.BOSS).split(',');
  const extra = (process.env.VARS || '').split(',').filter(Boolean);
  const S = ['mode','room','hp','boss_on','music_cur','boss_hp', dv].concat(extra);
  const bc = async m => page.evaluate(m => { vm.runtime.startHats('event_whenbroadcastreceived', {BROADCAST_OPTION: m}); return 0; }, m);
  await L.W(1500); await bc(ev); await L.W(2500);
  for (let i=0;i<4;i++){ await L.W(600); await L.skipDialogue(30);}
  await L.sv('dmg_in', 0);
  if (process.env.KB) { await L.sv('kbranch', +process.env.KB); await L.sv('kuro_in', +process.env.KB === 1 ? 1 : 0); }
  if (process.env.SHARDS) await L.sv('shards', +process.env.SHARDS);
  await L.goto(+room, +(process.env.SX || -150), -124); await L.W(600);
  await page.evaluate(()=>{ bot.on=true; });
  const musicSprites = () => page.evaluate(() => vm.runtime.threads.filter(t => t.target && t.target.sprite && t.target.sprite.name.startsWith('Music_')).map(t => t.target.sprite.name + '@' + Math.round(t.target.volume)).join(' '));
  const t0 = Date.now();
  for (let k=0; k < +secs/5; k++) {
    await L.W(5000);
    const s = await L.g(S);
    console.log(tag, 't'+(k+1)*5, JSON.stringify(s), '| playing:', await musicSprites());
    if (k % 3 == 0) await L.shot(tag + '_' + k);
    if (+s[dv] >= 1) break;
  }
  await page.evaluate(()=>{ bot.on=false; });
  for (let i=0;i<24;i++){ await L.W(700); if (i % 3 == 0) await L.shot(tag + '_after' + i); await L.skipDialogue(2); const s = await L.g(S); if (i % 3 == 0) console.log(tag, 'after', i, JSON.stringify(s)); }
};
