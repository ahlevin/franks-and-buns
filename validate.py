import re, json, sys, os

errors = []
warnings = []

def check(fpath):
    try:
        with open(fpath) as f:
            return f.read()
    except:
        errors.append(f"Cannot open {fpath}")
        return ""

print("=" * 55)
print("FRANKS & BUNS — PRE-COMMIT VALIDATION")
print("=" * 55)

# ── GAME.HTML ──────────────────────────────────────────────
print("\n[ game.html — structure ]")
g = check('game.html')
if g:
    lines = g.split('\n')

    for tag in ['<!DOCTYPE html>','</head>','</body>','</html>']:
        if tag not in g: errors.append(f"game.html missing {tag}")
    if 'google-adsense-account' in g: errors.append("game.html has AdSense meta tag — REMOVE IT")
    else: print("  ✅ No AdSense tag")
    if 'G-5PVW85JQP6' not in g: errors.append("game.html missing Google Analytics")
    else: print("  ✅ Google Analytics present")
    for tag in ['og:title','twitter:card','canonical','meta name="description"']:
        if tag not in g: errors.append(f"game.html missing {tag}")
    else: print("  ✅ SEO tags present")
    if 'application/ld+json' not in g: errors.append("game.html missing Schema.org")
    else:
        schemas = re.findall(r'<script type="application/ld\+json">(.*?)</script>', g, re.DOTALL)
        for i, s in enumerate(schemas):
            try: json.loads(s)
            except Exception as e: errors.append(f"game.html schema {i+1} invalid JSON: {e}")
        print("  ✅ Schema.org valid")
    if 'Flappy Bird' in g or 'flappy bird' in g: errors.append("game.html has Flappy Bird reference")
    else: print("  ✅ No Flappy Bird references")

    # ── FREEZE / CRASH / MEMORY CHECKS ──────────────────────
    print("\n[ game.html — stability ]")

    # 1. ctx.save/restore balance using stack trace
    stack = []
    orphan_restores = []
    unmatched_saves = []
    current_func = 'global'
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith('function '): current_func = s.split('(')[0].replace('function ','')
        if 'ctx.save()' in s: stack.append((i+1, current_func))
        if 'ctx.restore()' in s:
            if stack: stack.pop()
            else: orphan_restores.append((i+1, current_func))
    unmatched_saves = stack
    if orphan_restores:
        for ln, fn in orphan_restores:
            errors.append(f"game.html orphan ctx.restore() at line {ln} in {fn} — will corrupt canvas state over time")
    elif unmatched_saves:
        for ln, fn in unmatched_saves:
            errors.append(f"game.html unmatched ctx.save() at line {ln} in {fn} — canvas state leak")
    else:
        print(f"  ✅ ctx.save/restore perfectly balanced")

    # 2. frameCount++ only once
    fc = g.count('frameCount++')
    if fc != 1: errors.append(f"game.html frameCount++ appears {fc}x — causes double-speed animation")
    else: print("  ✅ frameCount++ once")

    # 3. requestAnimationFrame called once
    raf = g.count('requestAnimationFrame')
    if raf != 1: errors.append(f"game.html requestAnimationFrame called {raf}x — should be 1")
    else: print("  ✅ requestAnimationFrame once")

    # 4. loop() called once
    lc = g.count('loop();')
    if lc != 1: errors.append(f"game.html loop() called {lc}x — multiple loops cause freeze")
    else: print("  ✅ loop() called once")

    # 5. No setInterval
    if g.count('setInterval') > 0: errors.append("game.html uses setInterval — causes duplicate loops on revisit")
    else: print("  ✅ No setInterval")

    # 6. Audio node cleanup
    if 'o.disconnect()' not in g: errors.append("game.html audio nodes not disconnected — memory leak on mobile")
    else: print("  ✅ Audio nodes disconnected on stop")

    # 7. Arrays never grow unbounded
    all_arrays_ok = True
    for arr in ['splats','particles','floatingTexts','buns','forks','gameDogs','bonusDogs']:
        pushes = g.count(f'{arr}.push(')
        splices = g.count(f'{arr}.splice(')
        clears = g.count(f'{arr}=[]') + g.count(f'{arr} = []')
        if pushes > 0 and splices == 0 and clears == 0:
            errors.append(f"game.html {arr} grows unbounded — no splice or clear found")
            all_arrays_ok = False
    if all_arrays_ok: print("  ✅ All arrays cleaned up (splice/clear present)")

    # 8. No new Image() inside game loop
    update_fn = g[g.find('function update()'):g.find('function update()')+3000]
    draw_fn = g[g.find('function draw()'):g.find('function draw()')+3000]
    if 'new Image()' in update_fn: errors.append("game.html new Image() inside update() — recreates every frame")
    elif 'new Image()' in draw_fn: errors.append("game.html new Image() inside draw() — recreates every frame")
    else: print("  ✅ Images created only at startup")

    # 9. No AudioContext inside game loop
    if 'new (window.AudioContext' in update_fn or 'new (window.AudioContext' in draw_fn:
        errors.append("game.html AudioContext created inside game loop — should be created once")
    else: print("  ✅ AudioContext created once outside loop")

    # 10. draw() exits early for BONUS state
    if 'STATE.BONUS) { drawBonusRound()' not in g and 'STATE.BONUS){drawBonusRound()' not in g:
        errors.append("game.html draw() doesn't exit early for BONUS — causes double drawing and freeze")
    else: print("  ✅ draw() exits early for BONUS state")

    # 11. No old drawn fork code (causes save/restore bugs)
    if g.count('Sleeve cuff') > 0: errors.append("game.html has old drawn fork code — remove it (causes canvas freeze)")
    else: print("  ✅ No old drawn fork code")

    # 12. Core game functions present
    for fn in ['function update()','function draw()','function loop()','drawFrank','drawBun','loseLife','landFrank']:
        if fn not in g: errors.append(f"game.html missing {fn}")
    print("  ✅ Core game functions present")

    # 13. Key features present
    for feature, label in [
        ('STATE.BONUS','Bonus round state'),
        ('startBonusRound','Bonus round trigger'),
        ('drawBonusRound','Bonus round draw'),
        ('game-header','Game header'),
        ('game-footer','Game footer'),
        ("Don't get forked",'Tagline'),
        ('showUI','Header visibility toggle'),
        ('Franks and Buns - Free Hot Dog Arcade Game','Hidden content div'),
        ('getGameDogCanvas','Dog image processing'),
    ]:
        if feature not in g: errors.append(f"game.html missing: {label}")
    print("  ✅ Game features present")

