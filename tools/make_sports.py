"""Sports modes (basketball, football, water polo, golf): key out the backgrounds of new-art/sports/<sport>/*.png,
split the sheets and write the game pictures <sport>-*.png at game sizes (4 sprite pixels per game pixel), like
tools/make_soccer.py does for Soccer. Run from the repo root: python3 tools/make_sports.py
It prints each sport's boxes for SPORTS in game.html."""
import json
import os
import numpy as np
from PIL import Image
from scipy import ndimage
import make_soccer as ms

SPORTS = {
    # key: background colour. venue: kitchen id for the backgrounds (None: reuse an existing kitchen).
    # ball: game size of the flying ball (w, h). target: game width of the goal picture and where its opening is
    # (fraction of the empty target's height from the top; None: the bottom sits where the bun's bottom is, like Soccer)
    'basketball': dict(key='green', venue='arena', ball=(38, 38), target=(80, 0.36)),
    'football': dict(key='green', venue='gridiron', ball=(48, 30), target=(96, 0.42)),
    'waterpolo': dict(key='green', venue='pool', ball=(38, 38), target=(84, None)),
    'golf': dict(key='magenta', venue=None, ball=(32, 32), target=(88, 0.62)),
}
BUN_BOTTOM = 18      # game px below the bun's centre where the bun picture ends
MOUTH_Y = -6         # game px: where a target's opening sits (rim, cup)

def key(path, bg):
    a = np.asarray(Image.open(path).convert('RGB')).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    if bg == 'green':
        x = g - np.maximum(r, b)
        alpha = np.clip(1 - (x - 60) / 110, 0, 1)
        g = np.where(x > 0, np.maximum(r, b), g)
    else:   # magenta
        x = np.minimum(r, b) - g
        alpha = np.clip(1 - (x - 60) / 110, 0, 1)
        lim = g + 6
        r = np.where(x > 0, np.minimum(r, np.maximum(lim, r - x)), r)
        b = np.where(x > 0, np.minimum(b, np.maximum(lim, b - x)), b)
    return np.dstack([r, g, b, alpha * 255]).astype(np.uint8)

def sheet(sport, name, cols, rows):
    return ms.pieces(key('new-art/sports/%s/%s.png' % (sport, name), SPORTS[sport]['key']), cols, rows)

def largest(im):
    """keep only the biggest opaque blob (drops stray splash drops next to a ball)"""
    a = np.asarray(im).copy(); lab, n = ndimage.label(a[..., 3] > 40)
    if n > 1:
        big = np.argmax(ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))) + 1
        a[..., 3] = np.where(ndimage.binary_dilation(lab == big, iterations=3), a[..., 3], 0)
    im = Image.fromarray(a); return im.crop(im.getbbox())

def save(im, name):
    im.save(name, optimize=True); print(name, im.size)

def canvas_of(im, w, h, x, y):
    c = Image.new('RGBA', (w, h), (0, 0, 0, 0)); c.alpha_composite(im, (x, y)); return c

