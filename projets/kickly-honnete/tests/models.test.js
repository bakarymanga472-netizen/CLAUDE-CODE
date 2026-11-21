const M = require('../models.js'); const assert = require('assert');
const near = (a, b, e = 1e-6) => assert(Math.abs(a - b) < e, `${a} != ${b}`);
// cotes américaines
near(M.americanToDecimal('-340'), 1 + 100 / 340); near(M.americanToDecimal('+650'), 7.5); near(M.americanToDecimal('EVEN'), 2);
assert.strictEqual(M.americanToDecimal('abc'), null); assert.strictEqual(M.americanToDecimal(null), null);
// devig : somme 1, marge correcte
const d = M.devig([1.85, 3.8, 4.2]); near(d.p.reduce((a, b) => a + b, 0), 1); near(d.margin, 1 / 1.85 + 1 / 3.8 + 1 / 4.2 - 1);
// football : somme des probas = 1, domicile plus fort => proba plus haute
const g = (f, a, n = 10) => Array.from({ length: n }, () => ({ f, a }));
const m1 = M.footballModel(g(2, 0.5), g(0.5, 2), 1.35); near(m1.p.reduce((a, b) => a + b, 0), 1);
assert(m1.p[0] > 0.6 && m1.p[2] < 0.15, 'favori domicile');
const m2 = M.footballModel(g(1.35, 1.35), g(1.35, 1.35), 1.35); assert(m2.p[0] > m2.p[2], 'avantage du terrain'); near(m2.lA, 1.35 * 1.08); near(m2.lB, 1.35 * 0.93);
const m3 = M.footballModel([], [], 0); assert(isFinite(m3.p[0]) && m3.base === 1.35, 'sans données');
assert(m1.o25 >= 0 && m1.o25 <= 1 && m1.btts >= 0 && m1.btts <= 1 && m1.top.length === 5);
// basket
const b1 = M.basketModel(g(120, 105), g(105, 120)); near(b1.p[0] + b1.p[1], 1); assert(b1.p[0] > 0.8 && b1.margin > 0);
const b2 = M.basketModel(g(110, 110), g(110, 110)); assert(b2.p[0] > 0.5 && b2.p[0] < 0.65, 'avantage du terrain NBA'); assert.strictEqual(M.basketModel([], g(1, 1)), null);
// mma
const x = M.mmaModel({ w: 20, l: 2, d: 0 }, { w: 5, l: 5, d: 0 }); near(x.p[0] + x.p[1], 1); assert(x.p[0] > 0.7 && x.p[0] < 0.9, 'MMA non surconfiant');
near(M.mmaModel({ w: 3, l: 3, d: 0 }, { w: 3, l: 3, d: 0 }).p[0], 0.5);
assert.deepStrictEqual(M.parseRecord('7-4-0'), { w: 7, l: 4, d: 0 }); assert.deepStrictEqual(M.parseRecord(''), { w: 0, l: 0, d: 0 });
near(M.entropyNorm([1 / 3, 1 / 3, 1 / 3]), 1); near(M.phi(0), 0.5, 1e-4);
console.log('Tous les tests de modèles passent');
