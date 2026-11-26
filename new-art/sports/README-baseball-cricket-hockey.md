# Baseball, Cricket and Ice Hockey — art handoff

Each sport has 11 original generated source images: ball/puck, target sheet, player sheet, defender, defender arm, dog sheet, fireball sheet, venue back wall, ground strip, start screen and passer-by. The baseball ballpark artwork is newly generated for this set; it does not reuse the earlier Ballpark kitchen images.

Sprites retain chroma green backgrounds and need to be keyed, split, trimmed, aligned and scaled to the existing game asset sizes. Backgrounds are opaque and have not been resized to the game's target dimensions. These are source artwork, not integrated game assets.

Review before use:

- In each player sheet, the first two running or skating poses look very similar; redraw or replace one if a convincing alternating two-frame cycle is needed.
- The hockey player's visor contains green-tinted highlights that may be affected by chroma keying. Inspect and repair the visor edges and reflections.
- Check green spill, detached elements, net openings, frame registration and any clothing details on all keyed sprites, especially at actual game size.
- The horizontal venue tiling was requested but has not been verified; test the seams in motion and fix if needed.
- Check that the wickets, mitts and nets remain readable and align correctly with game hitboxes after cropping.

The only intended lettering on the sprites is the player's number 25. No game code, gameplay, sounds, feature flags or store assets were modified.
