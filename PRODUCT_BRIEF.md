# Product Brief: Franks and Buns 🌭

## You are my development partner.

I want to build a mobile-first web game called **"Franks and Buns"**.

---

## Purpose
A fast, silly, addictive arcade game where players catch falling hot dog ingredients, assemble ridiculous combos, and serve increasingly impatient customers — all against the clock.

## Target User
- Casual mobile gamers (ages 10+)
- People who want a quick 2-minute game to kill time
- Anyone who thinks hot dogs are inherently funny

## Game Concept
**Hot dogs rain from the sky. Catch them. Build them. Serve them. Don't drop them.**

The player holds a bun at the bottom of the screen and swipes/tilts to catch falling franks and toppings. Customers appear with orders. Match the order = points. Miss the frank = splat sound + lost life.

## Core Gameplay Loop
1. A customer appears with an order (e.g., "Frank + Mustard + Relish")
2. Ingredients fall from the top of the screen
3. Player slides their bun left/right to catch the RIGHT ingredients
4. Catch the wrong topping? Gross combo — lose points
5. Complete the order? Satisfying *DING* + score multiplier
6. Speed increases every 5 orders
7. Game ends when you lose 3 lives (dropped franks)

## Core Features (MVP)
- **Catch mechanic**: Slide bun left/right to catch falling items
- **Ingredient types**: Frank, mustard, ketchup, relish, onions, cheese, jalapeños
- **Customer orders**: Simple orders that get more complex over time
- **Scoring system**: Base points + combo multipliers + speed bonuses
- **Lives system**: 3 lives, lose one per dropped frank
- **Progressive difficulty**: Speed and order complexity increase
- **Silly sound effects**: Splats, dings, sizzles, cartoon boings
- **High score tracking**: Local high score saved in browser

## Visual Style
- Bright, cartoonish, playful
- Big chunky ingredients that are easy to tap/see on mobile
- Exaggerated animations (bouncy catches, dramatic splats)
- Fun color palette: yellow, red, green, warm browns

## Tech Preferences
- **Single HTML file** with embedded CSS and JavaScript (beginner-friendly, no build tools)
- **Vanilla JavaScript** — no frameworks needed for a game this scope
- **Canvas API** for the game rendering
- **Mobile-first**: Touch controls, responsive to phone screens
- **No backend needed** — everything runs in the browser
- **localStorage** only for high scores

## What to Build First
**Phase 1**: Just the core catch mechanic
- A bun at the bottom that slides left/right with touch
- Franks falling from the top
- Catch detection
- Score counter
- That's it. Get this feeling fun first.

---

## Future Phases (not yet — just the vision)
- Phase 2: Customer orders + ingredient variety
- Phase 3: Combo system + difficulty ramp
- Phase 4: Sound effects + animations + juice
- Phase 5: High scores + share functionality
- Phase 6: Power-ups (speed freeze, magnet bun, double points)
- Phase 7: Themed levels (ballpark, food truck, space station)

---

*This is a PROJECT.md-style document. Keep all development aligned with this brief.*
