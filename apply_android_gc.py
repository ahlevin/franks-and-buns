# v1.1: Game Center is iPhone/iPad only; on Android the 🏆 button never shows.
p='game.html'; s=open(p,encoding='utf-8').read()
o="  if (!C || !C.isNativePlatform || !C.isNativePlatform()) return null;\n  return (C.Plugins && C.Plugins.GameCenter)"
n="  if (!C || !C.isNativePlatform || !C.isNativePlatform()) return null;\n  if (C.getPlatform && C.getPlatform() !== 'ios') return null;   // Game Center is iPhone/iPad only (no button on Android)\n  return (C.Plugins && C.Plugins.GameCenter)"
if "getPlatform() !== 'ios'" in s: print('already applied'); raise SystemExit
assert s.count(o)==1, 'anchor not found'
open(p,'w',encoding='utf-8').write(s.replace(o,n)); print('ok')
