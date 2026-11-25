import React, {useEffect, useState} from 'react';
import {AbsoluteFill, continueRender, delayRender, Easing, Img, interpolate, interpolateColors, random, Sequence, spring, staticFile, useCurrentFrame} from 'remotion';
import {Audio} from '@remotion/media';
import {geoAzimuthalEqualArea, geoInterpolate, geoNaturalEarth1, geoPath} from 'd3-geo';
import monde from './monde.json';
import carteAf from './afrique-carte.json';
import phrases from './phrases-afrique.json';
import mots from './mots-afrique.json';
import evts from './evts-afrique.json';

// ─── Réglages ────────────────────────────────────────────────────────────────
const FPS = 30;
const AMBRE = '#F5B43A';
const ROUGE = '#E5383B';
const PAPIER = '#ECE6D6';
const OSW = 'Oswald, Impact, sans-serif';
const MONO = '"Courier Prime", "Courier New", monospace';
const INTER = 'Inter, Arial, sans-serif';
const MAIN = 'Caveat, cursive';
const SERIF = '"DejaVu Serif", Georgia, serif';
const c = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const fr = (s: number) => Math.round(s * FPS);
const PANNEAU = {x: 40, y: 500, w: 1000, h: 640};
const EV = evts as Record<string, number | number[]>;
const evS = (n: string) => (typeof EV[n] === 'number' ? (EV[n] as number) : 0);
const PH = phrases as {texte: string; debut: number; fin: number}[];
export const DUREE_AFRIQUE = fr(PH[PH.length - 1].fin + 1.6);

// ─── Polices (fichiers libres dans public/fonts) ─────────────────────────────
const POLICES: [string, string, FontFaceDescriptors][] = [
  ['Oswald', 'fonts/Oswald.ttf', {weight: '200 700'}],
  ['Courier Prime', 'fonts/CourierPrime.ttf', {weight: '400'}],
  ['Courier Prime', 'fonts/CourierPrime-Bold.ttf', {weight: '700'}],
  ['Caveat', 'fonts/Caveat.ttf', {weight: '400 700'}],
];
let chargement: Promise<void> | null = null;
const chargerPolices = () =>
  (chargement ??= Promise.all(
    POLICES.map(([f, u, d]) => new FontFace(f, `url(${staticFile(u)})`, d).load().then((x) => {
      document.fonts.add(x);
    })),
  ).then(() => undefined));

// ─── Briques ─────────────────────────────────────────────────────────────────
const Etiquette: React.FC<{t: number; texte: string; fond?: string; couleur?: string; taille?: number; style?: React.CSSProperties}> = ({t, texte, fond = ROUGE, couleur = '#fff', taille = 40, style}) => {
  if (t < 0) return null;
  const p = interpolate(t, [0, 9], [0, 100], {...c, easing: Easing.out(Easing.cubic)});
  return (
    <div style={{position: 'absolute', ...style, background: fond, color: couleur, fontFamily: OSW, fontWeight: 600, fontSize: taille, letterSpacing: 1,
      textTransform: 'uppercase', padding: `${taille * 0.1}px ${taille * 0.32}px`, lineHeight: 1.18, clipPath: `inset(0 ${100 - p}% 0 0)`, whiteSpace: 'nowrap'}}>
      {texte}
    </div>
  );
};

const Tampon: React.FC<{t: number; texte: string; couleur?: string; taille?: number; angle?: number; style?: React.CSSProperties}> = ({t, texte, couleur = ROUGE, taille = 64, angle = -12, style}) => {
  if (t < 0) return null;
  const s = interpolate(t, [0, 5], [2.6, 1], {...c, easing: Easing.in(Easing.quad)});
  const o = interpolate(t, [0, 3], [0, 0.9], c);
  return (
    <div style={{position: 'absolute', ...style, transform: `rotate(${angle}deg) scale(${s})`, border: `${taille * 0.09}px solid ${couleur}`, color: couleur,
      fontFamily: OSW, fontWeight: 700, fontSize: taille, padding: `0 ${taille * 0.28}px`, letterSpacing: 4, borderRadius: 10, opacity: o, whiteSpace: 'nowrap',
      textTransform: 'uppercase', lineHeight: 1.2, maskImage: 'repeating-linear-gradient(115deg, #000 0 7px, rgba(0,0,0,0.72) 7px 9px)'}}>
      {texte}
    </div>
  );
};

const Silhouette: React.FC<{w: number; couleur?: string}> = ({w, couleur = '#2a303c'}) => (
  <svg width={w} height={w} viewBox="0 0 100 100">
    <circle cx={50} cy={38} r={19} fill={couleur} />
    <path d="M12 100 Q14 64 50 62 Q86 64 88 100 Z" fill={couleur} />
  </svg>
);

