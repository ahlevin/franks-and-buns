# Soccer Edition artwork

The `incoming` folder contains all 12 generated images from the Soccer Edition brief. The eight soccer sprite sheets and the team bus use green backgrounds for chroma keying; the three stadium backgrounds are opaque. Sprite sheets have not been keyed, split, aligned, or resized to game dimensions.

Before integrating:

- Remove green backgrounds, including spaces inside goal nets; check anti-aliased edges for green spill, then split the sheets into their individual states and align them on consistent canvases.
- The first two poses in `soccer-player.png` are very similar, rather than clearly alternating running strides. Review the animation and redraw or replace one pose if an alternating run is required.
- `soccer-keeper-arm.png` has a small exposed wrist between glove and sleeve and the arm stops just short of the bottom edge; extend or trim as needed for the hazard.
- Test the horizontal seams of `stadium-back-wall.png` and `stadium-counter.png` in motion. Seamless tiling was requested but is not guaranteed; repair the joins if needed.
- Scale and crop the generated images to the game dimensions in the brief, and test readability at actual display size. They are source art, not finalized game-ready sprites.
- Keep the imagery generic: no school name, initials, logos, crest or mascot; the player's only text should be the number 25.
