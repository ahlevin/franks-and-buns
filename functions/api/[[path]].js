// Franks & Buns Packs API: private Wienerboards for groups of friends.
// Runs as a Cloudflare Pages Function at /api/*. Needs a D1 database bound as "DB"
// (Pages > Settings > Bindings, for both Production and Preview). Tables create themselves.

const ALPHA = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ';   // 32 symbols, no 0/O/1/I to misread
const MAX_PACKS_PER_PLAYER = 5;
const MAX_MEMBERS = 50;
const NEW_PLAYERS_PER_IP_PER_DAY = 20;
const NEW_SILENT_PLAYERS_PER_IP_PER_DAY = 200;   // nameless profiles the game makes to keep costumes (schools and phone networks share IPs)
const MAX_SKINS = 300;
const NEW_PACKS_PER_PLAYER_PER_DAY = 10;
const RECOVER_TRIES_PER_IP_PER_DAY = 60;   // recovery codes can't be guessed (80 random bits); this stops anyone hammering the server trying
const WRONG_JOIN_CODES_PER_DAY = 30;   // per player and per network: Dog House codes are short, so guessing them has to stay slow
const NEW_CODES_PER_PLAYER_PER_DAY = 5;   // "Get a new recovery code"
// BunBux: earned by playing (never sold). Amounts agreed with Alan, Nov 22, 2026.
const BUX = { perBox: 1, maxBoxes: 10, daily: 25, cap: 100, cost: 300 };   // cap: most BunBux a day from games and the challenge
// Limited Edition costumes are purchase only (same list as SKINS_LIMITED in game.html)
const BUX_LIMITED = new Set(['santa', 'bernedoodle', 'labradoodle', 'persian', 'mainecoon', 'slamdunk', 'goalgetter', 'axolotl', 'anglerfish', 'unidentifiedfryingobject', 'babykaiju', 'phoenix', 'shadowwizard',
  'glazedandconfused', 'blanketburrito', 'royaltreatment', 'raccoon', 'forkimpostor', 'professorfrank', 'glowgetter', 'specialdelivery',
  'discodog', 'maneevent']);
// The only costumes BunBux can unlock: the ones in Collections that are on sale (SHOP_COLS in game.html), minus Limited Edition.
// Anything else (Free & Earned, Collections not on sale yet) is refused. When a Collection goes on sale, add its costumes here.
const BUX_SKINS = new Set([
  'midnight', 'cupid', 'lucky', 'easter', 'yankee', 'frankula', 'gobble',   // Holiday
  'dachshund', 'corgi', 'golden', 'frenchie', 'husky', 'dalmatian', 'poodle', 'shiba', 'bernese',   // Dogs
  'tabby', 'tuxedo', 'calico', 'siamese', 'british', 'ragdoll', 'sphynx',   // Cats
  'touchdown', 'kickflip', 'partee',   // Sports
  'jellyfish', 'octopus', 'pufferfish',   // Deep Sea Dogs
].filter(id => !BUX_LIMITED.has(id)));
// Kitchens that unlock with BunBux, and their price (same as KITCHENS in game.html). Saved in bux_skins like costumes.
const BUX_KITCHENS = { kitchensf: 500, kitchenchicago: 500, kitchenconey: 500, kitchenboston: 500, kitchenseattle: 500, kitchenla: 500, kitchenportland: 500, kitchenparis: 500, kitchenmunich: 500, kitchenrome: 500, kitchenamsterdam: 500, kitchenmexicocity: 500, kitchenrio: 500, kitchenhavana: 500, kitchengolf: 500, kitchenpittsburgh: 500 };
const BUX_MILESTONES = { 3: 25, 7: 75, 30: 200 };   // day-streak bonuses, on top of the daily cap
// Daily challenge: everyone gets the same one each day (midnight Pacific). Same list and order as DAILY in game.html.
const DAILY = [['streak', 10], ['boxes', 2], ['franks', 20], ['chili', 1], ['streak', 12], ['boxes', 3], ['franks', 25], ['streak', 15],
  ['boxes', 4], ['chili', 2], ['franks', 30], ['streak', 8], ['boxes', 3], ['franks', 35], ['streak', 18], ['chili', 1], ['boxes', 5],
  ['franks', 20], ['streak', 12], ['boxes', 2]];
const pacDay = ms => new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Los_Angeles', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date(ms));
const dayNum = d => Math.round(Date.UTC(+d.slice(0, 4), +d.slice(5, 7) - 1, +d.slice(8, 10)) / 864e5);
const dayBefore = d => new Date((dayNum(d) - 1) * 864e5).toISOString().slice(0, 10);
const dailyFor = d => { const c = DAILY[(dayNum(d) * 7) % DAILY.length]; return { stat: c[0], n: c[1] }; };
const ALLOWED_ORIGINS = new Set(['capacitor://localhost', 'https://localhost', 'http://localhost', 'ionic://localhost']);

