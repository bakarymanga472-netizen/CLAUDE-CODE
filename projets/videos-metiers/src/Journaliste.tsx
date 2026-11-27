import React, {useEffect, useState} from 'react';
import {AbsoluteFill, continueRender, delayRender, Easing, Img, interpolate, random, Sequence, spring, staticFile, useCurrentFrame} from 'remotion';
import {Audio} from '@remotion/media';
import phrases from './phrases-journaliste.json';
import mots from './mots-journaliste.json';
import evts from './evts-journaliste.json';
import dispo from './images-journaliste.json';

const FPS = 30;
const c = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const fr = (s: number) => Math.round(s * FPS);
const ROSE = '#ff4f8b';
const JAUNE = '#ffd23f';
const CYAN = '#3ee0ff';
const OSW = 'Oswald, Impact, sans-serif';
const BANG = 'Bangers, Impact, sans-serif';
const INTER = 'Inter, Arial, sans-serif';
const PH = phrases as {texte: string; debut: number; fin: number}[];
const EV = evts as Record<string, number>;
const DISPO = dispo as string[];
export const DUREE_JOURNALISTE = fr(PH[PH.length - 1].fin + 1.4);

// ─── Polices ─────────────────────────────────────────────────────────────────
let chargement: Promise<void> | null = null;
const chargerPolices = () =>
  (chargement ??= Promise.all([
    new FontFace('Oswald', `url(${staticFile('fonts/Oswald.ttf')})`, {weight: '200 700'}),
    new FontFace('Bangers', `url(${staticFile('fonts/Bangers.ttf')})`),
  ].map((f) => f.load().then((g) => {
    document.fonts.add(g);
  }))).then(() => undefined));

// ─── Effets « anime » ────────────────────────────────────────────────────────
const LignesVitesse: React.FC<{t: number; duree?: number; couleur?: string}> = ({t, duree = 18, couleur = '#fff'}) => {
  if (t < 0 || t > duree) return null;
  const o = interpolate(t, [0, 2, duree - 4, duree], [0, 0.85, 0.85, 0], c);
  return (
    <svg width={1080} height={1920} style={{position: 'absolute', opacity: o}}>
      {Array.from({length: 90}, (_, i) => {
        const a = (i / 90) * Math.PI * 2 + random(`a${i}`) * 0.05;
        const r0 = 330 + random(`r${i}${Math.floor(t / 2)}`) * 260;
        const ep = 2 + random(`e${i}`) * 9;
        const x0 = 540 + Math.cos(a) * r0, y0 = 960 + Math.sin(a) * r0;
        const x1 = 540 + Math.cos(a) * 1500, y1 = 960 + Math.sin(a) * 1500;
        return <polygon key={i} points={`${x0},${y0} ${x1 + Math.sin(a) * ep * 6},${y1 - Math.cos(a) * ep * 6} ${x1 - Math.sin(a) * ep * 6},${y1 + Math.cos(a) * ep * 6}`} fill={couleur} />;
      })}
    </svg>
  );
};

const Pluie: React.FC<{t: number}> = ({t}) => (
  <svg width={1080} height={1920} style={{position: 'absolute', opacity: 0.55}}>
    {Array.from({length: 110}, (_, i) => {
      const x = (random(`px${i}`) * 1300 + t * 4) % 1300 - 110;
      const y = (random(`py${i}`) * 2100 + t * (38 + random(`pv${i}`) * 18)) % 2100 - 90;
      return <line key={i} x1={x} y1={y} x2={x - 9} y2={y + 60} stroke="#cfe6ff" strokeWidth={2} strokeLinecap="round" />;
    })}
  </svg>
);

const Etincelles: React.FC<{t: number}> = ({t}) => (
  <svg width={1080} height={1920} style={{position: 'absolute'}}>
    {Array.from({length: 34}, (_, i) => {
      const x = random(`sx${i}`) * 1080;
      const y = (random(`sy${i}`) * 1920 - t * (0.6 + random(`sv${i}`))) % 1920;
      const s = 4 + 10 * Math.abs(Math.sin(t / 9 + i));
      return <path key={i} d={`M${x},${y - s} L${x + s * 0.25},${y} L${x},${y + s} L${x - s * 0.25},${y} Z M${x - s},${y} L${x},${y + s * 0.25} L${x + s},${y} L${x},${y - s * 0.25} Z`} fill="#fff8d6" opacity={0.75} />;
    })}
  </svg>
);

