# Christmas free costume gift (xmasgift)

Every player can pick **one** costume that BunBux could unlock, for free. Limited Edition and premium costumes are left out, and so are costumes the player already owns.
It runs from **Dec 24 2026 00:00 to Jan 1 2027 23:59:59, California time**. It starts and stops on its own, with no deploy needed.

## What players see
- On the start screen, the first time the game opens each day during the gift: a "Merry Christmas!" pop-up with **Pick my gift** and **Later**. After it has shown once, it waits until the next day.
- Until they claim it, there is a red **FREE GIFT** tag on the SKINS button and a gift row at the top of the costume screen.
- **Pick my gift** shows the costumes they can choose. They pick one, confirm it, and then see a thank-you screen. The costume is unlocked like a BunBux unlock and they start wearing it right away.
- If the game can't reach the server (offline), nothing about the gift shows.

## Turn it off
In `flags.json`, set `"xmasgift": false` and push. The game hides the gift and the server refuses claims. A costume a player already claimed stays theirs.
The server re-reads `flags.json` within about a minute. Some players' games may keep showing the gift for up to 5 minutes because of browser caching, but the server will refuse their claims.

## Change the dates
In `flags.json`:
```json
"xmasgiftwindow": { "id": "xmas2026", "start": "2026-12-24T08:00:00Z", "end": "2027-01-02T08:00:00Z" }
```
- The times are in UTC. Midnight in California is `08:00:00Z` in winter (PST) and `07:00:00Z` in summer (PDT).
- `end` is when the gift stops. The value above means "through the end of Jan 1".
- Keep `id` as it is for this year. Each player can claim once per `id`, so changing it (for example to `xmas2027` next year) lets everyone claim again.

## Test it on the preview site
Add `?xmasgift=test` to the URL on preview.franks-and-buns.pages.dev, any other pages.dev preview, or localhost. The gift then opens whatever the date or the switch says.
- The picker lists costumes this browser doesn't really own, even on the preview site, where every costume is shown as unlocked. Add `&shop=test` to see the costume screen as a normal player does.
- The pop-up shows once a day per browser. To see it again, clear the `fb_gift_day` entry in site data (or use a private window).
- Each test profile can only claim once. A new private window gives you a new profile.
- `?xmasgift=off` hides it on a test site.
- The override never works on franksandbuns.com or in the apps. The server ignores it anywhere except pages.dev and localhost.

## How it works (for developers)
- API (`functions/api/[[path]].js`):
  - `GET /api/gift` returns `{ gift, open, start, end, claimed, skin, eligible[] }`. It works without a sign-in.
  - `POST /api/gift/claim {skin}` needs the player's token. Nameless profiles can claim.
- The server reads `xmasgift` and `xmasgiftwindow` from the site's own `flags.json`.
- A claim is accepted only if all of these are true:
  - the switch is on and now is inside the window (or it's a test host with `?test=1`)
  - the costume can be unlocked with BunBux today (`buxSkinOk`), and it isn't Limited Edition or a kitchen
  - the player doesn't already own it
  - the player hasn't claimed this gift before
- D1 table `gift_claims (player_id, gift_id, skin, claimed_at, PRIMARY KEY (player_id, gift_id))`. It is created by itself, like the other tables. The claim row and the costume are written in one transaction.
- Recovery code merge (`mergecode`):
  - If only the device's nameless profile had claimed, its claim moves over with it, so the merged profile can't claim again.
  - If both profiles had claimed, the merged profile keeps only its own gift costume.
- Deleting a profile also deletes its claim rows.
