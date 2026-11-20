# Flying hot dog thicker: body 78x24 (was 78x20). Hit checks follow FRANK_ART_H automatically.
p='game.html'; s=open(p,encoding='utf-8').read()
E=[("const FRANK_ART_W = 78, FRANK_ART_H = 20;", "const FRANK_ART_W = 78, FRANK_ART_H = 24;"),
   ("ctx.drawImage(sp.frank, -41, -12, 82, 24);   // 78x20 body plus outline glow",
    "ctx.drawImage(sp.frank, -41, -14, 82, 28);   // 78x24 body plus outline glow")]
if "FRANK_ART_H = 24" in s: print('already applied'); raise SystemExit
for o,n in E:
    if s.count(o)!=1: raise SystemExit('anchor not found exactly once, nothing written: '+o[:60])
for o,n in E: s=s.replace(o,n,1)
open(p,'w',encoding='utf-8').write(s); print('hot dog thicker')
