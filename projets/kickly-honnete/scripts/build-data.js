#!/usr/bin/env node
/* Récupère les données ESPN côté serveur et les écrit en JSON statique (même origine que le site).
   Usage : node scripts/build-data.js <dossier-sortie>   (Node >= 20) */
const fs = require('fs'), path = require('path');
const OUT = path.resolve(process.argv[2] || 'data');
const API = 'https://site.api.espn.com/apis/site/v2/sports/';
const UA = { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36', Accept: 'application/json' };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const num = s => (s && typeof s === 'object') ? +(s.value != null ? s.value : s.displayValue) : +s;

const SPORTS = {
  foot: { kind: 'foot', comps: ['ita.1', 'eng.1', 'esp.1', 'ger.1', 'fra.1', 'uefa.champions'], path: c => 'soccer/' + c },
  nba: { kind: 'nba', comps: ['nba'], path: () => 'basketball/nba' },
  mma: { kind: 'mma', comps: ['ufc'], path: () => 'mma/ufc' },
  tennis: { kind: 'tennis', comps: ['atp', 'wta'], path: c => 'tennis/' + c },
  f1: { kind: 'f1', comps: ['f1'], path: () => 'racing/f1' }
};
const stats = { ok: 0, fail: 0, failed: [] };
async function getJSON(url, tries = 3) {
  for (let i = 0; i < tries; i++) {
    try { const r = await fetch(url, { headers: UA }); if (!r.ok) throw new Error('HTTP ' + r.status); stats.ok++; return await r.json(); }
    catch (e) { if (i === tries - 1) { stats.fail++; stats.failed.push(url + ' -> ' + e.message); throw e; } await sleep(600 * (i + 1)); }
  }
}
async function pool(items, limit, fn) {
  const out = new Array(items.length); let i = 0;
  await Promise.all(Array.from({ length: limit }, async () => { while (i < items.length) { const k = i++; try { out[k] = await fn(items[k], k); } catch (e) { out[k] = undefined; } } }));
  return out;
}
const ymd = d => d.getUTCFullYear() + String(d.getUTCMonth() + 1).padStart(2, '0') + String(d.getUTCDate()).padStart(2, '0');
const addDays = (n) => { const d = new Date(); d.setUTCDate(d.getUTCDate() + n); return d; };

const dec = M => M; // (conversion cotes faite ci-dessous)
function americanToDecimal(a) {
  if (a == null) return null;
  if (typeof a === 'string') { a = a.trim().toUpperCase(); if (a === 'EVEN' || a === 'EV') return 2; a = parseFloat(a); }
  if (!isFinite(a) || a === 0) return null;
  return a > 0 ? 1 + a / 100 : 1 + 100 / Math.abs(a);
}
function parseOdds(o, kind) {
  if (!o) return null;
  const ml = o.moneyline || {};
  const pick = (side, alt) => americanToDecimal((ml[side] && ml[side].close && ml[side].close.odds) || (ml[side] && ml[side].open && ml[side].open.odds) || alt);
  const h = pick('home', o.homeTeamOdds && o.homeTeamOdds.moneyLine), a = pick('away', o.awayTeamOdds && o.awayTeamOdds.moneyLine);
  const d = kind === 'foot' ? pick('draw', o.drawOdds && o.drawOdds.moneyLine) : null;
  const decs = kind === 'foot' ? [h, d, a] : [h, a];
  if (decs.some(x => !x)) return null;
  const t = o.total || {};
  return { provider: (o.provider && (o.provider.displayName || o.provider.name)) || 'bookmaker', dec: decs, line: o.overUnder || null,
    over: americanToDecimal(t.over && t.over.close && t.over.close.odds), under: americanToDecimal(t.under && t.under.close && t.under.close.odds) };
}
function normalize(sp, comp, day, j) {
  const kind = SPORTS[sp].kind, out = [];
  for (const e of (j.events || [])) {
    try {
      if (kind === 'foot' || kind === 'nba') {
        const c = e.competitions[0], h = c.competitors.find(x => x.homeAway === 'home'), a = c.competitors.find(x => x.homeAway === 'away'); if (!h || !a) continue;
        const side = x => ({ id: x.team.id, name: x.team.displayName, logo: x.team.logo, score: x.score == null ? null : num(x.score), rec: ((x.records || []).find(r => r.type === 'total') || {}).summary || '', win: !!x.winner });
        out.push({ key: comp + ':' + e.id, id: e.id, sp, comp, day, date: e.date, state: e.status.type.state, status: e.status.type.shortDetail, home: side(h), away: side(a), odds: parseOdds(c.odds && c.odds[0], kind) });
      } else if (kind === 'tennis') {
        for (const g of (e.groupings || [])) for (const c of (g.competitions || [])) {
          const pl = (c.competitors || []).map(x => ({ name: (x.athlete && x.athlete.displayName) || (x.team && x.team.displayName) || '?', sets: (x.linescores || []).map(l => l.value).join(' '), win: !!x.winner }));
          if (pl.length < 2) continue;
          out.push({ key: comp + ':' + c.id, id: c.id, sp, comp, day, date: c.date, state: c.status.type.state, status: c.status.type.shortDetail, tour: e.name, cat: g.grouping && g.grouping.displayName, court: c.venue && c.venue.court, pl, note: (c.notes && c.notes[0] && c.notes[0].text) || '' });
        }
      } else if (kind === 'mma') {
        for (const c of (e.competitions || [])) {
          const f = (c.competitors || []).slice().sort((x, y) => (x.order || 0) - (y.order || 0)).map(x => ({ id: x.id, name: x.athlete && x.athlete.displayName, rec: ((x.records || []).find(r => r.type === 'total') || {}).summary || '', win: !!x.winner }));
          if (f.length < 2) continue;
          const st = (c.status || e.status).type || {};
          out.push({ key: comp + ':' + c.id, id: c.id, sp, comp, day, date: c.date, state: st.state, status: st.shortDetail, tour: e.name, cls: c.type && c.type.abbreviation, f, odds: parseOdds(c.odds && c.odds[0], 'nba') });
        }
      } else if (kind === 'f1') {
        out.push({ key: comp + ':' + e.id, id: e.id, sp, comp, day, date: e.date, state: e.status.type.state, status: e.status.type.shortDetail, tour: e.name,
          sessions: (e.competitions || []).map(c => { const w = (c.competitors || []).find(x => x.winner); return { t: c.type && (c.type.abbreviation || c.type.text), d: c.date, s: c.status && c.status.type && c.status.type.state, w: w && w.athlete && w.athlete.displayName }; }) });
      }
    } catch (err) { /* événement mal formé : ignoré */ }
  }
  return out;
}
function outcomeOf(ev) {
  if (ev.state !== 'post') return null;
  if (ev.sp === 'foot') { if (ev.home.score == null || ev.away.score == null) return null; return ev.home.score > ev.away.score ? 0 : ev.home.score === ev.away.score ? 1 : 2; }
  if (ev.sp === 'nba') return ev.home.win ? 0 : ev.away.win ? 1 : null;
  if (ev.sp === 'mma') { const i = ev.f.findIndex(x => x.win); return i < 0 ? null : i; }
  return null;
}
function parseGames(sc, teamId) {
  const out = [];
  for (const e of (sc.events || [])) {
    const c = e.competitions && e.competitions[0]; if (!c) continue;
    const done = c.status && c.status.type && (c.status.type.completed || c.status.type.state === 'post'); if (!done) continue;
    const me = c.competitors.find(x => x.team && String(x.team.id) === String(teamId)), op = c.competitors.find(x => x !== me); if (!me || !op) continue;
    const f = num(me.score), a = num(op.score); if (!isFinite(f) || !isFinite(a)) continue;
    out.push({ d: e.date, f, a, home: me.homeAway === 'home', opp: op.team.displayName, oppId: String(op.team.id) });
  }
  return out;
}
const schedCache = new Map();
function teamGames(sp, comp, id) {
  const k = sp + comp + id;
  if (!schedCache.has(k)) schedCache.set(k, (async () => {
    const base = API + SPORTS[sp].path(comp) + '/teams/' + id + '/schedule';
    const cur = await getJSON(base); let games = parseGames(cur, id);
    const y = (cur.season && cur.season.year) || (cur.requestedSeason && cur.requestedSeason.year);
    if (y && games.length < 20) { try { games = parseGames(await getJSON(base + '?season=' + (y - 1)), id).concat(games); } catch (e) { /* saison précédente absente */ } }
    return games.sort((a, b) => Date.parse(a.d) - Date.parse(b.d)).slice(-30);
  })());
  return schedCache.get(k);
}
function parseStandings(sum) {
  const out = [];
  try {
    const st = sum.standings, groups = st.groups || st.children || [];
    for (const g of groups) for (const en of ((g.standings && g.standings.entries) || [])) {
      const stat = n => { const s = (en.stats || []).find(x => x.name === n); return s ? (s.value != null ? +s.value : +s.displayValue) : null; };
      out.push({ id: String(en.id || (en.team && en.team.id)), name: typeof en.team === 'string' ? en.team : (en.team && en.team.displayName), rank: stat('rank'), pts: stat('points'), gp: stat('gamesPlayed'), pf: stat('pointsFor'), pa: stat('pointsAgainst'), gd: stat('pointDifferential') });
    }
  } catch (e) { /* classement absent */ }
  return out;
}
const tableCache = new Map();
function leagueTable(comp) {
  if (!tableCache.has(comp)) tableCache.set(comp, (async () => {
    const j = await getJSON('https://site.api.espn.com/apis/v2/sports/soccer/' + comp + '/standings');
    const out = [];
    for (const g of (j.children || [])) for (const en of ((g.standings && g.standings.entries) || [])) {
      const stat = n => { const s = (en.stats || []).find(x => x.name === n); return s ? (s.value != null ? +s.value : +s.displayValue) : null; };
      out.push({ id: String(en.team && en.team.id), name: en.team && en.team.displayName, rank: stat('rank'), pts: stat('points'), gp: stat('gamesPlayed'), pf: stat('pointsFor'), pa: stat('pointsAgainst'), gd: stat('pointDifferential') });
    }
    return out;
  })().catch(() => []));
  return tableCache.get(comp);
}
const write = (rel, obj) => { const f = path.join(OUT, rel); fs.mkdirSync(path.dirname(f), { recursive: true }); fs.writeFileSync(f, JSON.stringify(obj)); };

(async () => {
  const t0 = Date.now();
  fs.rmSync(OUT, { recursive: true, force: true });
  const upDays = Array.from({ length: 10 }, (_, i) => ymd(addDays(i - 1)));     // hier -> J+8
  const pastDays = Array.from({ length: 14 }, (_, i) => ymd(addDays(-i)));       // aujourd'hui -> J-13
  const jobs = [];
  for (const day of upDays) for (const [sp, c] of Object.entries(SPORTS)) for (const comp of c.comps) jobs.push({ sp, comp, day, up: true });
  for (const day of pastDays) for (const sp of ['foot', 'nba', 'mma']) for (const comp of SPORTS[sp].comps) if (!upDays.includes(day)) jobs.push({ sp, comp, day, up: false });
  // les jours passés déjà couverts par upDays (aujourd'hui, hier) servent aussi aux résultats
  const results = {}, dayFiles = {}; const events = [];
  await pool(jobs, 8, async j => {
    const evs = normalize(j.sp, j.comp, j.day, await getJSON(API + SPORTS[j.sp].path(j.comp) + '/scoreboard?dates=' + j.day));
    for (const e of evs) { const o = outcomeOf(e); if (o != null) results[e.key] = o; }
    if (j.up) { (dayFiles[j.day] = dayFiles[j.day] || {})[j.sp] = dayFiles[j.day][j.sp] || {}; dayFiles[j.day][j.sp][j.comp] = evs; evs.forEach(e => events.push(e)); }
  });
  for (const day of upDays) write('day/' + day + '.json', dayFiles[day] || {});
  // détails des matchs à venir (football, NBA)
  const upcoming = events.filter(e => (e.sp === 'foot' || e.sp === 'nba') && e.state === 'pre');
  const seen = new Set(); const todo = upcoming.filter(e => !seen.has(e.key) && seen.add(e.key));
  let nDetail = 0;
  await pool(todo, 6, async e => {
    const [hg, ag, sum] = await Promise.all([teamGames(e.sp, e.comp, e.home.id).catch(() => []), teamGames(e.sp, e.comp, e.away.id).catch(() => []), getJSON(API + SPORTS[e.sp].path(e.comp) + '/summary?event=' + e.id).catch(() => null)]);
    const st = e.sp === 'foot' ? await leagueTable(e.comp) : (sum ? parseStandings(sum) : []);
    const gp = st.reduce((s, x) => s + (x.gp || 0), 0), pf = st.reduce((s, x) => s + (x.pf || 0), 0);
    const p = sum && sum.predictor && sum.predictor.homeTeam ? +sum.predictor.homeTeam.gameProjection / 100 : null;
    write('ev/' + e.sp + '/' + e.comp + '/' + e.id + '.json', { hg, ag, st, base: e.sp === 'foot' && gp > 0 ? pf / gp : 0, pred: isFinite(p) ? p : null,
      inj: ((sum && sum.injuries) || []).map(t => ({ team: t.team && t.team.displayName, list: (t.injuries || []).slice(0, 8).map(i => ({ n: i.athlete && i.athlete.displayName, s: i.status })) })) });
    nDetail++;
  });
  write('results.json', results);
  const nEvents = events.length;
  write('meta.json', { generated: new Date().toISOString(), source: 'ESPN', days: upDays, events: nEvents, details: nDetail, results: Object.keys(results).length, requestsOk: stats.ok, requestsFailed: stats.fail });
  console.log(`events=${nEvents} details=${nDetail}/${todo.length} results=${Object.keys(results).length} ok=${stats.ok} fail=${stats.fail} en ${((Date.now() - t0) / 1000).toFixed(0)} s`);
  if (stats.fail) console.log('Échecs (extrait) :\n' + stats.failed.slice(0, 8).join('\n'));
  if (!nEvents) { console.error('Aucun événement récupéré : ESPN inaccessible ?'); process.exit(1); }
})();
