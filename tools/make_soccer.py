"""Soccer Edition: key out the green backgrounds of new-art/soccer/*.png, split the sheets into pictures and
write the game sprites (soccer-*.png) at the sizes game.html draws them (4 sprite pixels per game pixel, like sp-*.png).
Run from the repo root: python3 tools/make_soccer.py"""
import numpy as np
from PIL import Image
from scipy import ndimage

SRC = 'new-art/soccer/'

def key(path):
    """RGBA with the chroma green removed and green spill pulled out of the edges"""
    a = np.asarray(Image.open(SRC + path).convert('RGB')).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    green = g - np.maximum(r, b)                     # how much greener than the other channels
    alpha = np.clip(1 - (green - 60) / 110, 0, 1)    # >170 greener: background; <60: solid
    # despill: no pixel stays greener than its other channels
    g2 = np.where(green > 0, np.maximum(r, b) + np.minimum(green, 0) , g)
    out = np.dstack([r, np.minimum(g, g2 + 6), b, alpha * 255]).astype(np.uint8)
    # drop tiny specks and keep the big shapes and their nearby bits
    return out

def pieces(rgba, cols, rows, min_px=400):
    """Split a sheet laid out as a cols x rows grid: each opaque blob goes to the cell its centre falls in"""
    h, w = rgba.shape[:2]
    mask = rgba[..., 3] > 40
    lab, n = ndimage.label(mask)
    cells = {}
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        ys, xs = sl
        size = (lab[sl] == i).sum()
        if size < min_px: continue
        cy, cx = (ys.start + ys.stop) / 2, (xs.start + xs.stop) / 2
        c = (int(cy * rows / h), int(cx * cols / w))
        keep = np.zeros_like(mask); keep[lab == i] = True
        if c in cells: cells[c][0] |= keep
        else: cells[c] = [keep]
    out = {}
    for c, (keep,) in cells.items():
        # include the soft edge pixels around the blobs
        grown = ndimage.binary_dilation(keep, iterations=3)
        im = rgba.copy(); im[..., 3] = np.where(grown, im[..., 3], 0)
        ys, xs = np.where(im[..., 3] > 8)
        out[c] = Image.fromarray(im[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
    return out

def fit(im, w, h, anchor='center', scale=None):
    """Place im on a transparent w x h canvas, scaled to fit (or by scale), centred or sitting on the bottom"""
    s = scale or min(w / im.width, h / im.height)
    j = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
    c = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    x = (w - j.width) // 2
    y = (h - j.height) // 2 if anchor == 'center' else h - j.height
    c.alpha_composite(j, (x, max(0, y))); return c

def sheet(f, cols, rows):
    return pieces(key(f), cols, rows)

def bottom_scaled(im, s):
    return im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)

def place(canvas_size, im, box):
    """fit im inside box (x0, y0, x1, y1) of a transparent canvas: centred across, sitting on the box bottom"""
    x0, y0, x1, y1 = box
    s = min((x1 - x0) / im.width, (y1 - y0) / im.height)
    j = bottom_scaled(im, s)
    c = Image.new('RGBA', canvas_size, (0, 0, 0, 0))
    c.alpha_composite(j, (x0 + (x1 - x0 - j.width) // 2, y1 - j.height)); return c

def save(im, name):
    im.save(name, optimize=True); print(name, im.size)

if __name__ == '__main__':
    BOXES = {}   # skin draw boxes for game.html
    # ball: the in-flight ball (38 game px), and the title / intro ball like hotdog.png
    ball = sheet('soccer-ball.png', 2, 1)
    save(fit(ball[(0, 0)], 152, 152), 'skin-soccer-fly.png'); BOXES['fly'] = [-19, -19, 38, 38]
    save(place((512, 512), ball[(0, 0)], (96, 96, 416, 416)), 'soccer-ball.png')
    # goals: 88 game px wide like the bun picture; the same scale for all four so the posts line up
    g = sheet('soccer-goals.png', 2, 2)
    empty, scored, hot, hotscored = g[(0, 0)], g[(0, 1)], g[(1, 0)], g[(1, 1)]
    s = 352 / max(empty.width, hot.width)
    for im, name in [(empty, 'soccer-goal.png'), (hot, 'soccer-goal-hot.png'), (scored, 'soccer-goal-ball.png')]:
        j = bottom_scaled(im, s); c = Image.new('RGBA', (352, 148), (0, 0, 0, 0)); c.alpha_composite(j, ((352 - j.width) // 2, 148 - 3 - j.height)); save(c, name)
    j = bottom_scaled(hotscored, s); c = Image.new('RGBA', (352, 148), (0, 0, 0, 0))
    c.alpha_composite(j, ((352 - j.width) // 2, 148 - 3 - j.height)); save(c, 'soccer-goal-hot-ball.png')   # steam cut off: the costume picture below keeps it
    for im, part in [(scored, 'bun'), (hotscored, 'grill')]:
        j = bottom_scaled(im, s); save(j, 'skin-soccer-' + part + '.png')
        w, h = j.width / 4, j.height / 4; BOXES[part] = [round(-w / 2, 1), round(5 - 0.75 - h, 1), round(w, 1), round(h, 1)]
    # fire ball power-up (2 frames) like sp-chili-a/b
    fb = sheet('soccer-fireball.png', 2, 1)
    sc = min(320 / max(fb[(0, 0)].width, fb[(0, 1)].width), 241 / max(fb[(0, 0)].height, fb[(0, 1)].height))
    for c_, n in [((0, 0), 'a'), ((0, 1), 'b')]:
        j = bottom_scaled(fb[c_], sc); c = Image.new('RGBA', (320, 255), (0, 0, 0, 0)); c.alpha_composite(j, ((320 - j.width) // 2, 255 - j.height)); save(c, 'soccer-fireball-' + n + '.png')
    # dogs: intro thief with the ball, plain dog, bonus dogs carrying a goal (2 frames like sp-dog-a/b)
    d = sheet('soccer-dog.png', 2, 2)
    save(place((512, 512), d[(0, 0)], (14, 104, 468, 404)), 'soccer-dog.png')
    save(place((512, 512), d[(0, 1)], (14, 104, 468, 404)), 'soccer-dognodog.png')
    # bonus dogs (Dog Parade and the +1000 dogs): the plain dog with a referee's yellow or red card in its teeth (Alan, 2026-11-26).
    # The card is cut from the pickups sheet above the referee's hand, laid over the lower jaw, and the upper muzzle is put back on top.
    pk = sheet('soccer-pickups.png', 5, 1)
    dog = d[(0, 1)]
    for c_, n in [((0, 0), 'yellow'), ((0, 1), 'red')]:
        card = pk[c_].crop((70, 0, pk[c_].width, 228)); card = bottom_scaled(card, 0.5)
        w, h = card.size; pad = Image.new('RGBA', (w * 3, h * 3), (0, 0, 0, 0)); pad.alpha_composite(card, (w, h))
        rot = pad.rotate(-125, center=(w + w // 2, h + h), resample=Image.BICUBIC)
        cv = Image.new('RGBA', (dog.width + 200, dog.height + 200), (0, 0, 0, 0))
        cv.alpha_composite(dog, (0, 0)); cv.alpha_composite(rot, (472 - (w + w // 2), 190 - (h + h)))
        top = np.asarray(dog).copy(); yy, xx = np.mgrid[0:top.shape[0], 0:top.shape[1]]
        top[..., 3] = np.where((yy < 188) & (xx > 400), top[..., 3], 0)
        cv.alpha_composite(Image.fromarray(top), (0, 0)); cv = cv.crop(cv.getbbox())
        save(place((280, 208), cv, (0, 22, 280, 186)), 'soccer-dog-' + n + '.png')
    # keeper (chef in the intro) and his arm (the fork hazard): glove where the fork's tines were
    save(place((512, 512), sheet('soccer-keeper.png', 1, 1)[(0, 0)], (38, 44, 436, 433)), 'soccer-keeper.png')
    save(place((512, 768), sheet('soccer-keeper-arm.png', 1, 1)[(0, 0)], (140, 64, 396, 740)), 'soccer-keeper-arm.png')
    # bonus pickups (the condiments), 64x128 each
    pk = sheet('soccer-pickups.png', 5, 1)
    for i, n in enumerate(['mustard', 'ketchup', 'relish', 'cheese', 'jalapeno']):
        save(place((64, 128), pk[(0, i)], (2, 7, 62, 120)), 'soccer-pick-' + n + '.png')
    # the player: same scale for every pose, 72 game px tall (4x)
    pl = sheet('soccer-player.png', 4, 1)
    sc = 288 / max(p.height for p in pl.values())
    W_ = round(max(p.width for p in pl.values()) * sc) + 8
    for i, n in enumerate(['run-a', 'run-b', 'kick', 'cheer']):
        j = bottom_scaled(pl[(0, i)], sc); c = Image.new('RGBA', (W_, 292), (0, 0, 0, 0)); c.alpha_composite(j, ((W_ - j.width) // 2, 292 - j.height)); save(c, 'soccer-player-' + n + '.png')
    # stadium kitchen
    bus = sheet('stadium-passer-by.png', 1, 1)[(0, 0)]
    save(bottom_scaled(bus, 560 / bus.width), 'kitchen-stadium-passer.png')
    for src, name in [('stadium-back-wall.png', 'bg-wall-stadium.jpg'), ('stadium-counter.png', 'bg-counter-stadium.jpg'), ('stadium-start.png', 'bg-start-stadium.jpg')]:
        Image.open(SRC + src).convert('RGB').save(name, quality=84, optimize=True); print(name)
    print('SOCCER_SKIN boxes', BOXES)
