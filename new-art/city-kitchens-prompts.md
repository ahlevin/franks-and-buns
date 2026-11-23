# City Kitchens: art prompts (v2: colors tuned for gameplay)

These are for the image generator in your other project. Give it **chef.png** and **dog.png** as style references, plus **bg-wall-a.jpg** for line weight. Each city needs 4 pictures:
1. **Back wall**: landscape 3:2. Scrolls slowly behind the game and repeats left to right.
2. **Counter strip**: very wide 3:1. The counter and ground at the bottom of the screen, also repeating.
3. **Start screen**: portrait 9:16. The hero shot, with a calm middle for the title and buttons.
4. **Passer-by**: a transparent train or cable car that rolls across the back wall now and then.

## Why the colors matter (read before generating)
Everything you play with is **warm**: franks are red-brown (#b54224), buns are golden tan (#d39d5a), and ketchup is red, mustard yellow, relish green, cheese orange and the chili dog red-orange. The chef's fork arm is silver and white, and the score and buttons are gold (#FFD700) and orange (#FF6600). So the backgrounds get their wow from **cool, saturated color**: twilight blues, indigo, violet, magenta-pink, teal and cyan. That's vibrant, but nothing in it can be mistaken for a frank or a bun.

**Every prompt below already includes these rules. Keep them if you edit a prompt.**
- **Middle band (about 15% to 85% of the back wall's height)**: this is where franks and buns fly. Use mid-value cool colors with soft, low-contrast detail. No large red, orange, tan, gold, yellow, bright green, pure white or silver areas, and no busy high-contrast patterns.
- **Wow zones**: the sky in the top 15% (the score sits there under a dark band), the left and right thirds, the start screen, and small glowing accents. Here, go rich: golden-hour or twilight light, glowing fog, neon, depth and detail.
- **Warm colors only as small accents**: lit windows, a sunset rim of light, a street lamp glow. Tiny spots, never big areas.
- **Landmarks** sit high or at the sides and are softened by haze or fog where they cross the middle band.
- **Counter strip**: anything goes except bun-tan and frank-red. Steel, teal, blue and cream all work.
- **Start screen**: full color, the most dramatic picture of the set. The game dims it under the title, so it can be bold.

General rules: stylized cartoon landmarks only. No real logos, transit maps, route numbers, team names, store names or readable words anywhere, including the graffiti. No people, animals, food or hot dogs.

---

## New York (twilight)

### nyc-back-wall
Use case: stylized-concept. Generate one finished game background asset, not a sheet or mockup.
Input images are STYLE REFERENCES ONLY: chef and dog. Match their bold dark outlines, appealing rounded cartoon shapes and crisp cel shading. Do not include these characters or copy their gray backdrops.
Asset: BACK WALL for the New York level of Franks and Buns, a 2D side-scrolling arcade game. Landscape 3:2, request 3072 x 2048 or the largest available landscape resolution.
New York at twilight, seen straight on. Upper half: a gorgeous dusk sky, deep indigo at the top fading to violet and soft magenta-pink at the horizon, with a few pink-lit clouds. Against it, a stylized Manhattan skyline in deep blue-violet silhouettes with tiny glowing windows (mostly pale cyan-white, a few small warm ones), an Art Deco spire tower with a stepped crown catching a thin pink rim light, and a stepped skyscraper with a mast. On one side, a stylized stone suspension bridge with Gothic arches in cool slate blue, softened by haze. A dark slate-blue elevated train track runs straight across at about 55% height. Below the track: a periwinkle-blue painted brick wall, mid-value and low contrast, with two or three glowing neon-style abstract graffiti pieces (bubbly blobs, stars, swooshes, drips in electric cyan, violet and magenta, NO letters or words) placed low and toward the sides, and one black iron fire escape.
Palette rules: the middle band (15% to 85% of the height) stays mid-value, cool and calm: blues, violets, periwinkle, teal. No large red, orange, tan, gold, yellow, bright green, white or silver areas. Warm color only as tiny window lights.
Perfectly flat orthographic straight-on elevation, no perspective vanishing point. Seamless horizontal repetition: left and right edges match exactly, landmarks kept away from both side edges. No vignette.
No people, animals, food, hot dogs, buns, vehicles, shelves, countertops, platforms, floor, text, letters, numbers, logos, signs, UI or watermark. Opaque full-bleed background.

### nyc-counter
Use case: stylized-concept. Generate one finished COUNTER AND GROUND STRIP for a 2D side-scrolling mobile arcade game, not a scene mockup. Chef and dog are STYLE references only, no characters. The NYC back wall is the palette reference. Very wide 3:1, target 3264x1088 or the largest wide format available. Full bleed, opaque.
A long shiny stainless-steel street-cart counter EDGE flush against the very TOP of the image (top 8%) with a cool blue-white reflection, then brushed steel cart panels with simple rivets and a bold cobalt-blue and sky-blue striped trim band (roughly the next 60%), then a blue-grey city sidewalk of square concrete slabs with a curb along the bottom 30%. Cool twilight light with a faint violet bounce. No wall or sky above the counter. Flat straight-on elevation, no vanishing point, identical slab sizes, no converging lines. Bold clean cartoon outlines and soft cel shading. Seamless horizontal repetition with a whole number of repeating panels. No tan, gold, yellow or red. No people, animals, food, objects on the counter, text, logos, numbers, UI or watermark.

### nyc-start
Use case: stylized-concept. One finished mobile arcade game title screen BACKDROP, portrait 9:16, request 1440x2560 or the maximum available. Chef and dog are STYLE references only, no characters. The NYC back wall is the palette reference.
The hero shot, full color and dramatic: New York at golden hour turning to twilight. A rich sky from deep indigo at the top to glowing magenta, coral and peach at the horizon. A tall stylized Manhattan skyline in deep blue-violet silhouettes with hundreds of tiny glowing windows, an Art Deco spire tower lit by a sunset rim, and the arches of a stone suspension bridge glowing at one side. Lower down, a periwinkle painted brick wall with a glowing neon-style abstract graffiti piece (no letters) and a shiny stainless-steel street-cart counter across the bottom quarter on a blue-grey sidewalk. Depth and atmosphere: light haze between the layers, a few lit clouds. Keep the CENTER (roughly the middle 50% of the height) calm with no detail: open glowing sky for the title and menu. Straight-on, no vignette. No people, animals, food, hot dogs, vehicles, text, letters, logos, signs, UI or watermark.

### nyc-passer-by
Use case: stylized-concept. One transparent PNG game sprite: a cute chunky cartoon subway train of three cars, side view, moving right to left, on a fully transparent background. Cool blue-silver body with a cobalt stripe, rounded windows glowing soft pale cyan, bold dark outlines, soft cel shading, no people in the windows. Wide 4:1. No yellow, orange or red. No route letters, numbers, logos, words, tracks, background or shadow.

---

## San Francisco (glowing fog)

### sf-back-wall
Use case: stylized-concept. Generate one finished game background asset, not a sheet or mockup.
Input images are STYLE REFERENCES ONLY: chef and dog. Match their bold dark outlines, rounded cartoon shapes and crisp cel shading. Do not include these characters.
Asset: BACK WALL for the San Francisco level of Franks and Buns, a 2D side-scrolling arcade game. Landscape 3:2, request 3072 x 2048 or the largest available.
San Francisco in the late afternoon, seen straight on. Upper part: a sky from clear blue at the top to soft pink-lavender lower down. The stylized suspension bridge in its signature orange-red, with its two tall towers and sweeping cables, sits in the TOP THIRD only, half-veiled by a glowing band of pink-lavender fog that softens it. Below it, calm blue bay water with a few sparkles, blue-grey hills, and a small distant skyline with a pointed pyramid-shaped tower. Lower half: a row of Victorian houses with bay windows and gingerbread trim in vivid COOL pastels (lavender, mint-teal, periwinkle blue, orchid pink, sky blue), with crisp white trim. Lower half detail stays simple and mid-value.
Palette rules: the middle band (15% to 85% of the height) stays cool and calm: blues, lavenders, teals, orchid pink. No large orange, red, tan, gold, butter-yellow, peach, bright green, pure white or silver areas there. The bridge's orange-red stays small, high up and softened by fog.
Perfectly flat orthographic straight-on elevation, no vanishing point. Seamless horizontal repetition with landmarks away from both side edges. No vignette.
No people, animals, food, hot dogs, buns, vehicles, shelves, countertops, platforms, floor, text, letters, numbers, logos, signs, UI or watermark. Opaque full-bleed background.

### sf-counter
Use case: stylized-concept. Generate one finished COUNTER AND GROUND STRIP for a 2D side-scrolling mobile arcade game. Chef and dog are STYLE references only. The SF back wall is the palette reference. Very wide 3:1, target 3264x1088. Full bleed, opaque.
A long glossy teal painted wooden food-stand counter EDGE flush against the very TOP (top 8%), then cool cream-white wooden stand panels with teal trim and simple bolts (roughly the next 60%), then a light blue-grey sidewalk with a strip of slate-grey paving and a curb along the bottom 30%. No sky above the counter. Flat straight-on elevation, no vanishing point. Bold clean cartoon outlines, soft cel shading. Seamless horizontal repetition. No tan, gold, yellow, orange or red. No people, animals, food, objects on the counter, text, logos, numbers, UI or watermark.

### sf-start
Use case: stylized-concept. One finished mobile arcade game title screen BACKDROP, portrait 9:16, request 1440x2560. Chef and dog are STYLE references only. The SF back wall is the palette reference.
The hero shot, full color and dramatic: San Francisco at golden hour. One tower of the orange-red suspension bridge rises tall at one side, glowing in warm sunset light, its cables sweeping across the top. Glowing pink-and-peach fog rolls through below the deck over deep blue water that sparkles. A small skyline with a pyramid-shaped tower sits in the distance, and a row of vivid cool-pastel Victorian houses lines the lower edge. A teal wooden food-stand counter runs across the bottom quarter. Depth and atmosphere: sunbeams through the fog. Keep the CENTER (roughly the middle 50% of the height) calm with no detail: soft glowing fog and sky for the title and menu. Straight-on, no vignette. No people, animals, food, hot dogs, vehicles, text, letters, logos, signs, UI or watermark.

### sf-passer-by
Use case: stylized-concept. One transparent PNG game sprite: a cute chunky cartoon cable car, side view, moving right to left, on a fully transparent background. Deep teal and cream-white body with silver trim, an open-sided bench section, rounded roof, windows in soft pale blue, bold dark outlines, soft cel shading, no people. Wide 2.5:1. No red, orange or yellow. No numbers, route names, logos, words, rails, background or shadow.

---

## Checking new art before it goes in
Drop a picture into the game with `?bg=nyc` or `?bg=sf` and play one round. If a bun or frank ever blends into the wall in the middle of the screen, that area needs to be cooler or calmer.

## More cities later, same recipe
- **Chicago**: L train on a steel trestle, a dark skyscraper with two antennas, a river with a drawbridge, in an electric-blue night.
- **Coney Island boardwalk**: wooden roller coaster and Ferris wheel at sunset, summer only. Keep the warm sunset in the sky and the boardwalk in cool shadow.
- **Ballpark**: green outfield wall under stadium lights at night. No team names or logos.
