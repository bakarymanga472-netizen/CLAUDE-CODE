/* Verdict — application. Données : fichiers JSON du même site (générés par scripts/build-data.js depuis ESPN). Modèles : models.js */
(function () {
  'use strict';
  const M = window.Models;
  const $app = document.getElementById('app');
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const pc = x => (100 * x).toFixed(0) + ' %';
  const num = s => (s && typeof s === 'object') ? +(s.value != null ? s.value : s.displayValue) : +s;

  const SPORTS = {
    foot: { label: 'Football', icon: '⚽', kind: 'foot', comps: [['ita.1', 'Serie A'], ['eng.1', 'Premier League'], ['esp.1', 'Liga'], ['ger.1', 'Bundesliga'], ['fra.1', 'Ligue 1'], ['uefa.champions', 'Ligue des champions']], path: c => 'soccer/' + c },
    nba: { label: 'Basket', icon: '🏀', kind: 'nba', comps: [['nba', 'NBA']], path: () => 'basketball/nba' },
    mma: { label: 'MMA', icon: '🥊', kind: 'mma', comps: [['ufc', 'UFC']], path: () => 'mma/ufc' },
    tennis: { label: 'Tennis', icon: '🎾', kind: 'tennis', comps: [['atp', 'ATP'], ['wta', 'WTA']], path: c => 'tennis/' + c },
    f1: { label: 'F1', icon: '🏎️', kind: 'f1', comps: [['f1', 'Formule 1']], path: () => 'racing/f1' }
  };
  const compLabel = (sp, c) => (SPORTS[sp].comps.find(x => x[0] === c) || [c, c])[1];

  // ---------- réseau ----------
  const cache = new Map();
  function getJSON(url) {
    if (!cache.has(url)) cache.set(url, fetch(url).then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); }).catch(e => { cache.delete(url); throw e; }));
    return cache.get(url);
  }
  const ymd = d => d.getFullYear() + String(d.getMonth() + 1).padStart(2, '0') + String(d.getDate()).padStart(2, '0');

  async function fetchDay(sp, comp, day) {
    const j = await getJSON('data/day/' + day + '.json');
    return (j[sp] && j[sp][comp]) || [];
  }

  let META = { generated: new Date(0).toISOString() };
  const loadMeta = () => getJSON('data/meta.json').then(m => { META = m; }).catch(() => { /* meta absent */ });

  // ---------- stockage ----------
  const SKEY = 'verdict.v3';
  const load = () => { try { return Object.assign({ verdicts: {}, bets: [] }, JSON.parse(localStorage.getItem(SKEY) || '{}')); } catch (e) { return { verdicts: {}, bets: [] }; } };
  const store = s => { try { localStorage.setItem(SKEY, JSON.stringify(s)); } catch (e) { /* stockage indisponible */ } };

  // ---------- résultats (vérification automatique) ----------
  async function settleAll() {
    const s = load(); let changed = false, results = {};
    try { results = await getJSON('data/results.json'); } catch (e) { return s; }
    for (const [k, x] of [...Object.entries(s.verdicts), ...s.bets.map(b => [b.key, b])]) {
      if (x.res == null && results[k] != null) { x.res = results[k]; changed = true; }
    }
    if (changed) store(s);
    return s;
  }
  function briers(s) {
    const done = Object.values(s.verdicts).filter(v => v.res != null);
    if (!done.length) return null;
    const hit = done.filter(v => v.p.indexOf(Math.max(...v.p)) === v.res).length;
    const brier = done.reduce((a, v) => a + v.p.reduce((t, p, i) => t + Math.pow(p - (i === v.res ? 1 : 0), 2), 0), 0) / done.length;
    const base = done.reduce((a, v) => a + v.p.reduce((t, p, i) => t + Math.pow(1 / v.p.length - (i === v.res ? 1 : 0), 2), 0), 0) / done.length;
    return { n: done.length, hit, brier, base };
  }

  // ---------- composants ----------
  const fmtTime = d => new Date(d).toLocaleString('fr-FR', { weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
  const oddsRow = (o, labels) => o ? '<div class="odds">' + o.dec.map((x, i) => `<i><small>${labels[i]}</small>${x.toFixed(2)}</i>`).join('') + '</div>' : '';
  const statusTag = e => e.state === 'in' ? '<span class="live">● EN DIRECT</span>' : e.state === 'post' ? '<span class="badge">Terminé</span>' : esc(fmtTime(e.date));
  const formPills = g => g.slice(-6).reverse().map(x => { const c = x.f > x.a ? 'V' : x.f === x.a ? 'N' : 'D'; return `<span class="f f${c}" title="${esc(x.opp)} ${x.f}-${x.a}">${c}</span>`; }).join('');
  const tag = (t, c) => `<span class="badge ${c || ''}">${esc(t)}</span>`;

  function matchCard(e) {
    const link = esc('#/m/' + e.sp + '/' + e.comp + '/' + e.day + '/' + e.id);
    if (e.sp === 'foot' || e.sp === 'nba') {
      const lab = e.sp === 'foot' ? ['1', 'N', '2'] : ['1', '2'];
      return `<a class="match" href="${link}"><div class="mhead"><span>${esc(compLabel(e.sp, e.comp))}</span><span>${statusTag(e)}</span></div>
      <div class="teams"><div class="team"><img src="${esc(e.home.logo)}" alt="" loading="lazy"><span>${esc(e.home.name)}</span></div>
      <div class="vs">${e.state === 'pre' ? 'VS' : `<span class="score">${e.home.score} - ${e.away.score}</span>`}</div>
      <div class="team r"><span>${esc(e.away.name)}</span><img src="${esc(e.away.logo)}" alt="" loading="lazy"></div></div>
      ${e.state === 'pre' ? oddsRow(e.odds, lab) : ''}<div class="go">${e.state === 'pre' ? 'Analyser ce match →' : 'Voir l\'analyse →'}</div></a>`;
    }
    if (e.sp === 'mma') {
      return `<a class="match" href="${link}"><div class="mhead"><span>${esc(e.tour)}${e.cls ? ' · ' + esc(e.cls) : ''}</span><span>${statusTag(e)}</span></div>
      <div class="teams"><div class="team"><span>${esc(e.f[0].name)}</span></div><div class="vs">VS</div><div class="team r"><span>${esc(e.f[1].name)}</span></div></div>
      <div class="m" style="display:flex;justify-content:space-between"><span>${esc(e.f[0].rec)}</span><span>${esc(e.f[1].rec)}</span></div><div class="go">Analyser ce combat →</div></a>`;
    }
    if (e.sp === 'tennis') {
      return `<div class="match"><div class="mhead"><span>${esc(e.tour)} · ${esc(e.cat || '')}${e.court ? ' · ' + esc(e.court) : ''}</span><span>${statusTag(e)}</span></div>
      ${e.pl.map(p => `<div class="team" style="justify-content:space-between;${p.win ? '' : 'opacity:.75'}"><span>${esc(p.name)}${p.win ? ' ✓' : ''}</span><span class="m">${esc(p.sets)}</span></div>`).join('')}
      ${e.note ? `<div class="m" style="margin-top:6px">${esc(e.note)}</div>` : ''}</div>`;
    }
    return `<div class="match"><div class="mhead"><span>${esc(e.tour)}</span><span>${statusTag(e)}</span></div>
      <table>${e.sessions.map(s => `<tr><td><b>${esc(s.t)}</b></td><td>${esc(fmtTime(s.d))}</td><td>${s.s === 'post' ? '<span class="badge ok">Terminée</span>' + (s.w ? ' ' + esc(s.w) : '') : s.s === 'in' ? '<span class="live">● En cours</span>' : '<span class="badge">À venir</span>'}</td></tr>`).join('')}</table></div>`;
  }

  // ---------- page d'accueil ----------
  const ui = { sp: 'foot', comp: 'all', off: 0 };
  async function home() {
    await loadMeta();
    const sp = SPORTS[ui.sp];
    const days = Array.from({ length: 7 }, (_, i) => { const d = new Date(); d.setDate(d.getDate() + i); return d; });
    const dl = (d, i) => i === 0 ? 'Auj.' : i === 1 ? 'Demain' : d.toLocaleDateString('fr-FR', { weekday: 'short' });
    $app.innerHTML = `<section class="hero"><h1>L'analyse de match, <em>sans fausses promesses</em></h1>
      <p>Foot, basket, MMA, tennis, F1. Données réelles, cotes du marché, verdict en pourcentage — et un bilan de tes pronostics vérifié automatiquement.</p></section>
      <div class="chips" id="sports">${Object.entries(SPORTS).map(([k, v]) => `<button class="chip ${k === ui.sp ? 'on' : ''}" data-sp="${k}">${v.icon} ${v.label}</button>`).join('')}</div>
      <div class="chips" id="days">${days.map((d, i) => `<button class="chip day ${i === ui.off ? 'on' : ''}" data-off="${i}">${dl(d, i)}<small>${d.getDate()}/${d.getMonth() + 1}</small></button>`).join('')}</div>
      ${sp.comps.length > 1 ? `<div class="chips" id="comps"><button class="chip sm ${ui.comp === 'all' ? 'on' : ''}" data-c="all">Tous</button>${sp.comps.map(c => `<button class="chip sm ${ui.comp === c[0] ? 'on' : ''}" data-c="${c[0]}">${esc(c[1])}</button>`).join('')}</div>` : ''}
      <div id="fresh" class="m"></div><div id="list"><p class="m">Chargement des matchs…</p></div>
      <div id="bilanmini"></div>`;
    $app.querySelector('#sports').onclick = e => { const b = e.target.closest('[data-sp]'); if (b) { ui.sp = b.dataset.sp; ui.comp = 'all'; home(); } };
    $app.querySelector('#days').onclick = e => { const b = e.target.closest('[data-off]'); if (b) { ui.off = +b.dataset.off; home(); } };
    const cp = $app.querySelector('#comps'); if (cp) cp.onclick = e => { const b = e.target.closest('[data-c]'); if (b) { ui.comp = b.dataset.c; home(); } };
    const day = ymd(days[ui.off]), comps = ui.comp === 'all' ? sp.comps.map(c => c[0]) : [ui.comp];
    const res = await Promise.allSettled(comps.map(c => fetchDay(ui.sp, c, day)));
    if (!$app.querySelector('#list')) return;
    const all = res.flatMap(r => r.status === 'fulfilled' ? r.value : []).sort((a, b) => Date.parse(a.date) - Date.parse(b.date));
    const failed = res.filter(r => r.status === 'rejected').length;
    const list = $app.querySelector('#list');
    const age = (Date.now() - Date.parse(META.generated)) / 3600e3;
    $app.querySelector('#fresh').innerHTML = META.generated.startsWith('1970') ? '' : `Données ESPN du ${new Date(META.generated).toLocaleString('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}${age > 12 ? ' <span class="a">(plus de 12 h : les cotes et scores peuvent avoir changé)</span>' : ''}.`;
    const CAP = 30; const shown = all.slice(0, CAP);
    list.innerHTML = (failed ? `<div class="card note">Données indisponibles pour ${failed} compétition(s) (réseau ou source). Réessaie dans un instant.</div>` : '')
      + (all.length ? (ui.sp === 'tennis' ? '<div class="card note">Tennis et F1 : pas de pronostic. Aucun classement ni cote fiable n\'est disponible gratuitement, et un verdict sans données serait une invention.</div>' : '')
        + (ui.sp === 'f1' ? '<div class="card note">Pas de pronostic F1 : pas de données de performance fiables disponibles gratuitement.</div>' : '') + shown.map(matchCard).join('') + (all.length > CAP ? `<p class="m">${all.length - CAP} autres matchs masqués. <button class="alt" id="more">Tout afficher</button></p>` : '')
        : failed ? '' : `<div class="card"><b>Aucun match ce jour-là.</b><p class="m">Essaie un autre jour ou un autre sport.</p></div>`);
    const more = $app.querySelector('#more'); if (more) more.onclick = () => { list.innerHTML = all.map(matchCard).join(''); };
    const s = await settleAll(), b = briers(s);
    const bm = $app.querySelector('#bilanmini');
    if (bm) bm.innerHTML = `<div class="card"><b>Mon bilan vérifié</b> <span class="m">· ${b ? b.n + ' verdict(s) terminé(s), ' + b.hit + ' bon(s)' : 'aucun verdict terminé pour l\'instant'}</span> <a class="btn alt" style="float:right" href="#/bilan">Détails</a></div>`;
  }

  // ---------- page d'analyse ----------
  async function runSteps(box, steps) {
    const total = steps.length; const ctx = {};
    const draw = (i, state, extra) => {
      box.querySelector('#steps').innerHTML = steps.map((s, k) => `<div class="step ${k < i ? (s.err ? 'err' : 'done') : k === i ? state : ''}"><div class="ic">${k < i ? (s.err ? '!' : '✓') : k === i ? '…' : ''}</div><span class="t">${esc(s.label)}${s.note ? `<br><small>${esc(s.note)}</small>` : ''}</span></div>`).join('');
      const pcn = Math.min(100, Math.round(100 * i / total));
      box.querySelector('#pp').textContent = pcn + '%'; box.querySelector('#pb').style.width = pcn + '%';
    };
    for (let i = 0; i < total; i++) {
      draw(i, 'run');
      try { const note = await steps[i].fn(ctx); if (note) steps[i].note = note; } catch (e) { steps[i].err = true; steps[i].note = 'indisponible : ' + e.message; }
    }
    draw(total, 'done');
    return ctx;
  }

  function verdictHTML(labels, ref, srcTxt, reliab) {
    const best = ref.indexOf(Math.max(...ref));
    return `<div class="card"><div class="m">VERDICT</div><div class="big">${esc(labels[best])} <span class="r">${pc(ref[best])}</span></div>
      ${labels.map((l, i) => `<div class="vrow"><div class="l"><div>${esc(l)}</div><span>${pc(ref[i])}</span></div><div class="bar"><i class="${i === best ? 'top' : ''}" style="width:${ref[i] * 100}%"></i></div></div>`).join('')}
      <p class="m">Source : ${esc(srcTxt)}</p><p class="a" style="margin:6px 0 0">${esc(reliab)} Même une issue à ${pc(ref[best])} se rate ${Math.max(1, Math.round((1 - ref[best]) * 10))} fois sur 10.</p></div>`;
  }

  function betBox(ev, labels, ref, odds) {
    return `<div class="card"><b>Suivre un pari</b><p class="m">Enregistre ta mise : le résultat sera vérifié automatiquement après le match.</p>
      <div class="row3"><div><label>Issue</label><select id="bo">${labels.map((l, i) => `<option value="${i}">${esc(l)}</option>`).join('')}</select></div>
      <div><label>Cote</label><input id="bc" type="number" step="0.01" value="${odds ? odds.dec[0].toFixed(2) : ''}" placeholder="1.85"></div>
      <div><label>Mise (€)</label><input id="bs" type="number" step="1" value="10"></div></div>
      <p><button id="bgo">Enregistrer</button> <span class="m" id="bmsg"></span></p></div>`;
  }
  function wireBet(ev, labels, odds) {
    const sel = document.getElementById('bo'), cot = document.getElementById('bc');
    if (!sel) return;
    sel.onchange = () => { if (odds && odds.dec[sel.value]) cot.value = odds.dec[sel.value].toFixed(2); };
    document.getElementById('bgo').onclick = () => {
      const o = +cot.value, st = +document.getElementById('bs').value, msg = document.getElementById('bmsg');
      if (!(o > 1) || !(st > 0)) { msg.textContent = 'Cote > 1 et mise > 0 requises.'; msg.className = 'r'; return; }
      const s = load(); s.bets.push({ key: ev.key, sp: ev.sp, comp: ev.comp, day: ev.day, id: ev.id, date: ev.date, label: ev.home ? ev.home.name + ' – ' + ev.away.name : ev.f[0].name + ' – ' + ev.f[1].name, out: +sel.value, outLabel: labels[sel.value], odds: o, stake: st, res: null }); store(s);
      msg.textContent = 'Pari enregistré. Résultat vérifié automatiquement.'; msg.className = 'g';
    };
  }
  function saveVerdict(ev, labels, ref, src) {
    if (ev.state !== 'pre') return;
    const s = load(); if (s.verdicts[ev.key]) return;
    s.verdicts[ev.key] = { sp: ev.sp, comp: ev.comp, day: ev.day, id: ev.id, date: ev.date, label: ev.home ? ev.home.name + ' – ' + ev.away.name : ev.f[0].name + ' – ' + ev.f[1].name, labels, p: ref, src, res: null }; store(s);
  }

  async function analyse(sp, comp, day, id) {
    $app.innerHTML = '<a class="back" href="#/">← Retour aux matchs</a><p class="m">Chargement du match…</p>';
    await loadMeta();
    let ev;
    try { ev = (await fetchDay(sp, comp, day)).find(e => e.id === id); } catch (e) { /* géré ci-dessous */ }
    if (!ev) { $app.innerHTML = '<a class="back" href="#/">← Retour</a><div class="card note">Match introuvable (source indisponible ou match retiré). Reviens à la liste.</div>'; return; }
    const isTeam = sp === 'foot' || sp === 'nba';
    const title = isTeam ? `${esc(ev.home.name)} <span class="m">vs</span> ${esc(ev.away.name)}` : `${esc(ev.f[0].name)} <span class="m">vs</span> ${esc(ev.f[1].name)}`;
    $app.innerHTML = `<a class="back" href="#/">← Retour aux matchs</a>
      <div class="card"><div class="mhead"><span>${esc(isTeam ? compLabel(sp, comp) : ev.tour)}</span><span>${statusTag(ev)}</span></div>
      <h2 style="margin:6px 0 0;font-size:24px">${title}</h2>${ev.state !== 'pre' && isTeam ? `<div class="score" style="margin-top:6px">${ev.home.score} - ${ev.away.score}</div>` : ''}</div>
      <div class="prog"><span>ANALYSE DU MATCH…</span><span id="pp">0%</span></div><div class="pbar"><i id="pb" style="width:0"></i></div>
      <div class="steps" id="steps"></div><div id="result"></div>`;
    const box = $app, result = () => document.getElementById('result');
    if (sp === 'foot') return analyseFoot(ev, box, result);
    if (sp === 'nba') return analyseNba(ev, box, result);
    return analyseMma(ev, box, result);
  }

  function contextHTML(ev, hg, ag, st) {
    const rk = id => st.find(x => x.id === String(id));
    const line = (t, g, home) => {
      const r = rk(t.id); const sp = g.filter(x => x.home === home).slice(-8);
      const avg = sp.length ? (sp.reduce((s, x) => s + x.f, 0) / sp.length).toFixed(1) + ' marqués / ' + (sp.reduce((s, x) => s + x.a, 0) / sp.length).toFixed(1) + ' encaissés (' + sp.length + ' m.)' : '—';
      return `<div><b>${esc(t.name)}</b><br><span class="m">${r && r.rank ? r.rank + 'ᵉ · ' + r.pts + ' pts · diff. ' + (r.gd > 0 ? '+' : '') + r.gd + ' (' + r.gp + ' m.)' : (t.rec ? 'Bilan ' + esc(t.rec) : '')}</span><br>${formPills(g) || '—'}<br><span class="m">${home ? 'À domicile' : 'À l\'extérieur'} : ${avg}</span></div>`;
    };
    const h2h = hg.filter(x => x.oppId === String(ev.away.id)).slice(-5).reverse();
    return `<div class="card"><b>Contexte</b><div class="row" style="margin-top:8px">${line(ev.home, hg, true)}${line(ev.away, ag, false)}</div>
      <p class="m">Forme : du plus récent à gauche. Survole une pastille pour le détail.</p>
      <b>Confrontations récentes</b>${h2h.length ? '<table>' + h2h.map(x => `<tr><td>${esc(x.d.slice(0, 10))}</td><td>${x.home ? esc(ev.home.name) : esc(ev.away.name)}</td><td><b>${x.home ? x.f + '-' + x.a : x.a + '-' + x.f}</b></td><td>${x.home ? esc(ev.away.name) : esc(ev.home.name)}</td></tr>`).join('') + '</table>' : '<p class="m">Aucune dans les données chargées.</p>'}</div>`;
  }

  async function analyseFoot(ev, box, result) {
    const steps = [
      { label: 'Chargement des données du match', fn: async c => { c.d = await getJSON('data/ev/foot/' + ev.comp + '/' + ev.id + '.json'); return 'ESPN, mis à jour ' + new Date(META.generated).toLocaleString('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }); } },
      { label: 'Cotes du marché (1N2, total)', fn: async c => ev.odds ? ev.odds.provider + ', marge ' + (M.devig(ev.odds.dec).margin * 100).toFixed(1) + ' %' : (() => { throw new Error('pas de cotes publiées pour ce match'); })() },
      { label: 'Forme des deux équipes', fn: async c => { c.hg = c.d.hg; c.ag = c.d.ag; return c.hg.length + ' et ' + c.ag.length + ' matchs'; } },
      { label: 'Classement et moyenne de buts de la ligue', fn: async c => { c.st = c.d.st; c.base = c.d.base; return c.base ? c.base.toFixed(2) + ' buts / équipe / match' : (() => { throw new Error('classement indisponible, moyenne par défaut 1,35'); })(); } },
      { label: 'Modèle statistique (Poisson)', fn: async c => { c.m = M.footballModel(c.hg || [], c.ag || [], c.base); return c.m.lA.toFixed(2) + ' – ' + c.m.lB.toFixed(2) + ' buts attendus'; } },
      { label: 'Calcul du verdict', fn: async c => { c.mk = ev.odds ? M.devig(ev.odds.dec) : null; } }
    ];
    const c = await runSteps(box, steps);
    const labels = [ev.home.name + ' gagne', 'Match nul', ev.away.name + ' gagne'];
    const m = c.m, mk = c.mk, ref = mk ? mk.p : m.p;
    const src = mk ? 'cotes ' + ev.odds.provider + ' sans marge (' + (mk.margin * 100).toFixed(1) + ' % retirés)' : 'modèle statistique seul (pas de cotes publiées)';
    const rel = mk ? 'Dans notre test sur 5 256 matchs, les cotes prédisent mieux que notre modèle : elles sont la référence affichée.' : 'Sans cotes, seul le modèle parle. Dans notre test il prédit moins bien que le marché : fiabilité faible.';
    saveVerdict(ev, labels, ref, mk ? 'marché' : 'modèle');
    let tbl = '';
    if (mk) tbl = `<div class="card"><b>Marché vs modèle</b><table><tr><th>Issue</th><th>Cote</th><th>Marché</th><th>Modèle</th><th>Écart</th></tr>${labels.map((l, i) => { const d = m.p[i] - mk.p[i]; return `<tr><td>${esc(l)}</td><td>${ev.odds.dec[i].toFixed(2)}</td><td>${pc(mk.p[i])}</td><td>${pc(m.p[i])}</td><td>${d > 0 ? '+' : ''}${(d * 100).toFixed(1)} pt</td></tr>`; }).join('')}</table>
      <p class="m a">Un écart modèle-marché n'est pas une occasion : dans le test, les paris où le modèle voyait plus de 5 % d'avantage ont perdu 18 % de la mise.</p></div>`;
    result().innerHTML = verdictHTML(labels, ref, src, rel) + `<div class="card"><b>Scores et marchés</b> <span class="m">(modèle)</span>
      <div class="kpis"><div class="kpi"><b>${m.lA.toFixed(2)} – ${m.lB.toFixed(2)}</b><span>buts attendus</span></div><div class="kpi"><b>${pc(m.o25)}</b><span>plus de 2,5 buts</span></div><div class="kpi"><b>${pc(m.btts)}</b><span>les deux marquent</span></div></div>
      <div class="kpis"><div class="kpi"><b>${pc(m.o15)}</b><span>plus de 1,5</span></div><div class="kpi"><b>${pc(m.o35)}</b><span>plus de 3,5</span></div><div class="kpi"><b>${pc(1 - m.o25)}</b><span>moins de 2,5</span></div></div>
      <p>${m.top.map(g => `<span class="pill">${g.i}-${g.j} · ${(g.q * 100).toFixed(1)} %</span>`).join('')}</p>
      ${ev.odds && ev.odds.line ? `<p class="m">Marché : total ${ev.odds.line}${ev.odds.over ? ', plus à ' + ev.odds.over.toFixed(2) : ''}${ev.odds.under ? ', moins à ' + ev.odds.under.toFixed(2) : ''}.</p>` : ''}</div>` + tbl
      + contextHTML(ev, c.hg || [], c.ag || [], c.st || []) + (ev.state === 'pre' ? betBox(ev, labels, ref, ev.odds) : '');
    wireBet(ev, labels, ev.odds);
  }

  async function analyseNba(ev, box, result) {
    const steps = [
      { label: 'Chargement des données du match', fn: async c => { c.d = await getJSON('data/ev/nba/nba/' + ev.id + '.json'); return 'ESPN'; } },
      { label: 'Cotes du marché', fn: async c => ev.odds ? ev.odds.provider + ', marge ' + (M.devig(ev.odds.dec).margin * 100).toFixed(1) + ' %' : (() => { throw new Error('pas de cotes publiées pour ce match'); })() },
      { label: 'Forme des deux équipes (10 derniers matchs)', fn: async c => { c.hg = c.d.hg; c.ag = c.d.ag; return c.hg.length + ' et ' + c.ag.length + ' matchs'; } },
      { label: 'Blessures et prévision ESPN', fn: async c => { c.pred = c.d.pred; c.inj = c.d.inj || []; return c.pred ? 'ESPN : ' + pc(c.pred) + ' pour ' + ev.home.name : 'pas de prévision ESPN'; } },
      { label: 'Modèle statistique (points marqués / encaissés)', fn: async c => { c.m = M.basketModel(c.hg || [], c.ag || []); if (!c.m) throw new Error('historique insuffisant'); return 'marge attendue ' + (c.m.margin > 0 ? '+' : '') + c.m.margin.toFixed(1) + ' pts'; } },
      { label: 'Calcul du verdict', fn: async c => { c.mk = ev.odds ? M.devig(ev.odds.dec) : null; } }
    ];
    const c = await runSteps(box, steps);
    const labels = [ev.home.name + ' gagne', ev.away.name + ' gagne'];
    const m = c.m, mk = c.mk;
    const ref = mk ? mk.p : m ? m.p : c.pred ? [c.pred, 1 - c.pred] : null;
    if (!ref) { result().innerHTML = '<div class="card note">Données insuffisantes pour produire un verdict honnête sur ce match.</div>'; return; }
    const src = mk ? 'cotes ' + ev.odds.provider + ' sans marge' : m ? 'modèle statistique simple (points marqués et encaissés, avantage du terrain)' : 'prévision ESPN';
    saveVerdict(ev, labels, ref, mk ? 'marché' : m ? 'modèle' : 'espn');
    const inj = (c.inj || []).map(t => `<div style="margin:6px 0"><b>${esc(t.team)}</b><br><span class="m">${(t.list || []).map(i => esc(i.n + ' (' + (i.s || '?') + ')')).join(', ') || 'aucun signalé'}</span></div>`).join('');
    result().innerHTML = verdictHTML(labels, ref, src, mk ? 'Les cotes du marché sont la référence. Le modèle NBA n\'a pas été évalué en backtest.' : 'Modèle NBA simple, non évalué en backtest : fiabilité faible.')
      + (m ? `<div class="card"><b>Estimation (modèle)</b><div class="kpis"><div class="kpi"><b>${m.hPts.toFixed(0)} – ${m.aPts.toFixed(0)}</b><span>points attendus</span></div><div class="kpi"><b>${m.margin > 0 ? '+' : ''}${m.margin.toFixed(1)}</b><span>marge (dom.)</span></div><div class="kpi"><b>${m.total.toFixed(0)}</b><span>total de points</span></div></div>
        <p class="m">Modèle : ${pc(m.p[0])} pour ${esc(ev.home.name)}${c.pred ? ' · prévision ESPN : ' + pc(c.pred) : ''}${mk ? ' · marché : ' + pc(mk.p[0]) : ''}.</p></div>` : '')
      + `<div class="card"><b>Forme</b><div class="row" style="margin-top:8px"><div><b>${esc(ev.home.name)}</b> <span class="m">${esc(ev.home.rec)}</span><br>${formPills(c.hg || []) || '—'}</div><div><b>${esc(ev.away.name)}</b> <span class="m">${esc(ev.away.rec)}</span><br>${formPills(c.ag || []) || '—'}</div></div></div>`
      + (inj ? `<div class="card"><b>Blessures</b>${inj}</div>` : '') + (ev.state === 'pre' ? betBox(ev, labels, ref, ev.odds) : '');
    wireBet(ev, labels, ev.odds);
  }

  async function analyseMma(ev, box, result) {
    const steps = [
      { label: 'Fiche des combattants', fn: async c => ev.f[0].rec + ' / ' + ev.f[1].rec },
      { label: 'Cotes du marché', fn: async c => ev.odds ? ev.odds.provider : (() => { throw new Error('pas de cotes publiées'); })() },
      { label: 'Estimation (taux de victoire lissé, log5)', fn: async c => { c.m = M.mmaModel(M.parseRecord(ev.f[0].rec), M.parseRecord(ev.f[1].rec)); } },
      { label: 'Calcul du verdict', fn: async c => { c.mk = ev.odds ? M.devig(ev.odds.dec) : null; } }
    ];
    const c = await runSteps(box, steps);
    const labels = [ev.f[0].name + ' gagne', ev.f[1].name + ' gagne'], ref = c.mk ? c.mk.p : c.m.p;
    saveVerdict(ev, labels, ref, c.mk ? 'marché' : 'modèle');
    result().innerHTML = verdictHTML(labels, ref, c.mk ? 'cotes ' + ev.odds.provider + ' sans marge' : 'bilan victoires/défaites uniquement', c.mk ? 'Cotes du marché : référence.' : 'Estimation très grossière : elle ignore style, adversaires et forme récente. Fiabilité très faible.')
      + `<div class="card"><b>Fiche</b><table><tr><th></th><th>${esc(ev.f[0].name)}</th><th>${esc(ev.f[1].name)}</th></tr><tr><td>Bilan (V-D-N)</td><td>${esc(ev.f[0].rec)}</td><td>${esc(ev.f[1].rec)}</td></tr><tr><td>Catégorie</td><td colspan="2">${esc(ev.cls || '—')}</td></tr></table></div>`
      + (ev.state === 'pre' ? betBox(ev, labels, ref, ev.odds) : '');
    wireBet(ev, labels, ev.odds);
  }

  // ---------- bilan ----------
  async function bilan() {
    $app.innerHTML = '<a class="back" href="#/">← Retour</a><h2>Mon bilan</h2><p class="m">Vérification des résultats…</p>';
    const s = await settleAll(), b = briers(s);
    const vs = Object.values(s.verdicts).sort((x, y) => Date.parse(y.date) - Date.parse(x.date));
    const done = s.bets.filter(x => x.res != null), staked = done.reduce((a, x) => a + x.stake, 0);
    const pnl = done.reduce((a, x) => a + (x.res === x.out ? x.stake * (x.odds - 1) : -x.stake), 0);
    $app.innerHTML = `<a class="back" href="#/">← Retour</a><h2 style="margin:6px 0">Mon bilan</h2>
      <div class="card note">Tout est calculé sur <b>tes</b> verdicts et tes paris, vérifiés automatiquement avec les résultats officiels. Rien n'est affiché si aucun match n'est terminé.</div>
      <div class="kpis k4"><div class="kpi"><b>${b ? b.n : 0}</b><span>verdicts terminés</span></div><div class="kpi"><b>${b ? pc(b.hit / b.n) : '—'}</b><span>issue la plus probable gagnante</span></div>
      <div class="kpi"><b>${b ? b.brier.toFixed(3) : '—'}</b><span>Brier (hasard : ${b ? b.base.toFixed(3) : '—'})</span></div><div class="kpi"><b>${staked ? (100 * pnl / staked).toFixed(1) + ' %' : '—'}</b><span>ROI de tes paris</span></div></div>
      <p class="m">Brier : plus c'est bas, mieux c'est ; un verdict qui ne bat pas la valeur « hasard » n'apporte aucune information. Il faut au moins plusieurs dizaines de matchs pour que ces chiffres veuillent dire quelque chose.</p>
      <div class="sec">Verdicts</div>${vs.length ? '<div class="card tc"><table><tr><th>Date</th><th>Match</th><th>Verdict</th><th>Résultat</th></tr>' + vs.map(v => { const best = v.p.indexOf(Math.max(...v.p)); return `<tr><td>${esc(v.date.slice(0, 10))}</td><td>${esc(v.label)}</td><td>${esc(v.labels[best])} ${pc(v.p[best])}</td><td>${v.res == null ? '<span class="badge">en attente</span>' : v.res === best ? '<span class="badge ok">bon</span>' : '<span class="badge ko">raté</span>'}</td></tr>`; }).join('') + '</table></div>' : '<p class="m">Aucun verdict enregistré. Ouvre l\'analyse d\'un match à venir.</p>'}
      <div class="sec">Paris suivis</div>${s.bets.length ? '<div class="card tc"><table><tr><th>Match</th><th>Pari</th><th>Cote</th><th>Mise</th><th>Résultat</th></tr>' + s.bets.map(x => `<tr><td>${esc(x.label)}</td><td>${esc(x.outLabel)}</td><td>${x.odds}</td><td>${x.stake} €</td><td>${x.res == null ? '<span class="badge">en attente</span>' : x.res === x.out ? '<span class="badge ok">gagné</span>' : '<span class="badge ko">perdu</span>'}</td></tr>`).join('') + '</table></div>' : '<p class="m">Aucun pari suivi.</p>'}
      <p><button class="alt" id="rst">Tout effacer</button></p>`;
    document.getElementById('rst').onclick = () => { if (confirm('Effacer tous tes verdicts et paris ?')) { store({ verdicts: {}, bets: [] }); bilan(); } };
  }

  // ---------- méthode ----------
  function methode() {
    $app.innerHTML = `<a class="back" href="#/">← Retour</a><h2 style="margin:6px 0">Méthode et limites</h2>
      <div class="card note"><b>Résultat du test (football).</b> Sur 5 256 matchs de 5 championnats (2023-2026), le modèle prédit moins bien que les cotes de clôture : log-loss 0,998 contre 0,964 (plus bas = mieux). Aucun mélange ne bat le marché seul. Les paris où le modèle voyait plus de 5 % d'avantage : 2 476 paris, 21 % gagnés, ROI −18 %.
      C'est pourquoi la référence affichée est le marché dès que des cotes existent. Détails et code : dossier <code>backtest/</code> du dépôt.</div>
      <div class="card"><b>Football</b><p class="m">Force offensive/défensive de chaque équipe sur ses 20 derniers matchs, divisée par la moyenne de la ligue, ramenée vers 1 par n/(n+6). Buts attendus = base × attaque × défense adverse × 1,08 (domicile) ou 0,93 (extérieur), puis loi de Poisson. Paramètres choisis sur 2020-23, évalués une seule fois sur 2023-26.</p></div>
      <div class="card"><b>Basket (NBA)</b><p class="m">Points marqués et encaissés sur 10 matchs, marge rétrécie vers 0, avantage du terrain 2,5 pts, loi normale (écart-type 12). <b>Non évalué en backtest</b> : fiabilité faible.</p></div>
      <div class="card"><b>MMA</b><p class="m">Taux de victoire lissé et formule log5. Très grossier, <b>non évalué</b>.</p></div>
      <div class="card"><b>Tennis et F1</b><p class="m">Pas de pronostic : aucune donnée de classement ou de cotes fiable n'est disponible gratuitement. Afficher un pourcentage serait inventer.</p></div>
      <div class="card"><b>Ce qui manque</b><p class="m">Blessures et compositions (football), repos et calendrier, motivation, météo. Les cotes sont celles de DraftKings quand ESPN les publie, souvent quelques jours avant le match seulement.</p></div>
      <div class="sec">Questions</div>
      <details><summary>Est-ce gratuit ?</summary><p>Oui. Aucun compte, aucun paiement, aucune donnée de ta part envoyée à un serveur : tes verdicts et paris restent dans ton navigateur.</p></details>
      <details><summary>Peut-on gagner avec ce site ?</summary><p>Rien ne le garantit, et le test montre que ce modèle ne bat pas le marché. Le site sert à comprendre un match et à mesurer honnêtement tes résultats.</p></details>
      <details><summary>Pourquoi pas de « % de réussite » affiché ?</summary><p>Parce qu'un taux de réussite n'a de sens que mesuré sur des pronostics faits avant les matchs. Le seul affiché ici est le tien, dans « Mon bilan », vérifié automatiquement.</p></details>
      <details><summary>D'où viennent les données ?</summary><p>D'ESPN (résultats, planning, classements, cotes DraftKings quand elles sont publiées). Un script les récupère toutes les 3 heures et les publie avec le site : ton navigateur ne contacte aucun service de données externe (seuls les logos d'équipes viennent du CDN d'ESPN). L'heure de la dernière mise à jour est affichée sur la page d'accueil.</p></details>`;
  }

  // ---------- routeur ----------
  function route() {
    const h = location.hash.replace(/^#\/?/, '').split('/');
    window.scrollTo(0, 0);
    if (h[0] === 'm' && h.length >= 5 && SPORTS[h[1]] && /^[\w.]+$/.test(h[2]) && /^\d{8}$/.test(h[3]) && /^\d+$/.test(h[4])) return analyse(h[1], h[2], h[3], h[4]);
    if (h[0] === 'bilan') return bilan();
    if (h[0] === 'methode') return methode();
    return home();
  }
  window.addEventListener('hashchange', route);
  route();
})();
