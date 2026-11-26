"""Cut the costume skin strips (new-art/skins/*.png) into game sprites (skin-<id>-<state>[-b].png)
and print the draw boxes game.html uses. Each strip holds 3 pictures: flying frank, frank in bun, grilled bun.
Flying pictures are placed by the hot dog body (measured by eye on a grid); bun pictures by the bun."""
import json, sys
import numpy as np
from PIL import Image
from scipy import ndimage

SRC, OUT = sys.argv[1], sys.argv[2]
RES = 4   # sprite pixels per game pixel (matches the other sprites)
BODY_W = 76   # flying hot dog body width in game pixels (the classic frank is about 78)
BUN_W = 79    # bun width in game pixels (the classic bun picture)
BUN_BOTTOM = 1.25   # bun bottom sits this far below the bun's half height (hh), like sp-bun-frank
# flying body box in each strip's first picture (x0, x1, y0, y1), measured on a 50px grid
BODY = {'bunny': (125, 670, 355, 525), 'dragon': (156, 621, 350, 518), 'rocket': (150, 690, 285, 470),
        'shark': (176, 691, 330, 520), 'superhero': (105, 680, 295, 520), 'unicorn': (76, 666, 360, 545),
        # holiday set: the sausage between its tied ends (the classic frank has none)
        'midnight': (102, 654, 304, 520), 'cupid': (80, 680, 285, 550), 'lucky': (104, 656, 310, 538),
        'easter': (74, 680, 355, 545), 'yankee': (100, 695, 316, 520), 'frankula': (90, 660, 268, 496),
        'gobble': (126, 684, 290, 540), 'santa': (72, 675, 298, 500),
        # dog set: the costume's body between tail and nose (ears and tails stick out)
        'bernedoodle': (80, 690, 330, 555), 'bernese': (76, 696, 350, 560), 'corgi': (40, 670, 300, 525),
        'dachshund': (76, 691, 320, 540), 'dalmatian': (80, 690, 340, 550), 'frenchie': (40, 696, 300, 530),
        'golden': (110, 700, 330, 555), 'husky': (96, 691, 350, 560), 'labradoodle': (70, 700, 300, 560),
        'poodle': (126, 701, 320, 545), 'shiba': (50, 700, 330, 560),
        # cat set
        'british': (95, 690, 310, 535), 'calico': (116, 686, 320, 530), 'mainecoon': (120, 680, 300, 525),
        'tabby': (106, 681, 330, 530), 'persian': (90, 700, 310, 550), 'ragdoll': (136, 691, 330, 550),
        'siamese': (110, 695, 310, 525), 'sphynx': (80, 696, 320, 525), 'tuxedo': (100, 690, 335, 550)}
# source strips for each skin (a second file is the B pose of a 2-frame flap)
FRAMES = {'bunny': ['bunny-a', 'bunny-b'], 'dragon': ['dragon-a', 'dragon-b'], 'rocket': ['rocket'],
          'shark': ['shark'], 'superhero': ['superhero'], 'unicorn': ['unicorn'],
          'midnight': ['holiday/new-years-party'], 'cupid': ['holiday/valentines-cupid'], 'lucky': ['holiday/st-patricks-lucky'],
          'easter': ['holiday/easter-bunny'], 'yankee': ['holiday/july-fourth'], 'frankula': ['holiday/halloween-vampire'],
          'gobble': ['holiday/thanksgiving-turkey'], 'santa': ['holiday/christmas-santa'],
          'bernedoodle': ['dogs/bernedoodle'], 'bernese': ['dogs/bernese-mountain-dog'], 'corgi': ['dogs/corgi'],
          'dachshund': ['dogs/dachshund'], 'dalmatian': ['dogs/dalmatian'], 'frenchie': ['dogs/french-bulldog'],
          'golden': ['dogs/golden-retriever'], 'husky': ['dogs/husky'], 'labradoodle': ['dogs/labradoodle'],
          'poodle': ['dogs/poodle'], 'shiba': ['dogs/shiba-inu'],
          'british': ['cats/british-shorthair'], 'calico': ['cats/calico'], 'mainecoon': ['cats/maine-coon'],
          'tabby': ['cats/orange-tabby'], 'persian': ['cats/persian'], 'ragdoll': ['cats/ragdoll'],
          'siamese': ['cats/siamese'], 'sphynx': ['cats/sphynx'], 'tuxedo': ['cats/tuxedo']}
# bun widths measured by hand where the costume hides the bun's top (poodle fluff)
BUN_PX = {'poodle': 560, 'ragdoll': 600, 'persian': 600, 'sad': 636, 'forgotthebuns': 613, 'wrongturn': 603, 'bunbandit': (628, 1048),
          'gardengnome': (655, 1035, 633), 'laundryday': (631, 1076, 653), 'plantparent': (622, 1058, 633), 'lostluggage': (660, 1068, 650),
          'rollerskate': (633, 1065, 630), 'officechair': (660, 1067, 540), 'airportsprinter': (530, 1075, 554), 'shoppingcartracer': (655, 1063, 532),
          'brickstep': (560, 1020, 544), 'dieselengine': (670, 1083), 'bakedbeans': (554, 1058), 'lemonade': (542, 1056), 'tomatosoup': (536, 1059),
          'dojochamp': (635, 1059.5), 'karatemaster': (639, 1066), 'nightninja': (605, 1080), 'chaosdad': (556, 1025, 626),
          'sitcommom': (572, 1052, 590), 'trailerparkdad': (574, 1034, 583), 'trailerparkmom': (554, 1031, 590)}   # (width, centre x) where the colour check misses the bun   # sad: rain boots hang below the bun