const Trame: React.FC = () => (
  <AbsoluteFill style={{backgroundImage: 'radial-gradient(rgba(0,0,0,0.22) 1.2px, transparent 1.4px)', backgroundSize: '7px 7px', mixBlendMode: 'multiply', opacity: 0.35}} />
);

// Carte « chiffre » au style anime : gros chiffre, contour épais, pop élastique
const Chiffre: React.FC<{t: number; valeur: string; legende: string; couleur?: string; style?: React.CSSProperties; source?: string}> = ({t, valeur, legende, couleur = JAUNE, style, source}) => {
  if (t < 0) return null;
  const s = spring({frame: t, fps: FPS, config: {damping: 9, mass: 0.7}});
  return (
    <div style={{position: 'absolute', left: 0, right: 0, textAlign: 'center', ...style, transform: `scale(${s}) rotate(${(1 - s) * -8}deg)`}}>
      <div style={{fontFamily: BANG, fontSize: 190, letterSpacing: 4, lineHeight: 1, color: couleur, WebkitTextStroke: '10px #111', paintOrder: 'stroke fill', textShadow: '0 12px 0 rgba(0,0,0,0.35)'}}>{valeur}</div>
      <div style={{display: 'inline-block', marginTop: 10, background: '#111', color: '#fff', fontFamily: OSW, fontWeight: 600, fontSize: 44, padding: '4px 22px', transform: 'skewX(-8deg)'}}>{legende}</div>
      {source ? <div style={{marginTop: 8, fontFamily: INTER, fontSize: 24, color: '#fff', textShadow: '0 2px 6px #000'}}>{source}</div> : null}
    </div>
  );
};

const Bulle: React.FC<{t: number; texte: string; style: React.CSSProperties; couleur?: string}> = ({t, texte, style, couleur = '#fff'}) => {
  if (t < 0) return null;
  const s = spring({frame: t, fps: FPS, config: {damping: 10}});
  return (
    <div style={{position: 'absolute', ...style, transform: `scale(${s})`, background: couleur, color: '#111', fontFamily: BANG, fontSize: 64, letterSpacing: 2,
      padding: '6px 30px', border: '6px solid #111', borderRadius: 40, boxShadow: '8px 8px 0 #111', whiteSpace: 'nowrap'}}>{texte}</div>
  );
};

