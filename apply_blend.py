# Chef, dogs, intro hot dog and fork arm: draw normally (full colour) on the kitchen art; keep the old 'screen' blend for the classic dark look (?bg=off).
p='game.html'; s=open(p,encoding='utf-8').read()
A="const ART_SET = (new URLSearchParams(location.search).get('bg') || 'a').toLowerCase();"
N=A+"\n// The older images already have see-through backgrounds; 'screen' washes them out on the light kitchen walls\nconst OLD_ART_BLEND = (ART_SET === 'a' || ART_SET === 'b') ? 'source-over' : 'screen';"
O="ctx.globalCompositeOperation = 'screen'"
if 'OLD_ART_BLEND' in s: print('already applied'); raise SystemExit
if s.count(A)!=1: raise SystemExit('ART_SET line not found exactly once, nothing written')
if s.count(O)!=5: raise SystemExit('expected 5 screen blends, found %d, nothing written' % s.count(O))
s=s.replace(A,N,1).replace(O,"ctx.globalCompositeOperation = OLD_ART_BLEND")
open(p,'w',encoding='utf-8').write(s); print('blend fixed (5 places)')
