# No fork through a bun: keep buns clear of the whole fork (tines and the chef's arm), not just the tines.
p='game.html'; s=open(p,encoding='utf-8').read()
E=[
("  const clashes = ty => buns.some(b => Math.abs(b.x - (W + 50)) < 130 && Math.abs(tineAt(ty) - b.y) < FORK_BUN_CLEAR);\n",
 "  const clashes = ty => buns.some(b => {\n"
 "    const dx = Math.abs(b.x - (W + 50));\n"
 "    if (dx < 130 && Math.abs(tineAt(ty) - b.y) < FORK_BUN_CLEAR) return true;                 // tines at the bun's height\n"
 "    if (dx < 100 && (fromBottom ? b.y > tineAt(ty) : b.y < tineAt(ty))) return true;           // the arm would pass through the bun\n"
 "    return false;\n"
 "  });\n"),
("    if (Math.abs(tine - y) < FORK_BUN_CLEAR) y = (y < tine ? tine - FORK_BUN_CLEAR : tine + FORK_BUN_CLEAR);\n",
 "    if (Math.abs(tine - y) < FORK_BUN_CLEAR) y = (y < tine ? tine - FORK_BUN_CLEAR : tine + FORK_BUN_CLEAR);\n"
 "    if (Math.abs(f.x - (W + 60)) < 100) y = f.fromBottom ? Math.min(y, tine - FORK_BUN_CLEAR) : Math.max(y, tine + FORK_BUN_CLEAR);  // never inside the arm\n"),
]
if 'the arm would pass through the bun' in s: print('already applied'); raise SystemExit
for o,n in E:
    if s.count(o)!=1: raise SystemExit('anchor not found exactly once, nothing written: '+o[:60])
for o,n in E: s=s.replace(o,n,1)
open(p,'w',encoding='utf-8').write(s); print('fork arm rule added')
