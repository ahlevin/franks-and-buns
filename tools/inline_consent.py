"""Copy consent.js into every page between the FB-CONSENT markers.
The website build only publishes .html/.png/.jpg files, so the consent code is inlined.
Run after editing consent.js:  python3 tools/inline_consent.py [extra.html ...]"""
import re, sys, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
code = (root / 'consent.js').read_text()
block = '<!-- FB-CONSENT START (generated from consent.js by tools/inline_consent.py; edit consent.js, not this) -->\n<script>\n' + code + '</script>\n<!-- FB-CONSENT END -->'
pages = [root / p for p in ['index.html', 'about.html', 'privacy.html', 'terms.html', 'game.html']] + [pathlib.Path(a) for a in sys.argv[1:]]
for p in pages:
    s = p.read_text()
    if '<script src="consent.js" defer></script>' in s:
        s = s.replace('<script src="consent.js" defer></script>', block, 1)
    else:
        s, n = re.subn(r'<!-- FB-CONSENT START.*?<!-- FB-CONSENT END -->', lambda m: block, s, flags=re.S)
        if n != 1: sys.exit(f'{p}: consent block not found')
    p.write_text(s)
    print('updated', p.name)
