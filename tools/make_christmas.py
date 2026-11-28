"""Christmas Edition: cut new-art/christmas/*.png (Alan's art, white backgrounds) into the game pictures,
the same slots the sports modes use (tools/make_sports.py), and print the boxes for SPORTS.christmas in game.html.
Run from the repo root: python3 tools/make_christmas.py

  present          -> christmas-ball.png (title / intro / mode picker) and skin-christmas-fly.png (what the player flies)
  sleigh (4)       -> christmas-goal / -goal-ball (sleigh, sleigh with a present), -goal-hot / -goal-hot-ball (Santa's bag)
  rudolph (2)      -> christmas-fireball-a / -b (the bonus rush pickup, in place of the chili dog)
  dog (3)          -> christmas-dog-a / -b (runs with a present), christmas-dog (intro thief), christmas-dognodog
  mrs-claus        -> christmas-keeper (the chef), mrs-claus-arm -> christmas-keeper-arm (the fork)
  elves (3)        -> christmas-player-run-a / -run-b / -kick / -cheer
  treats (5)       -> christmas-pick-mustard / ketchup / relish / cheese / jalapeno
  reindeer-team    -> christmas-reindeer.png (the sleigh that crosses the sky)
  skin (3)         -> skin-reindeer-fly / -bun / -grill (the Reindeer Frank costume)
  back-wall, counter, start, passer-by -> bg-wall / bg-counter / bg-start-northpole.jpg, kitchen-northpole-passer.png"""
import json
import numpy as np
from PIL import Image
from scipy import ndimage
import make_soccer as ms

SRC = 'new-art/christmas/christmas-'
BUN_BOTTOM = 18


def key(name, holes=False):
    """RGBA with the white background removed: white connected to the edges, plus (holes=True) closed-in
    background-white gaps (neutral grey-white, unlike the warm white of fur and icing; holes=(x0, x1) limits
    this to a band of the sheet, as fractions of its width). Edges are un-mixed from white."""
    a = np.asarray(Image.open(SRC + name + '.png').convert('RGB')).astype(np.float32)
    mn, mx = a.min(2), a.max(2)
    white = (mn >= 236) & (mx - mn < 14)
    lab, n = ndimage.label(white)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(edge))
    if holes:
        for i, sl in enumerate(ndimage.find_objects(lab), 1):
            if i in edge or sl is None: continue
            m = lab[sl] == i
            if m.sum() < 250: continue
            if holes is not True and not (holes[0] * a.shape[1] <= sl[1].start and sl[1].stop <= holes[1] * a.shape[1]): continue
            px = a[sl][m]
            if abs(px[:, 0].mean() - px[:, 2].mean()) < 1.6: bg[sl] |= m
    # soft edge: a 2-pixel ring around the background gets alpha from how far it is from white
    ring = ndimage.binary_dilation(bg, iterations=2) & ~bg
    alpha = np.where(bg, 0.0, 1.0)
    ra = np.clip((255 - mn) / 70.0, 0, 1)
    alpha = np.where(ring, np.maximum(ra, 0.0), alpha)
    al = np.maximum(alpha, 1e-3)[..., None]
    rgb = np.where(ring[..., None], np.clip((a - (1 - al) * 255) / al, 0, 255), a)
    return np.dstack([rgb, alpha * 255]).astype(np.uint8)


def sheet(name, cols, rows=1, holes=False, min_px=400):
    return ms.pieces(key(name, holes), cols, rows, min_px)


def save(im, name):
    im.save(name, optimize=True); print(name, im.size)


def canvas_of(im, w, h, x, y):
    c = Image.new('RGBA', (w, h), (0, 0, 0, 0)); c.alpha_composite(im, (x, y)); return c


