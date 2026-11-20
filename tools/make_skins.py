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
        'shark': (176, 691, 330, 520), 'superhero': (105, 680, 295, 520), 'unicorn': (76, 666, 360, 545)}
FRAMES = {'bunny': ['bunny-a', 'bunny-b'], 'dragon': ['dragon-a', 'dragon-b'], 'rocket': ['rocket'],
          'shark': ['shark'], 'superhero': ['superhero'], 'unicorn': ['unicorn']}

def runs(alpha):
    col = (alpha > 20).sum(0); out = []; s = None
    for x, v in enumerate(col):
        if v and s is None: s = x
        if not v and s is not None: out.append((s, x - 1)); s = None
    if s is not None: out.append((s, len(col) - 1))
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
    ims = [np.array(Image.open(f'{SRC}/{f}.png').convert('RGBA')) for f in frames]
    rr = [runs(im[..., 3]) for im in ims]
    g = {}
    # plain bun: scale and centre from the first frame; grilled bun uses the same scale,
    # centred the same distance from the picture's right (face) end, since grill marks upset the colour check
    bx0, bx1 = bun_box(ims[0], *rr[0][1]); sb = BUN_W / (bx1 - bx0)
    bun_cx = {1: (bx0 + bx1) / 2}
    gx0, gx1 = bun_box(ims[0], *rr[0][2])
    bun_cx[2] = (gx0 + gx1) / 2 if abs((gx1 - gx0) - (bx1 - bx0)) < 0.03 * (bx1 - bx0) else rr[0][2][1] - (rr[0][1][1] - bun_cx[1])
    for state, name in ((0, 'fly'), (1, 'bun'), (2, 'grill')):
        # one crop box shared by every frame of this state, so A/B frames don't jitter
        x0 = min(r[state][0] for r in rr) - 4; x1 = max(r[state][1] for r in rr) + 4
        ys = [np.where((im[:, r[state][0]:r[state][1] + 1, 3] > 20).any(1))[0] for im, r in zip(ims, rr)]
        y0 = max(0, min(y.min() for y in ys) - 4); y1 = min(ims[0].shape[0] - 1, max(y.max() for y in ys) + 4)
        if state == 0:
            bx = BODY[skin]; s = BODY_W / (bx[1] - bx[0]); cx = (bx[0] + bx[1]) / 2; cy = (bx[2] + bx[3]) / 2
            dx, dy = (x0 - cx) * s, (y0 - cy) * s
        else:
            s = sb; cx = bun_cx[state]
            bottom = max(y.max() for y in ys[:1])   # bun bottom in the first frame
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
