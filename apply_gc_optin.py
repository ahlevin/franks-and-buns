# v1.1: Game Center button shows for every app player; tapping it is the only way the sign-in sheet appears.
p='game.html'; s=open(p,encoding='utf-8').read()
E=[
("function gcShowBoard() {\n  const gc = gcPlugin(); if (!gc || !gcSignedIn) return;\n  gc.showLeaderboard({ leaderboardId: GC_BOARD }).catch(() => {});\n}",
 "function gcShowBoard() {\n  const gc = gcPlugin(); if (!gc) return;\n  if (gcSignedIn) { gc.showLeaderboard({ leaderboardId: GC_BOARD }).catch(() => {}); return; }\n  // Not signed in: only now, because the player tapped the button, show Apple's Game Center sign-in\n  gc.signIn({ present: true }).then(r => {\n    gcSignedIn = !!(r && r.signedIn);\n    if (gcSignedIn) { gcSubmitScore(score); gc.showLeaderboard({ leaderboardId: GC_BOARD }).catch(() => {}); }\n  }).catch(() => {});\n}"),
("function gcBtnVisible() { return state === STATE.GAMEOVER && gcSignedIn && !!gcPlugin(); }",
 "function gcBtnVisible() { return state === STATE.GAMEOVER && !!gcPlugin(); }"),
("// Game-over \"Game Center\" button (app only, once signed in)", "// Game-over \"Game Center\" button (app only; signs in only when tapped)"),
]
if 'present: true' in s: print('already applied'); raise SystemExit
for o,n in E:
    if s.count(o)!=1: raise SystemExit('anchor not found exactly once, nothing written: '+o[:60])
for o,n in E: s=s.replace(o,n,1)
open(p,'w',encoding='utf-8').write(s); print('Game Center sign-in is now tap-only')
