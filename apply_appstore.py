# v2.22: App Store button + QR code on the home page; App Store link in home and About footers.
URL = 'https://apps.apple.com/app/franks-buns/id6761290671'
def edit(p, pairs):
    s = open(p, encoding='utf-8').read()
    if 'apps.apple.com/app/franks-buns' in s: print('already applied', p); return
    for o, n in pairs:
        if s.count(o) != 1: raise SystemExit('anchor not found exactly once in ' + p + ': ' + o[:60])
    for o, n in pairs: s = s.replace(o, n, 1)
    open(p, 'w', encoding='utf-8').write(s); print('ok', p)
CSS = """    .app-get{display:flex;align-items:center;justify-content:center;gap:1.6rem;flex-wrap:wrap;margin-top:1.8rem;position:relative;z-index:1;animation:fadein 0.8s 0.7s ease both;}
    .btn-appstore{display:inline-flex;flex-direction:column;align-items:flex-start;background:#000;color:#fff;border:1px solid #a6a6a6;border-radius:12px;padding:8px 20px 9px;text-decoration:none;line-height:1.1;font-family:-apple-system,'Helvetica Neue',Arial,sans-serif;transition:transform 0.15s;}
    .btn-appstore:hover{transform:translateY(-2px);}
    .btn-appstore .as-small{font-size:0.72rem;letter-spacing:0.02em;}
    .btn-appstore .as-big{font-size:1.45rem;font-weight:600;letter-spacing:-0.01em;}
    .app-qr{display:flex;flex-direction:column;align-items:center;gap:6px;font-size:0.78rem;color:var(--muted);}
    .app-qr img{background:#fff;border-radius:10px;padding:4px;width:124px;height:124px;}
    @media(max-width:600px){.app-qr{display:none;}}
"""
HERO = """  <p class="hero-sub">No download &nbsp;·&nbsp; No login &nbsp;·&nbsp; Works on any device</p>
  <div class="app-get">
    <a class="btn-appstore" href="%s" target="_blank" rel="noopener" aria-label="Download Franks and Buns on the App Store"><span class="as-small">Download on the</span><span class="as-big">App Store</span></a>
    <div class="app-qr"><img src="qr-appstore.png" alt="QR code that opens Franks and Buns in the App Store"><span>Scan with your iPhone camera</span></div>
  </div>""" % URL
edit('index.html', [
  ("    .responsible-band{", CSS + "    .responsible-band{"),
  ('  <p class="hero-sub">No download &nbsp;·&nbsp; No login &nbsp;·&nbsp; Works on any device</p>', HERO),
  ('    <a href="game.html">Play the Game</a>\n    <a href="about.html">About</a>',
   '    <a href="game.html">Play the Game</a>\n    <a href="%s" target="_blank" rel="noopener">iPhone &amp; iPad App</a>\n    <a href="about.html">About</a>' % URL),
  ('"gamePlatform": ["Web Browser", "Mobile Browser", "Desktop Browser"],', '"gamePlatform": ["Web Browser", "Mobile Browser", "Desktop Browser", "iOS"],\n  "sameAs": ["%s"],' % URL),
])
edit('about.html', [
  ('    <a href="game.html">Play the Game</a>\n    <a href="privacy.html">Privacy Policy</a>',
   '    <a href="game.html">Play the Game</a>\n    <a href="%s" target="_blank" rel="noopener">iPhone &amp; iPad App</a>\n    <a href="privacy.html">Privacy Policy</a>' % URL),
])
