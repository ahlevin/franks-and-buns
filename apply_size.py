# Longer, straighter frank; longer buns; frank fills the bun when landed. Run from the repo folder.
p='game.html'; s=open(p,encoding='utf-8').read()
E=[
("ctx.drawImage(sp.frank, -23, -10.5, 46, 21);   // drawn a little larger than the 40x14 hit box",
 "ctx.drawImage(sp.frank, -29, -11, 58, 22);   // drawn larger than the 40x14 hit box, about the old drawn length"),
("ctx.drawImage(sp.grilled, -37, hh+5-52, 74, 52);", "ctx.drawImage(sp.grilled, -42, hh+5-60, 84, 60);"),
("ctx.drawImage(sp.bun, -37, -hh-8, 74, 39);", "ctx.drawImage(sp.bun, -42, -hh-8, 84, 38);"),
("ctx.drawImage(sp.frank, -22, -14, 44, 20);", "ctx.drawImage(sp.frank, -39, -15, 78, 30);"),
]
if "sp.frank, -29, -11, 58, 22" in s: print('already applied'); raise SystemExit
for o,n in E:
    if s.count(o)!=1: raise SystemExit('anchor not found exactly once, nothing written: '+o[:60])
for o,n in E: s=s.replace(o,n,1)
open(p,'w',encoding='utf-8').write(s); print('sizes updated')