const SCHEMA = [
  `CREATE TABLE IF NOT EXISTS players (id TEXT PRIMARY KEY, token_hash TEXT NOT NULL UNIQUE, nickname TEXT NOT NULL,
     best INTEGER NOT NULL DEFAULT 0, best_at INTEGER, last_score_at INTEGER NOT NULL DEFAULT 0, created_at INTEGER NOT NULL)`,
  `CREATE TABLE IF NOT EXISTS packs (id TEXT PRIMARY KEY, code TEXT NOT NULL UNIQUE, name TEXT NOT NULL, owner_id TEXT NOT NULL,
     default_board TEXT NOT NULL DEFAULT 'week', created_at INTEGER NOT NULL, approval INTEGER NOT NULL DEFAULT 1)`,
  `CREATE TABLE IF NOT EXISTS members (pack_id TEXT NOT NULL, player_id TEXT NOT NULL, joined_at INTEGER NOT NULL,
     PRIMARY KEY (pack_id, player_id))`,
  `CREATE INDEX IF NOT EXISTS members_player ON members (player_id)`,
  `CREATE TABLE IF NOT EXISTS weekly (player_id TEXT NOT NULL, week TEXT NOT NULL, best INTEGER NOT NULL, best_at INTEGER NOT NULL,
     PRIMARY KEY (player_id, week))`,
  `CREATE TABLE IF NOT EXISTS limits (k TEXT PRIMARY KEY, n INTEGER NOT NULL, day TEXT NOT NULL)`,
  `CREATE TABLE IF NOT EXISTS requests (pack_id TEXT NOT NULL, player_id TEXT NOT NULL, requested_at INTEGER NOT NULL,
     PRIMARY KEY (pack_id, player_id))`,
  `CREATE INDEX IF NOT EXISTS requests_player ON requests (player_id)`,
  `CREATE INDEX IF NOT EXISTS weekly_week ON weekly (week, best)`,   // last week's top dog
  `CREATE INDEX IF NOT EXISTS limits_day ON limits (day)`,            // clearing old counters
];
const MAX_WAITING_PER_PACK = 50, MAX_REQUESTS_PER_PLAYER = 5;
let schemaReady = false;
async function ensureSchema(db) {
  if (schemaReady) return;
  // Every new server copy starts here, and with many players there are many copies: one quick look first,
  // and the full setup below only when a table, column or index is missing.
  try {
    const r = await db.prepare(`SELECT (SELECT rc_id FROM players LIMIT 0) AS c, (SELECT bux_skins FROM players LIMIT 0) AS b,
        (SELECT COUNT(*) FROM sqlite_master WHERE type = 'index' AND name IN ('weekly_week', 'limits_day', 'requests_player', 'members_player')) AS ix`).first();
    if (r && r.ix === 4) { schemaReady = true; return; }
  } catch (e) {}
  await db.batch(SCHEMA.map(s => db.prepare(s)));
  // Packs made before "approve to join" existed get the column (it already exists everywhere after the first run)
  try { await db.prepare('ALTER TABLE packs ADD COLUMN approval INTEGER NOT NULL DEFAULT 1').run(); } catch (e) {}
  // Costumes won, kept with the profile so they come back with the recovery code (comma-separated skin ids)
  try { await db.prepare("ALTER TABLE players ADD COLUMN skins TEXT NOT NULL DEFAULT ''").run(); } catch (e) {}
  // The RevenueCat buyer id, stored so the recovery code can be changed without losing purchases.
  // Filled from the code the first time each player is seen (same value the apps and website already work out).
  try { await db.prepare("ALTER TABLE players ADD COLUMN rc_id TEXT NOT NULL DEFAULT ''").run(); } catch (e) {}
  // BunBux balance, today's BunBux (for the daily cap), the daily challenge streak, and costumes unlocked with BunBux
  for (const col of ["bux INTEGER NOT NULL DEFAULT 0", "bux_day TEXT NOT NULL DEFAULT ''", "bux_today INTEGER NOT NULL DEFAULT 0",
      "daily_last TEXT NOT NULL DEFAULT ''", "daily_streak INTEGER NOT NULL DEFAULT 0", "bux_skins TEXT NOT NULL DEFAULT ''"]) {
    try { await db.prepare('ALTER TABLE players ADD COLUMN ' + col).run(); } catch (e) {}
  }
  schemaReady = true;
}

// ---------- small helpers ----------
class ApiError extends Error { constructor(status, message) { super(message); this.status = status; } }
const fail = (status, message) => { throw new ApiError(status, message); };

function randCode(n) {
  const b = new Uint8Array(n); crypto.getRandomValues(b);
  let s = ''; for (let i = 0; i < n; i++) s += ALPHA[b[i] & 31];
  return s;
}
async function sha256(text) {
  const d = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
  return [...new Uint8Array(d)].map(x => x.toString(16).padStart(2, '0')).join('');
}
// Same formula as shopBuyerId() in game.html: 'fb_' + the first 20 bytes of SHA-256('franksandbuns-buyer:' + code)
async function buyerIdFor(tok) { return 'fb_' + (await sha256('franksandbuns-buyer:' + tok)).slice(0, 40); }
// One key per network: an IPv4 address, or an IPv6 /64 (one home or phone gets a whole /64, so single addresses are free to rotate)
function netOf(ip) {
  if (!ip.includes(':')) return ip;
  const [head, tail = ''] = ip.split('::'), h = head ? head.split(':') : [], t = tail ? tail.split(':') : [];
  const full = h.concat(Array(Math.max(0, 8 - h.length - t.length)).fill('0'), t);
  return full.slice(0, 4).map(x => (x || '0').toLowerCase()).join(':') + '::/64';
}
const cleanCode = raw => String(raw || '').toUpperCase().split('').filter(c => ALPHA.includes(c)).join('');
const fmtToken = t => t.match(/.{4}/g).join('-');
const today = () => new Date().toISOString().slice(0, 10);
function weekKey(ms) {   // weeks start Monday 00:00 UTC
  const d = new Date(ms), back = (d.getUTCDay() + 6) % 7;
  return new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate() - back)).toISOString().slice(0, 10);
}
function prevWeekKey(ms) { return weekKey(ms - 7 * 86400000); }

// ---------- name rules ----------
// Blocked anywhere in a name (after undoing l33t spellings): words that are never innocent inside other words.
const BLOCK_ANYWHERE = ['fuck', 'fuk', 'shit', 'cunt', 'nigger', 'nigga', 'faggot', 'bitch', 'whore', 'slut', 'rapist', 'raping',
  'porn', 'penis', 'vagina', 'pussy', 'twat', 'wank', 'dildo', 'retard', 'kike', 'wetback', 'tranny', 'nazi', 'hitler',
  'jizz', 'molest', 'hentai', 'horny', 'butthole', 'asshole', 'motherf', 'blowjob', 'handjob', 'boner', 'clit', 'orgasm',
  'masturb', 'semen', 'testicle', 'scrotum', 'bollock', 'bastard', 'douche', 'skank', 'killyourself', 'heilhitler', 'siegheil',
  'whitepower', 'gaschamber', 'kkk', 'isis', 'jihad', 'cocaine', 'heroin', 'meth'];
// Blocked only as a whole word (these hide inside harmless words, e.g. "peacock", "raccoon", "spicy").
const BLOCK_WORD = ['ass', 'arse', 'cock', 'dick', 'fag', 'fags', 'spic', 'chink', 'coon', 'dyke', 'cum', 'anal', 'anus', 'sex',
  'sexy', 'tit', 'tits', 'boob', 'boobs', 'nude', 'nudes', 'naked', 'rape', 'raped', 'pedo', 'kys', 'gook', 'homo', 'queer',
  'damn', 'crap', 'piss', 'hoe', 'hoes', 'thot', 'weed', 'nsfw', 'xxx', 'milf', 'gay', 'lesbo', 'negro', 'jap', 'paki'];