// ─── Scènes ──────────────────────────────────────────────────────────────────
type Sc = {t: number; dur: number; ev: (n: string) => number; m: number[]};
const SCENES: {de: number; a: number; img: string[]; effet?: 'pluie' | 'etincelles'; sens: number; C?: React.FC<Sc>}[] = [
  {de: 0, a: 1, img: ['01-accroche'], sens: 1, C: ({t, ev}) => (
    <>
      <LignesVitesse t={t - 2} duree={20} />
      <Chiffre t={t - 4} valeur="10 ANS" legende="de journalisme" style={{top: 560}} />
      <Bulle t={t - ev('jamais') + 4} texte="CE QU'ON NE TE DIT JAMAIS" couleur={ROSE} style={{left: 90, top: 1080}} />
    </>
  )},
  {de: 2, a: 2, img: ['02-debuts', '11-fin'], effet: 'etincelles', sens: -1, C: ({t, ev}) => <Bulle t={t - ev('changer')} texte="Changer le monde ✨" style={{left: 150, top: 330}} />},
  {de: 3, a: 3, img: ['03-pige', '01-accroche'], effet: 'pluie', sens: 1, C: ({t, ev}) => <Bulle t={t - ev('piges')} texte="Payée à la pige…" couleur="#cfe6ff" style={{left: 170, top: 330}} />},
  {de: 4, a: 5, img: ['04-carte', '07-enquete', '01-accroche'], sens: -1, C: ({t, ev, m}) => (
    <>
      {t < m[1] ? <Chiffre t={t - ev('carte')} valeur="34 948" legende="cartes de presse en 2024" style={{top: 900}} source="Source : CCIJP, bilan 2024" /> : null}
      {t >= m[1] ? <><LignesVitesse t={t - m[1]} duree={16} couleur={ROSE} /><Chiffre t={t - m[1] - 2} valeur="1 SUR 4" legende="pigiste ou en CDD" couleur={ROSE} style={{top: 900}} /></> : null}
    </>
  )},
  {de: 6, a: 7, img: ['05-salaire', '03-pige'], sens: 1, C: ({t, ev, m}) => (
    <>
      <LignesVitesse t={t} duree={18} />
      <Bulle t={t - 2} texte="LE SALAIRE ?!" couleur={JAUNE} style={{left: 270, top: 300}} />
      <Chiffre t={t - ev('cdi')} valeur="3 560 €" legende="salaire médian brut en CDI" style={{top: 640}} />
      <Chiffre t={t - ev('pigistes')} valeur="1 951 €" legende="médian des pigistes" couleur={CYAN} style={{top: 1040}} source="Source : Afdas, 2023 (via L'Essentiel de l'éco)" />
    </>
  )},
  {de: 8, a: 9, img: ['06-nuit', '03-pige'], effet: 'pluie', sens: -1, C: ({t, ev}) => (
    <>
      <LignesVitesse t={t} duree={18} couleur={CYAN} />
      <Bulle t={t - 2} texte="LES HORAIRES ?!" couleur={CYAN} style={{left: 230, top: 300}} />
      <Bulle t={t - ev('nuits')} texte="🌙 Les nuits" style={{left: 90, top: 760}} />
      <Bulle t={t - ev('dimanches')} texte="📅 Les dimanches" style={{left: 280, top: 900}} />
      <Bulle t={t - ev('feries')} texte="🎉 Les jours fériés" style={{left: 130, top: 1040}} />
    </>
  )},
  {de: 10, a: 10, img: ['07-enquete', '01-accroche'], sens: 1, C: ({t, ev}) => (
    <>
      <Chiffre t={t - ev('mois')} valeur="4 MOIS" legende="pour une enquête" style={{top: 600}} />
      <Bulle t={t - ev('regle')} texte="Règle : tout vérifier 2 fois ✔" couleur={JAUNE} style={{left: 70, top: 1040}} />
    </>
  )},
  {de: 11, a: 11, img: ['08-publication', '01-accroche'], sens: -1, C: ({t, ev}) => (
    <>
      {[0, 1, 2, 3, 4].map((k) => <Bulle key={'i' + k} t={t - ev('insultes') - k * 3} texte="😡" couleur="#ff8a8a" style={{left: 80 + random(`ix${k}`) * 700, top: 300 + random(`iy${k}`) * 380}} />)}
      {[0, 1, 2, 3, 4].map((k) => <Bulle key={'m' + k} t={t - ev('mercis') - k * 3} texte="❤️" couleur="#b9ffcf" style={{left: 80 + random(`mx${k}`) * 700, top: 760 + random(`my${k}`) * 380}} />)}
    </>
  )},
  {de: 12, a: 12, img: ['09-defiance', '08-publication', '01-accroche'], sens: 1, C: ({t, ev}) => (
    <>
      <LignesVitesse t={t - ev('six')} duree={18} couleur={ROSE} />
      <Chiffre t={t - ev('six')} valeur="61 %" legende="des Français méfiants envers les médias" couleur={ROSE} style={{top: 480}} source="Source : baromètre La Croix-Verian, 2026" />
    </>
  )},
  {de: 13, a: 13, img: ['10-sources', '07-enquete'], sens: -1, C: ({t, ev}) => <Bulle t={t - ev('sources')} texte="Mes sources ✔ toujours" couleur={JAUNE} style={{left: 160, top: 330}} />},
  {de: 14, a: 14, img: ['11-fin', '02-debuts', '01-accroche'], effet: 'etincelles', sens: 1, C: ({t, ev}) => <Bulle t={t - ev('ouverts')} texte="Les yeux ouverts 👀" style={{left: 180, top: 1040}} />},
  {de: 15, a: 16, img: ['11-fin', '01-accroche'], sens: -1, C: ({t}) => {
    const s = spring({frame: t, fps: FPS, config: {damping: 10}});
    return (
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,0.45)'}}>
        <div style={{transform: `scale(${s})`, textAlign: 'center'}}>
          <div style={{fontSize: 120}}>💬</div>
          <div style={{fontFamily: BANG, fontSize: 130, letterSpacing: 3, color: JAUNE, WebkitTextStroke: '8px #111', paintOrder: 'stroke fill', lineHeight: 1.05}}>QUEL MÉTIER<br />ENSUITE ?</div>
          <div style={{marginTop: 20, display: 'inline-block', background: '#fff', color: '#111', fontFamily: OSW, fontWeight: 700, fontSize: 52, padding: '6px 34px', border: '6px solid #111', borderRadius: 40}}>Dis-le en commentaire</div>
        </div>
      </AbsoluteFill>
    );
  }},
];
const debutScene = (i: number) => (i === 0 ? 0 : fr(PH[SCENES[i].de].debut) - 4);
const choisir = (liste: string[]) => liste.find((n) => DISPO.includes(n)) ?? DISPO[0];

