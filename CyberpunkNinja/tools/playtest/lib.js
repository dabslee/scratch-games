module.exports = (page) => {
  const L = {};
  L.W = ms => page.waitForTimeout(ms);
  L.shot = async n => { await page.screenshot({path: `s_${n}.png`}); };
  L.g = async names => page.evaluate(ns => Object.fromEntries(ns.map(n => [n, gv(n)])), names);
  L.log = async (label, names) => console.log(label, JSON.stringify(await L.g(names)));
  L.down = async k => page.evaluate(k => key(k, true), k);
  L.up = async k => page.evaluate(k => key(k, false), k);
  L.press = async (k, ms=160) => { await L.down(k); await L.W(ms); await L.up(k); await L.W(40); };
  L.hold = async (keys, ms) => { for (const k of keys) await L.down(k); await L.W(ms); for (const k of keys) await L.up(k); };
  L.sv = async (n, v) => page.evaluate(([n, v]) => sv(n, v), [n, v]);
  L.until = async (expr, timeout=8000) => { const t0 = Date.now(); while (Date.now() - t0 < timeout) { if (await page.evaluate(expr)) return true; await L.W(50);} return false; };
  L.skipDialogue = async (max=20) => { for (let i=0;i<max;i++){ if (!(await page.evaluate(()=>gv('mode')==='dlg'))) return; await L.W(300); await L.press('e'); } };
  L.goto = async (room, x, y) => { await page.evaluate(([r,x,y])=>{sv('cp_x',x);sv('cp_y',y);sv('want_room',r);sv('enter_dir','C');}, [room,x,y]); await L.W(700); };
  L.newGame = async () => { await L.W(1200); await L.press(' '); await L.W(400); await L.press('Enter'); await L.W(1500); };
  return L;
};