# Collections cut by automatic body measurement (folder -> skins); ids are the file names without hyphens
AUTO_SETS = ['questionable-decisions', 'space-cases', 'tiny-terrors', 'deep-sea-dogs', 'final-boss-franks', 'mythical-misfits',
             'trash-pack', 'sports', 'snack-pack', 'cozy-crew', 'main-character-energy',
             'academic', 'bugged-out', 'side-hustles', 'throwback-franks', 'wild-things', 'emotions',
             'game-night', 'career-day', 'oops-all-franks', 'brain-modes', 'weather-report',
             'music-festival', 'mystery-and-mayhem', 'mythical-professions', 'retro-tech', 'everyday-icons', 'fantasy-foods', 'pirates-and-treasure',
             'backyard-legends', 'rise-and-dine', 'cleanup-crew', 'dessert-disasters', 'dinos-in-disguise', 'hair-raising', 'wild-hobbies',
             'magical-mishaps', 'mini-monsters', 'outdoor-adventure', 'pet-peeves', 'school-days', 'things-with-wheels', 'travel-troubles', 'unnecessary-accessories',
             'all-aboard', 'blast-off', 'cans-and-bottles', 'campus-life', 'famous-sculptures', 'lunar-new-year', 'japanese-heroes',
             'sitcom-families', 'fashion-couture', 'robot-rally']
import glob, os
for folder in AUTO_SETS:
    for f in sorted(glob.glob(f'{SRC}/{folder}/*.png')):
        # ids are letters only (the Packs server keeps costumes by id): y2k-byte -> ytwokbyte
        sid = os.path.basename(f)[:-4].replace('-', '').replace('2', 'two')[:24]
        assert sid not in FRAMES, sid
        FRAMES[sid] = [f'{folder}/{os.path.basename(f)[:-4]}']
# Automatic body measurement: the band of rows at least 75% as wide as the widest, corrected by the average
# difference from the 34 hand-measured costumes (tails widen the band and pull it left and up a little).
AUTO_DX, AUTO_DY, AUTO_W = 3.5, 1.5, 1.06   # game pixels right, game pixels down, width ratio
def auto_body(a, x0, x1):
    al = a[:, x0:x1 + 1, 3] > 128
    w = al.sum(1); rows = np.where(w > 0.75 * w.max())[0]
    xs = [np.where(al[y])[0] for y in rows]
    cx = np.mean([(r.min() + r.max()) / 2 for r in xs]) + x0
    bw = np.mean([r.max() - r.min() for r in xs]) / AUTO_W
    s = BODY_W / bw
    return s, cx + AUTO_DX / s, (rows.min() + rows.max()) / 2 + AUTO_DY / s
ONLY = sys.argv[3:]   # optional: just these skins

def runs(alpha):
    col = (alpha > 20).sum(0); out = []; s = None
    for x, v in enumerate(col):
        if v and s is None: s = x
        if not v and s is not None: out.append((s, x - 1)); s = None
    if s is not None: out.append((s, len(col) - 1))
    # stray specks or a detached puff of steam: merge the smallest piece into its nearest neighbour
    while len(out) > 3:
        i = min(range(len(out)), key=lambda k: col[out[k][0]:out[k][1] + 1].sum())
        gl = out[i][0] - out[i - 1][1] if i > 0 else 1e9; gr = out[i + 1][0] - out[i][1] if i < len(out) - 1 else 1e9
        j = i - 1 if gl <= gr else i + 1; a, b = sorted((i, j))
        out[a:b + 1] = [(out[a][0], out[b][1])]
    # pictures that touch (a long dragon): split the widest piece at its thinnest column near the middle
    while len(out) < 3:
        i = max(range(len(out)), key=lambda k: out[k][1] - out[k][0]); a, b = out[i]; m = (b - a) // 5
        x = a + m + int(np.argmin(col[a + m:b - m + 1])); out[i:i + 1] = [(a, x - 1), (x, b)]
    assert len(out) == 3, out
    return out

def bun_box(rgba, x0, x1):
    c = rgba[:, x0:x1 + 1].astype(int); R, G, B, A = c[..., 0], c[..., 1], c[..., 2], c[..., 3]
    m = (A > 200) & (R > 180) & (G > 110) & (B < 130) & (R - G < 120) & (R - G > 15)
    m = ndimage.binary_closing(m, iterations=6); lab, n = ndimage.label(m)
    k = int(np.argmax(ndimage.sum(m, lab, range(1, n + 1)))) + 1
    ys, xs = np.where(lab == k); return xs.min() + x0, xs.max() + x0