const LEET = { '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's', '7': 't', '8': 'b', '9': 'g', '@': 'a', '$': 's', '!': 'i', '|': 'i', '+': 't' };
const unleet = s => s.toLowerCase().normalize('NFKD').replace(/\p{M}/gu, '').split('').map(c => LEET[c] || c).join('');
function isRude(name) {
  const flat = unleet(name).replace(/[^a-z]/g, '');
  const flatOnce = flat.replace(/(.)\1+/g, '$1');                // "fuuuck" -> "fuck"
  if (BLOCK_ANYWHERE.some(w => flat.includes(w) || (!/(.)\1/.test(w) && flatOnce.includes(w)))) return true;
  const words = unleet(name).split(/[^a-z]+/).filter(Boolean);
  return words.some(w => BLOCK_WORD.includes(w) || BLOCK_WORD.includes(w.replace(/(.)\1+/g, '$1')));
}
// Emoji rude enough to block in names (checked after removing skin tones and variation marks)
const BLOCK_EMOJI = ['🖕', '🍆', '🍑', '💦', '🔞', '👅', '🩲', '🫦', '👙', '🍒', '🌮', '🥒', '🔫', '💉', '💊', '🚬', '🍺', '🍻', '🍷', '🥃', '🍸', '🍾', '🌿', '🍁', '🤬', '💀', '☠', '⚰', '🪦', '卐', '卍'];
const EMOJI_PART = /[\p{Extended_Pictographic}\p{Emoji_Modifier}\p{Regional_Indicator}\u200d\ufe0f\u20e3]/u;
// Length in characters as people see them: a family emoji or a flag counts as one
function seen(s) { try { return [...new Intl.Segmenter('en', { granularity: 'grapheme' }).segment(s)].length; } catch (e) { return [...s].length; } }
function cleanName(raw, min, max, what, emoji) {
  if (typeof raw !== 'string') fail(400, `Please enter a ${what}.`);
  // keep the zero-width joiner (it glues emoji like 👨‍👩‍👧 together) only when emoji are allowed
  const hidden = emoji ? /[\u0000-\u001f\u007f-\u009f\u200b\u200c\u200e\u200f\u2028-\u202e\u2060-\u206f\ufeff]/g : /[\u0000-\u001f\u007f-\u009f\u200b-\u200f\u2028-\u202e\u2060-\u206f\ufeff]/g;
  const s = raw.normalize('NFKC').replace(hidden, '').replace(/\s+/g, ' ').trim();
  const len = seen(s);
  if (len < min) fail(400, `Your ${what} needs at least ${min} characters.`);
  if (len > max) fail(400, `Your ${what} can be up to ${max} characters.`);
  const ok = emoji ? /^(?:[\p{L}\p{N}\p{M} _.'!&-]|[\p{Extended_Pictographic}\p{Emoji_Modifier}\p{Regional_Indicator}\u200d\ufe0f\u20e3])+$/u
                   : /^[\p{L}\p{N}\p{M} _.'!&-]+$/u;
  if (!ok.test(s)) fail(400, `Use letters, numbers, ${emoji ? 'emoji, ' : ''}spaces and . _ - ' ! & in your ${what}.`);
  if (emoji && !/[\p{L}\p{N}]/u.test(s) && !EMOJI_PART.test(s)) fail(400, `Please pick a different ${what}.`);
  const bare = s.replace(/[\p{Emoji_Modifier}\ufe0f]/gu, '');
  if (isRude(s) || (emoji && BLOCK_EMOJI.some(e => bare.includes(e.replace(/\ufe0f/g, ''))))) fail(400, `Please pick a different ${what}.`);
  return s;
}

// ---------- limits ----------
// One statement, so many requests at once can't slip past a limit (D1 runs each statement on its own)
async function underLimit(db, key, max) {
  const r = await db.prepare(`INSERT INTO limits (k, n, day) VALUES (?, 1, ?)
      ON CONFLICT (k) DO UPDATE SET n = CASE WHEN day = excluded.day THEN n + 1 ELSE 1 END, day = excluded.day RETURNING n`)
    .bind(key, today()).first();
  return !r || r.n <= max;
}
async function overLimit(db, key, max) {   // look without counting
  const r = await db.prepare('SELECT n FROM limits WHERE k = ? AND day = ?').bind(key, today()).first();
  return !!(r && r.n >= max);
}

// ---------- players ----------
async function authPlayer(db, request) {
  const m = (request.headers.get('Authorization') || '').match(/^Bearer\s+([A-Za-z0-9-]{16,40})$/);
  if (!m) return null;
  const tok = cleanCode(m[1]);
  if (tok.length !== 16) return null;
  const p = await db.prepare('SELECT * FROM players WHERE token_hash = ?').bind(await sha256(tok)).first();
  if (p) await ensureBuyerId(db, p, tok);
  return p;
}
async function ensureBuyerId(db, p, tok) {
  if (p.rc_id) return;
  p.rc_id = await buyerIdFor(tok);
  await db.prepare("UPDATE players SET rc_id = ? WHERE id = ? AND rc_id = ''").bind(p.rc_id, p.id).run();
}
async function needPlayer(db, request) {
  const p = await authPlayer(db, request);
  if (!p) fail(401, 'Your Dog House sign-in was not found on this device. Use your recovery code to restore it.');
  return p;
}
const skinList = p => String(p.skins || '').split(',').filter(Boolean);
// What the game shows: BunBux balance, costumes unlocked with BunBux, and the daily challenge streak
const buxOf = p => ({ bux: p.bux || 0, skins: String(p.bux_skins || '').split(',').filter(Boolean), dailyLast: p.daily_last || '', streak: p.daily_streak || 0 });
// A profile the game made silently has no name yet; it needs one before it can make or join a Pack
async function needName(db, p, body, ip) {
  if (p.nickname) return;
  if (!body.nickname) fail(400, 'Pick your name on Wienerboards first.');
  const nick = cleanName(body.nickname, 2, 16, 'name', true);
  if (!(await underLimit(db, 'np:' + (await sha256(netOf(ip) + today())), NEW_PLAYERS_PER_IP_PER_DAY))) fail(429, 'Too many new players from here today. Try again tomorrow.');
  p.nickname = nick;
  await db.prepare('UPDATE players SET nickname = ? WHERE id = ?').bind(p.nickname, p.id).run();
}
async function meResponse(db, p, extra) {
  const [packs, requests] = await db.batch([   // one trip to the database
    db.prepare(`SELECT p.id, p.code, p.name, p.default_board, p.owner_id,
            (SELECT COUNT(*) FROM members m2 WHERE m2.pack_id = p.id) AS members,
            CASE WHEN p.owner_id = m.player_id THEN (SELECT COUNT(*) FROM requests r WHERE r.pack_id = p.id) ELSE 0 END AS waiting
       FROM members m JOIN packs p ON p.id = m.pack_id WHERE m.player_id = ? ORDER BY m.joined_at`).bind(p.id),
    db.prepare('SELECT p.id, p.name FROM requests r JOIN packs p ON p.id = r.pack_id WHERE r.player_id = ? ORDER BY r.requested_at').bind(p.id),
  ]);
  return Object.assign({ player: { id: p.id, nickname: p.nickname, best: p.best, skins: skinList(p), buyerId: p.rc_id || '', bux: buxOf(p) },
    packs: packs.results.map(r => ({ id: r.id, code: r.code, name: r.name, defaultBoard: r.default_board,
      members: r.members, isOwner: r.owner_id === p.id, waiting: r.waiting })),
    requests: requests.results.map(r => ({ id: r.id, name: r.name })) }, extra || {});
}

// ---------- packs ----------
async function packForMember(db, packId, playerId) {
  const pack = await db.prepare('SELECT p.*, EXISTS (SELECT 1 FROM members m WHERE m.pack_id = p.id AND m.player_id = ?) AS is_member FROM packs p WHERE p.id = ?')
    .bind(playerId, packId).first();
  if (!pack) fail(404, 'That Dog House no longer exists.');
  if (!pack.is_member) fail(403, 'You are not in that Dog House.');
  delete pack.is_member;
  return pack;
}
// Adds a member only if the Dog House has room and the player is in fewer than the most Dog Houses, in one statement
// (so two requests at once can't both squeeze past the limits). Returns true if they were added (or already in).
async function addMember(db, packId, playerId, now) {
  const r = await db.prepare(`INSERT OR IGNORE INTO members (pack_id, player_id, joined_at)
      SELECT ?, ?, ? WHERE (SELECT COUNT(*) FROM members WHERE pack_id = ?) < ${MAX_MEMBERS}
                       AND (SELECT COUNT(*) FROM members WHERE player_id = ?) < ${MAX_PACKS_PER_PLAYER}`)
    .bind(packId, playerId, now, packId, playerId).run();
  if (((r && r.meta) ? r.meta.changes : (r && r.changes)) > 0) return true;
  return !!(await db.prepare('SELECT 1 FROM members WHERE pack_id = ? AND player_id = ?').bind(packId, playerId).first());
}
async function packCount(db, playerId) {
  const r = await db.prepare('SELECT COUNT(*) AS n FROM members WHERE player_id = ?').bind(playerId).first();
  return r ? r.n : 0;
}
async function leavePack(db, pack, playerId) {
  await db.prepare('DELETE FROM members WHERE pack_id = ? AND player_id = ?').bind(pack.id, playerId).run();
  if (pack.owner_id !== playerId) return;
  const next = await db.prepare('SELECT player_id FROM members WHERE pack_id = ? ORDER BY joined_at LIMIT 1').bind(pack.id).first();
  if (next) await db.prepare('UPDATE packs SET owner_id = ? WHERE id = ?').bind(next.player_id, pack.id).run();
  else await db.batch([   // last one out: the Pack and its join requests are gone
    db.prepare('DELETE FROM requests WHERE pack_id = ?').bind(pack.id),
    db.prepare('DELETE FROM packs WHERE id = ?').bind(pack.id),
  ]);
}
async function board(db, pack, playerId, which, now) {
  const week = weekKey(now);
  const sql = which === 'all'
    ? `SELECT pl.id, pl.nickname, pl.best AS score FROM members m JOIN players pl ON pl.id = m.player_id
        WHERE m.pack_id = ? ORDER BY pl.best DESC, m.joined_at LIMIT ${MAX_MEMBERS}`
    : `SELECT pl.id, pl.nickname, COALESCE(w.best, 0) AS score FROM members m JOIN players pl ON pl.id = m.player_id
         LEFT JOIN weekly w ON w.player_id = m.player_id AND w.week = ?
        WHERE m.pack_id = ? ORDER BY score DESC, m.joined_at LIMIT ${MAX_MEMBERS}`;
  const isOwner = pack.owner_id === playerId;
  const stmts = [which === 'all' ? db.prepare(sql).bind(pack.id) : db.prepare(sql).bind(week, pack.id)];
  if (isOwner) stmts.push(db.prepare(`SELECT pl.id, pl.nickname FROM requests r JOIN players pl ON pl.id = r.player_id
        WHERE r.pack_id = ? ORDER BY r.requested_at LIMIT ${MAX_WAITING_PER_PACK}`).bind(pack.id));
  if (which !== 'all') stmts.push(db.prepare(`SELECT pl.nickname, w.best FROM weekly w JOIN members m ON m.player_id = w.player_id AND m.pack_id = ?
         JOIN players pl ON pl.id = w.player_id WHERE w.week = ? ORDER BY w.best DESC, w.best_at LIMIT 1`).bind(pack.id, prevWeekKey(now)));
  const res = await db.batch(stmts), results = res[0].results;   // one trip to the database
  const rows = results.map(r => ({ id: r.id, name: r.nickname, score: r.score, you: r.id === playerId, owner: r.id === pack.owner_id }));
  const out = { pack: { id: pack.id, code: pack.code, name: pack.name, defaultBoard: pack.default_board,
    isOwner: pack.owner_id === playerId, members: rows.length, approval: !!pack.approval }, board: which, rows };
  if (isOwner) out.requests = res[1].results.map(r => ({ id: r.id, name: r.nickname }));
  if (which !== 'all') {
    out.resetsAt = new Date(week + 'T00:00:00Z').getTime() + 7 * 86400000;
    const last = res[res.length - 1].results[0];
    if (last && last.best > 0) out.lastWeekTop = { name: last.nickname, score: last.best };
  }
  return out;
}

async function newPackCode(db) {
  for (let i = 0; i < 6; i++) {
    const c = randCode(6);
    if (!(await db.prepare('SELECT 1 FROM packs WHERE code = ?').bind(c).first())) return c;
  }
  fail(503, 'Could not make a Dog House code. Please try again.');
}

// ---------- scores ----------
// A basic sanity check, not a guarantee: the game runs on the player's device, so a determined cheat can still fake a run.
function plausible(b) {
  const score = b.score, frames = b.frames, franks = b.franks, boxes = b.boxes;
  if (![score, frames, franks, boxes].every(v => Number.isInteger(v) && v >= 0)) return false;
  if (score < 1 || score > 50000000 || frames < 60) return false;
  const secs = frames / 60;
  if (franks > secs * 2 + 3) return false;
  if (boxes > Math.floor(franks / 6)) return false;
  const parades = Math.floor(boxes / 4);
  const max = franks * 13100 + 50 * boxes * (boxes + 1) + parades * 40 * 500 + secs * 1500 + 5000;
  return score <= max;
}

// ---------- router ----------
async function route(request, env, path) {
  const db = env.DB;
  if (!db) fail(503, 'Dog Houses are not switched on yet.');
  await ensureSchema(db);
  const method = request.method, now = Date.now();
  if (method === 'POST' && Number(request.headers.get('Content-Length') || 0) > 16384) fail(413, 'That request is too big.');
  let body = method === 'POST' ? await request.json().catch(() => ({})) : {};
  if (!body || typeof body !== 'object' || Array.isArray(body)) body = {};
  const ip = request.headers.get('CF-Connecting-IP') || 'local';

  if (method === 'POST' && path === 'player') {
    // silent: the game makes a nameless profile in the background to keep a player's costumes
    const silent = body.silent === true;
    const nickname = silent ? '' : cleanName(body.nickname, 2, 16, 'name', true);
    if (!(await underLimit(db, (silent ? 'ns:' : 'np:') + (await sha256(netOf(ip) + today())), silent ? NEW_SILENT_PLAYERS_PER_IP_PER_DAY : NEW_PLAYERS_PER_IP_PER_DAY))) fail(429, 'Too many new players from here today. Try again tomorrow.');
    if (Math.random() < 0.02) await db.prepare('DELETE FROM limits WHERE day < ?').bind(today()).run();   // yesterday's counters
    const id = randCode(12), token = randCode(16);
    await db.prepare('INSERT INTO players (id, token_hash, nickname, created_at, rc_id) VALUES (?, ?, ?, ?, ?)')
      .bind(id, await sha256(token), nickname, now, await buyerIdFor(token)).run();
    const p = await db.prepare('SELECT * FROM players WHERE id = ?').bind(id).first();
    return meResponse(db, p, { token: fmtToken(token) });
  }
  if (method === 'POST' && path === 'recover') {
    const tok = cleanCode(body.code);
    if (tok.length !== 16) fail(400, 'Recovery codes have 16 letters and numbers.');
    if (!(await underLimit(db, 'rc:' + (await sha256(netOf(ip) + today())), RECOVER_TRIES_PER_IP_PER_DAY))) fail(429, 'Too many recovery code tries from here today. Try again tomorrow.');
    const p = await db.prepare('SELECT * FROM players WHERE token_hash = ?').bind(await sha256(tok)).first();
    if (!p) fail(404, 'That recovery code was not found. Check it and try again.');
    await ensureBuyerId(db, p, tok);
    return meResponse(db, p, { token: fmtToken(tok) });
  }
  if (method === 'GET' && path === 'me') return meResponse(db, await needPlayer(db, request));
  if (method === 'POST' && path === 'me/skins') {   // adds costumes won on this device (never removes any)
    const p = await needPlayer(db, request);
    const have = skinList(p), seenIds = new Set(have), all = have.slice();
    for (const k of (Array.isArray(body.skins) ? body.skins : []).slice(0, MAX_SKINS)) {
      if (all.length >= MAX_SKINS) break;
      if (typeof k === 'string' && /^[a-z]{2,24}$/.test(k) && !seenIds.has(k)) { seenIds.add(k); all.push(k); }
    }
    if (all.length !== have.length) { p.skins = all.join(','); await db.prepare('UPDATE players SET skins = ? WHERE id = ?').bind(p.skins, p.id).run(); }
    return meResponse(db, p);
  }
  if (method === 'POST' && path === 'me/bux') {
    // Finished games: 1 BunBux per box packed (up to 10 a game), 25 for today's challenge (once a day), day-streak bonuses.
    // To keep database writes down, the game saves several games in one go: `games` is how many, and the totals are added up.
    // `best` is the single game that met today's challenge (the challenge is "in one game"), sent when there is one.
    // The game runs on the player's device, so the daily cap is what keeps a faked game from earning more than a real day's play.
    const p = await needPlayer(db, request);
    const games = body.games === undefined ? 1 : body.games;
    const run = { score: body.score, frames: body.frames, franks: body.franks, boxes: body.boxes };
    const st = { streak: body.streak, chili: body.chili, franks: body.franks, boxes: body.boxes };
    if (!Number.isInteger(games) || games < 1 || games > 200 || !plausible(run) ||
        ![st.streak, st.chili].every(v => Number.isInteger(v) && v >= 0) || st.streak > st.franks ||
        st.chili > Math.floor(run.frames / 60 / 25) + games) fail(422, 'That game could not be checked.');
    let best = games === 1 ? st : null;
    if (body.best && typeof body.best === 'object') {
      const b = { streak: body.best.streak, chili: body.best.chili, franks: body.best.franks, boxes: body.best.boxes };
      if (!['streak', 'chili', 'franks', 'boxes'].every(k => Number.isInteger(b[k]) && b[k] >= 0 && b[k] <= st[k]) ||
          b.streak > b.franks || b.boxes > Math.floor(b.franks / 6)) fail(422, 'That game could not be checked.');
      best = b;
    }
    // BUX_TEST=1 (only ever set on a test copy of the site) lets the game say which day it is, to try streaks without waiting
    const day = env.BUX_TEST === '1' && /^\d{4}-\d{2}-\d{2}$/.test(String(body.testDay || '')) ? body.testDay : pacDay(now);
    const ch = dailyFor(day);
    let done = false, bonus = 0;
    if (best && (best[ch.stat] || 0) >= ch.n && p.daily_last !== day) {   // one statement, so two saves at once can't both claim it
      const r = await db.prepare(`UPDATE players SET daily_streak = CASE WHEN daily_last = ? THEN daily_streak + 1 ELSE 1 END, daily_last = ?
          WHERE id = ? AND daily_last <> ? RETURNING daily_streak`).bind(dayBefore(day), day, p.id, day).first();
      if (r) { done = true; bonus = BUX_MILESTONES[r.daily_streak] || 0; }
    }
    const capLeft = BUX.cap - (p.bux_day === day ? p.bux_today || 0 : 0);
    const want = Math.min(run.boxes, BUX.maxBoxes * games) * BUX.perBox + (done ? BUX.daily : 0);
    if (!done && (want <= 0 || capLeft <= 0)) {   // nothing to add: no write
      const p2 = await db.prepare('SELECT * FROM players WHERE id = ?').bind(p.id).first();
      return { bux: buxOf(p2), day, earned: 0, bonus: 0, dailyDone: false, capped: capLeft <= 0 };
    }
    const earn = `MAX(0, MIN(?, ${BUX.cap} - CASE WHEN bux_day = ? THEN bux_today ELSE 0 END))`;
    const r = await db.prepare(`UPDATE players SET bux = bux + ${earn} + ?, bux_today = CASE WHEN bux_day = ? THEN bux_today ELSE 0 END + ${earn},
        bux_day = ? WHERE id = ? RETURNING bux, bux_today, bux_skins, daily_last, daily_streak`)
      .bind(want, day, bonus, day, want, day, day, p.id).first();
    const earned = Math.max(0, r.bux - (p.bux || 0));
    return { bux: buxOf(r), day, earned, bonus, dailyDone: done, capped: r.bux_today >= BUX.cap };
  }
  if (method === 'POST' && path === 'me/bux/spend') {   // unlock one shop costume (or a kitchen) for BunBux
    const p = await needPlayer(db, request);
    const id = String(body.skin || '');
    if (!/^[a-z]{2,24}$/.test(id)) fail(400, 'That costume was not found.');
    const kitchen = Object.prototype.hasOwnProperty.call(BUX_KITCHENS, id), cost = kitchen ? BUX_KITCHENS[id] : BUX.cost, what = kitchen ? 'kitchen' : 'costume';
    if (BUX_LIMITED.has(id)) fail(400, 'Limited Edition costumes can only be bought, not unlocked with BunBux.');
    if (!kitchen && !BUX_SKINS.has(id)) fail(400, 'That costume can’t be unlocked with BunBux.');
    const r = await db.prepare(`UPDATE players SET bux = bux - ${cost}, bux_skins = CASE WHEN bux_skins = '' THEN ? ELSE bux_skins || ',' || ? END
        WHERE id = ? AND bux >= ${cost} AND instr(',' || bux_skins || ',', ?) = 0 AND length(bux_skins) < 8000
        RETURNING bux, bux_skins, daily_last, daily_streak`).bind(id, id, p.id, ',' + id + ',').first();
    if (r) return { bux: buxOf(r), unlocked: id };
    const now2 = await db.prepare('SELECT * FROM players WHERE id = ?').bind(p.id).first();
    if (buxOf(now2).skins.indexOf(id) >= 0) return { bux: buxOf(now2), unlocked: id };
    fail(409, `This ${what} needs ${cost} BunBux. You have ${now2.bux || 0}.`);
  }
  if (method === 'POST' && path === 'me/newcode') {   // "Get a new recovery code": the old one stops working everywhere
    const p = await needPlayer(db, request);
    if (!(await underLimit(db, 'rk:' + p.id, NEW_CODES_PER_PLAYER_PER_DAY))) fail(429, 'That is a lot of new codes for one day. Try again tomorrow.');
    const token = randCode(16);
    await db.prepare('UPDATE players SET token_hash = ? WHERE id = ?').bind(await sha256(token), p.id).run();
    return meResponse(db, p, { token: fmtToken(token) });
  }
  if (method === 'POST' && path === 'me/name') {
    const p = await needPlayer(db, request);
    const nickname = cleanName(body.nickname, 2, 16, 'name', true);
    if (!p.nickname && !(await underLimit(db, 'np:' + (await sha256(netOf(ip) + today())), NEW_PLAYERS_PER_IP_PER_DAY))) fail(429, 'Too many new players from here today. Try again tomorrow.');
    await db.prepare('UPDATE players SET nickname = ? WHERE id = ?').bind(nickname, p.id).run();
    p.nickname = nickname;
    return meResponse(db, p);
  }
  if (method === 'POST' && path === 'me/delete') {   // deletes the profile, its scores and memberships (Pack leadership passes on)
    const p = await needPlayer(db, request);
    const { results } = await db.prepare('SELECT p.* FROM members m JOIN packs p ON p.id = m.pack_id WHERE m.player_id = ?').bind(p.id).all();
    for (const pack of results) await leavePack(db, pack, p.id);
    await db.batch([
      db.prepare('DELETE FROM weekly WHERE player_id = ?').bind(p.id),
      db.prepare('DELETE FROM requests WHERE player_id = ?').bind(p.id),
      db.prepare('DELETE FROM limits WHERE k = ?').bind('nk:' + p.id),
      db.prepare('DELETE FROM players WHERE id = ?').bind(p.id),
    ]);
    // RevenueCat keeps a customer record per buyer id. Remove it too (Cloudflare Pages secret RC_SECRET_KEY, a RevenueCat
    // secret API key). Apple / Google purchases stay on the player's store account and come back with Restore Purchases.
    if (env.RC_SECRET_KEY && p.rc_id) {
      try {
        const r = await fetch('https://api.revenuecat.com/v1/subscribers/' + encodeURIComponent(p.rc_id),
          { method: 'DELETE', headers: { Authorization: 'Bearer ' + env.RC_SECRET_KEY } });
        if (!r.ok && r.status !== 404) console.error('revenuecat delete', r.status);
      } catch (e) { console.error('revenuecat delete', e && e.message); }
    }
    return { deleted: true };
  }
  if (method === 'POST' && path === 'packs') {
    const p = await needPlayer(db, request);
    await needName(db, p, body, ip);
    const name = cleanName(body.name, 3, 24, 'Dog House name');
    const defaultBoard = body.defaultBoard === 'all' ? 'all' : 'week';
    const approval = body.approval === false ? 0 : 1;
    if ((await packCount(db, p.id)) >= MAX_PACKS_PER_PLAYER) fail(409, `You can be in up to ${MAX_PACKS_PER_PLAYER} Dog Houses. Quit one to make a new one.`);
    if (!(await underLimit(db, 'nk:' + p.id, NEW_PACKS_PER_PLAYER_PER_DAY))) fail(429, 'That is a lot of new Dog Houses for one day. Try again tomorrow.');
    const id = randCode(12), code = await newPackCode(db);
    await db.prepare('INSERT INTO packs (id, code, name, owner_id, default_board, created_at, approval) VALUES (?, ?, ?, ?, ?, ?, ?)').bind(id, code, name, p.id, defaultBoard, now, approval).run();
    if (!(await addMember(db, id, p.id, now))) {
      await db.prepare('DELETE FROM packs WHERE id = ?').bind(id).run();
      fail(409, `You can be in up to ${MAX_PACKS_PER_PLAYER} Dog Houses. Quit one to make a new one.`);
    }
    const pack = await db.prepare('SELECT * FROM packs WHERE id = ?').bind(id).first();
    return board(db, pack, p.id, defaultBoard, now);
  }
  if (method === 'POST' && path === 'packs/join') {
    const p = await needPlayer(db, request);
    await needName(db, p, body, ip);
    const code = cleanCode(body.code);
    if (code.length !== 6) fail(400, 'Dog House codes have 6 letters and numbers.');
    const wrongKeys = ['jw:' + p.id, 'jw:' + (await sha256(netOf(ip) + today()))];
    if ((await overLimit(db, wrongKeys[0], WRONG_JOIN_CODES_PER_DAY)) || (await overLimit(db, wrongKeys[1], WRONG_JOIN_CODES_PER_DAY))) fail(429, 'Too many wrong Dog House codes today. Check the code with whoever invited you and try again tomorrow.');
    const pack = await db.prepare('SELECT * FROM packs WHERE code = ?').bind(code).first();
    if (!pack) { for (const k of wrongKeys) await underLimit(db, k, WRONG_JOIN_CODES_PER_DAY + 1); fail(404, 'No Dog House has that code. Check it and try again.'); }
    const already = await db.prepare('SELECT 1 FROM members WHERE pack_id = ? AND player_id = ?').bind(pack.id, p.id).first();
    if (!already) {
      if ((await packCount(db, p.id)) >= MAX_PACKS_PER_PLAYER) fail(409, `You can be in up to ${MAX_PACKS_PER_PLAYER} Dog Houses. Quit one to join this one.`);
      const n = await db.prepare('SELECT COUNT(*) AS n FROM members WHERE pack_id = ?').bind(pack.id).first();
      if (n && n.n >= MAX_MEMBERS) fail(409, `That Dog House is full (${MAX_MEMBERS} players).`);
      if (pack.approval) {   // the leader lets each new player in
        const asked = await db.prepare('SELECT 1 FROM requests WHERE pack_id = ? AND player_id = ?').bind(pack.id, p.id).first();
        if (!asked) {
          const mine = await db.prepare('SELECT COUNT(*) AS n FROM requests WHERE player_id = ?').bind(p.id).first();
          if (mine && mine.n >= MAX_REQUESTS_PER_PLAYER) fail(409, `You're already waiting on ${MAX_REQUESTS_PER_PLAYER} Dog Houses. Cancel one to ask to join another.`);
          const waiting = await db.prepare('SELECT COUNT(*) AS n FROM requests WHERE pack_id = ?').bind(pack.id).first();
          if (waiting && waiting.n >= MAX_WAITING_PER_PACK) fail(409, 'That Dog House has too many players waiting. Try again later.');
          await db.prepare('INSERT OR IGNORE INTO requests (pack_id, player_id, requested_at) VALUES (?, ?, ?)').bind(pack.id, p.id, now).run();
        }
        return meResponse(db, p, { pending: { id: pack.id, name: pack.name } });
      }
      if (!(await addMember(db, pack.id, p.id, now))) fail(409, `That Dog House is full, or you're already in ${MAX_PACKS_PER_PLAYER} Dog Houses.`);
    }
    return board(db, pack, p.id, pack.default_board, now);
  }
  let m = path.match(/^packs\/([A-Z0-9]{12})\/cancel$/);
  if (m && method === 'POST') {   // take back your own request to join
    const p = await needPlayer(db, request);
    await db.prepare('DELETE FROM requests WHERE pack_id = ? AND player_id = ?').bind(m[1], p.id).run();
    return meResponse(db, p);
  }
  m = path.match(/^packs\/([A-Z0-9]{12})(?:\/(leave|remove|settings|approve|decline|newcode))?$/);
  if (m) {
    const p = await needPlayer(db, request);
    const pack = await packForMember(db, m[1], p.id);
    const action = m[2];
    if (method === 'GET' && !action) {
      const which = new URL(request.url).searchParams.get('board') === 'all' ? 'all' : 'week';
      return board(db, pack, p.id, which, now);
    }
    if (method === 'POST' && action === 'leave') { await leavePack(db, pack, p.id); return meResponse(db, p); }
    if (method === 'POST' && action) {
      if (pack.owner_id !== p.id) fail(403, 'Only the Dog House leader can do that.');
      const who = String(body.playerId || '');
      if (action === 'remove') {
        if (who === p.id) fail(400, 'Use Quit this Dog House to leave your own Dog House.');
        await db.prepare('DELETE FROM members WHERE pack_id = ? AND player_id = ?').bind(pack.id, who).run();
      } else if (action === 'approve') {
        const asked = await db.prepare('SELECT 1 FROM requests WHERE pack_id = ? AND player_id = ?').bind(pack.id, who).first();
        if (!asked) fail(404, 'That request is gone. The player may have cancelled it.');
        const n = await db.prepare('SELECT COUNT(*) AS n FROM members WHERE pack_id = ?').bind(pack.id).first();
        if (n && n.n >= MAX_MEMBERS) fail(409, `Your Dog House is full (${MAX_MEMBERS} players).`);
        if ((await packCount(db, who)) >= MAX_PACKS_PER_PLAYER) {
          await db.prepare('DELETE FROM requests WHERE pack_id = ? AND player_id = ?').bind(pack.id, who).run();
          fail(409, `That player is already in ${MAX_PACKS_PER_PLAYER} Dog Houses, so they can't join. Their request was removed.`);
        }
        if (!(await addMember(db, pack.id, who, now))) fail(409, `Your Dog House is full (${MAX_MEMBERS} players), or that player is already in ${MAX_PACKS_PER_PLAYER} Dog Houses.`);
        await db.prepare('DELETE FROM requests WHERE pack_id = ? AND player_id = ?').bind(pack.id, who).run();
      } else if (action === 'decline') {
        await db.prepare('DELETE FROM requests WHERE pack_id = ? AND player_id = ?').bind(pack.id, who).run();
      } else if (action === 'newcode') {   // the old code stops working right away
        pack.code = await newPackCode(db);
        await db.prepare('UPDATE packs SET code = ? WHERE id = ?').bind(pack.code, pack.id).run();
      } else {
        const defaultBoard = body.defaultBoard === 'all' ? 'all' : body.defaultBoard === 'week' ? 'week' : pack.default_board;
        const approval = body.approval === undefined ? pack.approval : (body.approval ? 1 : 0);
        const name = body.name === undefined ? pack.name : cleanName(body.name, 3, 24, 'Dog House name');
        await db.prepare('UPDATE packs SET default_board = ?, name = ?, approval = ? WHERE id = ?').bind(defaultBoard, name, approval, pack.id).run();
        pack.default_board = defaultBoard; pack.name = name; pack.approval = approval;
      }
      return board(db, pack, p.id, body.board === 'all' ? 'all' : 'week', now);
    }
  }
  if (method === 'POST' && path === 'score') {
    const p = await needPlayer(db, request);
    // nameless profiles only keep costumes: their scores are never stored (the privacy policy promises this)
    if (!p.nickname) return { ok: true, score: Number(body.score) || 0, weekBest: 0, newWeekBest: false, packs: [] };
    const run = { score: body.score, frames: body.frames, franks: body.franks, boxes: body.boxes };
    if (!plausible(run)) fail(422, 'That score could not be checked.');
    const secs = run.frames / 60;
    if (p.last_score_at && now - p.last_score_at < Math.max(3000, secs * 700)) fail(429, 'Scores are coming in too fast.');
    const week = weekKey(now);
    // Save it and work out where it leaves you in each Dog House this week (Game Over screen), in one trip
    const res = await db.batch([
      db.prepare('UPDATE players SET last_score_at = ?, best = MAX(best, ?), best_at = CASE WHEN ? > best THEN ? ELSE best_at END WHERE id = ?')
        .bind(now, run.score, run.score, now, p.id),
      db.prepare(`INSERT INTO weekly (player_id, week, best, best_at) VALUES (?, ?, ?, ?)
                  ON CONFLICT (player_id, week) DO UPDATE SET best = MAX(best, excluded.best),
                  best_at = CASE WHEN excluded.best > best THEN excluded.best_at ELSE best_at END`).bind(p.id, week, run.score, now),
      db.prepare('SELECT best FROM weekly WHERE player_id = ? AND week = ?').bind(p.id, week),
      db.prepare(`SELECT p.id, p.name,
              (SELECT COUNT(*) FROM members m2 WHERE m2.pack_id = p.id) AS players,
              (SELECT COUNT(*) FROM members m3 JOIN weekly w ON w.player_id = m3.player_id AND w.week = ?
                 WHERE m3.pack_id = p.id AND w.best > (SELECT best FROM weekly WHERE player_id = ? AND week = ?)) AS ahead
         FROM members m JOIN packs p ON p.id = m.pack_id WHERE m.player_id = ? ORDER BY m.joined_at`).bind(week, p.id, week, p.id),
    ]);
    const me = res[2].results[0], weekBest = me ? me.best : run.score, results = res[3].results;
    return { ok: true, score: run.score, weekBest, newWeekBest: run.score >= weekBest,
      packs: results.map(r => ({ id: r.id, name: r.name, rank: r.ahead + 1, players: r.players })) };
  }
  fail(404, 'Not found.');
}

function corsHeaders(request) {
  const o = request.headers.get('Origin');
  const h = { 'Vary': 'Origin' };
  if (o && ALLOWED_ORIGINS.has(o)) Object.assign(h, {
    'Access-Control-Allow-Origin': o, 'Access-Control-Allow-Headers': 'Authorization, Content-Type',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS', 'Access-Control-Max-Age': '86400' });
  return h;
}

export async function onRequest(context) {
  const { request, env, params } = context;
  const cors = corsHeaders(request);
  if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });
  const path = [].concat(params.path || []).join('/');
  const headers = Object.assign({ 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' }, cors);
  // Server-Timing: how long this request spent waiting on the database and in total (durations only; for load checks)
  const t0 = Date.now(); let dbMs = 0, trips = 0;
  const timed = f => async (...a) => { const s = Date.now(); trips++; try { return await f(...a); } finally { dbMs += Date.now() - s; } };
  const wrapStmt = st => ({ bind: (...a) => wrapStmt(st.bind(...a)), first: timed((...a) => st.first(...a)), all: timed(() => st.all()), run: timed(() => st.run()), raw: st });
  const db = env.DB && { prepare: sql => wrapStmt(env.DB.prepare(sql)), batch: timed(list => env.DB.batch(list.map(x => x.raw || x))) };
  const timing = () => ({ 'Server-Timing': `db;dur=${dbMs};desc="${trips} trips", total;dur=${Date.now() - t0}` });
  try {
    const data = await route(request, Object.assign({}, env, { DB: db }), path);
    return new Response(JSON.stringify(data), { status: 200, headers: Object.assign(timing(), headers) });
  } catch (e) {
    const status = e instanceof ApiError ? e.status : 500;
    const message = e instanceof ApiError ? e.message : 'Something went wrong. Please try again.';
    if (!(e instanceof ApiError)) console.error('packs api', e && e.stack || e);
    return new Response(JSON.stringify({ error: message }), { status, headers: Object.assign(timing(), headers) });
  }
}
