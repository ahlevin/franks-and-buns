# Franks and Buns — Game Design Document

## The Flappy Bird Principle
Flappy Bird worked because of ONE thing: **tap timing**. One input. Infinite skill ceiling. Instant death. Instant restart. "Just one more try."

Franks and Buns uses the same principle: **tap to pump the frank upward, stop tapping to let it drop into a bun.**

---

## THE CORE MECHANIC

### The Setup
You're looking at a side-scrolling kitchen. A hot dog (the frank) is on the left side of the screen, floating in mid-air. The kitchen scrolls right-to-left, and **buns appear at different heights** — tucked in cabinets, sitting in open ovens, balanced on shelves, even in a dog's mouth.

### The One Input
**TAP** = the frank bounces upward (like Flappy Bird's flap)
**STOP TAPPING** = the frank drops with gravity

### The Goal
Guide your frank through the scrolling kitchen and **drop it perfectly into a bun**.

### How It Actually Plays

```
THE SCREEN (phone held vertically):

┌─────────────────────────────┐
│  Score: 7    Best: 23       │
│  [🌭 x7 ████████░░ box!]   │
│                             │
│   ┌─────┐                   │
│   │ 🌭  │← your frank       │
│   └─────┘                   │
│              ╔═══════╗      │
│              ║ shelf ║      │
│              ║  🥖   ║← bun!│
│              ╚═══════╝      │
│                             │
│     ┌──────────┐            │
│     │  OVEN    │            │
│     │   🥖    │← bun in    │
│     │         │   oven!     │
│     └──────────┘            │
│                             │
│         🐕← dog with bun   │
│        (🥖 in mouth)        │
│                             │
│▓▓▓▓▓▓ counter ▓▓▓▓▓▓▓▓▓▓▓▓│
└─────────────────────────────┘

Tap tap tap → frank rises
Stop tapping → frank drops
Land in bun → SCORE!
Miss → SPLAT! 🟥 ketchup everywhere
```

---

## WHY THIS IS ADDICTIVE (The Psychology)

### 1. Tap Rhythm Creates Flow State
Just like Flappy Bird, you develop a TAP RHYTHM. Your brain locks into "tap-tap-tap... release... DROP!" It becomes muscle memory. When you're in the zone, it feels effortless. When you mess up, you KNOW it was your fault. That's what makes you hit restart.

### 2. The Drop Is the Dopamine Hit
The frank doesn't just land in the bun — it **nestles in with a satisfying SNAP sound**, the bun closes slightly around it, and a little steam puff appears. That micro-reward is what keeps people playing. Every successful drop feels *chef's kiss*.

### 3. Near Misses Are Brutal (In a Good Way)
When you BARELY miss a bun, the frank clips the edge and tumbles off with a sad trombone. Ketchup splatters across the screen. You can SEE how close you were. "ONE MORE TRY."

### 4. The Kitchen Scrolls — You Can't Stop
Like Flappy Bird's pipes, the kitchen keeps scrolling. Buns keep coming. You can't pause to think. It's react or die.

---

## THE BUNS — Where They Appear

Buns show up in increasingly ridiculous kitchen locations:

| Location | Difficulty | Visual |
|---|---|---|
| Open counter | Easy | Bun sitting on countertop |
| Cabinet shelf | Medium | Bun inside an open cabinet |
| Inside oven | Medium | Bun visible through oven door opening |
| Top of fridge | Hard | Bun balanced on top of fridge |
| Dog's mouth | Hard | A cartoon dog walking by with a bun in its mouth — it MOVES |
| Toaster (popping) | Very Hard | Bun pops up from toaster briefly — tiny timing window |
| Ceiling fan | Insane | Bun rotating on a ceiling fan blade |

The further you get, the crazier the bun placements become.

---

## CONDIMENT SYSTEM — Extra Points

### Golden Buns (Condiment Buns)
Every few buns, a special **condiment bun** appears. These buns already have a condiment loaded on top, shown as a little icon:

- 🟡 **Mustard Bun** = 2x points
- 🔴 **Ketchup Bun** = 3x points
- 🟢 **Relish Bun** = 5x points (rare)
- 🧀 **Cheese Bun** = 5x points (rare, melty animation)
- 🌶️ **Jalapeño Bun** = 10x points (VERY rare, bun is literally on fire)

When you land a frank in a condiment bun:
- The condiment does a little SQUIRT animation onto the frank
- Special sound effect (squiiiiish)
- Points flash big on screen
- Screen does a tiny shake for the rare ones

### The Miss = Ketchup Splatter
When you miss ANY bun and the frank hits the counter/floor:
- **SPLAT** — a big ketchup splatter covers part of the screen
- The splatter partially obscures your view for 1-2 seconds
- It slowly drips away
- This is both punishment AND humor
- Multiple misses = screen gets messier (but never unplayable)

---

## THE BOX SYSTEM — Combo Milestone

This is your "level up" mechanic that keeps long runs exciting.

### How It Works
- A **hot dog box** meter sits at the top of the screen
- Every frank you land fills one slot in the box (boxes hold 8 franks)
- When the box is FULL (8 franks):
  - The box CLOSES with a satisfying cardboard-flap sound
  - Big "BOXED!" text slams onto screen
  - You get a fat bonus (box number × 100 points)
  - A new empty box appears
  - **The kitchen speeds up slightly**

### The Box Counter
```
Box Progress Bar:
[🌭🌭🌭🌭🌭🌭🌭░]  7/8  — ONE MORE!

BOXED! → 🎁 +800pts → Box #8 complete!
```

### Why Boxes Make It Addictive
- You're ALWAYS close to finishing a box
- "I just need 2 more franks to box it..."
- The speed increase after each box means the game gets harder at a perfect rate
- Box count becomes bragging rights: "I boxed 12 in one run!"

---

## SCORING SYSTEM

| Action | Points |
|---|---|
| Frank in regular bun | 100 |
| Frank in mustard bun | 200 |
| Frank in ketchup bun | 300 |
| Frank in relish bun | 500 |
| Frank in cheese bun | 500 |
| Frank in jalapeño bun | 1000 |
| Completing a box | Box # × 100 |
| Dog's mouth bun | 2x whatever the bun is worth |
| Toaster bun | 3x |

### Streak Bonus
- Land 3 in a row without missing = "ON A ROLL!" (1.5x multiplier)
- Land 5 in a row = "FRANKS ON FIRE!" (2x multiplier)
- Land 10 in a row = "WIENER WIZARD!" (3x multiplier)
- Miss once = streak resets

---

## GAME OVER & RESTART

### Lives System
- You start with **3 lives** (shown as 3 little franks at the top)
- Dropping a frank (missing all buns as it scrolls past) = lose a life
- Hitting an obstacle (e.g., cabinet door that swings shut) = lose a life
- At 0 lives: Game Over

### The Game Over Screen
```
┌─────────────────────────────┐
│                             │
│     GAME OVER               │
│                             │
│     Score: 4,700            │
│     Best:  12,300           │
│     Franks Landed: 23       │
│     Boxes: 2                │
│     Best Streak: 7          │
│                             │
│     ┌─────────────────┐     │
│     │   TAP TO RETRY  │     │
│     └─────────────────┘     │
│                             │
│     🌭 "You're on a roll!"  │
│                             │
└─────────────────────────────┘
```

### Key Addiction Element: INSTANT RESTART
Just like Flappy Bird — one tap and you're back in. No menus. No loading. No friction. Die → see score → tap → playing again in under 1 second.

---

## DIFFICULTY PROGRESSION

| Boxes Completed | What Changes |
|---|---|
| 0 | Slow scroll, big buns, easy placements |
| 1 | Slightly faster |
| 2 | Cabinet buns start appearing |
| 3 | Oven buns, smaller bun targets |
| 5 | Dog walks through, toaster buns |
| 7 | Obstacles appear (swinging cabinet doors) |
| 10 | Ceiling fan buns, maximum chaos |
| 12+ | "Nightmare Kitchen" — everything at once |

---

## SOUND DESIGN (Critical for Addiction)

- **Tap**: Quick little "boing" (like a spring)
- **Frank rising**: Tiny whistle sound ascending
- **Frank dropping**: Whoooosh
- **Landing in bun**: Satisfying SNAP + sizzle
- **Condiment bun**: SQUISH + sparkle sound
- **Miss / splat**: Wet SPLAT + sad trombone
- **Box complete**: Cardboard FLAP + cash register CHING
- **Streak sounds**: Escalating "ding ding ding!"
- **Game over**: Cartoon deflate sound
- **Background**: Upbeat kitchen-themed music (optional, toggle-able)

---

## VISUAL JUICE (What Makes It Feel Amazing)

- Frank squishes slightly on each tap (squash & stretch animation)
- Buns have a subtle glow/bounce to draw your eye
- Condiment buns sparkle
- Screen shake on big moments (box complete, jalapeño bun)
- Ketchup splatter on misses that drips down the screen
- Streak counter gets bigger and more fiery with each consecutive hit
- Speed lines appear at the edges when kitchen scrolls fast
- Everything is slightly bouncy — nothing is static

---

## SUMMARY: Why This Works

1. **One mechanic** — tap to rise, release to drop (Flappy Bird simplicity)
2. **Instant feedback** — every action has a sound and visual response
3. **Always almost winning** — boxes keep you "one more" away from a milestone
4. **Escalating chaos** — the kitchen gets crazier the longer you survive
5. **Humor** — ketchup splats, dogs with buns, ceiling fan buns = shareable moments
6. **Bragging rights** — high scores + box count + best streak
7. **Zero friction restart** — die and retry in 1 second
8. **The sounds** — satisfying snap, sizzle, and squish sounds are 50% of the addiction

This is a "just one more try" game. That's the whole point.
