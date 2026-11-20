# Fair play: if a fork sits between two buns, only ask the player to cross its tines when there is time to do it after the fork passes.
p='game.html'; s=open(p,encoding='utf-8').read()
O=("  // Fair play: don't put a bun at the height of fork tines parked right beside it\n")
N=("  // Fair play: a fork between the previous bun and this one must not wall off the climb or drop between them\n"
   "  if (prev) {\n"
   "    for (const f of forks) {\n"
   "      if (f.x <= prev.x || f.x >= W + 60) continue;\n"
   "      const tine = f.fromBottom ? f.targetY - 56 : f.targetY + 56;\n"
   "      const lowY = Math.min(prev.y, y) - FORK_BUN_CLEAR, highY = Math.max(prev.y, y) + FORK_BUN_CLEAR;\n"
   "      if (tine < lowY || tine > highY) continue;                         // tines are clear of the path\n"
   "      const after = ((W + 60) - f.x - 75) / scrollSpeed;                 // frames left once the fork has passed\n"
   "      if (after >= Math.abs(y - prev.y) / 3.2 + 8) continue;             // enough time to make the move after it\n"
   "      y = prev.y > tine ? Math.max(y, tine + FORK_BUN_CLEAR) : Math.min(y, tine - FORK_BUN_CLEAR);  // stay on the player's side\n"
   "    }\n"
   "  }\n")+O
if 'wall off the climb' in s: print('already applied'); raise SystemExit
if s.count(O)!=1: raise SystemExit('anchor not found exactly once, nothing written')
s=s.replace(O,N,1); open(p,'w',encoding='utf-8').write(s); print('fork crossing rule added')
