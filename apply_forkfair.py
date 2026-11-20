# Fair play: a fork never parks its tines at the height of a bun right next to it (that made some buns impossible).
p='game.html'; s=open(p,encoding='utf-8').read()
A=("  const targetY = fromBottom\n"
   "    ? H * 0.45 + Math.random() * H * 0.25   // reaches up into play area\n"
   "    : H * 0.15 + Math.random() * H * 0.2;  // reaches down from top\n")
N=("  const pickY = () => fromBottom\n"
   "    ? H * 0.45 + Math.random() * H * 0.25   // reaches up into play area\n"
   "    : H * 0.15 + Math.random() * H * 0.2;  // reaches down from top\n"
   "  // Fair play: forks and buns scroll together, so keep the tines away from the height of any bun close beside the fork\n"
   "  const tineAt = ty => fromBottom ? ty - 56 : ty + 56;\n"
   "  const clashes = ty => buns.some(b => Math.abs(b.x - (W + 50)) < 130 && Math.abs(tineAt(ty) - b.y) < FORK_BUN_CLEAR);\n"
   "  let targetY = pickY();\n"
   "  for (let k = 0; k < 12 && clashes(targetY); k++) targetY = pickY();\n"
   "  if (clashes(targetY)) { nextForkDist = 40; return; }   // no fair spot right now; try again a little later\n")
B=("  let y = type.yRange[0]*H + Math.random()*(type.yRange[1]-type.yRange[0])*H;\n")
C=("    y = lo <= hi ? Math.min(Math.max(y, lo), hi) : prev.y;\n"
   "  }\n")
C2=C+("  // Fair play: don't put a bun at the height of fork tines parked right beside it\n"
     "  for (const f of forks) {\n"
     "    if (Math.abs(f.x - (W + 60)) >= 130) continue;\n"
     "    const tine = f.fromBottom ? f.targetY - 56 : f.targetY + 56;\n"
     "    if (Math.abs(tine - y) < FORK_BUN_CLEAR) y = (y < tine ? tine - FORK_BUN_CLEAR : tine + FORK_BUN_CLEAR);\n"
     "  }\n"
     "  y = Math.min(Math.max(y, H * 0.12), H * 0.75);\n")
K="let buns = [], nextBunDist = 0;"
K2=K+"\nconst FORK_BUN_CLEAR = 80;   // minimum height gap between a bun and fork tines beside it"
if 'FORK_BUN_CLEAR' in s: print('already applied'); raise SystemExit
for o in (A,C,K):
    if s.count(o)!=1: raise SystemExit('anchor not found exactly once, nothing written: '+o[:60])
s=s.replace(A,N,1).replace(C,C2,1).replace(K,K2,1)
open(p,'w',encoding='utf-8').write(s); print('fork/bun spacing rule added')
