import React, {useEffect, useState} from 'react';
import {AbsoluteFill, continueRender, delayRender, Easing, Img, interpolate, random, Sequence, spring, staticFile, useCurrentFrame} from 'remotion';
import {Audio} from '@remotion/media';
import {geoDistance, geoGraticule10, geoInterpolate, geoOrthographic, geoPath} from 'd3-geo';
import monde from './monde.json';
import phrases from './phrases-enquete.json';
import mots from './mots-enquete.json';
import evts from './evts-enquete.json';

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
export const DUREE_ENQUETE = fr(PH[PH.length - 1].fin + 1.6);

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

// ─── Scènes (t = image locale, ev(n) = image locale d'un mot clé) ─────────────
type Sc = {t: number; dur: number; ev: (n: string) => number; m: number[]};

const Port: React.FC<Sc> = ({t, ev, m}) => {
  const b1 = ev('b1');
  const b2 = ev('b2');
  const sx = tremble(t, b1, 34, 'a') + tremble(t, b2, 40, 'b');
  const sy = tremble(t, b1, 24, 'c') + tremble(t, b2, 28, 'd');
  const zoom = interpolate(t, [0, m[2] + 120], [1, 1.1], c);
  const tilt = interpolate(t, [b1, b2 + 90], [0, 8], {...c, easing: Easing.out(Easing.quad)});
  const coule = interpolate(t, [b1, b2 + 120], [0, 46], {...c, easing: Easing.out(Easing.quad)});
  const houle = Math.sin(t / 17) * 3;
  const flash = Math.max(flashA(t, b1), flashA(t, b2));
  const immeubles = Array.from({length: 42}, (_, i) => {
    const w = 18 + random(`w${i}`) * 18;
    const h = 26 + random(`h${i}`) * 92;
    return {x: i * 25 - 12, w, h};
  });
  const explosion = (b: number, x: number, y: number, g: string) => {
    const d = t - b;
    if (d < 0) return null;
    const r = interpolate(d, [0, 6, 50], [0, 150, 70], c);
    const o = interpolate(d, [0, 3, 60], [0, 1, 0], c);
    return (
      <g>
        <circle cx={x} cy={y} r={r} fill="url(#feu)" opacity={o} />
        <ellipse cx={x} cy={y + 6} rx={interpolate(d, [0, 40], [10, 230], c)} ry={interpolate(d, [0, 40], [3, 34], c)} fill="none" stroke="#cfe0ff" strokeWidth={3} opacity={interpolate(d, [0, 40], [0.8, 0], c)} />
        {Array.from({length: 18}, (_, k) => {
          const a = -Math.PI / 2 + (random(`${g}a${k}`) - 0.5) * 1.6;
          const v = 6 + random(`${g}v${k}`) * 9;
          const px = x + Math.cos(a) * v * d;
          const py = y + Math.sin(a) * v * d + 0.32 * d * d;
          return py < y + 20 ? <circle key={k} cx={px} cy={py} r={2 + random(`${g}r${k}`) * 4} fill="#e8f0ff" opacity={interpolate(d, [0, 30], [0.9, 0], c)} /> : null;
        })}
      </g>
    );
  };
  return (
    <AbsoluteFill>
      <svg width={1000} height={640} viewBox="0 0 1000 640" style={{transform: `translate(${sx}px, ${sy}px) scale(${zoom})`, transformOrigin: '48% 58%'}}>
        <defs>
          <linearGradient id="ciel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#070b17" /><stop offset="1" stopColor="#1b2540" /></linearGradient>
          <linearGradient id="eau" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#0d1627" /><stop offset="1" stopColor="#03060c" /></linearGradient>
          <radialGradient id="lune"><stop offset="0" stopColor="#f4efd8" stopOpacity={0.55} /><stop offset="1" stopColor="#f4efd8" stopOpacity={0} /></radialGradient>
          <radialGradient id="feu"><stop offset="0" stopColor="#fff6d0" /><stop offset="0.35" stopColor="#ffb340" /><stop offset="0.7" stopColor="#ff5a1f" stopOpacity={0.6} /><stop offset="1" stopColor="#ff3d00" stopOpacity={0} /></radialGradient>
          <clipPath id="horsEau"><rect x={-100} y={-200} width={1200} height={560} /></clipPath>
        </defs>
        <rect width={1000} height={340} fill="url(#ciel)" />
        {Array.from({length: 45}, (_, i) => (
          <circle key={i} cx={random(`ex${i}`) * 1000} cy={random(`ey${i}`) * 240} r={0.8 + random(`er${i}`) * 1.3} fill="#dfe6ff" opacity={0.3 + 0.5 * Math.abs(Math.sin(t / 20 + i))} />
        ))}
        <circle cx={840} cy={92} r={95} fill="url(#lune)" />
        <circle cx={840} cy={92} r={30} fill="#efe9cf" />
        {immeubles.map((b, i) => (
          <g key={i}>
            <rect x={b.x} y={340 - b.h} width={b.w} height={b.h} fill="#0c1120" />
            {Array.from({length: 6}, (_, k) => (random(`f${i}-${k}`) > 0.55 ? <rect key={k} x={b.x + 4 + (k % 2) * 8} y={340 - b.h + 8 + Math.floor(k / 2) * 14} width={3} height={4} fill={AMBRE} opacity={0.75} /> : null))}
          </g>
        ))}
        <g fill="#0c1120">
          <polygon points="262,340 280,340 274,196 268,196" />
          <ellipse cx={271} cy={188} rx={20} ry={10} />
          <ellipse cx={271} cy={176} rx={13} ry={5} />
          <rect x={269.5} y={84} width={3} height={92} />
        </g>
        <circle cx={271} cy={84} r={3} fill={ROUGE} opacity={Math.sin(t / 6) > 0 ? 1 : 0.2} />
        <rect y={340} width={1000} height={300} fill="url(#eau)" />
        {Array.from({length: 16}, (_, i) => (
          <line key={i} x1={0} x2={1000} y1={352 + i * 18} y2={352 + i * 18} stroke="#8fb0e0" strokeOpacity={0.1} strokeWidth={1.5} strokeDasharray={`${30 + i * 4} ${22 + i * 3}`} strokeDashoffset={-t * (1 + i * 0.15)} />
        ))}
        {Array.from({length: 14}, (_, i) => (
          <rect key={i} x={840 - (10 + random(`lr${i}${Math.floor(t / 4)}`) * 30)} y={352 + i * 18} width={20 + random(`lw${i}${Math.floor(t / 4)}`) * 60} height={3} fill="#efe9cf" opacity={0.22} />
        ))}
        <rect x={640} y={358} width={360} height={14} fill="#121827" />
        {Array.from({length: 9}, (_, i) => <rect key={i} x={652 + i * 40} y={372} width={6} height={40} fill="#0e1320" />)}
        <g clipPath="url(#horsEau)">
          <g transform={`translate(470 ${362 + coule + houle}) rotate(${tilt})`}>
            <line x1={-120} y1={-36} x2={-120} y2={-262} stroke="#9aa3b5" strokeWidth={4} />
            <line x1={110} y1={-52} x2={110} y2={-248} stroke="#9aa3b5" strokeWidth={4} />
            <path d="M-120 -262 L-232 -40 M-120 -262 L110 -248 M110 -248 L238 -64 M-120 -200 L-40 -200 M110 -200 L170 -196" stroke="#9aa3b5" strokeOpacity={0.4} strokeWidth={1.5} fill="none" />
            <path d="M-232 -40 L238 -66 L222 -8 Q205 24 168 26 L-200 26 Q-228 22 -232 -8 Z" fill="#183a2d" />
            <path d="M-232 -40 L238 -66" stroke="#d8dde6" strokeWidth={4} />
            {['#e5383b', '#f39c35', '#f5d33a', '#4fb55b', '#3d7fd9', '#7d4fd0'].map((col, k) => (
              <line key={col} x1={150 + k * 9} y1={-50 - k * 0.5} x2={128 + k * 9} y2={10} stroke={col} strokeWidth={6} opacity={0.85} />
            ))}
            <rect x={-60} y={-108} width={120} height={66} fill="#59616f" />
            <rect x={-38} y={-138} width={80} height={32} fill="#6b7383" />
            {[0, 1, 2, 3].map((k) => <rect key={k} x={-48 + k * 27} y={-94} width={16} height={12} fill={AMBRE} opacity={0.85} />)}
            {[0, 1].map((k) => <rect key={k} x={-26 + k * 34} y={-130} width={20} height={10} fill={AMBRE} opacity={0.6} />)}
            <circle cx={-120} cy={-262} r={3.5} fill="#fff" />
            <circle cx={110} cy={-248} r={3.5} fill={ROUGE} />
          </g>
        </g>
        {[-48, -21, 6, 33].map((x, k) => (
          <rect key={k} x={470 + x + 4} y={372 + coule} width={8} height={40 + 10 * Math.sin(t / 7 + k)} fill={AMBRE} opacity={0.18} />
        ))}
        {explosion(b1, 430, 370 + coule * 0.5, 'x')}
        {explosion(b2, 560, 368 + coule * 0.5, 'y')}
        <rect width={1000} height={640} fill="#fff" opacity={flash * 0.8} />
      </svg>
      <Etiquette t={t - 4} texte="10 juillet 1985" taille={60} style={{left: 34, top: t < m[2] ? 446 : 9999}} />
      <Etiquette t={t - 12} texte="Port d'Auckland · Nouvelle-Zélande" fond="rgba(0,0,0,0.8)" taille={30} style={{left: 34, top: t < m[2] ? 530 : 9999}} />
      {t >= m[1] && t < m[2] ? <Horloge t={t - m[1]} /> : null}
      <Etiquette t={t - b1} texte="2 bombes sous la coque" taille={52} style={{left: 34, top: 460}} />
      <Etiquette t={t - ev('rainbow')} texte="Rainbow Warrior · Greenpeace" fond={AMBRE} couleur="#111" taille={34} style={{left: 34, top: 40}} />
      <Photo t={t - ev('rainbow') - 4} src="photos/rw-auckland-1985.jpg" w={380} h={250} angle={3} style={{left: 590, top: 70}}
        legende="Le Rainbow Warrior à Auckland, 1985" credit="Photo : Ot · Wikimedia Commons · CC BY-SA 4.0" />
    </AbsoluteFill>
  );
};

