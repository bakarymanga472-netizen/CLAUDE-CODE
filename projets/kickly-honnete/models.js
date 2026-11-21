/* Modèles purs (aucun accès réseau) : utilisables dans le navigateur (window.Models) et dans Node (tests). */
(function (root) {
  const fact = n => { let f = 1; for (let i = 2; i <= n; i++) f *= i; return f; };
  const pois = (l, k) => Math.exp(-l) * Math.pow(l, k) / fact(k);

  // Cote américaine (+150, -340, "EVEN") -> décimale
  function americanToDecimal(a) {
    if (a == null) return null;
    if (typeof a === 'string') { a = a.trim().toUpperCase(); if (a === 'EVEN' || a === 'EV') return 2; a = parseFloat(a); }
    if (!isFinite(a) || a === 0) return null;
    return a > 0 ? 1 + a / 100 : 1 + 100 / Math.abs(a);
  }
  // Retire la marge du bookmaker (normalisation proportionnelle)
  function devig(odds) {
    const r = odds.map(x => 1 / x), s = r.reduce((a, b) => a + b, 0);
    return { p: r.map(x => x / s), margin: s - 1 };
  }
  // Fonction de répartition de la loi normale
  function phi(x) {
    const t = 1 / (1 + 0.2316419 * Math.abs(x)), d = 0.3989423 * Math.exp(-x * x / 2);
    const p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));
    return x > 0 ? 1 - p : p;
  }

  // Football : mêmes paramètres que le backtest (fenêtre 20, rétrécissement n/(n+6), 1,08 / 0,93)
  const N_WIN = 20, K_SH = 6;
  function footballModel(homeGames, awayGames, base) {
    base = base > 0 ? base : 1.35;
    const force = g => {
      const r = g.slice(-N_WIN); if (!r.length) return { att: 1, def: 1, n: 0 };
      const w = r.length / (r.length + K_SH);
      const gf = r.reduce((s, x) => s + x.f, 0) / r.length, ga = r.reduce((s, x) => s + x.a, 0) / r.length;
      return { att: 1 + (gf / base - 1) * w, def: 1 + (ga / base - 1) * w, n: r.length };
    };
    const A = force(homeGames), B = force(awayGames);
    const lA = base * A.att * B.def * 1.08, lB = base * B.att * A.def * 0.93;
    let H = 0, D = 0, V = 0, o25 = 0, o15 = 0, o35 = 0, btts = 0; const grid = [];
    for (let i = 0; i <= 8; i++) for (let j = 0; j <= 8; j++) {
      const q = pois(lA, i) * pois(lB, j); grid.push({ i, j, q });
      if (i > j) H += q; else if (i === j) D += q; else V += q;
      if (i + j > 2) o25 += q; if (i + j > 1) o15 += q; if (i + j > 3) o35 += q;
      if (i > 0 && j > 0) btts += q;
    }
    const t = H + D + V; grid.sort((x, y) => y.q - x.q);
    return { p: [H / t, D / t, V / t], lA, lB, o15, o25, o35, btts, top: grid.slice(0, 5), A, B, base };
  }

  // Basket : marge attendue à partir des points marqués/encaissés, rétrécie vers 0, avantage du terrain 2,5 pts
  function basketModel(homeGames, awayGames) {
    const st = g => {
      const r = g.slice(-10); if (!r.length) return null;
      return { n: r.length, pf: r.reduce((s, x) => s + x.f, 0) / r.length, pa: r.reduce((s, x) => s + x.a, 0) / r.length };
    };
    const H = st(homeGames), A = st(awayGames);
    if (!H || !A) return null;
    const hPts = (H.pf + A.pa) / 2, aPts = (A.pf + H.pa) / 2;
    const w = Math.min(H.n, A.n) / (Math.min(H.n, A.n) + 8);
    const margin = (hPts - aPts) * w + 2.5;
    return { p: [phi(margin / 12), 1 - phi(margin / 12)], margin, total: hPts + aPts, hPts, aPts, H, A };
  }

  // MMA : taux de victoire lissé combiné par la formule log5
  function mmaModel(recA, recB) {
    const s = r => (r.w + 5) / (r.w + r.l + r.d + 10);   // a priori : 5 victoires / 5 défaites (évite les 90 % sur 12-0)
    const a = s(recA), b = s(recB), p = a * (1 - b) / (a * (1 - b) + b * (1 - a));
    return { p: [p, 1 - p], a, b };
  }
  function parseRecord(str) {
    const m = /^(\d+)-(\d+)(?:-(\d+))?/.exec(str || '');
    return m ? { w: +m[1], l: +m[2], d: +(m[3] || 0) } : { w: 0, l: 0, d: 0 };
  }

  const entropyNorm = p => -p.reduce((s, x) => s + (x > 0 ? x * Math.log(x) : 0), 0) / Math.log(p.length);
  root.Models = { americanToDecimal, devig, phi, footballModel, basketModel, mmaModel, parseRecord, entropyNorm };
  if (typeof module !== 'undefined') module.exports = root.Models;
})(typeof window !== 'undefined' ? window : globalThis);
