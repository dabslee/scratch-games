window.bot = {on:false, ev:[], held:new Set(), taps:[], stats:{deflectPress:0, dash:0, atk:0, jump:0}};
function lvars(t){ const o={}; for (const id in t.variables) o[t.variables[id].name]=t.variables[id].value; return o; }
window.clonesOf = (name)=>vm.runtime.targets.filter(t=>!t.isOriginal && t.sprite.name===name).map(t=>lvars(t));
const KMAP={left:'ArrowLeft',right:'ArrowRight',up:'ArrowUp',down:'ArrowDown'};
function hold(k,on){ k=KMAP[k]||k; if(on && !bot.held.has(k)){bot.held.add(k); key(k,true);} if(!on && bot.held.has(k)){bot.held.delete(k); key(k,false);} }
bot.cool={}; bot.tick=0;
function tap(k){ k=KMAP[k]||k; if ((bot.cool[k]||-99) > bot.tick-4) return; bot.cool[k]=bot.tick; key(k,true); bot.taps.push([k,2]); }
window.botTick = ()=>{
  bot.tick++;
  // release taps
  bot.taps = bot.taps.filter(([k,n])=>{ if(n<=1){ key(k,false); return false;} return true; }).map(([k,n])=>[k,n-1]);
  if(!bot.on) { for(const k of [...bot.held]) hold(k,false); return; }
  const mode=gv('mode');
  if(mode==='dlg'){ hold('left',false); hold('right',false); if(Math.random()<0.3) tap('e'); return; }
  if(mode!=='play') return;
  const px=+gv('px'), py=+gv('py'), pst=gv('pst');
  const T=gv('ent_type'), EX=gv('ent_x').map(Number), EY=gv('ent_y').map(Number), AL=gv('ent_alive').map(Number), FO=gv('ent_foe').map(Number), ST=gv('ent_stag').map(Number);
  let danger=null;
  for (const h of clonesOf('HannyaBoy')) { if (h.st==='wind' && Math.abs(h.x-px)<70) danger={kind: +h.breach? 'breach':'parry', t:+h.t, at:22, x:+h.x}; }
  for (const h of clonesOf('HannyaBoy')) { if (h.st==='crouch' && Math.abs(h.x-px)<170) danger={kind:'parry', t:+h.t, at:19, x:+h.x}; }
  for (const a of clonesOf('Dobunushi')) { if (a.role==='arm' && Math.abs(+a.tx-px)<44) { if (a.st==='rear') danger={kind:'parry', t:+a.t, at:33-6*(+gv('dobu_ph')-1), x:+a.tx}; if (a.st==='slam') danger={kind:'parry', t:9, at:0, x:+a.tx}; } }
  for (const h of clonesOf('Harmacist')) { const dx=Math.abs(h.x-px); if (h.st==='slash' && dx<75) danger={kind:'parry', t:+h.t, at:12, x:+h.x}; if (h.st==='burst' && dx<120) danger={kind:'breach', t:+h.t, at:24, x:+h.x}; }
  for (const o of clonesOf('BigOni')) { const dx=Math.abs(o.x-px); if (o.st==='swing' && dx<150) danger={kind:'parry', t:+o.t, at:14, x:+o.x}; if (o.st==='slam' && dx<170) danger={kind:'breach', t:+o.t, at:36, x:+o.x}; }
  for (const l of clonesOf('LadyLuck')) { const dx=Math.abs(l.x-px); if (l.st==='slash' && dx<90) { const tt=+l.t; danger={kind:'parry', t: (tt<=12? tt : tt-18), at:12, x:+l.x}; } if (l.st==='skull' && dx<200) danger={kind:'breach', t:+l.t, at:30, x:+l.x}; }
  for (const w of clonesOf('Warden')) { const dx=Math.abs(w.x-px); if (w.st==='combo' && dx<80) { const tt=+w.t; danger={kind:'parry', t:(tt<=16? tt : tt-14), at:16, x:+w.x}; } if (w.st==='heavy' && dx<90) danger={kind:'breach', t:+w.t, at:24, x:+w.x}; }
  for (const m of clonesOf('Mukuro')) { if (m.role==='shadow') continue; const dx=Math.abs(m.x-px); if (m.st==='combo' && +m.ci>0 && dx<(m.ck==='lunge'?220:95)) danger={kind: +m.bb===1?'breach':'parry', t:+m.t, at:+m.ht, x:+m.x}; }
  for (const b of clonesOf('Projectiles')) if (b.kind==='shell' && b.owner==='e') { const d=Math.hypot(b.x-px, b.y-(py+18)); const sp=Math.hypot(+b.vx,+b.vy)+0.01; if ((d-14)/sp <= 2.5) danger={kind:'parry', t:1, at:1, x:+b.x}; }
  if (clonesOf('Raijin').length) { const arm=+gv('rj_arm'); if (arm>px && arm<900 && (arm-px-12)/11 <= 2.5) danger={kind:'parry',t:1,at:1,x:arm};
    const plow=+gv('rj_plow'); if (plow<900 && plow-px>20 && plow-px<120 && pst!=='dash') { tap('up'); bot.stats.jump++; }
    const RZ=gv('RZ'); if (!danger && RZ && RZ.length===4 && clonesOf('Raijin').length) { const seg=Math.min(3,Math.max(0,Math.floor((px+240)/120))); if (+RZ[seg]>=1) { let best=-1,bd=9; for(let k=0;k<4;k++) if(+RZ[k]===0 && Math.abs(k-seg)<bd){bd=Math.abs(k-seg);best=k;} if(best>=0){ const cxz=-180+best*120; hold(cxz>px?'right':'left',true); hold(cxz>px?'left':'right',false); if (Math.abs(cxz-px)>60 && Math.random()<0.2) tap(' '); return; } } } }
  for (const k of clonesOf('KuroBoss')) { if (k.role!=='body') { const ex = k.role==='echo1'? +gv('ke1') : +gv('ke2'); if (ex<900 && Math.abs(ex-px)<70 && Math.abs(ex-px)>20) { tap('up'); bot.stats.jump++; } continue; }
      const dx=Math.abs(k.x-px);
      if ((k.st==='combo' || k.st==='blink') && dx<95) danger={kind:'parry', t:+k.t, at:(k.st==='blink'?26:+k.ht), x:+k.x};
      if (k.st==='cut') { const tt=+k.t; const eta = tt<30 ? 30-tt + Math.max(0,(dx-30)/16) : Math.max(0,(dx-24)/16); if (eta<=6 && pst!=='dash') { hold(k.x>px?'right':'left',true); hold(k.x>px?'left':'right',false); tap(' '); bot.stats.dash++; return; } if (tt<30) { hold('left',false); hold('right',false); return; } } }
  for (const m of clonesOf('Mukuro')) { if (m.role!=='body') continue; const dx=Math.abs(m.x-px);
      if (m.st==='shadow') { const tt=+m.t; if (tt<=18) danger={kind:'parry',t:tt,at:18,x:+gv('sh_x')}; else danger={kind:'parry',t:tt,at:30,x:+m.x}; }
      if (m.st==='dive' && +m.t>=20) { danger={kind:'breach', t:+m.t, at:42, x:+m.x}; }
      if (m.st==='kneel') { /* finish him off for the test */ } }
  for (const m of clonesOf('Daimyo')) { if (m.role!=='body') continue; const dx=Math.abs(m.x-px); const tt=+m.t;
      if (+gv('dm_ph')===1) {
        if (m.st==='iaido' && dx<150) danger={kind:'parry', t:tt, at:26, x:+m.x};
        if (m.st==='combo' && dx<110) danger={kind:'parry', t:(tt<=26?tt:(tt<=42?tt-16:tt-32)), at:26, x:+m.x};
        if (m.st==='stomp' && dx<80) danger={kind:'breach', t:tt, at:30, x:+m.x};
        if (m.st==='charge' && tt>=30 && dx<90) danger={kind:'breach', t:99, at:0, x:+m.x};
        if (m.st==='charge' && tt<30) { const eta=30-tt+Math.max(0,(dx-20)/14); if (eta<=5) danger={kind:'breach', t:99, at:0, x:+m.x}; }
      } else if (+gv('dm_ph')===3) {
        if (m.st==='draw' && dx<200) danger={kind:'parry', t:tt, at:26, x:+m.x};
        if (m.st==='grab' && dx<150) danger={kind:'breach', t:tt, at:24, x:+m.x};
        if ((m.st==='storm'||m.st==='rend'||m.st==='cut3'||m.st==='riposte') && dx<110) { const H=(gv('dm_hits')||[]).map(Number); const nh=H[(+m.hi)-1]; if (nh!==undefined) danger={kind:'parry', t:tt, at:nh, x:+m.x}; }
      } else if (false && m.st==='swoop' && tt>=18 && tt<40) { const mx=+gv('mk_x'), my=+gv('mk_y'); if (Math.hypot(mx-px, my-py-18)<90) danger={kind:'breach', t:99, at:0, x:mx}; } }
  for (const z of clonesOf('SweepLaser')) { const d=z.x-px; if (Math.abs(d)<46 && Math.sign(-d)===Math.sign(+z.t<75? +z.vx : -z.vx)) { danger={kind:'breach', t:99, at:0, x:+z.x}; } }
  for (const d of clonesOf('ScavDrone')) { if (d.st==='dive' && Math.hypot(d.x-px, d.y-(py+18))<60) danger={kind:'parry', t:1, at:1, x:+d.x}; }
  for (const b of clonesOf('Projectiles')) {
    if (b.owner==='e' && Math.abs(b.y-(py+18))<34) { const dist=(b.x-px)*Math.sign(-b.vx); if (dist>0 && dist<32) danger={kind:'parry', t:1, at:1, x:+b.x}; }
    if (b.kind==='wave' && Math.abs(b.x-px)<70 && Math.sign(px-b.x)===Math.sign(+b.vx)) { tap('up'); bot.stats.jump++; }
  }
  if (danger) {
    hold('left',false); hold('right',false);
    if (danger.kind==='parry' && danger.t>=danger.at-2) { if (pst!=='deflect' && pst!=='block'){ tap('down'); bot.stats.deflectPress++; } return; }
    if (danger.kind==='breach' && danger.t>=danger.at-6) { hold(danger.x>px?'right':'left',true); tap(' '); bot.stats.dash++; return; }
    return;
  }
  if (bot.noMove) { hold('left',false); hold('right',false); return; }
  // choose target
  let best=-1, bd=1e9;
  for (let i=0;i<T.length;i++){ if(AL[i]===1 && (FO[i]===1 || T[i]==='crate')){ const d=Math.abs(EX[i]-px)+Math.abs(EY[i]-py)*0.5; if(d<bd){bd=d;best=i;} } }
  if (best<0) { hold('left',false); hold(bot.goLeft?'left':'right',true); hold(bot.goLeft?'right':'left',false); if (Math.random()<0.04) tap('up'); return; }
  const dx=EX[best]-px, dy=EY[best]-py;
  if (bot.relDown>0) { bot.relDown--; if (bot.relDown===0) hold('down',false); }
  if (dy < -40 && Math.abs(dx) < 80 && Math.random()<0.15) { hold('left',false); hold('right',false); hold('down',true); tap(' '); bot.relDown=3; return; }
  if (clonesOf('Daimyo').some(c=>c.role==='body' && c.st==='counter')) { hold('left',false); hold('right',false); return; }
  if (bot.pendX>0){ bot.pendX--; if(bot.pendX==0){ tap('x'); bot.stats.heavy=(bot.stats.heavy||0)+1; } return; }
  if ((T[best]==='oni'||T[best]==='dobu'||T[best]==='harm'||T[best]==='luck'||T[best]==='mukuro'||T[best]==='raijin'||T[best]==='kuro'||T[best]==='daimyo') && Math.abs(dx)<110 && Math.abs(dx)>40 && Math.random()<0.06) { hold(dx>0?'right':'left',true); tap(' '); bot.pendX=2; return; }
  if (ST[best]===1 && Math.abs(dx)<60) { hold('left',false); hold('right',false); tap('x'); bot.stats.atk++; return; }
  if (Math.abs(dx)>34) { hold(dx>0?'right':'left',true); hold(dx>0?'left':'right',false); if (Math.random()<0.02) tap('up'); }
  else { hold('left',false); hold('right',false); if (dx*(+gv('pface'))<0) { tap(dx>0?'right':'left'); } }
  if (Math.abs(dx)<46) {
    if (dy>40 && dy<120 && Math.random()<0.25) { tap('up'); }
    if (Math.random()<0.5) { tap('x'); bot.stats.atk++; }
  }
  if (+gv('hp')<5 && +gv('gourd')>0 && Math.random()<0.05) tap('r');
};
window.hookBot = ()=>{ const rt=vm.runtime; const orig=rt._step.bind(rt); rt._step=function(){ try{botTick();}catch(e){console.log('boterr '+e);} orig(); }; };
// --- frame-accurate input replay: steps = [[frames, 'keys held', 'keys tapped at start'], ...]
window.seq = {steps:[], i:0, f:0, held:new Set(), log:[]};
window.runSeq = (steps)=>{ seq.steps=steps; seq.i=0; seq.f=0; seq.log=[]; };
const _botTick = window.botTick;
window.botTick = ()=>{
  if (seq.i < seq.steps.length) {
    bot.tick++;
    bot.taps = bot.taps.filter(([k,n])=>{ if(n<=1){ key(k,false); return false;} return true; }).map(([k,n])=>[k,n-1]);
    const [n, holdS, tapS] = seq.steps[seq.i];
    const want = new Set((holdS||'').split(' ').filter(Boolean).map(k=>KMAP[k]||k));
    for (const k of [...seq.held]) if (!want.has(k)) { key(k,false); seq.held.delete(k); }
    for (const k of want) if (!seq.held.has(k)) { key(k,true); seq.held.add(k); }
    if (seq.f === 0 && tapS) for (const k of tapS.split(' ')) { const kk = k==='space'?' ':(KMAP[k]||k); key(kk,true); bot.taps.push([kk,2]); }
    if (gv('mode')==='play') seq.f++;
    seq.log.push([gv('frame'), seq.i, (+gv('px')).toFixed(1), (+gv('py')).toFixed(1), gv('pst'), lv('Hotaru','cling'), gv('room')].join(' '));
    if (seq.f >= n) { seq.i++; seq.f = 0; }
    if (seq.i >= seq.steps.length) for (const k of [...seq.held]) { key(k,false); seq.held.delete(k); }
    return;
  }
  _botTick();
};