// Vraie photo (licence libre) façon tirage papier, avec léger zoom et crédit lisible
const Photo: React.FC<{t: number; src: string; credit: string; legende?: string; w: number; h: number; style: React.CSSProperties; angle?: number; nb?: boolean}> = ({t, src, credit, legende, w, h, style, angle = -2, nb}) => {
  if (t < 0) return null;
  const s = spring({frame: t, fps: FPS, config: {damping: 14}});
  return (
    <div style={{position: 'absolute', ...style, width: w, transform: `rotate(${angle}deg) scale(${0.7 + 0.3 * s})`, opacity: s, background: '#f2efe6', padding: 10, boxSizing: 'border-box', boxShadow: '0 25px 50px rgba(0,0,0,0.6)'}}>
      <div style={{width: w - 20, height: h, overflow: 'hidden'}}>
        <Img src={staticFile(src)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${1.04 + t * 0.0012})`, filter: nb ? 'grayscale(1) contrast(1.1)' : 'contrast(1.05) saturate(0.9)'}} />
      </div>
      {legende ? <div style={{fontFamily: MONO, fontWeight: 700, fontSize: 19, color: '#222', marginTop: 7}}>{legende}</div> : null}
      <div style={{fontFamily: INTER, fontSize: 14, color: '#555', marginTop: 3}}>{credit}</div>
    </div>
  );
};

const flashA = (t: number, b: number) => interpolate(t - b, [0, 1, 9], [0, 1, 0], c);
const tremble = (t: number, b: number, force: number, graine: string) => {
  const d = t - b;
  if (d < 0 || d > 16) return 0;
  return (random(`${graine}${Math.floor(t)}`) - 0.5) * force * (1 - d / 16);
};

// ─── Carte de l'Afrique (Natural Earth) ──────────────────────────────────────
const AF = carteAf as {afrique: string[]; droites: number[][][]; empire: Record<string, string>; indep1960: string[]};
const FEATS = (monde as any).features as any[];
const FEAT_AF = FEATS.filter((f) => AF.afrique.includes(f.properties.a3));
const COLL_AF = {type: 'FeatureCollection', features: FEAT_AF} as any;
const projAf = () => geoAzimuthalEqualArea().rotate([-18, -2]).fitExtent([[40, 24], [560, 616]], COLL_AF).clipExtent([[-50, -50], [1050, 690]]);
const COULEUR_EMPIRE: Record<string, string> = {France: '#4a7bd8', 'Royaume-Uni': '#e2567a', Allemagne: '#d9a13a', Belgique: '#9b6bd1', Portugal: '#2fb37a', Italie: '#2bb3c0', Espagne: '#e67e22', 'Indépendant': '#f2f2f2'};
const VERT = '#2fb344';

const CarteAfrique: React.FC<{t: number; trace?: number; fond?: (a3: string) => string; droites?: number; zoom?: {x: number; y: number; s: number}; extra?: (p: any) => React.ReactNode; voisins?: boolean}> = ({t, trace = 1, fond, droites = 0, zoom, extra, voisins = true}) => {
  const proj = projAf();
  const path = geoPath(proj);
  const tr = zoom ? `translate(${300 - zoom.x * zoom.s + zoom.x * 0},0)` : '';
  const g = zoom ? `translate(300 320) scale(${zoom.s}) translate(${-zoom.x} ${-zoom.y})` : '';
  return (
    <svg width={1000} height={640} style={{position: 'absolute'}}>
      <defs>
        <radialGradient id="merAf" cx="35%" cy="45%"><stop offset="0" stopColor="#101b33" /><stop offset="1" stopColor="#05080f" /></radialGradient>
      </defs>
      <rect width={1000} height={640} fill="url(#merAf)" />
      <g transform={g || tr}>
        {voisins ? FEATS.filter((f) => !AF.afrique.includes(f.properties.a3)).map((f, i) => (
          <path key={'v' + i} d={path(f) ?? ''} fill="#141b2c" stroke="#26314a" strokeWidth={0.8} vectorEffect="non-scaling-stroke" />
        )) : null}
        {FEAT_AF.map((f, i) => (
          <path key={i} d={path(f) ?? ''} fill={fond ? fond(f.properties.a3) : '#22304f'} fillOpacity={interpolate(trace, [0.6, 1], [0, 1], c)}
            stroke="#8fa6d8" strokeWidth={1.1} vectorEffect="non-scaling-stroke" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - trace} />
        ))}
        {AF.droites.map((d, i) => {
          const p = interpolate(droites * AF.droites.length - i * 0.6, [0, 1], [0, 1], c);
          if (p <= 0) return null;
          const a = proj(d[0] as [number, number]) as [number, number];
          const b = proj(d[1] as [number, number]) as [number, number];
          return <line key={'d' + i} x1={a[0]} y1={a[1]} x2={a[0] + (b[0] - a[0]) * p} y2={a[1] + (b[1] - a[1]) * p} stroke={AMBRE} strokeWidth={5} strokeLinecap="round" vectorEffect="non-scaling-stroke"
            style={{filter: `drop-shadow(0 0 ${4 + 3 * Math.sin(t / 5)}px ${AMBRE})`}} />;
        })}
        {extra ? extra(proj) : null}
      </g>
    </svg>
  );
};

const Compteur: React.FC<{t: number; de: number; a: number; duree?: number; format?: (v: number) => string}> = ({t, de, a, duree = 40, format}) => {
  const v = interpolate(t, [0, duree], [de, a], {...c, easing: Easing.out(Easing.cubic)});
  return <>{format ? format(v) : Math.round(v).toLocaleString('fr-FR')}</>;
};

const Jauge: React.FC<{t: number; valeur: number; texte: string; couleur?: string}> = ({t, valeur, texte, couleur = AMBRE}) => {
  const p = interpolate(t, [0, 30], [0, valeur / 100], {...c, easing: Easing.out(Easing.cubic)});
  return (
    <div style={{position: 'relative', width: 260, height: 260, opacity: t < 0 ? 0 : 1}}>
      <svg width={260} height={260} viewBox="0 0 260 260">
        <circle cx={130} cy={130} r={105} stroke="rgba(255,255,255,0.12)" strokeWidth={26} fill="none" />
        <circle cx={130} cy={130} r={105} stroke={couleur} strokeWidth={26} fill="none" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p} transform="rotate(-90 130 130)" />
      </svg>
      <div style={{position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'}}>
        <div style={{fontFamily: OSW, fontWeight: 700, fontSize: 84, color: '#fff', lineHeight: 1}}>{Math.round(p * 100)} %</div>
        <div style={{fontFamily: INTER, fontWeight: 700, fontSize: 20, color: '#b9c0cc', marginTop: 6, textAlign: 'center', width: 170}}>{texte}</div>
      </div>
    </div>
  );
};

// ─── Scènes ──────────────────────────────────────────────────────────────────
type Sc = {t: number; dur: number; ev: (n: string) => number; m: number[]};

const Frontieres: React.FC<Sc> = ({t, ev, m}) => {
  const trace = interpolate(t, [0, 36], [0, 1], {...c, easing: Easing.inOut(Easing.cubic)});
  const droites = interpolate(t, [ev('droites') - 4, ev('droites') + 40], [0, 1], c);
  const q = spring({frame: t - m[2], fps: FPS, config: {damping: 9}});
  return (
    <AbsoluteFill>
      <CarteAfrique t={t} trace={trace} droites={droites} />
      <Etiquette t={t - ev('droites') - 6} texte="Plus d'1/3 des frontières" taille={28} style={{left: 585, top: 150}} />
      <Etiquette t={t - ev('droites') - 12} texte="= des lignes droites" fond={AMBRE} couleur="#111" taille={34} style={{left: 585, top: 196}} />
      <Etiquette t={t - ev('droites') - 18} texte="Étude APSR 2024 : 37 %" fond="rgba(0,0,0,0.8)" taille={22} style={{left: 585, top: 252}} />
      {t >= m[2] ? <div style={{position: 'absolute', left: 690, top: 300, fontFamily: OSW, fontWeight: 700, fontSize: 230, color: AMBRE, transform: `scale(${q})`, lineHeight: 1}}>?</div> : null}
      <Etiquette t={t - ev('qui')} texte="Qui ? Pourquoi ?" taille={40} style={{left: 585, top: 560}} />
    </AbsoluteFill>
  );
};

const PTS: Record<string, [number, number]> = {
  Senegambie: [-16.5, 13.5], Benin: [2.4, 6.4], Luanda: [13.2, -8.8], Elmina: [-1.35, 5.1],
  Caraibes: [-72, 19], Salvador: [-38.5, -12.97], Rio: [-43.2, -22.9], Jamaique: [-77.3, 18.1], Charleston: [-79.9, 32.8],
  Tombouctou: [-3, 16.77], Marrakech: [-8, 31.6], Kano: [8.5, 12], Tripoli: [13.2, 32.9], Darfour: [24.9, 13.6], LeCaire: [31.2, 30],
  Zanzibar: [39.2, -6.16], Mascate: [58.4, 23.6], Kilwa: [39.5, -8.9], Aden: [45, 12.8],
};
const ROUTES_ATL: [string, string][] = [['Benin', 'Salvador'], ['Luanda', 'Rio'], ['Senegambie', 'Caraibes'], ['Elmina', 'Jamaique'], ['Benin', 'Charleston']];
const ROUTES_AUTRES: [string, string][] = [['Tombouctou', 'Marrakech'], ['Kano', 'Tripoli'], ['Darfour', 'LeCaire'], ['Zanzibar', 'Mascate'], ['Kilwa', 'Aden']];

const Traite: React.FC<Sc> = ({t, ev, m}) => {
  const zone = {type: 'Feature', geometry: {type: 'Polygon', coordinates: [[[-100, -40], [62, -40], [62, 50], [-100, 50], [-100, -40]]]}} as any;
  const proj = geoNaturalEarth1().fitExtent([[10, 10], [990, 630]], zone);
  const path = geoPath(proj);
  const route = (a: string, b: string, p: number) => {
    const it = geoInterpolate(PTS[a], PTS[b]);
    return {type: 'LineString', coordinates: Array.from({length: 33}, (_, i) => it((i / 32) * p))} as any;
  };
  const tA = t - m[1];
  const tO = t - m[3];
  return (
    <AbsoluteFill style={{background: '#05080f'}}>
      <svg width={1000} height={640} style={{position: 'absolute'}}>
        <path d={path({type: 'Sphere'} as any) ?? ''} fill="#08101f" />
        {FEATS.map((f, i) => (
          <path key={i} d={path(f) ?? ''} fill={AF.afrique.includes(f.properties.a3) ? '#2a3a60' : '#151d30'} stroke="#34466e" strokeWidth={0.6} />
        ))}
        {ROUTES_ATL.map(([a, b], i) => {
          const p = interpolate(tA - i * 8, [0, 34], [0, 1], {...c, easing: Easing.inOut(Easing.quad)});
          if (p <= 0) return null;
          const fin = proj(geoInterpolate(PTS[a], PTS[b])(p)) as [number, number];
          return (
            <g key={i}>
              <path d={path(route(a, b, p)) ?? ''} fill="none" stroke={ROUGE} strokeWidth={3.5} strokeLinecap="round" opacity={0.9} />
              <circle cx={fin[0]} cy={fin[1]} r={6} fill="#fff" />
            </g>
          );
        })}
        {ROUTES_AUTRES.map(([a, b], i) => {
          const p = interpolate(tO - i * 6, [0, 26], [0, 1], c);
          if (p <= 0) return null;
          return <path key={'o' + i} d={path(route(a, b, p)) ?? ''} fill="none" stroke="#b07cf0" strokeWidth={3} strokeDasharray="8 7" />;
        })}
      </svg>
      <Etiquette t={t - 4} texte="XVIᵉ siècle" taille={56} style={{left: 30, top: 24}} />
      {tA >= 0 ? (
        <div style={{position: 'absolute', right: 28, top: 26, textAlign: 'right'}}>
          <div style={{fontFamily: OSW, fontWeight: 700, fontSize: 76, color: '#fff', lineHeight: 1}}><Compteur t={t - ev('millions') + 6} de={0} a={12500000} duree={45} /></div>
          <div style={{fontFamily: INTER, fontWeight: 700, fontSize: 24, color: '#d5d8de'}}>Africains déportés (1501-1866)</div>
          <div style={{fontFamily: INTER, fontSize: 18, color: '#8a8f98'}}>Estimation SlaveVoyages</div>
        </div>
      ) : null}
      {t >= m[2] ? (
        <div style={{position: 'absolute', right: 28, top: 170, textAlign: 'right'}}>
          <div style={{fontFamily: OSW, fontWeight: 700, fontSize: 60, color: ROUGE, lineHeight: 1}}>≈ <Compteur t={t - m[2]} de={0} a={1800000} duree={35} /></div>
          <div style={{fontFamily: INTER, fontWeight: 700, fontSize: 24, color: '#d5d8de'}}>morts pendant la traversée</div>
        </div>
      ) : null}
      <Photo t={t - m[2] - 6} src="photos-afrique/stowage-british-slave-ship-brookes.jpg" w={300} h={170} angle={-3} style={{left: 650, top: 360}}
        legende="Le navire négrier Brookes, 1788" credit="Plan d'époque · CC0 (rawpixel)" />
      <Etiquette t={tO - 4} texte="Traite transsaharienne" fond="#7d4fd0" taille={26} style={{left: 30, top: 524}} />
      <Etiquette t={tO - 14} texte="Traite de l'océan Indien" fond="#7d4fd0" taille={26} style={{left: 30, top: 568}} />
    </AbsoluteFill>
  );
};

const Abolition: React.FC<Sc> = ({t, ev, m}) => {
  const fleches: [[number, number], [number, number]][] = [[[-16, 14], [-4, 13]], [[3, 6.3], [7, 11]], [[12, -6], [20, -3]], [[39.3, -6.5], [32, -3]], [[18.4, -33.9], [25, -26]], [[31.3, 30], [31, 20]]];
  const pF = interpolate(t, [10, 50], [0, 1], {...c, easing: Easing.inOut(Easing.cubic)});
  return (
    <AbsoluteFill>
      <CarteAfrique t={t} extra={(proj) => fleches.map(([a, b], i) => {
        const A = proj(a) as [number, number];
        const B = proj(b) as [number, number];
        const x = A[0] + (B[0] - A[0]) * pF, y = A[1] + (B[1] - A[1]) * pF;
        const ang = (Math.atan2(B[1] - A[1], B[0] - A[0]) * 180) / Math.PI;
        return (
          <g key={i} opacity={pF > 0 ? 1 : 0}>
            <line x1={A[0]} y1={A[1]} x2={x} y2={y} stroke={AMBRE} strokeWidth={5} strokeLinecap="round" />
            <polygon points="0,-9 16,0 0,9" fill={AMBRE} transform={`translate(${x} ${y}) rotate(${ang})`} />
          </g>
        );
      })} />
      <Etiquette t={t - 4} texte="XIXᵉ siècle" taille={50} style={{left: 600, top: 40}} />
      <Etiquette t={t - ev('abolit')} texte="Fin de la traite" fond="rgba(0,0,0,0.85)" taille={32} style={{left: 600, top: 108}} />
      <Etiquette t={t - ev('interieur')} texte="Cap sur l'intérieur" fond={AMBRE} couleur="#111" taille={32} style={{left: 600, top: 160}} />
      <Etiquette t={t - ev('esclavage')} texte="Prétexte : « lutter" fond={ROUGE} taille={28} style={{left: 600, top: 214}} />
      <Etiquette t={t - ev('esclavage') - 5} texte="contre l'esclavage »" fond={ROUGE} taille={28} style={{left: 600, top: 256}} />
      <div style={{position: 'absolute', left: 650, top: 318}}><Jauge t={t - m[1]} valeur={10} texte="de l'Afrique contrôlée par l'Europe en 1870" /></div>
    </AbsoluteFill>
  );
};

const Berlin: React.FC<Sc> = ({t, ev, m}) => {
  const zoom = 1.05 + t * 0.0008;
  const tM = t - m[2];
  const barre = interpolate(tM, [8, 20], [0, 100], c);
  return (
    <AbsoluteFill style={{background: '#0a0a0c'}}>
      <Img src={staticFile('photos-afrique/kongokonferenz-jpg.jpg')} style={{position: 'absolute', width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${zoom})`,
        filter: `sepia(0.5) brightness(${t < m[2] ? 0.8 : 0.35})`}} />
      <div style={{position: 'absolute', left: 14, bottom: 8, fontFamily: INTER, fontSize: 14, color: '#bbb'}}>Conférence de Berlin, gravure d'Adalbert von Rößler, 1884 · domaine public</div>
      <Etiquette t={t - 6} texte="Berlin · 15 nov. 1884" taille={44} style={{left: 30, top: 24}} />
      <Etiquette t={t - ev('berlin')} texte="14 pays" fond={AMBRE} couleur="#111" taille={44} style={{left: 30, top: 92}} />
      {t < m[2] ? <Photo t={t - ev('bismarck')} src="photos-afrique/bundesarchiv-bild-146-2005-0057-otto-von-bismarck.jpg" w={210} h={250} angle={3} style={{left: 760, top: 30}}
        legende="Otto von Bismarck, 1890" credit="Photo : J. Pilartz · domaine public" nb /> : null}
      {t < m[2] ? <Tampon t={t - ev('aucun')} texte="Aucun Africain" taille={70} angle={-8} style={{left: 250, top: 270}} /> : null}
      {tM >= 0 ? (
        <>
          <Photo t={tM} src="photos-afrique/cartoon-depicting-leopold-2-and-other-emperial-pow.jpg" w={230} h={250} angle={-3} style={{left: 40, top: 200}}
            legende="Caricature française, 1884" credit="F. Maréchal · domaine public" nb />
          <div style={{position: 'absolute', left: 320, top: 210, width: 640}}>
            <Etiquette t={tM - 2} texte="Idée reçue" fond="rgba(0,0,0,0.85)" taille={30} style={{position: 'relative'}} />
            <div style={{position: 'relative', marginTop: 10, fontFamily: OSW, fontWeight: 600, fontSize: 46, color: '#fff', opacity: interpolate(tM, [4, 10], [0, 1], c)}}>
              « Berlin a découpé l'Afrique »
              <div style={{position: 'absolute', left: 0, top: '52%', height: 6, width: `${barre}%`, background: ROUGE}} />
            </div>
            <Etiquette t={t - ev('regles')} texte="En réalité : les règles du partage" fond={AMBRE} couleur="#111" taille={36} style={{position: 'relative', marginTop: 16}} />
            <Etiquette t={t - m[3]} texte="Règle : occuper le terrain" fond={ROUGE} taille={36} style={{position: 'relative', marginTop: 12}} />
          </div>
        </>
      ) : null}
    </AbsoluteFill>
  );
};

