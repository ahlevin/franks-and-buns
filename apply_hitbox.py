# Flying hot dog: a bit shorter and thicker, and every hit check grows with the drawn size
# (forks, landing in a bun, game dogs, bonus dogs, grace glow). Classic look (?bg=off) is unchanged.
p='game.html'; s=open(p,encoding='utf-8').read()
E=[
("const FRANK_W = 40, FRANK_H = 14;",
 "const FRANK_W = 40, FRANK_H = 14;\n"
 "const FRANK_ART_W = 78, FRANK_ART_H = 20;   // kitchen-art hot dog body as drawn\n"
 "// extra reach for hit checks, which were tuned for the 40x14 classic hot dog\n"
 "function frankGrowX() { return spriteReady('frank') ? (FRANK_ART_W - FRANK_W) / 2 : 0; }\n"
 "function frankGrowY() { return spriteReady('frank') ? (FRANK_ART_H - FRANK_H) / 2 : 0; }"),
("      if (dx < 18 && dy < 26) {", "      if (dx < 18 + frankGrowX() && dy < 26 + frankGrowY()) {"),
("      if (dx < 28 && dy < 28) {", "      if (dx < 28 + frankGrowX() && dy < 28 + frankGrowY()) {"),
("Math.abs(frank.x-d.x)<30 && Math.abs(frank.y-d.y)<30)", "Math.abs(frank.x-d.x)<30+frankGrowX() && Math.abs(frank.y-d.y)<30+frankGrowY())"),
("frank.y>by-10 && frank.y<by+BUN_H+5 && frank.vy>0)", "frank.y>by-10-frankGrowY() && frank.y<by+BUN_H+5 && frank.vy>0)"),
("ctx.drawImage(sp.frank, -44, -10.5, 88, 21);   // same size as the hot dog inside a caught bun; hit box unchanged",
 "ctx.drawImage(sp.frank, -41, -12, 82, 24);   // 78x20 body plus outline glow; hit checks use FRANK_ART_W/H"),
("ctx.ellipse(0,0,FRANK_W/2+6,FRANK_H/2+6,0,0,Math.PI*2);", "ctx.ellipse(0,0,FRANK_W/2+6+frankGrowX(),FRANK_H/2+6+frankGrowY(),0,0,Math.PI*2);"),
]
if 'FRANK_ART_W' in s: print('already applied'); raise SystemExit
for o,n in E:
    if s.count(o)!=1: raise SystemExit('anchor not found exactly once, nothing written: '+o[:60])
for o,n in E: s=s.replace(o,n,1)
open(p,'w',encoding='utf-8').write(s); print('hot dog size and hit checks updated')
