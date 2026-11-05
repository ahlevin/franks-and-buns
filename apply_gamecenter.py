# v1.1: Game Center hooks for the iPhone app. Everything is skipped on the website
# (no native Game Center there), so the web game is unchanged.
p='game.html'; s=open(p,encoding='utf-8').read()
GC_JS = r'''loadRuns();
// ============================================================
// GAME CENTER (iPhone app only; does nothing on the website)
// ============================================================
const GC_BOARD = 'franksandbuns.highscore';
const GC_ACH = { firstbox: 'franksandbuns.firstbox', wienerwizard: 'franksandbuns.wienerwizard', dogparade: 'franksandbuns.dogparade' };
let gcSignedIn = false;
const gcSent = new Set();
function gcPlugin() {
  const C = window.Capacitor;
  if (!C || !C.isNativePlatform || !C.isNativePlatform()) return null;
  return (C.Plugins && C.Plugins.GameCenter) || (C.registerPlugin ? C.registerPlugin('GameCenter') : null);
}
function gcSignIn() {
  const gc = gcPlugin(); if (!gc) return;
  gc.signIn().then(r => { gcSignedIn = !!(r && r.signedIn); }).catch(() => {});
}
function gcSubmitScore(value) {
  const gc = gcPlugin(); if (!gc || !gcSignedIn || !(value > 0)) return;
  gc.submitScore({ leaderboardId: GC_BOARD, score: Math.floor(value) }).catch(() => {});
}
function gcAchieve(key) {
  const gc = gcPlugin(); if (!gc || !gcSignedIn || gcSent.has(key)) return;
  gcSent.add(key);
  gc.unlockAchievement({ achievementId: GC_ACH[key] }).catch(() => { gcSent.delete(key); });
}
function gcShowBoard() {
  const gc = gcPlugin(); if (!gc || !gcSignedIn) return;
  gc.showLeaderboard({ leaderboardId: GC_BOARD }).catch(() => {});
}
setTimeout(gcSignIn, 1500);
// Game-over "Game Center" button (app only, once signed in)
const GC_BTN = { w: 170, h: 32 };
function gcBtnRect() { return { x: W / 2 - GC_BTN.w / 2, y: H * 0.115 - GC_BTN.h / 2, w: GC_BTN.w, h: GC_BTN.h }; }
function gcBtnVisible() { return state === STATE.GAMEOVER && gcSignedIn && !!gcPlugin(); }
function drawGcButton() {
  if (!gcBtnVisible()) return;
  const r = gcBtnRect();
  ctx.save();
  ctx.fillStyle = 'rgba(0,0,0,0.55)'; ctx.strokeStyle = '#FFD700'; ctx.lineWidth = 1.5;
  ctx.beginPath(); ctx.roundRect(r.x, r.y, r.w, r.h, 16); ctx.fill(); ctx.stroke();
  ctx.fillStyle = '#FFD700'; ctx.font = 'bold 14px Arial'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.fillText('🏆 Game Center', W / 2, r.y + r.h / 2 + 1);
  ctx.restore();
}
function isGcTap(clientX, clientY) {
  if (!gcBtnVisible()) return false;
  const rect = canvas.getBoundingClientRect();
  const cx = (clientX - rect.left) * (W / rect.width), cy = (clientY - rect.top) * (H / rect.height);
  const r = gcBtnRect();
  return cx > r.x - 6 && cx < r.x + r.w + 6 && cy > r.y - 6 && cy < r.y + r.h + 6;
}
'''
E = [
  ("loadRuns();\n// ============================================================\n", GC_JS + "// ============================================================\n"),
  ("  lastRunIndex = bestRuns.indexOf(run);\n  try { localStorage.setItem(RUNS_KEY, JSON.stringify(bestRuns)); } catch (e) {}\n}",
   "  lastRunIndex = bestRuns.indexOf(run);\n  try { localStorage.setItem(RUNS_KEY, JSON.stringify(bestRuns)); } catch (e) {}\n  gcSubmitScore(score);\n}"),
  ("  if      (streak>=10){sm=3;streakText='WIENER WIZARD!';streakTimer=90;sndStreak();}",
   "  if      (streak>=10){sm=3;streakText='WIENER WIZARD!';streakTimer=90;sndStreak();gcAchieve('wienerwizard');}"),
  ("    boxFranks=0; boxesCompleted++;", "    boxFranks=0; boxesCompleted++; gcAchieve('firstbox');"),
  ("function startBonusRound() {\n", "function startBonusRound() {\n  gcAchieve('dogparade');\n"),
  ("  drawLeaderboard(H * 0.65);\n", "  drawLeaderboard(H * 0.65);\n  drawGcButton();\n"),
  ("  if (isMuteTap(t.clientX, t.clientY)) { muted = !muted; return; }\n  onTap();",
   "  if (isMuteTap(t.clientX, t.clientY)) { muted = !muted; return; }\n  if (isGcTap(t.clientX, t.clientY)) { gcShowBoard(); return; }\n  onTap();"),
  ("  if (isMuteTap(e.clientX, e.clientY)) { muted = !muted; return; }\n  onTap();",
   "  if (isMuteTap(e.clientX, e.clientY)) { muted = !muted; return; }\n  if (isGcTap(e.clientX, e.clientY)) { gcShowBoard(); return; }\n  onTap();"),
]
if 'GC_BOARD' in s: print('already applied'); raise SystemExit
for o, n in E:
    if s.count(o) != 1: raise SystemExit('anchor not found exactly once, nothing written: ' + o[:60])
for o, n in E: s = s.replace(o, n, 1)
open(p, 'w', encoding='utf-8').write(s); print('Game Center hooks added')