const Partage: React.FC<Sc> = ({t, ev, m}) => {
  const ordre = (a3: string) => random(`o${a3}`);
  const p = interpolate(t, [m[0] + 10, m[1] + 10], [0, 1], c);
  const fond = (a3: string) => {
    const e = AF.empire[a3];
    if (e === 'Indépendant') return t >= m[2] ? interpolateColors(Math.sin(t / 4), [-1, 1], ['#2fb344', '#f2f2f2']) : '#22304f';
    return ordre(a3) < p ? COULEUR_EMPIRE[e] : '#22304f';
  };
  const legende = Object.keys(COULEUR_EMPIRE);
  return (
    <AbsoluteFill>
      <CarteAfrique t={t} fond={fond} extra={(proj) => t >= m[2] ? [['Éthiopie', [39.5, 8.5]], ['Libéria', [-9.4, 6.4]]].map(([n, ll]) => {
        const [x, y] = proj(ll as [number, number]) as [number, number];
        return <text key={n as string} x={x} y={y + 6} textAnchor="middle" fill="#111" stroke="#fff" strokeWidth={5} paintOrder="stroke" fontFamily={OSW} fontWeight={700} fontSize={26}>{n}</text>;
      }) : null} />
      {t < m[1] ? <Photo t={t - 4} src="photos-afrique/punch-rhodes-colossus-png.png" w={300} h={330} angle={3} style={{left: 640, top: 40}}
        legende="« The Rhodes Colossus », 1892" credit="E. L. Sambourne, Punch · domaine public" nb /> : null}
      <Etiquette t={t - ev('course')} texte="La course aux colonies" taille={34} style={{left: 600, top: 470}} />
      {t >= m[1] ? (
        <>
          <div style={{position: 'absolute', left: 630, top: 20}}><Jauge t={t - m[1]} valeur={90} texte="de l'Afrique contrôlée en 1914" couleur={ROUGE} /></div>
          <div style={{position: 'absolute', left: 600, top: 300, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 18px', opacity: interpolate(t - m[1], [6, 16], [0, 1], c)}}>
            {legende.map((e) => (
              <div key={e} style={{display: 'flex', alignItems: 'center', gap: 8, fontFamily: INTER, fontWeight: 700, fontSize: 21, color: '#e6e8ec'}}>
                <div style={{width: 20, height: 20, borderRadius: 4, background: COULEUR_EMPIRE[e]}} />{e}
              </div>
            ))}
          </div>
          <div style={{position: 'absolute', left: 600, top: 440, fontFamily: INTER, fontSize: 16, color: '#8a8f98'}}>1914, simplifié, sur les frontières actuelles</div>
        </>
      ) : null}
    </AbsoluteFill>
  );
};

const SOMALIS: [number, number][] = [[42.4, 12.4], [43.6, 11.4], [51.3, 11.9], [51, 10.2], [48, 4.6], [41.6, -1.7], [39.6, -0.6], [39.7, 2.8], [41, 3.9], [42.2, 4.6], [43.9, 5], [44.3, 6.6], [42.8, 8], [41.9, 9.6], [42.1, 11.2], [42.4, 12.4]];
const Peuples: React.FC<Sc> = ({t, ev, m}) => {
  const z = interpolate(t, [m[1] - 4, m[1] + 26], [0, 1], {...c, easing: Easing.inOut(Easing.cubic)});
  const corne = projAf()([44.5, 6.5]) as [number, number];
  const zoom = {x: 300 + (corne[0] - 300) * z, y: 320 + (corne[1] - 320) * z, s: 1 + 2.4 * z};
  const pays = ['SOM', 'SOL', 'ETH', 'KEN', 'DJI'];
  return (
    <AbsoluteFill>
      <CarteAfrique t={t} droites={t < m[1] ? 1 : 0} zoom={zoom} fond={(a3) => (z > 0.3 && pays.includes(a3) ? '#2c3f6e' : '#22304f')}
        extra={(proj) => (
          <g opacity={interpolate(z, [0.6, 1], [0, 1], c)}>
            <path d={geoPath(proj)({type: 'Polygon', coordinates: [SOMALIS]} as any) ?? ''} fill={AMBRE} fillOpacity={0.35} stroke={AMBRE} strokeWidth={3} strokeDasharray="6 5" vectorEffect="non-scaling-stroke" />
            {[['SOMALIE', [46.5, 5.5]], ['ÉTHIOPIE', [39.5, 9]], ['KENYA', [37.8, 0.6]], ['DJIBOUTI', [42.6, 11.7]]].map(([n, ll]) => {
              const [x, y] = proj(ll as [number, number]) as [number, number];
              return <text key={n as string} x={x} y={y} textAnchor="middle" fill="#fff" stroke="#000" strokeWidth={2.5 / zoom.s} paintOrder="stroke" fontFamily={OSW} fontWeight={700} fontSize={22 / zoom.s}>{n}</text>;
            })}
          </g>
        )} />
      {t < m[1] ? (
        <>
          <Etiquette t={t - ev('regle')} texte="À la règle" fond={AMBRE} couleur="#111" taille={32} style={{left: 590, top: 80}} />
          <Etiquette t={t - ev('fleuves')} texte="Le long des fleuves" fond="#2b6fd0" taille={32} style={{left: 590, top: 134}} />
          <Etiquette t={t - ev('royaumes')} texte="D'anciens royaumes" fond="#2fb37a" taille={32} style={{left: 590, top: 188}} />
          <Etiquette t={t - ev('royaumes') - 4} texte="africains" fond="#2fb37a" taille={32} style={{left: 590, top: 236}} />
          <Etiquette t={t - ev('royaumes') - 10} texte="62 % des frontières influencées" fond="rgba(0,0,0,0.85)" taille={21} style={{left: 590, top: 300}} />
          <Etiquette t={t - ev('royaumes') - 14} texte="par d'anciens États africains" fond="rgba(0,0,0,0.85)" taille={21} style={{left: 590, top: 332}} />
          <Etiquette t={t - ev('royaumes') - 18} texte="(étude APSR 2024)" fond="rgba(0,0,0,0.85)" taille={21} style={{left: 590, top: 364}} />
        </>
      ) : (
        <>
          <Etiquette t={t - ev('somalis')} texte="Les Somalis" taille={46} style={{left: 640, top: 60}} />
          <Etiquette t={t - ev('quatre')} texte="Répartis entre 4 pays" fond={AMBRE} couleur="#111" taille={34} style={{left: 640, top: 130}} />
          <div style={{position: 'absolute', left: 640, top: 190, fontFamily: INTER, fontSize: 16, color: '#8a8f98', opacity: z}}>Zone de peuplement : tracé approximatif</div>
        </>
      )}
    </AbsoluteFill>
  );
};

const Independances: React.FC<Sc> = ({t}) => {
  const p = interpolate(t, [10, 60], [0, 1], c);
  const ordre = AF.indep1960;
  const allume = (a3: string) => ordre.indexOf(a3) >= 0 && ordre.indexOf(a3) / ordre.length < p;
  return (
    <AbsoluteFill>
      <CarteAfrique t={t} fond={(a3) => (allume(a3) ? VERT : '#22304f')} />
      <div style={{position: 'absolute', left: 600, top: 30}}>
        <div style={{fontFamily: OSW, fontWeight: 700, fontSize: 130, color: VERT, lineHeight: 1}}><Compteur t={t - 10} de={0} a={17} duree={50} /></div>
        <div style={{fontFamily: INTER, fontWeight: 800, fontSize: 28, color: '#fff'}}>pays indépendants en 1960</div>
        <div style={{fontFamily: INTER, fontSize: 21, color: '#b9c0cc', marginTop: 4}}>dont 14 anciennes colonies françaises</div>
      </div>
      <Photo t={t - 20} src="photos-afrique/patrice-lumumba-1960-jpg.jpg" w={230} h={290} angle={3} style={{left: 700, top: 250}}
        legende="Patrice Lumumba, 1960" credit="Anefo / Nationaal Archief · CC0" nb />
      <Etiquette t={t - 6} texte="« L'année de l'Afrique »" fond={AMBRE} couleur="#111" taille={30} style={{left: 34, top: 24}} />
    </AbsoluteFill>
  );
};

const Caire: React.FC<Sc> = ({t, ev}) => {
  return (
    <AbsoluteFill style={{background: 'radial-gradient(circle at 30% 40%, #1d2233, #06070a 75%)'}}>
      <Photo t={t} src="photos-afrique/selassie-and-nasser-1963-jpg.jpg" w={420} h={390} angle={-2} style={{left: 50, top: 60}}
        legende="Hailé Sélassié et Gamal Abdel Nasser, 1963" credit="Photo non créditée · domaine public" nb />
      <Etiquette t={t - ev('caire')} texte="Le Caire · juillet 1964" taille={40} style={{left: 520, top: 70}} />
      <Etiquette t={t - ev('caire') - 8} texte="Organisation de l'unité africaine" fond="rgba(0,0,0,0.85)" taille={26} style={{left: 520, top: 134}} />
      <Tampon t={t - ev('garder')} texte="On garde" taille={64} angle={-8} style={{left: 560, top: 230}} />
      <Tampon t={t - ev('garder') - 6} texte="les frontières" taille={52} angle={-8} style={{left: 540, top: 320}} />
      <Etiquette t={t - ev('guerres')} texte="Objectif : éviter" fond={AMBRE} couleur="#111" taille={30} style={{left: 520, top: 450}} />
      <Etiquette t={t - ev('guerres') - 4} texte="des guerres sans fin" fond={AMBRE} couleur="#111" taille={30} style={{left: 520, top: 500}} />
    </AbsoluteFill>
  );
};

const Aujourdhui: React.FC<Sc> = ({t}) => (
  <AbsoluteFill>
    <CarteAfrique t={t} droites={interpolate(t, [0, 30], [0, 1], c)} fond={(a3) => interpolateColors(random(`c${a3}`), [0, 1], ['#22304f', '#3a5288'])} />
    <Etiquette t={t - 8} texte="Aujourd'hui" taille={50} style={{left: 610, top: 120}} />
    <Etiquette t={t - 16} texte="Les lignes coloniales" fond={AMBRE} couleur="#111" taille={30} style={{left: 610, top: 192}} />
    <Etiquette t={t - 22} texte="sont toujours là" fond={AMBRE} couleur="#111" taille={30} style={{left: 610, top: 242}} />
  </AbsoluteFill>
);

const Fin: React.FC<Sc> = ({t, ev}) => {
  const s = spring({frame: t, fps: FPS, config: {damping: 12}});
  const b = spring({frame: t - ev('abonne'), fps: FPS, config: {damping: 8}});
  return (
    <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 45%, #10251a, #050506 70%)', alignItems: 'center', justifyContent: 'center'}}>
      <div style={{fontSize: 110, transform: `scale(${s})`}}>💬</div>
      <div style={{marginTop: 10, transform: `scale(${s})`, background: AMBRE, color: '#111', fontFamily: OSW, fontWeight: 700, fontSize: 70, padding: '0 34px', lineHeight: 1.25}}>QUELLE FRONTIÈRE ?</div>
      <div style={{marginTop: 18, fontFamily: INTER, fontWeight: 700, fontSize: 34, color: '#d5d8de', opacity: interpolate(t, [8, 18], [0, 1], c)}}>Dis-le en commentaire</div>
      <div style={{marginTop: 34, transform: `scale(${b * (1 + 0.05 * Math.sin(t / 4))})`, background: '#fff', color: '#111', fontFamily: INTER, fontWeight: 900, fontSize: 38, padding: '14px 44px', borderRadius: 60}}>🔔 S'ABONNER</div>
    </AbsoluteFill>
  );
};

// ─── Découpage : quelles phrases pour quelle scène ────────────────────────────
const SCENES: {de: number; a: number; C: React.FC<Sc>; tag: string}[] = [
  {de: 0, a: 2, C: Frontieres, tag: 'Carte'},
  {de: 3, a: 6, C: Traite, tag: 'Carte'},
  {de: 7, a: 8, C: Abolition, tag: 'Carte'},
  {de: 9, a: 12, C: Berlin, tag: 'Archives'},
  {de: 13, a: 15, C: Partage, tag: 'Carte'},
  {de: 16, a: 17, C: Peuples, tag: 'Carte'},
  {de: 18, a: 18, C: Independances, tag: 'Carte'},
  {de: 19, a: 19, C: Caire, tag: 'Archives'},
  {de: 20, a: 20, C: Aujourdhui, tag: 'Carte'},
  {de: 21, a: 21, C: Fin, tag: 'À vous'},
];

const debutScene = (i: number) => (i === 0 ? 0 : fr(PH[SCENES[i].de].debut) - 6);

// ─── Sous-titres mot à mot ───────────────────────────────────────────────────
type Mot = {m: string; d: number; f: number; k: boolean};
const MOTS = mots as Mot[];
const BLOCS: {i0: number; i1: number}[] = (() => {
  const b: {i0: number; i1: number}[] = [];
  let i0 = 0;
  MOTS.forEach((w, i) => {
    const suivant = MOTS[i + 1];
    const coupe = !suivant || i - i0 + 1 >= 3 || /[.,:?!;]$/.test(w.m) || suivant.d - w.f > 0.35;
    if (coupe) {
      b.push({i0, i1: i});
      i0 = i + 1;
    }
  });
  return b;
})();

const SousTitres: React.FC = () => {
  const f = useCurrentFrame();
  const s = f / FPS;
  const bi = BLOCS.findIndex((b, k) => s >= MOTS[b.i0].d - 0.05 && (k === BLOCS.length - 1 ? s < MOTS[b.i1].f + 0.6 : s < MOTS[BLOCS[k + 1].i0].d - 0.05));
  if (bi < 0) return null;
  const b = BLOCS[bi];
  const t0 = fr(MOTS[b.i0].d - 0.05);
  const pop = spring({frame: f - t0, fps: FPS, config: {damping: 14, mass: 0.5}});
  return (
    <div style={{position: 'absolute', top: 1190, width: '100%', textAlign: 'center', transform: `scale(${0.85 + 0.15 * pop})`, padding: '0 50px', boxSizing: 'border-box'}}>
      {MOTS.slice(b.i0, b.i1 + 1).map((w, k) => {
        const actif = s >= w.d - 0.03;
        return (
          <span key={k} style={{fontFamily: INTER, fontWeight: 900, fontSize: 68, textTransform: 'uppercase', color: w.k ? AMBRE : '#fff', opacity: actif ? 1 : 0.4,
            margin: '0 10px', textShadow: '0 4px 18px rgba(0,0,0,0.9)', display: 'inline-block'}}>
            {w.m.replace(/[.,:;]+$/, '')}
          </span>
        );
      })}
    </div>
  );
};

// ─── Habillage ───────────────────────────────────────────────────────────────
const Poussiere: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill>
      {Array.from({length: 70}, (_, i) => {
        const x = (random(`px${i}`) * 1080 + f * (0.2 + random(`pv${i}`) * 0.5)) % 1080;
        const y = (random(`py${i}`) * 1920 - f * (0.3 + random(`pw${i}`) * 0.6) + 1920 * 4) % 1920;
        return <div key={i} style={{position: 'absolute', left: x, top: y, width: 3, height: 3, borderRadius: 2, background: '#c9a56a', opacity: 0.12 + 0.2 * random(`po${i}`)}} />;
      })}
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, transparent 45%, rgba(0,0,0,0.85) 100%)'}} />
    </AbsoluteFill>
  );
};