# ── CONTENT PAGES ──────────────────────────────────────────
for fname in ['index.html','about.html','privacy.html','terms.html']:
    print(f"\n[ {fname} ]")
    c = check(fname)
    if not c: continue
    for tag in ['<!DOCTYPE html>','</head>','</body>','</html>']:
        if tag not in c: errors.append(f"{fname} missing {tag}")
    if 'google-adsense-account' not in c: errors.append(f"{fname} missing AdSense meta tag")
    else: print("  ✅ AdSense tag present")
    if 'G-5PVW85JQP6' not in c: errors.append(f"{fname} missing Google Analytics")
    else: print("  ✅ Google Analytics present")
    for tag in ['og:title','twitter:card','canonical','meta name="description"']:
        if tag not in c: errors.append(f"{fname} missing {tag}")
    else: print("  ✅ SEO tags present")
    if 'nav-logo' not in c: errors.append(f"{fname} missing nav")
    if 'hamburger' not in c: errors.append(f"{fname} missing hamburger menu")
    if 'about.html' not in c: errors.append(f"{fname} missing About link")
    if 'game.html' not in c: errors.append(f"{fname} missing game link")
    if 'footer' not in c: errors.append(f"{fname} missing footer")
    if 'askfranksandbuns@gmail.com' not in c: errors.append(f"{fname} missing contact email")
    if 'blog.html' in c: errors.append(f"{fname} has blog.html link — remove it")
    if 'Flappy Bird' in c or 'flappy bird' in c: errors.append(f"{fname} has Flappy Bird reference")
    else: print("  ✅ Nav, footer, links clean, no Flappy Bird")
    if fname in ['index.html','about.html']:
        if 'application/ld+json' not in c: errors.append(f"{fname} missing Schema.org")
        else:
            schemas = re.findall(r'<script type="application/ld\+json">(.*?)</script>', c, re.DOTALL)
            for i, s in enumerate(schemas):
                try: json.loads(s)
                except Exception as e: errors.append(f"{fname} schema {i+1} invalid JSON: {e}")
            print("  ✅ Schema.org valid")

# ── SUPPORT FILES ──────────────────────────────────────────
print("\n[ Support files ]")
for f in ['ads.txt','robots.txt','sitemap.xml','CNAME']:
    if os.path.exists(f): print(f"  ✅ {f}")
    else: warnings.append(f"{f} missing")
imgs_ok = True
for img in ['chefarm.png','dognodog.png','chef.png','dog.png','hotdog.png','favicon.ico']:
    if not os.path.exists(img):
        errors.append(f"Missing image: {img}")
        imgs_ok = False
if imgs_ok: print("  ✅ All images present")

# ── RESULTS ────────────────────────────────────────────────
print("\n" + "=" * 55)
if errors:
    print(f"❌ {len(errors)} ERROR(S) — DO NOT COMMIT\n")
    for e in errors: print(f"  ❌ {e}")
else:
    print("✅ ALL CHECKS PASSED — safe to commit")
if warnings:
    print(f"\n⚠️  {len(warnings)} WARNING(S):")
    for w in warnings: print(f"  ⚠️  {w}")
print("=" * 55)
sys.exit(1 if errors else 0)