const Horloge: React.FC<{t: number}> = ({t}) => {
  const s = spring({frame: t, fps: FPS, config: {damping: 14}});
  const aig = (deg: number, l: number, w: number, col: string) => (
    <line x1={60} y1={60} x2={60 + l * Math.sin((deg * Math.PI) / 180)} y2={60 - l * Math.cos((deg * Math.PI) / 180)} stroke={col} strokeWidth={w} strokeLinecap="round" />
  );
  return (
    <div style={{position: 'absolute', right: 40, top: 150, transform: `scale(${s})`, textAlign: 'center'}}>
      <svg width={150} height={150} viewBox="0 0 120 120">
        <circle cx={60} cy={60} r={54} fill="rgba(5,8,15,0.85)" stroke="#e8e8e8" strokeWidth={4} />
        {Array.from({length: 12}, (_, k) => aig(k * 30, 50, 2, '#888'))}
        {aig(355, 30, 6, '#fff')}
        {aig(258 + t * 0.15, 44, 4, '#fff')}
        {aig(t * 6, 46, 2, ROUGE)}
        <circle cx={60} cy={60} r={4} fill="#fff" />
      </svg>
      <Etiquette t={t - 4} texte="presque minuit" fond={AMBRE} couleur="#111" taille={30} style={{position: 'relative', marginTop: 8}} />
    </div>
  );
};