const Titre: React.FC = () => {
  const f = useCurrentFrame();
  const lignes = ['Qui a tracé les', "frontières de l'Afrique ? 🌍"];
  return (
    <div style={{position: 'absolute', top: 160, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
      {lignes.map((l, i) => {
        const s = spring({frame: f - i * 3, fps: FPS, config: {damping: 14}});
        return (
          <div key={l} style={{background: '#fff', color: '#111', fontFamily: INTER, fontWeight: 700, fontSize: 60, padding: '2px 26px', borderRadius: 16, marginTop: -4, transform: `scale(${s})`}}>{l}</div>
        );
      })}
    </div>
  );
};

const Entete: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <>
      <div style={{position: 'absolute', top: 440, left: 44, right: 44, display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 12}}>
          <div style={{width: 34, height: 34, borderRadius: 17, background: `radial-gradient(circle at 35% 35%, #ff6b5e, #9e1622)`, color: '#fff', fontFamily: OSW, fontWeight: 700, fontSize: 20, textAlign: 'center', lineHeight: '34px'}}>S</div>
          <div style={{fontFamily: INTER, fontWeight: 900, fontSize: 30, color: '#fff', letterSpacing: 1}}>SOUS SCELLÉS</div>
        </div>
        <div style={{fontFamily: MONO, fontSize: 24, color: AMBRE, letterSpacing: 3}}>DOSSIER Nº02 · HISTOIRE</div>
      </div>
      <div style={{position: 'absolute', top: 484, left: 44, width: 992, height: 4, background: 'rgba(255,255,255,0.1)'}}>
        <div style={{width: `${(f / DUREE_AFRIQUE) * 100}%`, height: '100%', background: AMBRE}} />
      </div>
    </>
  );
};