const Fond: React.FC<{t: number; dur: number; nom: string; sens: number}> = ({t, dur, nom, sens}) => {
  const z = interpolate(t, [0, dur], [1.08, 1.22], c);
  const x = interpolate(t, [0, dur], [-30 * sens, 30 * sens], c);
  const punch = interpolate(t, [0, 6], [1.12, 1], {...c, easing: Easing.out(Easing.cubic)});
  return (
    <AbsoluteFill style={{overflow: 'hidden', background: '#000'}}>
      <Img src={staticFile(`journaliste/${nom}.jpg`)} style={{position: 'absolute', width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${z * punch}) translateX(${x}px)`}} />
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0) 22%, rgba(0,0,0,0) 58%, rgba(0,0,0,0.65) 100%)'}} />
    </AbsoluteFill>
  );
};

// ─── Sous-titres mot à mot ───────────────────────────────────────────────────
type Mot = {m: string; d: number; f: number; k: boolean};
const MOTS = mots as Mot[];
const BLOCS: {i0: number; i1: number}[] = (() => {
  const b: {i0: number; i1: number}[] = [];
  let i0 = 0;
  MOTS.forEach((w, i) => {
    const s = MOTS[i + 1];
    if (!s || i - i0 + 1 >= 3 || /[.,:?!;]$/.test(w.m) || s.d - w.f > 0.35) {
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
  const pop = spring({frame: f - fr(MOTS[b.i0].d - 0.05), fps: FPS, config: {damping: 14, mass: 0.5}});
  return (
    <div style={{position: 'absolute', top: 1420, width: '100%', textAlign: 'center', padding: '0 60px', boxSizing: 'border-box', transform: `scale(${0.85 + 0.15 * pop})`}}>
      {MOTS.slice(b.i0, b.i1 + 1).map((w, k) => (
        <span key={k} style={{fontFamily: BANG, fontSize: 92, letterSpacing: 2, textTransform: 'uppercase', color: w.k ? JAUNE : '#fff', opacity: s >= w.d - 0.03 ? 1 : 0.45,
          WebkitTextStroke: '9px #000', paintOrder: 'stroke fill', margin: '0 10px', display: 'inline-block'}}>{w.m.replace(/[.,:;]+$/, '')}</span>
      ))}
    </div>
  );
};

export const Journaliste: React.FC = () => {
  const [poignee] = useState(() => delayRender('polices'));
  useEffect(() => {
    chargerPolices().then(() => continueRender(poignee));
  }, [poignee]);
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{background: '#000'}}>
      {SCENES.map((sc, i) => {
        const de = debutScene(i);
        const a = i === SCENES.length - 1 ? DUREE_JOURNALISTE : debutScene(i + 1);
        const m = Array.from({length: sc.a - sc.de + 1}, (_, k) => fr(PH[sc.de + k].debut) - de);
        const ev = (n: string) => fr(EV[n] ?? PH[sc.de].debut) - de;
        const t = f - de;
        const flash = interpolate(t, [0, 3], [0.9, 0], c);
        return (
          <Sequence key={i} from={de} durationInFrames={a - de}>
            <Fond t={t} dur={a - de} nom={choisir(sc.img)} sens={sc.sens} />
            {sc.effet === 'pluie' ? <Pluie t={t} /> : null}
            {sc.effet === 'etincelles' ? <Etincelles t={t} /> : null}
            <Trame />
            {sc.C ? <sc.C t={t} dur={a - de} ev={ev} m={m} /> : null}
            <AbsoluteFill style={{background: '#fff', opacity: i === 0 ? 0 : flash}} />
          </Sequence>
        );
      })}
      <div style={{position: 'absolute', top: 170, width: '100%', textAlign: 'center'}}>
        <span style={{background: 'rgba(0,0,0,0.6)', color: '#fff', fontFamily: INTER, fontWeight: 700, fontSize: 26, padding: '8px 22px', borderRadius: 30}}>
          Personnage fictif · chiffres réels · images IA
        </span>
      </div>
      <div style={{position: 'absolute', top: 225, width: '100%', textAlign: 'center', fontFamily: BANG, fontSize: 50, letterSpacing: 3, color: '#fff', WebkitTextStroke: '6px #000', paintOrder: 'stroke fill'}}>
        JOURNALISTE · <span style={{color: JAUNE}}>10 ANS</span>
      </div>
      <SousTitres />
      <Audio src={staticFile('journaliste-mix.wav')} />
    </AbsoluteFill>
  );
};