const Pereira: React.FC<Sc> = ({t, ev}) => {
  const entree = spring({frame: t, fps: FPS, config: {damping: 15}});
  return (
    <AbsoluteFill style={{background: 'linear-gradient(180deg, #0a1a2c 0%, #03070d 100%)', overflow: 'hidden'}}>
      <svg width={1000} height={640} style={{position: 'absolute'}}>
        {[0, 1, 2, 3].map((k) => (
          <polygon key={k} points={`${120 + k * 230 + Math.sin(t / 30 + k) * 30},0 ${200 + k * 230 + Math.sin(t / 30 + k) * 30},0 ${260 + k * 210},640 ${120 + k * 210},640`} fill="#5d8fc4" opacity={0.05} />
        ))}
        {Array.from({length: 34}, (_, i) => {
          const y = 660 - ((t * (1.2 + random(`bv${i}`) * 2.2) + random(`by${i}`) * 700) % 720);
          return <circle key={i} cx={random(`bx${i}`) * 1000 + Math.sin(t / 10 + i) * 6} cy={y} r={2 + random(`bs${i}`) * 6} fill="none" stroke="#a9cdf2" strokeOpacity={0.35} strokeWidth={1.5} />;
        })}
      </svg>
      <div style={{position: 'absolute', left: 90, top: 100, width: 300, height: 380, background: '#ece8dd', padding: '18px 18px 70px', boxSizing: 'border-box',
        transform: `translateY(${(1 - entree) * 60}px) rotate(-5deg)`, opacity: entree, boxShadow: '0 20px 50px rgba(0,0,0,0.6)'}}>
        <div style={{width: '100%', height: '100%', background: 'linear-gradient(160deg, #2a3242, #141922)', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
          <svg width={150} height={110} viewBox="0 0 150 110">
            <rect x={10} y={25} width={130} height={80} rx={10} fill="#5b6478" />
            <rect x={45} y={10} width={50} height={22} rx={5} fill="#5b6478" />
            <circle cx={75} cy={65} r={30} fill="#232937" stroke="#8a93a8" strokeWidth={5} />
            <circle cx={75} cy={65} r={14} fill="#3b4457" />
            <circle cx={118} cy={40} r={5} fill={AMBRE} />
          </svg>
        </div>
        <div style={{position: 'absolute', bottom: 16, left: 0, right: 0, textAlign: 'center', fontFamily: MONO, fontSize: 22, color: '#333'}}>1985</div>
      </div>
      <div style={{position: 'absolute', left: 450, top: 150, opacity: interpolate(t, [6, 16], [0, 1], c)}}>
        <div style={{fontFamily: MONO, fontSize: 26, color: AMBRE, letterSpacing: 4}}>À BORD</div>
        <div style={{fontFamily: OSW, fontWeight: 700, fontSize: 84, color: '#fff', lineHeight: 1.02, marginTop: 8}}>FERNANDO<br />PEREIRA</div>
        <div style={{fontFamily: INTER, fontSize: 30, color: '#b9c0cc', marginTop: 14}}>Photographe de Greenpeace</div>
      </div>
      <Etiquette t={t - ev('noye')} texte="Mort noyé" taille={54} style={{left: 450, top: 440}} />
    </AbsoluteFill>
  );
};

const VILLES: Record<string, [number, number]> = {Paris: [2.35, 48.86], Auckland: [174.76, -36.85], Mururoa: [-138.9, -21.83]};
const Carte: React.FC<Sc> = ({t, ev}) => {
  const k = interpolate(t, [0, 48], [0, 1], {...c, easing: Easing.inOut(Easing.cubic)});
  const rot: [number, number] = [-2 + 164 * k, -46 + 75 * k];
  const proj = geoOrthographic().scale(262).translate([320, 325]).rotate(rot).clipAngle(90);
  const path = geoPath(proj);
  const centre: [number, number] = [-rot[0], -rot[1]];
  const visible = (p: [number, number]) => geoDistance(p, centre) < Math.PI / 2 - 0.05;
  const pt = (n: string) => proj(VILLES[n]) as [number, number];
  const pRoute = interpolate(t, [52, 88], [0, 1], {...c, easing: Easing.inOut(Easing.quad)});
  const interp = geoInterpolate(VILLES.Auckland, VILLES.Mururoa);
  const route = Array.from({length: 41}, (_, i) => interp((i / 40) * pRoute));
  const arrivee = t - 88;
  return (
    <AbsoluteFill style={{background: 'radial-gradient(circle at 35% 50%, #101a30 0%, #04060b 70%)'}}>
      <svg width={1000} height={640} style={{position: 'absolute'}}>
        <defs>
          <radialGradient id="ocean" cx="40%" cy="35%"><stop offset="0" stopColor="#16233f" /><stop offset="1" stopColor="#070c18" /></radialGradient>
        </defs>
        <circle cx={320} cy={325} r={276} fill="none" stroke="#3c63b8" strokeOpacity={0.25} strokeWidth={14} />
        <path d={path({type: 'Sphere'}) ?? ''} fill="url(#ocean)" stroke="#4d6fb5" strokeWidth={1.5} />
        <path d={path(geoGraticule10()) ?? ''} fill="none" stroke="#fff" strokeOpacity={0.06} />
        {(monde as any).features.map((f: any, i: number) => (
          <path key={i} d={path(f) ?? ''} fill={f.properties.a3 === 'FRA' ? '#4466b8' : f.properties.a3 === 'NZL' ? '#4a5f94' : '#2c3b60'} stroke="#6a86c4" strokeWidth={0.9} />
        ))}
        {visible(VILLES.Paris) && k < 0.5 ? (
          <g opacity={interpolate(k, [0.2, 0.45], [1, 0], c)}>
            <circle cx={pt('Paris')[0]} cy={pt('Paris')[1]} r={8} fill={AMBRE} />
            <text x={pt('Paris')[0] + 14} y={pt('Paris')[1] - 10} fill="#fff" fontFamily={OSW} fontSize={30} fontWeight={600}>PARIS</text>
          </g>
        ) : null}
        {k > 0.9 ? (
          <g opacity={interpolate(k, [0.9, 1], [0, 1], c)}>
            <path d={path({type: 'LineString', coordinates: [VILLES.Auckland, VILLES.Mururoa]}) ?? ''} fill="none" stroke={AMBRE} strokeOpacity={0.3} strokeWidth={3} strokeDasharray="10 9" />
            {pRoute > 0 ? <path d={path({type: 'LineString', coordinates: route}) ?? ''} fill="none" stroke={AMBRE} strokeWidth={6} strokeLinecap="round" /> : null}
            <circle cx={pt('Auckland')[0]} cy={pt('Auckland')[1]} r={9} fill={AMBRE} />
            <text x={pt('Auckland')[0] - 18} y={pt('Auckland')[1] + 42} textAnchor="middle" fill="#fff" fontFamily={OSW} fontSize={30} fontWeight={600}>AUCKLAND</text>
            {arrivee > 0 ? [0, 1, 2].map((r) => {
              const d = (arrivee + r * 12) % 36;
              return <circle key={r} cx={pt('Mururoa')[0]} cy={pt('Mururoa')[1]} r={6 + d * 2.2} fill="none" stroke={ROUGE} strokeWidth={3} opacity={1 - d / 36} />;
            }) : null}
            <circle cx={pt('Mururoa')[0]} cy={pt('Mururoa')[1]} r={9} fill={ROUGE} />
            <text x={pt('Mururoa')[0]} y={pt('Mururoa')[1] - 22} textAnchor="middle" fill="#fff" fontFamily={OSW} fontSize={30} fontWeight={600}>MURUROA</text>
          </g>
        ) : null}
      </svg>
      <Photo t={t - Math.max(70, ev('nucleaires'))} src="photos/mururoa.jpg" w={350} h={165} angle={-2} style={{left: 615, top: 168}}
        legende="L'atoll de Mururoa" credit="Photo : NASA · domaine public" />
      <Etiquette t={t - 56} texte="4 700 km à vol d'oiseau" fond={AMBRE} couleur="#111" taille={30} style={{left: 610, top: 110}} />
      <Etiquette t={t - Math.max(70, ev('nucleaires'))} texte="Essais nucléaires" taille={42} style={{left: 610, top: 400}} />
      <Etiquette t={t - Math.max(76, ev('nucleaires') + 6)} texte="français" taille={42} style={{left: 610, top: 460}} />
      <Etiquette t={t - Math.max(84, ev('mururoa') + 4)} texte="À plus de 15 000 km" fond="rgba(0,0,0,0.85)" taille={30} style={{left: 610, top: 530}} />
      <Etiquette t={t - Math.max(88, ev('mururoa') + 8)} texte="de Paris" fond="rgba(0,0,0,0.85)" taille={30} style={{left: 610, top: 574}} />
    </AbsoluteFill>
  );
};

const Passeport: React.FC<{t: number; prenom: string; ouvre: number}> = ({t, prenom, ouvre}) => {
  const o = interpolate(t, [ouvre, ouvre + 16], [0, 1], {...c, easing: Easing.inOut(Easing.cubic)});
  const entree = spring({frame: t, fps: FPS, config: {damping: 16}});
  return (
    <div style={{position: 'relative', width: 330, height: 430, perspective: 1400, transform: `translateY(${(1 - entree) * 80}px)`, opacity: entree}}>
      <div style={{position: 'absolute', inset: 0, background: `repeating-linear-gradient(35deg, #f0e3da 0 6px, #ead9ce 6px 8px)`, borderRadius: 14, padding: 22, boxSizing: 'border-box', fontFamily: MONO, color: '#2b2b2b', boxShadow: '0 20px 40px rgba(0,0,0,0.5)'}}>
        <div style={{fontSize: 20, letterSpacing: 3, color: '#9e1b2c', fontWeight: 700}}>PASSEPORT · SUISSE</div>
        <div style={{display: 'flex', gap: 16, marginTop: 18}}>
          <div style={{width: 120, height: 150, background: '#cfc6bd', display: 'flex', alignItems: 'flex-end', justifyContent: 'center', overflow: 'hidden'}}>
            <Silhouette w={120} couleur="#7d7469" />
          </div>
          <div style={{fontSize: 19, lineHeight: 1.5}}>
            <div style={{color: '#777'}}>Nom</div>
            <div style={{fontSize: 30, fontWeight: 700}}>TURENGE</div>
            <div style={{color: '#777'}}>Prénom</div>
            <div style={{fontSize: 28, fontWeight: 700}}>{prenom}</div>
          </div>
        </div>
        <div style={{marginTop: 26, fontSize: 18, letterSpacing: 2, color: '#666', wordBreak: 'break-all'}}>{'P<CHETURENGE<<' + prenom + '<<<<<<<<<<<<<'}</div>
      </div>
      <div style={{position: 'absolute', inset: 0, background: 'linear-gradient(160deg, #b0202f, #7d1220)', borderRadius: 14, transformOrigin: 'left center',
        transform: `rotateY(${-178 * o}deg)`, backfaceVisibility: 'hidden', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 26}}>
        <div style={{width: 96, height: 96, background: '#fff', position: 'relative'}}>
          <div style={{position: 'absolute', left: 38, top: 12, width: 20, height: 72, background: '#b0202f'}} />
          <div style={{position: 'absolute', left: 12, top: 38, width: 72, height: 20, background: '#b0202f'}} />
        </div>
        <div style={{fontFamily: OSW, fontSize: 34, letterSpacing: 6, color: '#f1d27a'}}>PASSEPORT</div>
      </div>
    </div>
  );
};

const Passeports: React.FC<Sc> = ({t, ev, m}) => {
  const police = t < m[1] + 10 ? interpolate(t, [m[1] - 5, m[1] + 10], [1, 0], c) : 0;
  const rouge = Math.sin(t / 2.5) > 0;
  return (
    <AbsoluteFill style={{background: '#0d0f14'}}>
      <AbsoluteFill style={{opacity: police * 0.55, background: rouge ? 'radial-gradient(circle at 0% 0%, #ff2a2a 0%, transparent 55%)' : 'radial-gradient(circle at 100% 0%, #2a5bff 0%, transparent 55%)'}} />
      <div style={{position: 'absolute', left: 120, top: 70}}><Passeport t={t} prenom="ALAIN" ouvre={10} /></div>
      <div style={{position: 'absolute', left: 550, top: 70}}><Passeport t={t - 6} prenom="SOPHIE" ouvre={12} /></div>
      {t < m[1] ? <Etiquette t={t - ev('touristes')} texte="« Touristes suisses »" fond={AMBRE} couleur="#111" taille={40} style={{left: 330, top: 14}} /> : null}
      <Tampon t={t - ev('faux')} texte="Faux" taille={92} style={{left: 190, top: 210}} />
      <Tampon t={t - ev('faux') - 7} texte="Faux" taille={92} angle={9} style={{left: 640, top: 230}} />
      <Etiquette t={t - ev('faux') - 4} texte="Fausse identité" taille={40} style={{left: 360, top: 14}} />
      <Etiquette t={t - ev('mafart')} texte="Alain Mafart" fond={AMBRE} couleur="#111" taille={44} style={{left: 150, top: 530}} />
      <Etiquette t={t - ev('prieur')} texte="Dominique Prieur" fond={AMBRE} couleur="#111" taille={44} style={{left: 548, top: 530}} />
    </AbsoluteFill>
  );
};

const Dgse: React.FC<Sc> = ({t, ev}) => {
  const e = spring({frame: t, fps: FPS, config: {damping: 16}});
  const zoom = interpolate(t, [0, 120], [1, 1.06], c);
  return (
    <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 40%, #1c1a16, #07070a 75%)'}}>
      <div style={{position: 'absolute', left: 170, top: 60, width: 660, height: 470, transform: `translateY(${(1 - e) * 90}px) rotate(-2deg) scale(${zoom})`, opacity: e}}>
        <div style={{position: 'absolute', left: 30, top: -34, width: 220, height: 50, background: '#b9975b', borderRadius: '10px 10px 0 0'}} />
        <div style={{position: 'absolute', inset: 0, background: 'linear-gradient(170deg, #cfae6e, #b5934f)', borderRadius: 8, boxShadow: '0 30px 60px rgba(0,0,0,0.6)', padding: 40, boxSizing: 'border-box'}}>
          <div style={{display: 'flex', height: 8, width: 120}}><div style={{flex: 1, background: '#22438f'}} /><div style={{flex: 1, background: '#f4f4f4'}} /><div style={{flex: 1, background: '#d22b2b'}} /></div>
          <div style={{fontFamily: MONO, fontWeight: 700, fontSize: 24, color: '#2b2416', marginTop: 24, letterSpacing: 1}}>DIRECTION GÉNÉRALE DE<br />LA SÉCURITÉ EXTÉRIEURE</div>
          <div style={{fontFamily: OSW, fontWeight: 700, fontSize: 150, color: '#2b2416', lineHeight: 1, marginTop: 26}}>DGSE</div>
          <div style={{display: 'flex', gap: 20, marginTop: 20}}>
            {[0, 1].map((k) => (
              <div key={k} style={{width: 90, height: 90, background: 'rgba(43,36,22,0.15)', display: 'flex', alignItems: 'flex-end', justifyContent: 'center', overflow: 'hidden'}}><Silhouette w={90} couleur="#3d3322" /></div>
            ))}
          </div>
        </div>
      </div>
      <Tampon t={t - ev('agents')} texte="Secret défense" taille={60} angle={-10} style={{left: 430, top: 300}} />
      <Etiquette t={t - ev('secrets')} texte="Services secrets français" fond={AMBRE} couleur="#111" taille={40} style={{left: 250, top: 560}} />
    </AbsoluteFill>
  );
};

const MOIS = ['JANVIER', 'FÉVRIER', 'MARS', 'AVRIL', 'MAI', 'JUIN', 'JUILLET', 'AOÛT', 'SEPTEMBRE', 'OCTOBRE', 'NOVEMBRE', 'DÉCEMBRE'];
const Dementi: React.FC<Sc> = ({t, ev, dur}) => {
  const jours = interpolate(t, [8, Math.max(30, dur - 14)], [0, 69], {...c, easing: Easing.inOut(Easing.quad)});
  const d = new Date(Date.UTC(1985, 6, 10 + Math.floor(jours)));
  const frac = jours % 1;
  const dementis = ((EV.dementis as number[]) ?? []).map((s) => fr(s) - (fr(PH[8].debut) - 6));
  return (
    <AbsoluteFill style={{background: 'radial-gradient(circle at 30% 50%, #1a1d26, #06070a 75%)'}}>
      <div style={{position: 'absolute', left: 90, top: 90, width: 320, height: 400, background: '#f2efe6', borderRadius: 12, overflow: 'hidden', boxShadow: '0 30px 60px rgba(0,0,0,0.6)'}}>
        <div style={{height: 70, background: ROUGE, color: '#fff', fontFamily: OSW, fontWeight: 600, fontSize: 40, textAlign: 'center', lineHeight: '70px', letterSpacing: 6}}>1985</div>
        <div style={{transform: `translateY(${-frac * 14}px)`, opacity: 1 - frac * 0.35, textAlign: 'center'}}>
          <div style={{fontFamily: OSW, fontWeight: 700, fontSize: 190, color: '#16181d', lineHeight: 1.1}}>{d.getUTCDate()}</div>
          <div style={{fontFamily: OSW, fontWeight: 500, fontSize: 40, color: '#16181d', letterSpacing: 4}}>{MOIS[d.getUTCMonth()]}</div>
        </div>
      </div>
      {dementis.map((s, i) => (
        <Tampon key={i} t={t - s} texte="Démenti" taille={42} angle={-16 + random(`da${i}`) * 26} style={{left: 470 + (i % 2) * 240 + random(`dx${i}`) * 20, top: 70 + Math.floor(i / 2) * 140 + random(`dy${i}`) * 20}} />
      ))}
      <Etiquette t={t - ev('mois')} texte="Plus de 2 mois" fond={AMBRE} couleur="#111" taille={52} style={{left: 90, top: 520}} />
    </AbsoluteFill>
  );
};

const Journal: React.FC<Sc> = ({t, ev}) => {
  const e = spring({frame: t, fps: FPS, config: {damping: 14}});
  const ligne = (w: number, k: number) => <div key={k} style={{height: 10, width: `${w}%`, background: '#b8b2a3', marginTop: 9, borderRadius: 2}} />;
  const tEq = t - ev('troisieme');
  return (
    <AbsoluteFill style={{background: '#08090c'}}>
      <div style={{position: 'absolute', left: 120, top: 30, width: 760, height: 470, background: PAPIER, transform: `rotate(-3deg) scale(${0.6 + 0.4 * e}) translateY(${(1 - e) * 200}px)`, boxShadow: '0 30px 70px rgba(0,0,0,0.7)', padding: '26px 34px', boxSizing: 'border-box'}}>
        <div style={{height: 46, background: '#2a2a2a', width: '62%', margin: '0 auto', borderRadius: 3, opacity: 0.85}} />
        <div style={{borderTop: '3px solid #2a2a2a', borderBottom: '1px solid #2a2a2a', marginTop: 14, padding: '4px 0', fontFamily: SERIF, fontSize: 20, color: '#2a2a2a', textAlign: 'center', letterSpacing: 1}}>MARDI 17 SEPTEMBRE 1985</div>
        <div style={{marginTop: 18, height: 34, width: '92%', background: '#3a3a3a', borderRadius: 3}} />
        <div style={{marginTop: 10, height: 34, width: '70%', background: '#3a3a3a', borderRadius: 3}} />
        <div style={{display: 'flex', gap: 22, marginTop: 14}}>
          {[0, 1, 2].map((col) => <div key={col} style={{flex: 1}}>{[96, 88, 100, 92, 75, 98, 90, 84].map((w, k) => ligne(w - ((col * 7 + k * 3) % 13), k))}</div>)}
        </div>
      </div>
      <Etiquette t={t - ev('monde')} texte="Révélation · Le Monde" taille={44} style={{left: 60, top: 24}} />
      {tEq >= 0 ? (
        <div style={{position: 'absolute', left: 60, right: 60, bottom: 28, display: 'flex', gap: 18}}>
          {['Équipe 1', 'Équipe 2', 'Équipe 3'].map((n, i) => {
            const s = spring({frame: tEq - i * 4, fps: FPS, config: {damping: 13}});
            const trois = i === 2;
            const allume = trois && t >= ev('plongeurs');
            return (
              <div key={n} style={{flex: 1, height: 130, background: allume ? AMBRE : 'rgba(25,27,34,0.95)', border: `2px solid ${trois ? AMBRE : '#3a3f4b'}`, borderRadius: 12,
                transform: `translateY(${(1 - s) * 140}px) scale(${allume ? 1.06 : 1})`, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: allume ? '#111' : '#fff'}}>
                <div style={{fontFamily: OSW, fontWeight: 600, fontSize: 40}}>{n.toUpperCase()}</div>
                <div style={{fontFamily: INTER, fontWeight: 800, fontSize: 26}}>{allume ? '🤿 LES PLONGEURS' : trois ? '?' : ''}</div>
              </div>
            );
          })}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

const Drapeau: React.FC<{t: number}> = ({t}) => {
  const bande = (x0: number, col: string) => {
    const pts = Array.from({length: 11}, (_, i) => {
      const x = x0 + i * 13;
      return [x, Math.sin(t / 8 - x / 40) * 10 * (x / 400)] as const;
    });
    const haut = pts.map(([x, y]) => `${x},${60 + y}`).join(' ');
    const bas = pts.slice().reverse().map(([x, y]) => `${x},${330 + y}`).join(' ');
    return <polygon points={`${haut} ${bas}`} fill={col} />;
  };
  return (
    <svg width={420} height={400} style={{position: 'absolute', right: -10, top: 60, opacity: 0.22}}>
      {bande(0, '#2a4fae')}{bande(130, '#f2f2f2')}{bande(260, '#d42a2a')}
    </svg>
  );
};

const Hernu: React.FC<Sc> = ({t, ev}) => {
  const e = spring({frame: t, fps: FPS, config: {damping: 15}});
  return (
    <AbsoluteFill style={{background: 'radial-gradient(circle at 70% 40%, #1b2030, #06070a 75%)'}}>
      <Drapeau t={t} />
      <Photo t={t} src="photos/hernu.jpg" w={300} h={370} angle={-3} style={{left: 70, top: 60}}
        legende="Charles Hernu, 1983" credit="Photo : US Air Force · domaine public" />
      <div style={{position: 'absolute', left: 420, top: 120, opacity: interpolate(t, [4, 14], [0, 1], c)}}>
        <div style={{fontFamily: MONO, fontSize: 26, color: AMBRE, letterSpacing: 4}}>MINISTRE DE LA DÉFENSE</div>
        <div style={{fontFamily: OSW, fontWeight: 700, fontSize: 92, color: '#fff', lineHeight: 1.02, marginTop: 10}}>CHARLES<br />HERNU</div>
      </div>
      <Etiquette t={t - 10} texte="20 sept. 1985" taille={40} fond="rgba(0,0,0,0.85)" style={{left: 420, top: 400}} />
      <Tampon t={t - ev('demission')} texte="Démission" taille={86} angle={-9} style={{left: 360, top: 470}} />
    </AbsoluteFill>
  );
};

const Aveu: React.FC<Sc> = ({t, ev}) => {
  const flashs = ((EV.flashs as number[]) ?? []).map((s) => fr(s) - (fr(PH[11].debut) - 6));
  const f = Math.max(0, ...flashs.map((s) => interpolate(t - s, [0, 1, 6], [0, 1, 0], c)));
  const citation = '« Ils ont agi sur ordre. »';
  const n = Math.max(0, Math.floor((t - ev('ils')) / 1.5));
  return (
    <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 20%, #202638, #06070a 72%)'}}>
      <svg width={1000} height={640} style={{position: 'absolute'}}>
        <rect x={380} y={330} width={240} height={310} fill="#151925" stroke="#2f3647" strokeWidth={3} />
        <rect x={360} y={318} width={280} height={22} fill="#232938" />
        {[-60, -20, 20, 60].map((dx, k) => (
          <g key={k}>
            <line x1={500 + dx * 0.4} y1={318} x2={500 + dx} y2={250} stroke="#555c6c" strokeWidth={5} />
            <rect x={490 + dx} y={222} width={22} height={38} rx={10} fill={['#d9d9d9', '#2f6fe0', '#e04a3c', '#f0c040'][k]} />
          </g>
        ))}
        <circle cx={500} cy={140} r={60} fill="#2a3040" />
        <path d="M410 330 Q420 210 500 205 Q580 210 590 330 Z" fill="#2a3040" />
      </svg>
      <AbsoluteFill style={{background: '#fff', opacity: f * 0.55}} />
      <Photo t={t - ev('premier') - 4} src="photos/fabius.png" w={240} h={290} angle={3} style={{left: 720, top: 70}} nb
        legende="Laurent Fabius (1981)" credit="Photo : CEVIPOF Sciences Po · CC BY-SA 4.0" />
      <Etiquette t={t - ev('premier')} texte="Laurent Fabius · Premier ministre" fond={AMBRE} couleur="#111" taille={34} style={{left: 34, top: 30}} />
      <Etiquette t={t - ev('premier') - 6} texte="22 sept. 1985" taille={34} fond="rgba(0,0,0,0.85)" style={{left: 34, top: 88}} />
      {n > 0 ? (
        <div style={{position: 'absolute', left: 60, right: 60, bottom: 40, background: 'rgba(8,9,12,0.92)', borderLeft: `8px solid ${ROUGE}`, padding: '24px 30px', fontFamily: MONO, fontWeight: 700, fontSize: 46, color: '#fff', whiteSpace: 'nowrap'}}>
          {citation.slice(0, n)}<span style={{opacity: Math.sin(t / 3) > 0 ? 1 : 0}}>▌</span>
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

const Ordre: React.FC<Sc> = ({t, ev}) => {
  const g = (t % 23 < 2 ? (random(`g${t}`) - 0.5) * 30 : 0);
  const s = spring({frame: t - ev('qui'), fps: FPS, config: {damping: 9}});
  return (
    <AbsoluteFill style={{background: '#050506', alignItems: 'center', justifyContent: 'center'}}>
      <div style={{position: 'absolute', fontFamily: OSW, fontWeight: 700, fontSize: 620, color: ROUGE, opacity: 0.16 * s, transform: `scale(${0.6 + 0.4 * s}) translateX(${g}px)`, lineHeight: 1}}>?</div>
      <div style={{fontFamily: OSW, fontWeight: 600, fontSize: 84, color: '#fff', letterSpacing: 2, opacity: interpolate(t, [2, 10], [0, 1], c)}}>SUR L'ORDRE DE</div>
      <div style={{marginTop: 26, width: 620, height: 92, background: '#000', border: '2px solid #2a2a2a', position: 'relative', overflow: 'hidden'}}>
        <div style={{position: 'absolute', inset: 0, background: `linear-gradient(90deg, transparent, ${ROUGE}55, transparent)`, transform: `translateX(${((t * 18) % 1240) - 620}px)`}} />
      </div>
      <Etiquette t={t - ev('qui')} texte="Classé secret" taille={40} style={{position: 'relative', marginTop: 30}} />
    </AbsoluteFill>
  );
};

const Note: React.FC<Sc> = ({t, ev}) => {
  const an = Math.round(interpolate(t, [ev('vingt') - 4, ev('vingt') + 26], [1985, 2005], {...c, easing: Easing.out(Easing.cubic)}));
  const e = spring({frame: t - ev('manuscrite') + 6, fps: FPS, config: {damping: 15}});
  const lignes = ['nnnn mmmm nnn mmmmm', 'mmm nnnnn mm nnnnnn', 'nnnnnn mmm nnnn mm', 'mm nnnnnnn mmmm nn', 'nnnn mm nnnnn mmmm'];
  return (
    <AbsoluteFill style={{background: 'radial-gradient(circle at 30% 50%, #171a22, #050507 75%)'}}>
      <div style={{position: 'absolute', left: 50, top: 150, fontFamily: OSW, fontWeight: 700, fontSize: 170, color: an >= 2005 ? AMBRE : '#fff', lineHeight: 1}}>{an}</div>
      <div style={{position: 'absolute', left: 56, top: 340, fontFamily: MONO, fontSize: 26, color: '#9aa1ad', letterSpacing: 3}}>{an >= 2005 ? '20 ANS PLUS TARD' : 'LES ANNÉES PASSENT…'}</div>
      <div style={{position: 'absolute', left: 560, top: 40, width: 400, height: 520, background: '#f3f1ea', transform: `rotate(4deg) translateY(${(1 - e) * 500}px)`, boxShadow: '0 30px 60px rgba(0,0,0,0.65)',
        backgroundImage: 'repeating-linear-gradient(180deg, transparent 0 46px, #b7c8e6 46px 48px)', padding: '40px 30px', boxSizing: 'border-box', overflow: 'hidden'}}>
        {lignes.concat(lignes).map((l, i) => (
          <div key={i} style={{fontFamily: MAIN, fontSize: 36, color: '#1d2a55', lineHeight: '48px', filter: 'blur(4.5px)', whiteSpace: 'nowrap'}}>{l}</div>
        ))}
      </div>
      <Etiquette t={t - ev('manuscrite')} texte="Note manuscrite · 1986" taille={36} style={{left: 560, top: 480}} />
      <Etiquette t={t - ev('chef')} texte="Amiral Pierre Lacoste" fond={AMBRE} couleur="#111" taille={32} style={{left: 50, top: 400}} />
      <Etiquette t={t - ev('chef') - 5} texte="ex-chef de la DGSE" fond={AMBRE} couleur="#111" taille={32} style={{left: 50, top: 448}} />
      <Etiquette t={t - ev('publiee')} texte="Publiée en 2005" fond="rgba(0,0,0,0.88)" taille={38} style={{left: 50, top: 520}} />
    </AbsoluteFill>
  );
};

const Fin: React.FC<Sc> = ({t, ev}) => {
  const s = spring({frame: t, fps: FPS, config: {damping: 12}});
  const b = spring({frame: t - ev('abonne'), fps: FPS, config: {damping: 8}});
  const pulse = 1 + 0.05 * Math.sin(t / 4);
  return (
    <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 45%, #2a1012, #050506 70%)', alignItems: 'center', justifyContent: 'center'}}>
      <div style={{fontFamily: MONO, fontSize: 30, color: AMBRE, letterSpacing: 8, opacity: s}}>LA SUITE · PARTIE 2</div>
      <div style={{marginTop: 16, transform: `scale(${s})`, background: ROUGE, color: '#fff', fontFamily: OSW, fontWeight: 700, fontSize: 120, padding: '0 40px', lineHeight: 1.2}}>LA NOTE</div>
      <div style={{marginTop: 20, fontFamily: INTER, fontWeight: 700, fontSize: 36, color: '#d5d8de', opacity: interpolate(t, [8, 18], [0, 1], c)}}>Qui a donné l'ordre ?</div>
      <div style={{marginTop: 40, transform: `scale(${b * pulse})`, background: '#fff', color: '#111', fontFamily: INTER, fontWeight: 900, fontSize: 40, padding: '16px 46px', borderRadius: 60}}>🔔 S'ABONNER</div>
    </AbsoluteFill>
  );
};

// ─── Découpage : quelles phrases pour quelle scène ────────────────────────────
const SCENES: {de: number; a: number; C: React.FC<Sc>; tag: string}[] = [
  {de: 0, a: 2, C: Port, tag: 'Reconstitution'},
  {de: 3, a: 3, C: Pereira, tag: 'Illustration'},
  {de: 4, a: 4, C: Carte, tag: 'Carte'},
  {de: 5, a: 6, C: Passeports, tag: 'Reconstitution'},
  {de: 7, a: 7, C: Dgse, tag: 'Illustration'},
  {de: 8, a: 8, C: Dementi, tag: 'Chronologie'},
  {de: 9, a: 9, C: Journal, tag: 'Reconstitution'},
  {de: 10, a: 10, C: Hernu, tag: 'Archives'},
  {de: 11, a: 11, C: Aveu, tag: 'Reconstitution'},
  {de: 12, a: 12, C: Ordre, tag: 'Classé'},
  {de: 13, a: 13, C: Note, tag: 'Illustration'},
  {de: 14, a: 14, C: Fin, tag: 'À suivre'},
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
  const lignes = ['Le sabotage du', 'Rainbow Warrior 🇫🇷🇳🇿', 'Partie 1'];
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
        <div style={{fontFamily: MONO, fontSize: 24, color: AMBRE, letterSpacing: 3}}>AFFAIRE Nº01 · 1/3</div>
      </div>
      <div style={{position: 'absolute', top: 484, left: 44, width: 992, height: 4, background: 'rgba(255,255,255,0.1)'}}>
        <div style={{width: `${(f / DUREE_ENQUETE) * 100}%`, height: '100%', background: AMBRE}} />
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
        const a = i === SCENES.length - 1 ? DUREE_ENQUETE : debutScene(i + 1);
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

export const Enquete: React.FC = () => {
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
        Sources : police NZ · NZHistory · Universalis · Le Monde (2005) · Photos : Wikimedia Commons
      </div>
      <Audio src={staticFile('enquete-mix.wav')} />
    </AbsoluteFill>
  );
};
