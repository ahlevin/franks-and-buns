# Sports Mode artwork handoff

The incoming folders contain generated source artwork for basketball, American football, water polo and golf. Basketball, football and water polo each include the ball, targets, player, defender, defender arm, dog, fireball, venue back wall, ground strip, title background and passing object. Golf includes the seven sprite sheets and is intended to reuse the existing golf course backgrounds as described in the brief.

## Before game integration

- The sprites are supplied as unsplit, unkeyed source images. Remove the green backgrounds for basketball, football and water polo, and magenta for golf; inspect edges and holes inside nets for color spill. Split, trim, align and resize the states to the existing game asset sizes.
- The first two player poses in each sport are visually very similar, rather than clearly alternating strides or swimming strokes. Review the animations at game speed; redraw or replace a frame if a proper alternating cycle is required.
- The football target sheet depicts a wide net with short posts, rather than clearly raised goalpost uprights. Assess whether it reads sufficiently as a kicking net at game size or needs revision.
- The venue back walls and ground strips were requested as horizontally tileable, but seamless joins have not been verified. Test both edges in the scrolling game and repair if needed.
- Inspect each dog and fireball sheet for consistent animation alignment, and confirm the color keys and sprite boundaries before use. The artwork has not been integrated into or tested in the game.
- Keep the artwork generic, with no school, league, team or sponsor branding. The player's only lettering is intended to be number 25.

Baseball and cricket were future ideas in the brief, without full artwork prompts, and are not included.
