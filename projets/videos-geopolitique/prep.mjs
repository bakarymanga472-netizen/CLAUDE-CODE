import fs from 'fs';
import {geoAzimuthalEqualArea, geoPath, geoInterpolate, geoCentroid} from 'd3-geo';
const W = 1080, H = 1160;
const geo = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const cadre = {type: 'MultiPoint', coordinates: [[-18, -35], [52, -35], [52, 37], [-18, 37], [37.6, 56.5], [-10, 50]]};
const proj = geoAzimuthalEqualArea().rotate([-18, -12]).fitExtent([[30, 10], [W - 30, H - 10]], cadre);
const path = geoPath(proj);
const pays = geo.features.filter(f => {
  const c = geoCentroid(f); return f.properties.ADM0_A3 === 'RUS' || (c[0] > -40 && c[0] < 75 && c[1] > -45 && c[1] < 72);
}).map(f => {
  const p = f.properties; const c = proj(geoCentroid(f));
  return {iso: p.ADM0_A3, nom: p.NAME_FR || p.NAME, afrique: p.CONTINENT === 'Africa', d: path(f), c: c.map(v => Math.round(v))};
}).filter(p => p.d);
const villes = {Moscou: [37.62, 55.75], Bamako: [-8.0, 12.64], Ouagadougou: [-1.52, 12.37], Niamey: [2.11, 13.51], Bangui: [18.56, 4.36],
  Benghazi: [20.07, 32.12], 'Le Caire': [31.24, 30.04], Alger: [3.06, 36.75], Dakar: [-17.44, 14.69], Abuja: [7.49, 9.06],
  Kinshasa: [15.27, -4.44], Luanda: [13.23, -8.84], Nairobi: [36.82, -1.29], 'Addis-Abeba': [38.75, 9.03], Pretoria: [28.19, -25.75],
  Khartoum: [32.56, 15.5], Rabat: [-6.84, 34.02], Antananarivo: [47.52, -18.88], Harare: [31.05, -17.83], Conakry: [-13.68, 9.64]};
const pts = Object.fromEntries(Object.entries(villes).map(([k, v]) => [k, proj(v).map(x => Math.round(x))]));
const arcs = {};
for (const [k, v] of Object.entries(villes)) {
  if (k === 'Moscou') continue;
  const it = geoInterpolate(villes.Moscou, v);
  const p = Array.from({length: 49}, (_, i) => proj(it(i / 48)));
  // léger bombé pour un effet « trajectoire »
  const [x0, y0] = p[0], [x1, y1] = p[48]; const nx = -(y1 - y0), ny = x1 - x0; const n = Math.hypot(nx, ny) || 1;
  arcs[k] = 'M' + p.map(([x, y], i) => { const b = Math.sin(Math.PI * i / 48) * 60; return `${(x + nx / n * b).toFixed(1)},${(y + ny / n * b).toFixed(1)}`; }).join('L');
}
fs.writeFileSync(process.argv[3], JSON.stringify({W, H, pays, villes: pts, arcs}));
console.log(pays.length, 'pays dans le cadre,', pays.filter(p => p.afrique).length, 'africains; Moscou', pts.Moscou, 'Pretoria', pts.Pretoria);