def build(sport):
    cfg, out = SPORTS[sport], {}
    # ball: flying (skin fly picture) and the 512 title / intro ball
    ball = largest(sheet(sport, sport + '-ball', 2, 1)[(0, 0)])
    bw, bh = cfg['ball']
    save(ms.fit(ball, bw * 4, bh * 4), 'skin-%s-fly.png' % sport); out['fly'] = [-bw / 2, -bh / 2, bw, bh]
    save(ms.place((512, 512), ball, (96, 96, 416, 416)), sport + '-ball.png')
    # targets: one scale for all four, bottoms lined up; boxes relative to the bun's centre
    tname = {'basketball': 'basketball-hoops', 'football': 'football-nets', 'waterpolo': 'waterpolo-goals', 'golf': 'golf-greens'}[sport]
    if sport == 'football' and os.path.exists('new-art/sports/football/football-hands.png'): tname = 'football-hands'   # Alan's diamond catch
    t = sheet(sport, tname, 2, 2)
    states = {'goal': t[(0, 0)], 'goal-ball': t[(0, 1)], 'goal-hot': t[(1, 0)], 'goal-hot-ball': t[(1, 1)]}
    tw, frac = cfg['target']
    s = tw * 4 / max(states['goal'].width, states['goal-hot'].width)
    eh = states['goal'].height * s / 4
    bottom = BUN_BOTTOM if frac is None else MOUTH_Y + (1 - frac) * eh
    boxes = {}
    for n, im in states.items():
        j = ms.bottom_scaled(im, s); save(j, '%s-%s.png' % (sport, n))
        w, h = j.width / 4, j.height / 4; boxes[n] = [round(-w / 2, 1), round(bottom - h, 1), round(w, 1), round(h, 1)]
    out['targets'] = boxes
    # costume-style caught pictures (drawn with the bun's half height 13 as origin)
    for part, n in [('bun', 'goal-ball'), ('grill', 'goal-hot-ball')]:
        save(Image.open('%s-%s.png' % (sport, n)), 'skin-%s-%s.png' % (sport, part))
        b = boxes[n]; out[part] = [b[0], round(b[1] - 13, 1), b[2], b[3]]
    # fire ball (2 frames, 320x255 like sp-chili)
    fb = sheet(sport, sport + '-fireball', 2, 1)
    sc = min(320 / max(fb[(0, 0)].width, fb[(0, 1)].width), 241 / max(fb[(0, 0)].height, fb[(0, 1)].height))
    for c_, n in [((0, 0), 'a'), ((0, 1), 'b')]:
        j = ms.bottom_scaled(fb[c_], sc); save(canvas_of(j, 320, 255, (320 - j.width) // 2, 255 - j.height), '%s-fireball-%s.png' % (sport, n))
    # dogs: intro thief with the ball, plain dog, and two run frames carrying a target (bonus dogs, 280x208 like sp-dog)
    d = sheet(sport, sport + '-dog', 2, 2)
    save(ms.place((512, 512), d[(0, 0)], (14, 104, 468, 404)), sport + '-dog.png')
    save(ms.place((512, 512), d[(0, 1)], (14, 104, 468, 404)), sport + '-dognodog.png')
    sc = min(280 / max(d[(1, 0)].width, d[(1, 1)].width), 164 / max(d[(1, 0)].height, d[(1, 1)].height))
    for c_, n in [((1, 0), 'a'), ((1, 1), 'b')]:
        j = ms.bottom_scaled(d[c_], sc); save(canvas_of(j, 280, 208, (280 - j.width) // 2, 186 - j.height), '%s-dog-%s.png' % (sport, n))
    # defender (the chef in the intro) and his arm (the fork hazard)
    save(ms.place((512, 512), sheet(sport, sport + '-defender', 1, 1)[(0, 0)], (38, 44, 436, 433)), sport + '-keeper.png')
    save(ms.place((512, 768), sheet(sport, sport + '-defender-arm', 1, 1)[(0, 0)], (140, 64, 396, 740)), sport + '-keeper-arm.png')
    # the player: same scale for every pose, 72 game px tall (4x)
    pl = sheet(sport, sport + '-player', 4, 1)
    sc = 288 / max(p.height for p in pl.values())
    W_ = round(max(p.width for p in pl.values()) * sc) + 8
    for i, n in enumerate(['run-a', 'run-b', 'kick', 'cheer']):
        j = ms.bottom_scaled(pl[(0, i)], sc); save(canvas_of(j, W_, 292, (W_ - j.width) // 2, 292 - j.height), '%s-player-%s.png' % (sport, n))
    # venue: back wall, ground strip, start screen, passer-by
    v = cfg['venue']
    if v:
        pb = sheet(sport, v + '-passer-by', 1, 1)[(0, 0)]
        save(ms.bottom_scaled(pb, 560 / pb.width), 'kitchen-%s-passer.png' % v)
        for src, name in [('back-wall', 'wall'), ('counter', 'counter'), ('start', 'start')]:
            Image.open('new-art/sports/%s/%s-%s.png' % (sport, v, src)).convert('RGB').save('bg-%s-%s.jpg' % (name, v), quality=84, optimize=True); print('bg-%s-%s.jpg' % (name, v))
    return out

if __name__ == '__main__':
    import sys
    res = {s: build(s) for s in (sys.argv[1:] or SPORTS)}
    print('BOXES', json.dumps(res))
