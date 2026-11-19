# v1.1 (app only): on iPad and iPhone Duo the game scales up to fill the screen height,
# and the space at the sides shows the kitchen wall instead of black. Gameplay is unchanged.
p='game.html'; s=open(p,encoding='utf-8').read()
OLD = """function resize() {
  const dpr = window.devicePixelRatio || 1;
  const maxW = 420, maxH = 740;
  let w = Math.min(window.innerWidth, maxW);
  let h = Math.min(window.innerHeight, maxH);
  canvas.style.width = w + 'px';
  canvas.style.height = h + 'px';
  canvas.width = w * dpr;
  canvas.height = h * dpr;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  return { w, h };
}"""
NEW = """function resize() {
  const dpr = window.devicePixelRatio || 1;
  const maxW = 420, maxH = 740;
  let w = Math.min(window.innerWidth, maxW);
  let h = Math.min(window.innerHeight, maxH);
  // App on a big screen (iPad, iPhone Duo open): keep the same 420x740 game, drawn larger to fill the height
  const C = window.Capacitor, inApp = !!(C && C.isNativePlatform && C.isNativePlatform());
  let scale = 1;
  if (inApp) {
    const chrome = ['game-header', 'game-footer'].reduce((t, id) => { const el = document.getElementById(id); return t + (el ? el.offsetHeight : 0); }, 0);
    const availH = window.innerHeight - chrome, availW = window.innerWidth;
    if (availW >= 600 && availH >= 600) { w = maxW; h = maxH; scale = Math.min(availH / maxH, availW / maxW); }
    document.body.classList.toggle('fb-wide', scale > 1 && availW > w * scale + 8);   // iPad / open Duo only; phones keep the plain dark edge
    ['game-header', 'game-footer'].forEach(id => { const el = document.getElementById(id); if (el) el.style.maxWidth = Math.round(w * scale) + 'px'; });
  }
  canvas.style.width = (w * scale) + 'px';
  canvas.style.height = (h * scale) + 'px';
  canvas.width = Math.round(w * scale * dpr);
  canvas.height = Math.round(h * scale * dpr);
  ctx.setTransform(dpr * scale, 0, 0, dpr * scale, 0, 0);
  return { w, h };
}"""
CSS_O = "  canvas { display: block; margin: 0 auto; background: #2d1b0e; flex-shrink: 0; }\n"
CSS_N = CSS_O + "  /* app on iPad / iPhone Duo: kitchen wall beside the game instead of black bars */\n  body.fb-wide { background: linear-gradient(rgba(17,8,0,0.55), rgba(17,8,0,0.55)), url('bg-wall-a.jpg') center top / auto 100% repeat-x, #110800; }\n"
if 'fb-wide' in s: print('already applied'); raise SystemExit
for o in (OLD, CSS_O):
    if s.count(o) != 1: raise SystemExit('anchor not found exactly once, nothing written: ' + o[:50])
s = s.replace(OLD, NEW, 1).replace(CSS_O, CSS_N, 1)
open(p, 'w', encoding='utf-8').write(s); print('big-screen layout added (app only)')