geo = {}
for skin, frames in FRAMES.items():
    if ONLY and skin not in ONLY: continue
    ims = [np.array(Image.open(f'{SRC}/{f}.png').convert('RGBA')) for f in frames]
    rr = [runs(im[..., 3]) for im in ims]
    g = {}
    # plain bun: scale and centre from the first frame; grilled bun uses the same scale,
    # centred the same distance from the picture's right (face) end, since grill marks upset the colour check
    bx0, bx1 = bun_box(ims[0], *rr[0][1])
    if skin in BUN_PX:
        v = BUN_PX[skin] if isinstance(BUN_PX[skin], tuple) else (BUN_PX[skin], (bx0 + bx1) / 2)
        bw, c = v[:2]; bx0, bx1 = c - bw / 2, c + bw / 2
    elif skin not in BODY:   # automatic sets: cross-check the colour measurement against the bun's bottom edge
        x0_, x1_ = rr[0][1]; al = ims[0][:, x0_:x1_ + 1, 3]; bot = np.where((al > 20).any(1))[0].max()
        xs = np.where(al[bot - 70] > 200)[0]; edge = (xs.max() - xs.min()) * 1.035
        if not 0.97 <= (bx1 - bx0) / edge <= 1.08:
            print(skin, 'bun colour', bx1 - bx0, '-> edge', round(edge), file=sys.stderr)
            c = x0_ + (xs.min() + xs.max()) / 2; bx0, bx1 = c - edge / 2, c + edge / 2   # centre from the bun's bottom edge too
    sb = BUN_W / (bx1 - bx0)
    if skin not in BODY and not isinstance(BUN_PX.get(skin), tuple):   # keep the bun within 8% of what the body size predicts (1.01x across the hand-checked costumes)
        ref = 1.01 * auto_body(ims[0], *rr[0][0])[0]
        if not 0.92 * ref <= sb <= 1.08 * ref:
            print(skin, 'bun scale', round(sb / ref, 2), '-> body-based', file=sys.stderr)
            sb = min(max(sb, 0.92 * ref), 1.08 * ref)
    bun_cx = {1: (bx0 + bx1) / 2}
    # feet, wheels or chairs under the bun: (width, centre x, bun bottom y) measured by hand; lift both bun pictures to match
    lift = 0
    if isinstance(BUN_PX.get(skin), tuple) and len(BUN_PX[skin]) > 2:
        lift = np.where((ims[0][:, rr[0][1][0]:rr[0][1][1] + 1, 3] > 20).any(1))[0].max() - BUN_PX[skin][2]
    gx0, gx1 = bun_box(ims[0], *rr[0][2])
    bun_cx[2] = (gx0 + gx1) / 2 if abs((gx1 - gx0) - (bx1 - bx0)) < 0.03 * (bx1 - bx0) else rr[0][2][1] - (rr[0][1][1] - bun_cx[1])
    for state, name in ((0, 'fly'), (1, 'bun'), (2, 'grill')):
        # one crop box shared by every frame of this state, so A/B frames don't jitter
        x0 = max(0, min(r[state][0] for r in rr) - 4); x1 = min(ims[0].shape[1] - 1, max(r[state][1] for r in rr) + 4)   # art touching the edge
        ys = [np.where((im[:, r[state][0]:r[state][1] + 1, 3] > 20).any(1))[0] for im, r in zip(ims, rr)]
        y0 = max(0, min(y.min() for y in ys) - 4); y1 = min(ims[0].shape[0] - 1, max(y.max() for y in ys) + 4)
        if state == 0:
            if skin in BODY: bx = BODY[skin]; s = BODY_W / (bx[1] - bx[0]); cx = (bx[0] + bx[1]) / 2; cy = (bx[2] + bx[3]) / 2
            else: s, cx, cy = auto_body(ims[0], *rr[0][0])
            dx, dy = (x0 - cx) * s, (y0 - cy) * s
        else:
            s = sb; cx = bun_cx[state]
            bottom = max(y.max() for y in ys[:1]) - lift   # bun bottom in the first frame
            dx = (x0 - cx) * s; dy = BUN_BOTTOM - (bottom - y0) * s   # added to hh at draw time
        w, h = (x1 - x0 + 1) * s, (y1 - y0 + 1) * s
        for i, im in enumerate(ims):
            crop = Image.fromarray(im[y0:y1 + 1, x0:x1 + 1])
            crop = crop.resize((round(w * RES), round(h * RES)), Image.LANCZOS)
            # 256-colour palette keeps each file around 15-20 KB instead of 100 KB
            crop = crop.quantize(colors=256, method=Image.FASTOCTREE, dither=Image.FLOYDSTEINBERG)
            crop.save(f'{OUT}/skin-{skin}-{name}{"-b" if i else ""}.png', optimize=True)
        g[name] = [round(dx, 1), round(dy, 1), round(w, 1), round(h, 1)]
    g['frames'] = len(frames)
    geo[skin] = g
print(json.dumps(geo))