const Panneau: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <div style={{position: 'absolute', left: PANNEAU.x, top: PANNEAU.y + 10, width: PANNEAU.w, height: PANNEAU.h, borderRadius: 18, overflow: 'hidden', border: '2px solid rgba(255,255,255,0.12)', background: '#000',
      boxShadow: '0 0 80px rgba(229,56,59,0.12)'}}>
      {SCENES.map((sc, i) => {
        const de = debutScene(i);
        const a = i === SCENES.length - 1 ? DUREE_AFRIQUE : debutScene(i + 1);
        const m = Array.from({length: sc.a - sc.de + 1}, (_, k) => fr(PH[sc.de + k].debut) - de);
        const ev = (n: string) => fr(evS(n)) - de;
        const t = f - de;
        const glitch = t < 6 ? (random(`gl${i}${t}`) - 0.5) * 50 * (1 - t / 6) : 0;
        return (
          <Sequence key={i} from={de} durationInFrames={a - de}>
            <AbsoluteFill style={{opacity: interpolate(t, [0, 4], [0, 1], c), transform: `translateX(${glitch}px)`}}>
              <sc.C t={t} dur={a - de} ev={ev} m={m} />
              <div style={{position: 'absolute', right: 20, top: 16, fontFamily: MONO, fontSize: 20, color: ROUGE, letterSpacing: 3, textTransform: 'uppercase'}}>
                <span style={{opacity: Math.sin(f / 5) > 0 ? 1 : 0.25}}>●</span> {sc.tag}
              </div>
            </AbsoluteFill>
          </Sequence>
        );
      })}
      {[[0, 0], [1, 0], [0, 1], [1, 1]].map(([x, y], k) => (
        <div key={k} style={{position: 'absolute', [x ? 'right' : 'left']: 10, [y ? 'bottom' : 'top']: 10, width: 28, height: 28,
          [`border${y ? 'Bottom' : 'Top'}`]: `3px solid ${AMBRE}`, [`border${x ? 'Right' : 'Left'}`]: `3px solid ${AMBRE}`, opacity: 0.7} as React.CSSProperties} />
      ))}
    </div>
  );
};

export const Afrique: React.FC = () => {
  const [poignee] = useState(() => delayRender('polices'));
  useEffect(() => {
    chargerPolices().then(() => continueRender(poignee));
  }, [poignee]);
  return (
    <AbsoluteFill style={{background: '#050507'}}>
      <Poussiere />
      <Titre />
      <Entete />
      <Panneau />
      <SousTitres />
      <div style={{position: 'absolute', top: 1420, width: '100%', textAlign: 'center', fontFamily: INTER, fontSize: 22, color: '#7d828c'}}>
        Sources : Britannica · SlaveVoyages · APSR 2024 · OUA 1964 · Images : Wikimedia Commons
      </div>
      <Audio src={staticFile('afrique-mix.wav')} />
    </AbsoluteFill>
  );
};
