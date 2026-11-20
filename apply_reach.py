# Fair play: every bun is reachable from the previous one in the time between them (fixes impossible buns at high speed).
p='game.html'; s=open(p,encoding='utf-8').read()
E=[
("  const y = type.yRange[0]*H + Math.random()*(type.yRange[1]-type.yRange[0])*H;",
 "  let y = type.yRange[0]*H + Math.random()*(type.yRange[1]-type.yRange[0])*H;\n"
 "  // Fair play: keep each bun within reach of the previous one in the time between them.\n"
 "  // Steady tapping climbs about 5px a frame; after landing, the bounce rises before the hot dog can fall.\n"
 "  const prev = buns.length ? buns[buns.length-1] : null;\n"
 "  if (prev) {\n"
 "    const n = Math.max((W + 60 - prev.x) / scrollSpeed, 1);                        // frames between the two landings\n"
 "    const up = 3.2 * n;                                                             // brisk human tapping, with margin\n"
 "    const down = Math.max(0, 0.8 * (GRAVITY / 2 * n * n + FLAP_POWER * 0.7 * n));   // fall after the landing bounce, with margin\n"
 "    const lo = Math.max(prev.y - up, H * 0.12), hi = Math.min(prev.y + down, H * 0.75);\n"
 "    y = lo <= hi ? Math.min(Math.max(y, lo), hi) : prev.y;\n"
 "  }"),
("nextBunDist = Math.max(160+Math.random()*100-Math.min(boxesCompleted*5,40), 100);",
 "nextBunDist = Math.max(160+Math.random()*100-Math.min(boxesCompleted*5,40), 100, scrollSpeed*30);   // at least half a second between buns"),
]
if 'Fair play: keep each bun' in s: print('already applied'); raise SystemExit
for o,n in E:
    if s.count(o)!=1: raise SystemExit('anchor not found exactly once, nothing written: '+o[:60])
for o,n in E: s=s.replace(o,n,1)
open(p,'w',encoding='utf-8').write(s); print('bun reach rule added')