def build():
    out = {}
    # the present: flies at 60x26 game px (a little smaller than a frank), 4 sprite px per game px
    pr = sheet('present', 2)
    p0 = pr[(0, 0)]
    bw = 60; bh = round(bw * p0.height / p0.width)
    save(ms.fit(p0, bw * 4, bh * 4), 'skin-christmas-fly.png'); out['fly'] = [-bw / 2, -bh / 2, bw, bh]
    save(ms.place((512, 512), p0, (40, 140, 472, 372)), 'christmas-ball.png')
    # sleigh and Santa's bag: one scale for all four, bottoms on the bun's bottom
    t = sheet('sleigh', 4, holes=(0, 0.5))   # only the sleighs' runner gaps: Santa's beard is neutral white too
    states = {'goal': t[(0, 0)], 'goal-ball': t[(0, 1)], 'goal-hot': t[(0, 2)], 'goal-hot-ball': t[(0, 3)]}
    s = 92 * 4 / max(states['goal'].width, states['goal-ball'].width)
    sh = 84 * 4 / max(states['goal-hot'].width, states['goal-hot-ball'].width)
    sh = min(sh, 76 * 4 / max(states['goal-hot'].height, states['goal-hot-ball'].height))
    boxes = {}
    for n, im in states.items():
        j = ms.bottom_scaled(im, sh if 'hot' in n else s); save(j, 'christmas-%s.png' % n)
        w, h = j.width / 4, j.height / 4; boxes[n] = [round(-w / 2, 1), round(BUN_BOTTOM - h, 1), round(w, 1), round(h, 1)]
    out['targets'] = boxes
    for part, n in [('bun', 'goal-ball'), ('grill', 'goal-hot-ball')]:
        save(Image.open('christmas-%s.png' % n), 'skin-christmas-%s.png' % part)
        b = boxes[n]; out[part] = [b[0], round(b[1] - 13, 1), b[2], b[3]]
    # Rudolph: 2 frames on 320x255 like sp-chili
    rd = sheet('rudolph', 2)
    sc = min(320 / max(rd[(0, 0)].width, rd[(0, 1)].width), 241 / max(rd[(0, 0)].height, rd[(0, 1)].height))
    for c_, n in [((0, 0), 'a'), ((0, 1), 'b')]:
        j = ms.bottom_scaled(rd[c_], sc); save(canvas_of(j, 320, 255, (320 - j.width) // 2, 255 - j.height), 'christmas-fireball-%s.png' % n)
    # the dog in antlers: two running frames with a present, and standing without
    d = sheet('dog', 3, holes=True)
    save(ms.place((512, 512), d[(0, 0)], (14, 104, 468, 404)), 'christmas-dog.png')
    save(ms.place((512, 512), d[(0, 2)], (60, 70, 452, 420)), 'christmas-dognodog.png')
    sc = min(280 / max(d[(0, 0)].width, d[(0, 1)].width), 164 / max(d[(0, 0)].height, d[(0, 1)].height))
    for c_, n in [((0, 0), 'a'), ((0, 1), 'b')]:
        j = ms.bottom_scaled(d[c_], sc); save(canvas_of(j, 280, 208, (280 - j.width) // 2, 186 - j.height), 'christmas-dog-%s.png' % n)
    # Mrs. Claus (the chef) and her candy cane arm (the fork)
    save(ms.place((512, 512), sheet('mrs-claus', 1)[(0, 0)], (38, 44, 436, 433)), 'christmas-keeper.png')
    save(ms.place((512, 768), sheet('mrs-claus-arm', 1)[(0, 0)], (140, 64, 396, 768)), 'christmas-keeper-arm.png')
    # the elf: run (two frames from the same pose, the game bobs it), toss and cheer, 72 game px tall
    el = sheet('elves', 3, holes=True, min_px=2000)
    sc = 288 / max(p.height for p in el.values())
    W_ = round(max(p.width for p in el.values()) * sc) + 8
    for c_, n in [((0, 0), 'run-a'), ((0, 0), 'run-b'), ((0, 1), 'kick'), ((0, 2), 'cheer')]:
        j = ms.bottom_scaled(el[c_], sc); save(canvas_of(j, W_, 292, (W_ - j.width) // 2, 292 - j.height), 'christmas-player-%s.png' % n)
    # treats: 64x128 like the condiments
    tr = sheet('treats', 5)
    for i, c in enumerate(['mustard', 'ketchup', 'relish', 'cheese', 'jalapeno']):
        save(ms.fit(tr[(0, i)], 64, 128), 'christmas-pick-%s.png' % c)
    # Santa's reindeer team for the sky
    rt = key('reindeer-team', True); im = Image.fromarray(rt); im = im.crop(im.getbbox())
    save(ms.bottom_scaled(im, 900 / im.width), 'christmas-reindeer.png')
    # the North Pole venue
    pb = Image.fromarray(key('passer-by', True)); pb = pb.crop(pb.getbbox())
    save(ms.bottom_scaled(pb, 560 / pb.width), 'kitchen-northpole-passer.png')
    for src, name in [('back-wall', 'wall'), ('counter', 'counter'), ('start', 'start')]:
        Image.open(SRC + src + '.png').convert('RGB').save('bg-%s-northpole.jpg' % name, quality=84, optimize=True); print('bg-%s-northpole.jpg' % name)
    return out


if __name__ == '__main__':
    print('BOXES', json.dumps(build()))
