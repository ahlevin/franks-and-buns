# v1.1: Game Center is not contacted at all until the player taps the Game Center button.
# (iOS 26 shows its own "better with Game Center" sheet as soon as an app checks sign-in.)
import sys
p = sys.argv[1] if len(sys.argv) > 1 else 'game.html'
s = open(p, encoding='utf-8').read()
def rep(old, new):
    global s
    assert s.count(old) == 1, ('not found once', old[:60]); s = s.replace(old, new)
rep("""function gcSignIn() {
  const gc = gcPlugin(); if (!gc) return;
  gc.signIn().then(r => { gcSignedIn = !!(r && r.signedIn); }).catch(() => {});
}""", """const GC_OPTIN = 'fb_gc_optin';   // set once the player has tapped the Game Center button
let gcNoteUntil = 0;
function gcOptedIn() { try { return localStorage.getItem(GC_OPTIN) === '1'; } catch (e) { return false; } }
function gcSetOptIn(on) { try { on ? localStorage.setItem(GC_OPTIN, '1') : localStorage.removeItem(GC_OPTIN); } catch (e) {} }
function gcSignIn() {
  // Quiet sign-in at launch ONLY for players who already chose Game Center before
  const gc = gcPlugin(); if (!gc || !gcOptedIn()) return;
  gc.signIn().then(r => { gcSignedIn = !!(r && r.signedIn); if (!gcSignedIn) gcSetOptIn(false); }).catch(() => {});
}""")
rep("""  gc.signIn({ present: true }).then(r => {
    gcSignedIn = !!(r && r.signedIn);
    if (gcSignedIn) { gcSubmitScore(score); gc.showLeaderboard({ leaderboardId: GC_BOARD }).catch(() => {}); }
  }).catch(() => {});""", """  gc.signIn({ present: true }).then(r => {
    gcSignedIn = !!(r && r.signedIn);
    gcSetOptIn(gcSignedIn);
    if (gcSignedIn) { gcSubmitScore(score); gc.showLeaderboard({ leaderboardId: GC_BOARD }).catch(() => {}); }
    else gcNoteUntil = performance.now() + 5000;
  }).catch(() => { gcNoteUntil = performance.now() + 5000; });""")
rep("""  ctx.fillText('🏆 Game Center', W / 2, r.y + r.h / 2 + 1);
  ctx.restore();""", """  ctx.fillText('🏆 Game Center', W / 2, r.y + r.h / 2 + 1);
  if (performance.now() < gcNoteUntil) {
    ctx.fillStyle = '#FFFFFF'; ctx.font = 'bold 12px Arial';
    ctx.fillText('Sign in to Game Center in the Settings app', W / 2, r.y + r.h + 14);
  }
  ctx.restore();""")
open(p, 'w', encoding='utf-8').write(s); print('ok', p)
