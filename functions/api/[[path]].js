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
];
const MAX_WAITING_PER_PACK = 50, MAX_REQUESTS_PER_PLAYER = 5;
let schemaReady = false;
async function ensureSchema(db) {
  if (schemaReady) return;
  await db.batch(SCHEMA.map(s => db.prepare(s)));
  // Packs made before "approve to join" existed get the column (it already exists everywhere after the first run)
  try { await db.prepare('ALTER TABLE packs ADD COLUMN approval INTEGER NOT NULL DEFAULT 1').run(); } catch (e) {}
  // Costumes won, kept with the profile so they come back with the recovery code (comma-separated skin ids)
  try { await db.prepare("ALTER TABLE players ADD COLUMN skins TEXT NOT NULL DEFAULT ''").run(); } catch (e) {}
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
async function underLimit(db, key, max) {
  const day = today();
  const row = await db.prepare('SELECT n, day FROM limits WHERE k = ?').bind(key).first();
  if (row && row.day === day && row.n >= max) return false;
  if (!row || row.day !== day) await db.prepare('INSERT OR REPLACE INTO limits (k, n, day) VALUES (?, 1, ?)').bind(key, day).run();
  else await db.prepare('UPDATE limits SET n = n + 1 WHERE k = ?').bind(key).run();
  return true;
}

// ---------- players ----------
async function authPlayer(db, request) {
  const m = (request.headers.get('Authorization') || '').match(/^Bearer\s+([A-Za-z0-9-]{16,40})$/);
  if (!m) return null;
  const tok = cleanCode(m[1]);
  if (tok.length !== 16) return null;
  return db.prepare('SELECT * FROM players WHERE token_hash = ?').bind(await sha256(tok)).first();
}
async function needPlayer(db, request) {
  const p = await authPlayer(db, request);
  if (!p) fail(401, 'Your Packs sign-in was not found on this device. Use your recovery code to restore it.');
  return p;
}
async function myPacks(db, playerId) {
  const { results } = await db.prepare(
    `SELECT p.id, p.code, p.name, p.default_board, p.owner_id,
            (SELECT COUNT(*) FROM members m2 WHERE m2.pack_id = p.id) AS members,
            CASE WHEN p.owner_id = m.player_id THEN (SELECT COUNT(*) FROM requests r WHERE r.pack_id = p.id) ELSE 0 END AS waiting
       FROM members m JOIN packs p ON p.id = m.pack_id
      WHERE m.player_id = ? ORDER BY m.joined_at`).bind(playerId).all();
  return results.map(r => ({ id: r.id, code: r.code, name: r.name, defaultBoard: r.default_board,
    members: r.members, isOwner: r.owner_id === playerId, waiting: r.waiting }));
}
async function myRequests(db, playerId) {
  const { results } = await db.prepare(
    'SELECT p.id, p.name FROM requests r JOIN packs p ON p.id = r.pack_id WHERE r.player_id = ? ORDER BY r.requested_at').bind(playerId).all();
  return results.map(r => ({ id: r.id, name: r.name }));
}
const skinList = p => String(p.skins || '').split(',').filter(Boolean);
// A profile the game made silently has no name yet; it needs one before it can make or join a Pack
async function needName(db, p, body) {
  if (p.nickname) return;
  if (!body.nickname) fail(400, 'Pick your name on Wienerboards first.');
  p.nickname = cleanName(body.nickname, 2, 16, 'name', true);
  await db.prepare('UPDATE players SET nickname = ? WHERE id = ?').bind(p.nickname, p.id).run();
}
async function meResponse(db, p, extra) {
  return Object.assign({ player: { id: p.id, nickname: p.nickname, best: p.best, skins: skinList(p) }, packs: await myPacks(db, p.id),
    requests: await myRequests(db, p.id) }, extra || {});
}

// ---------- packs ----------
async function packForMember(db, packId, playerId) {
  const pack = await db.prepare('SELECT * FROM packs WHERE id = ?').bind(packId).first();
  if (!pack) fail(404, 'That Pack no longer exists.');
  const mem = await db.prepare('SELECT 1 FROM members WHERE pack_id = ? AND player_id = ?').bind(packId, playerId).first();
  if (!mem) fail(403, 'You are not in that Pack.');
  return pack;
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
  const stmt = which === 'all' ? db.prepare(sql).bind(pack.id) : db.prepare(sql).bind(week, pack.id);
  const { results } = await stmt.all();
  const rows = results.map(r => ({ id: r.id, name: r.nickname, score: r.score, you: r.id === playerId, owner: r.id === pack.owner_id }));
  const out = { pack: { id: pack.id, code: pack.code, name: pack.name, defaultBoard: pack.default_board,
    isOwner: pack.owner_id === playerId, members: rows.length, approval: !!pack.approval }, board: which, rows };
  if (pack.owner_id === playerId) {
    const { results: reqs } = await db.prepare(
      `SELECT pl.id, pl.nickname FROM requests r JOIN players pl ON pl.id = r.player_id
        WHERE r.pack_id = ? ORDER BY r.requested_at LIMIT ${MAX_WAITING_PER_PACK}`).bind(pack.id).all();
    out.requests = reqs.map(r => ({ id: r.id, name: r.nickname }));
  }
  if (which !== 'all') {
    const next = new Date(week + 'T00:00:00Z').getTime() + 7 * 86400000;
    out.resetsAt = next;
    const last = await db.prepare(
      `SELECT pl.nickname, w.best FROM weekly w JOIN members m ON m.player_id = w.player_id AND m.pack_id = ?
         JOIN players pl ON pl.id = w.player_id WHERE w.week = ? ORDER BY w.best DESC, w.best_at LIMIT 1`)
      .bind(pack.id, prevWeekKey(now)).first();
    if (last && last.best > 0) out.lastWeekTop = { name: last.nickname, score: last.best };
  }
  return out;
}

async function newPackCode(db) {
  for (let i = 0; i < 6; i++) {
    const c = randCode(6);
    if (!(await db.prepare('SELECT 1 FROM packs WHERE code = ?').bind(c).first())) return c;
  }
  fail(503, 'Could not make a Pack code. Please try again.');
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
  if (!db) fail(503, 'Packs are not switched on yet.');
  await ensureSchema(db);
  const method = request.method, now = Date.now();
  const body = method === 'POST' ? await request.json().catch(() => ({})) : {};
  const ip = request.headers.get('CF-Connecting-IP') || 'local';

  if (method === 'POST' && path === 'player') {
    // silent: the game makes a nameless profile in the background to keep a player's costumes
    const silent = body.silent === true;
    const nickname = silent ? '' : cleanName(body.nickname, 2, 16, 'name', true);
    if (!(await underLimit(db, (silent ? 'ns:' : 'np:') + (await sha256(ip + today())), silent ? NEW_SILENT_PLAYERS_PER_IP_PER_DAY : NEW_PLAYERS_PER_IP_PER_DAY))) fail(429, 'Too many new players from here today. Try again tomorrow.');
    await db.prepare('DELETE FROM limits WHERE day <> ?').bind(today()).run();
    const id = randCode(12), token = randCode(16);
    await db.prepare('INSERT INTO players (id, token_hash, nickname, created_at) VALUES (?, ?, ?, ?)')
      .bind(id, await sha256(token), nickname, now).run();
    const p = await db.prepare('SELECT * FROM players WHERE id = ?').bind(id).first();
    return meResponse(db, p, { token: fmtToken(token) });
  }
  if (method === 'POST' && path === 'recover') {
    const tok = cleanCode(body.code);
    if (tok.length !== 16) fail(400, 'Recovery codes have 16 letters and numbers.');
    const p = await db.prepare('SELECT * FROM players WHERE token_hash = ?').bind(await sha256(tok)).first();
    if (!p) fail(404, 'That recovery code was not found. Check it and try again.');
    return meResponse(db, p, { token: fmtToken(tok) });
  }
  if (method === 'GET' && path === 'me') return meResponse(db, await needPlayer(db, request));
  if (method === 'POST' && path === 'me/skins') {   // adds costumes won on this device (never removes any)
    const p = await needPlayer(db, request);
    const have = skinList(p), add = (Array.isArray(body.skins) ? body.skins : []).filter(k => typeof k === 'string' && /^[a-z]{2,24}$/.test(k));
    const all = have.concat(add.filter((k, i) => have.indexOf(k) < 0 && add.indexOf(k) === i)).slice(0, MAX_SKINS);
    if (all.length !== have.length) { p.skins = all.join(','); await db.prepare('UPDATE players SET skins = ? WHERE id = ?').bind(p.skins, p.id).run(); }
    return meResponse(db, p);
  }
  if (method === 'POST' && path === 'me/name') {
    const p = await needPlayer(db, request);
    const nickname = cleanName(body.nickname, 2, 16, 'name', true);
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
    return { deleted: true };
  }
  if (method === 'POST' && path === 'packs') {
    const p = await needPlayer(db, request);
    await needName(db, p, body);
    const name = cleanName(body.name, 3, 24, 'Pack name');
    const defaultBoard = body.defaultBoard === 'all' ? 'all' : 'week';
    const approval = body.approval === false ? 0 : 1;
    if ((await packCount(db, p.id)) >= MAX_PACKS_PER_PLAYER) fail(409, `You can be in up to ${MAX_PACKS_PER_PLAYER} Packs. Leave one to make a new one.`);
    if (!(await underLimit(db, 'nk:' + p.id, NEW_PACKS_PER_PLAYER_PER_DAY))) fail(429, 'That is a lot of new Packs for one day. Try again tomorrow.');
    const id = randCode(12), code = await newPackCode(db);
    await db.batch([
      db.prepare('INSERT INTO packs (id, code, name, owner_id, default_board, created_at, approval) VALUES (?, ?, ?, ?, ?, ?, ?)').bind(id, code, name, p.id, defaultBoard, now, approval),
      db.prepare('INSERT INTO members (pack_id, player_id, joined_at) VALUES (?, ?, ?)').bind(id, p.id, now),
    ]);
    const pack = await db.prepare('SELECT * FROM packs WHERE id = ?').bind(id).first();
    return board(db, pack, p.id, defaultBoard, now);
  }
  if (method === 'POST' && path === 'packs/join') {
    const p = await needPlayer(db, request);
    await needName(db, p, body);
    const code = cleanCode(body.code);
    if (code.length !== 6) fail(400, 'Pack codes have 6 letters and numbers.');
    const pack = await db.prepare('SELECT * FROM packs WHERE code = ?').bind(code).first();
    if (!pack) fail(404, 'No Pack has that code. Check it and try again.');
    const already = await db.prepare('SELECT 1 FROM members WHERE pack_id = ? AND player_id = ?').bind(pack.id, p.id).first();
    if (!already) {
      if ((await packCount(db, p.id)) >= MAX_PACKS_PER_PLAYER) fail(409, `You can be in up to ${MAX_PACKS_PER_PLAYER} Packs. Leave one to join this one.`);
      const n = await db.prepare('SELECT COUNT(*) AS n FROM members WHERE pack_id = ?').bind(pack.id).first();
      if (n && n.n >= MAX_MEMBERS) fail(409, `That Pack is full (${MAX_MEMBERS} players).`);
      if (pack.approval) {   // the leader lets each new player in
        const asked = await db.prepare('SELECT 1 FROM requests WHERE pack_id = ? AND player_id = ?').bind(pack.id, p.id).first();
        if (!asked) {
          const mine = await db.prepare('SELECT COUNT(*) AS n FROM requests WHERE player_id = ?').bind(p.id).first();
          if (mine && mine.n >= MAX_REQUESTS_PER_PLAYER) fail(409, `You're already waiting on ${MAX_REQUESTS_PER_PLAYER} Packs. Cancel one to ask to join another.`);
          const waiting = await db.prepare('SELECT COUNT(*) AS n FROM requests WHERE pack_id = ?').bind(pack.id).first();
          if (waiting && waiting.n >= MAX_WAITING_PER_PACK) fail(409, 'That Pack has too many players waiting. Try again later.');
          await db.prepare('INSERT INTO requests (pack_id, player_id, requested_at) VALUES (?, ?, ?)').bind(pack.id, p.id, now).run();
        }
        return meResponse(db, p, { pending: { id: pack.id, name: pack.name } });
      }
      await db.prepare('INSERT OR IGNORE INTO members (pack_id, player_id, joined_at) VALUES (?, ?, ?)').bind(pack.id, p.id, now).run();
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
      if (pack.owner_id !== p.id) fail(403, 'Only the Pack leader can do that.');
      const who = String(body.playerId || '');
      if (action === 'remove') {
        if (who === p.id) fail(400, 'Use Leave Pack to leave your own Pack.');
        await db.prepare('DELETE FROM members WHERE pack_id = ? AND player_id = ?').bind(pack.id, who).run();
      } else if (action === 'approve') {
        const asked = await db.prepare('SELECT 1 FROM requests WHERE pack_id = ? AND player_id = ?').bind(pack.id, who).first();
        if (!asked) fail(404, 'That request is gone. The player may have cancelled it.');
        const n = await db.prepare('SELECT COUNT(*) AS n FROM members WHERE pack_id = ?').bind(pack.id).first();
        if (n && n.n >= MAX_MEMBERS) fail(409, `Your Pack is full (${MAX_MEMBERS} players).`);
        if ((await packCount(db, who)) >= MAX_PACKS_PER_PLAYER) {
          await db.prepare('DELETE FROM requests WHERE pack_id = ? AND player_id = ?').bind(pack.id, who).run();
          fail(409, `That player is already in ${MAX_PACKS_PER_PLAYER} Packs, so they can't join. Their request was removed.`);
        }
        await db.batch([
          db.prepare('INSERT OR IGNORE INTO members (pack_id, player_id, joined_at) VALUES (?, ?, ?)').bind(pack.id, who, now),
          db.prepare('DELETE FROM requests WHERE pack_id = ? AND player_id = ?').bind(pack.id, who),
        ]);
      } else if (action === 'decline') {
        await db.prepare('DELETE FROM requests WHERE pack_id = ? AND player_id = ?').bind(pack.id, who).run();
      } else if (action === 'newcode') {   // the old code stops working right away
        pack.code = await newPackCode(db);
        await db.prepare('UPDATE packs SET code = ? WHERE id = ?').bind(pack.code, pack.id).run();
      } else {
        const defaultBoard = body.defaultBoard === 'all' ? 'all' : body.defaultBoard === 'week' ? 'week' : pack.default_board;
        const approval = body.approval === undefined ? pack.approval : (body.approval ? 1 : 0);
        const name = body.name === undefined ? pack.name : cleanName(body.name, 3, 24, 'Pack name');
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
    await db.batch([
      db.prepare('UPDATE players SET last_score_at = ?, best = MAX(best, ?), best_at = CASE WHEN ? > best THEN ? ELSE best_at END WHERE id = ?')
        .bind(now, run.score, run.score, now, p.id),
      db.prepare(`INSERT INTO weekly (player_id, week, best, best_at) VALUES (?, ?, ?, ?)
                  ON CONFLICT (player_id, week) DO UPDATE SET best = MAX(best, excluded.best),
                  best_at = CASE WHEN excluded.best > best THEN excluded.best_at ELSE best_at END`).bind(p.id, week, run.score, now),
    ]);
    // Where this leaves you in each of your Packs this week (shown on the Game Over screen)
    const me = await db.prepare('SELECT best FROM weekly WHERE player_id = ? AND week = ?').bind(p.id, week).first();
    const weekBest = me ? me.best : run.score;
    const { results } = await db.prepare(
      `SELECT p.id, p.name,
              (SELECT COUNT(*) FROM members m2 WHERE m2.pack_id = p.id) AS players,
              (SELECT COUNT(*) FROM members m3 JOIN weekly w ON w.player_id = m3.player_id AND w.week = ?
                 WHERE m3.pack_id = p.id AND w.best > ?) AS ahead
         FROM members m JOIN packs p ON p.id = m.pack_id WHERE m.player_id = ? ORDER BY m.joined_at`)
      .bind(week, weekBest, p.id).all();
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
  try {
    const data = await route(request, env, path);
    return new Response(JSON.stringify(data), { status: 200, headers });
  } catch (e) {
    const status = e instanceof ApiError ? e.status : 500;
    const message = e instanceof ApiError ? e.message : 'Something went wrong. Please try again.';
    if (!(e instanceof ApiError)) console.error('packs api', e && e.stack || e);
    return new Response(JSON.stringify({ error: message }), { status, headers });
  }
}
