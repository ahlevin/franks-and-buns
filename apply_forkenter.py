# Fair play: at high speed, forks finish rising (or lowering) into place before they reach the player.
p='game.html'; s=open(p,encoding='utf-8').read()
E=[
("    warned: false,\n  });",
 "    warned: false,\n"
 "    // finish entering by 60% of the way across, so the tines never sweep through the player at high speed\n"
 "    enterSpeed: Math.abs((fromBottom ? H + 120 : -120) - targetY) / Math.max(((W + 50) - W * 0.6) / scrollSpeed, 1),\n"
 "  });"),
("      const speed = 4.5 + boxesCompleted * 0.2;",
 "      const speed = Math.max(4.5 + boxesCompleted * 0.2, f.enterSpeed || 0);"),
("  if (clashes(targetY)) { nextForkDist = 40; return; }   // no fair spot right now; try again a little later\n",
 "  if (clashes(targetY)) return;   // no fair spot for this fork; skip it\n"),
]
if 'enterSpeed' in s: print('already applied'); raise SystemExit
for o,n in E:
    if s.count(o)!=1: raise SystemExit('anchor not found exactly once, nothing written: '+o[:60])
for o,n in E: s=s.replace(o,n,1)
open(p,'w',encoding='utf-8').write(s); print('fork entering rule added')
