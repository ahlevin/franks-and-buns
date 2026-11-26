"""Makes a shareable link for each video on the Videos page.

For every video below this writes:
  videos/<slug>.html       -> franksandbuns.com/videos/<slug>
                              A tiny page with link-preview tags (title, picture, video) that
                              sends visitors straight to that video on videos.html#<slug>.
  videos/share-<slug>.jpg  -> the 1200x630 picture shown when the link is shared.

Adding a video: add it to videos.html (the card's id is the slug), add it here, then run
    python3 tools/make_video_links.py
"""
import html, json, pathlib
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = 'https://franksandbuns.com'

VIDEOS = [
    dict(slug='how-to-play', title='How to Play', src='how-to-play.mp4', poster='how-to-play.jpg', secs=27,
         desc='Tap to boost, land in the bun, dodge the fork. Everything you need for your first game of Franks & Buns.'),
    dict(slug='dog-house', title="What's a Dog House?", src='videos/what-is-a-dog-house.mp4',
         poster='videos/what-is-a-dog-house.jpg', secs=26,
         desc='A private leaderboard for your family or friends. You can be in up to 5 Dog Houses, with up to 50 players in each.'),
    dict(slug='dog-house-tour', title='Dog House Tour', src='videos/dog-house-tour.mp4',
         poster='videos/dog-house-tour.jpg', secs=39,
         desc='Your code, inviting friends, letting new players in, and the weekly and all-time Wienerboards.'),
    dict(slug='recovery-code', title='Your Recovery Code', src='videos/recovery-code.mp4',
         poster='videos/recovery-code.jpg', secs=32,
         desc='Your code brings back your Dog Houses and costumes on a new phone or browser. Keep it safe and never share it.'),
]

FONT_BOLD = '/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'
FONT_REG = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | Franks &amp; Buns Videos</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="{site}/videos.html">
  <link rel="icon" type="image/x-icon" href="/favicon.ico">
  <meta property="og:type" content="video.other">
  <meta property="og:site_name" content="Franks &amp; Buns">
  <meta property="og:title" content="{title} | Franks &amp; Buns">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{site}/videos/{slug}">
  <meta property="og:image" content="{site}/videos/share-{slug}.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{title}: a {secs}-second Franks &amp; Buns video">
  <meta property="og:video" content="{site}/{src}">
  <meta property="og:video:secure_url" content="{site}/{src}">
  <meta property="og:video:type" content="video/mp4">
  <meta property="og:video:width" content="720">
  <meta property="og:video:height" content="1280">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title} | Franks &amp; Buns">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{site}/videos/share-{slug}.jpg">
  <script type="application/ld+json">{ld}</script>
  <script>location.replace('/videos.html' + location.search + '#{slug}');</script>
  <style>body{{background:#1a0e05;color:#fff8ee;font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;text-align:center;padding:80px 20px}}a{{color:#ffb347;font-size:1.2rem}}</style>
</head>
<body>
  <p><a href="/videos.html#{slug}">&#9654; Watch &ldquo;{title}&rdquo;</a></p>
</body>
</html>
"""


def card(v):
    W, H = 1200, 630
    img = Image.new('RGB', (W, H), '#1a0e05')
    d = ImageDraw.Draw(img)
    for y in range(H):  # warm glow
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(26 + 30 * (1 - t)), int(14 + 12 * (1 - t)), 5))
    poster = Image.open(ROOT / v['poster']).convert('RGB')
    ph = 560
    pw = round(poster.width * ph / poster.height)
    poster = poster.resize((pw, ph), Image.LANCZOS)
    px, py = W - pw - 70, (H - ph) // 2
    shadow = Image.new('L', (W, H), 0)
    ImageDraw.Draw(shadow).rounded_rectangle([px, py + 10, px + pw, py + ph + 10], 26, fill=170)
    img.paste((0, 0, 0), mask=shadow.filter(ImageFilter.GaussianBlur(18)))
    mask = Image.new('L', (pw, ph), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, pw - 1, ph - 1], 24, fill=255)
    img.paste(poster, (px, py), mask)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([px - 3, py - 3, px + pw + 2, py + ph + 2], 26, outline='#FFD700', width=4)
    cx, cy, r = px + pw // 2, py + ph - 80, 44  # play button, low so it does not cover the poster title
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill='#FF6600', outline='#fff8ee', width=4)
    d.polygon([(cx - 15, cy - 24), (cx - 15, cy + 24), (cx + 26, cy)], fill='#fff8ee')

    x, maxw = 70, px - 70 - 50
    d.text((x, 92), 'FRANKS & BUNS', font=ImageFont.truetype(FONT_BOLD, 38), fill='#FFD700')
    d.rectangle([x, 150, x + 90, 156], fill='#FF6600')
    size = 92
    while True:
        f = ImageFont.truetype(FONT_BOLD, size)
        words, lines, cur = v['title'].split(), [], ''
        for w in words:
            test = (cur + ' ' + w).strip()
            if d.textlength(test, font=f) <= maxw: cur = test
            else: lines.append(cur); cur = w
        lines.append(cur)
        if len(lines) <= 2 and all(d.textlength(l, font=f) <= maxw for l in lines): break
        size -= 4
    y = 190
    for l in lines:
        d.text((x, y), l, font=f, fill='#fff8ee')
        y += int(size * 1.12)
    d.text((x, y + 18), f"{v['secs']}-second video", font=ImageFont.truetype(FONT_REG, 36), fill='#c8a880')
    d.text((x, H - 120), 'franksandbuns.com/videos', font=ImageFont.truetype(FONT_REG, 32), fill='#FF6600')
    out = ROOT / 'videos' / f"share-{v['slug']}.jpg"
    img.save(out, quality=86, optimize=True, progressive=True)
    return out


def main():
    vids_html = (ROOT / 'videos.html').read_text()
    for v in VIDEOS:
        if f'id="{v["slug"]}"' not in vids_html:
            raise SystemExit(f'videos.html has no card with id="{v["slug"]}"')
        ld = {
            '@context': 'https://schema.org', '@type': 'VideoObject',
            'name': v['title'], 'description': v['desc'],
            'thumbnailUrl': f"{SITE}/{v['poster']}", 'contentUrl': f"{SITE}/{v['src']}",
            'uploadDate': '2026-11-22', 'duration': f"PT{v['secs']}S",
            'url': f"{SITE}/videos/{v['slug']}",
        }
        e = {k: html.escape(str(val), quote=True) for k, val in v.items()}
        page = PAGE.format(site=SITE, ld=json.dumps(ld, ensure_ascii=False).replace('</', '<\\/'), **e)
        (ROOT / 'videos' / f"{v['slug']}.html").write_text(page)
        print('wrote', f"videos/{v['slug']}.html", card(v).relative_to(ROOT))


if __name__ == '__main__':
    main()
