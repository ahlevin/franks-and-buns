# Caught hot dog sits INSIDE the bun (one picture), buns share one frame, flying frank matches the caught one.
p='game.html'; s=open(p,encoding='utf-8').read()
E=[
("['frank','bun','grilled','dog-a',", "['frank','bun','grilled','bun-frank','grilled-frank','dog-a',"),
("ctx.drawImage(sp.frank, -29, -11, 58, 22);   // drawn larger than the 40x14 hit box, about the old drawn length",
 "ctx.drawImage(sp.frank, -44, -15, 88, 30);   // same length as the hot dog inside a caught bun; hit box unchanged"),
("""  } else if (b.grilled && !b.scored && spriteReady('grilled')) {
    ctx.drawImage(sp.grilled, -42, hh+5-60, 84, 60);
  } else {
    ctx.drawImage(sp.bun, -42, -hh-8, 84, 38);
  }""",
"""  } else if (b.scored && spriteReady(b.grilled ? 'grilled-frank' : 'bun-frank')) {
    ctx.drawImage(sp[b.grilled ? 'grilled-frank' : 'bun-frank'], -44, hh+5-37, 88, 37);   // caught: hot dog inside the bun
  } else if (b.grilled && spriteReady('grilled')) {
    ctx.drawImage(sp.grilled, -44, hh+5-37, 88, 37);
  } else {
    ctx.drawImage(sp.bun, -44, hh+5-37, 88, 37);
  }"""),
("  if (b.scored && spriteReady('frank')) {\n    ctx.drawImage(sp.frank, -39, -15, 78, 30);",
 "  if (b.scored && spriteReady('bun-frank')) {\n    // hot dog is already drawn inside the caught-bun picture\n  } else if (b.scored && spriteReady('frank')) {\n    ctx.drawImage(sp.frank, -39, -15, 78, 30);"),
]
if "'bun-frank'," in s: print('already applied'); raise SystemExit
for o,n in E:
    if s.count(o)!=1: raise SystemExit('anchor not found exactly once, nothing written: '+o[:60])
for o,n in E: s=s.replace(o,n,1)
open(p,'w',encoding='utf-8').write(s); print('catch art wired in')
