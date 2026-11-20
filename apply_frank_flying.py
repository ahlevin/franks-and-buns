# Flying hot dog uses the new slim frank, same size as the hot dog inside a caught bun.
p='game.html'; s=open(p,encoding='utf-8').read()
o="ctx.drawImage(sp.frank, -44, -15, 88, 30);   // same length as the hot dog inside a caught bun; hit box unchanged"
n="ctx.drawImage(sp.frank, -44, -10.5, 88, 21);   // same size as the hot dog inside a caught bun; hit box unchanged"
if n in s: print('already applied'); raise SystemExit
if s.count(o)!=1: raise SystemExit('anchor not found exactly once, nothing written')
open(p,'w',encoding='utf-8').write(s.replace(o,n,1)); print('flying frank resized')
