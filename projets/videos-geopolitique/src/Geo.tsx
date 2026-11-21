import React from 'react';
import {AbsoluteFill, Easing, interpolate, interpolateColors, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Audio} from '@remotion/media';
import carte from './carte.json';
import phrases from './phrases-geo.json';

const DECALAGE = 0.2;
const police = 'Inter, "Helvetica Neue", Arial, sans-serif';
const ROUGE = '#E5383B';
const BLEU = '#2F6BFF';
const JAUNE = '#FFD23F';
const CARTE_Y = 210;
const PRESENCE = ['MLI', 'BFA', 'NER', 'CAF', 'LBY'];
const SAHEL = ['MLI', 'BFA', 'NER'];
const VILLES_PRESENCE = ['Bamako', 'Ouagadougou', 'Niamey', 'Bangui', 'Benghazi'];
const VILLES_SOMMET = ['Le Caire', 'Alger', 'Dakar', 'Abuja', 'Kinshasa', 'Luanda', 'Nairobi', 'Addis-Abeba', 'Pretoria', 'Khartoum', 'Rabat', 'Antananarivo', 'Harare', 'Conakry'];
const SOURCES = ['', 'Sources : France 24, Africa News Agency (oct. 2026)', 'Source : France 24 (oct. 2026)',
  'Sources : FOI (Suède, 2026), Congrès américain (CRS)', 'Sources : FOI (Suède, 2026), Congrès américain (CRS)',
  'Retraits français : Mali 2022, Burkina Faso 2023, Niger 2023', 'Source : SIPRI, mars 2026 (armes majeures, 2021-2025)',
  'Sources : Financial Afrik, chiffres russes (2026)', 'Sources : Le Brief, Financial Afrik (2026)', ''];

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

// Début de chaque scène en frames (calé sur la voix)
const useScenes = () => {
  const {fps, durationInFrames} = useVideoConfig();
  const debuts = phrases.map((p) => Math.round((p.debut + DECALAGE) * fps));
  return {debuts, fin: durationInFrames};
};

const Carte: React.FC<{scene: number; t: number}> = ({scene, t}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {debuts} = useScenes();
  const dans = (s: number) => frame - debuts[s];
  const trace = interpolate(frame, [0, 45], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});

  // caméra : zoom sur le Sahel (scènes 4-5), recul et assombrissement pour les graphiques (6-8)
  const sahel = ['Bamako', 'Ouagadougou', 'Niamey'].map((v) => (carte.villes as Record<string, number[]>)[v]);
  const cx = sahel.reduce((a, p) => a + p[0], 0) / 3, cy = sahel.reduce((a, p) => a + p[1], 0) / 3;
  const zoom = interpolate(frame, [debuts[5] - 10, debuts[5] + 20, debuts[6] - 5, debuts[6] + 15], [1, 1.9, 1.9, 1], clamp);
  const fx = interpolate(zoom, [1, 1.9], [0, 1]);
  const tx = fx * (540 - zoom * cx), ty = fx * (520 - zoom * cy);
  const opaCarte = interpolate(frame, [debuts[6] - 5, debuts[6] + 15, debuts[9] - 5, debuts[9] + 15], [1, 0.28, 0.28, 0.7], clamp);

  const couleurPays = (iso: string, afrique: boolean) => {
    if (iso === 'RUS') return interpolateColors(dans(1), [0, 20], ['#1C2440', '#8E1F2C']);
    if (SAHEL.includes(iso) && scene >= 5) return interpolateColors(dans(5), [0, 25, 45], [ROUGE, BLEU, ROUGE]);
    const k = PRESENCE.indexOf(iso);
    if (k >= 0 && scene >= 4) return interpolateColors(dans(4) - k * 7, [0, 12], ['#22305A', ROUGE]);
    return afrique ? '#22305A' : '#161D35';
  };

  return (
    <svg width={1080} height={carte.H} style={{position: 'absolute', top: CARTE_Y, left: 0, opacity: opaCarte}}>
      <g transform={`translate(${tx} ${ty}) scale(${zoom})`}>
        {carte.pays.map((p) => (
          <path key={p.iso + p.c.join()} d={p.d} fill={couleurPays(p.iso, p.afrique)} fillOpacity={p.afrique ? trace : 1}
            stroke={p.afrique ? '#6F86C9' : '#26304F'} strokeWidth={p.afrique ? 1.6 / zoom : 1}
            pathLength={1} strokeDasharray={1} strokeDashoffset={p.afrique ? 1 - trace : 0} />
        ))}
        {/* arcs du sommet : toute l'Afrique converge vers Moscou */}
        {scene >= 2 && VILLES_SOMMET.map((v, i) => {
          const pr = interpolate(dans(2) - i * 3, [0, 22], [0, 1], clamp);
          const sortie = interpolate(dans(3), [0, 12], [1, 0], clamp);
          return <path key={v} d={(carte.arcs as Record<string, string>)[v]} fill="none" stroke="#9FB4FF" strokeWidth={2.2 / zoom}
            strokeOpacity={0.75 * sortie} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - pr} />;
        })}
        {/* arcs de présence militaire */}
        {scene >= 4 && VILLES_PRESENCE.map((v, i) => {
          const pr = interpolate(dans(4) - i * 7, [0, 18], [0, 1], {...clamp, easing: Easing.inOut(Easing.quad)});
          return <path key={v} d={(carte.arcs as Record<string, string>)[v]} fill="none" stroke={ROUGE} strokeWidth={4.5 / zoom}
            strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - pr} />;
        })}
        {/* points des villes */}
        {scene >= 4 && VILLES_PRESENCE.map((v, i) => {
          const [x, y] = (carte.villes as Record<string, number[]>)[v];
          const s = spring({frame: dans(4) - i * 7 - 14, fps, config: {damping: 8}});
          const halo = (frame % 30) / 30;
          return (
            <g key={v}>
              <circle cx={x} cy={y} r={(10 + 26 * halo) / zoom} fill="none" stroke={JAUNE} strokeOpacity={(1 - halo) * s} strokeWidth={3 / zoom} />
              <circle cx={x} cy={y} r={9 * s / zoom} fill={JAUNE} />
            </g>
          );
        })}
        {/* Moscou */}
        {scene >= 1 && (() => {
          const [x, y] = (carte.villes as Record<string, number[]>).Moscou;
          const s = spring({frame: dans(1), fps, config: {damping: 9}});
          const halo = (frame % 36) / 36;
          return (
            <g>
              <circle cx={x} cy={y + 8} r={14 + 40 * halo} fill="none" stroke={ROUGE} strokeOpacity={1 - halo} strokeWidth={4} />
              <circle cx={x} cy={y + 8} r={13 * s} fill={ROUGE} stroke="#fff" strokeWidth={3} />
              <text x={x + 26} y={y + 22} fill="#fff" fontFamily={police} fontWeight={800} fontSize={40} opacity={s}>Moscou</text>
            </g>
          );
        })()}
      </g>
    </svg>
  );
};

const Panneau: React.FC<{children: React.ReactNode}> = ({children}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const e = spring({frame, fps, config: {damping: 14}});
  return (
    <div style={{position: 'absolute', top: 1390, left: 60, right: 60, height: 270, display: 'flex', flexDirection: 'column',
      justifyContent: 'center', alignItems: 'center', textAlign: 'center', fontFamily: police, color: '#fff',
      opacity: e, transform: `translateY(${interpolate(e, [0, 1], [60, 0])}px)`}}>
      {children}
    </div>
  );
};

const Compteur: React.FC<{valeur: number; decimales?: number; suffixe?: string; taille?: number; couleur?: string}> = ({valeur, decimales = 0, suffixe = '', taille = 130, couleur = JAUNE}) => {
  const frame = useCurrentFrame();
  const v = interpolate(frame, [0, 30], [0, valeur], {...clamp, easing: Easing.out(Easing.cubic)});
  return <span style={{fontSize: taille, fontWeight: 900, color: couleur}}>{v.toFixed(decimales).replace('.', ',')}{suffixe}</span>;
};

const Barre: React.FC<{label: string; valeur: number; max: number; texte: string; couleur: string; retard: number}> = ({label, valeur, max, texte, couleur, retard}) => {
  const frame = useCurrentFrame();
  const l = interpolate(frame - retard, [0, 25], [0, valeur / max], {...clamp, easing: Easing.out(Easing.cubic)});
  return (
    <div style={{display: 'flex', alignItems: 'center', width: 940, margin: '10px 0', fontSize: 44, fontWeight: 800}}>
      <div style={{width: 230, textAlign: 'left', whiteSpace: 'nowrap'}}>{label}</div>
      <div style={{flex: 1, height: 54, background: 'rgba(255,255,255,0.08)', borderRadius: 12, overflow: 'hidden'}}>
        <div style={{width: `${l * 100}%`, height: '100%', background: couleur, borderRadius: 12}} />
      </div>
      <div style={{width: 210, textAlign: 'right', whiteSpace: 'nowrap', color: couleur, opacity: l > 0.02 ? 1 : 0}}>{texte}</div>
    </div>
  );
};

const scenesPanneau = (frame: number): React.ReactNode[] => [
  <>
    <div style={{fontSize: 108, fontWeight: 900, letterSpacing: 2, lineHeight: 1}}>LA RUSSIE <span style={{color: ROUGE}}>EN AFRIQUE</span></div>
    <div style={{fontSize: 58, fontWeight: 700, color: JAUNE, marginTop: 22}}>ce qui a vraiment changé</div>
  </>,
  <div style={{display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', width: 940}}>
    {[['2019', 'Sotchi'], ['2023', 'St-Pétersbourg'], ['2026', 'Moscou']].map(([an, lieu], i) => {
      const s = interpolate(frame - i * 14, [0, 12], [0, 1], clamp);
      return (
        <div key={an} style={{opacity: s, transform: `scale(${0.6 + 0.4 * s})`, width: 300}}>
          <div style={{fontSize: 92, fontWeight: 900, color: i === 2 ? JAUNE : '#fff'}}>{an}</div>
          <div style={{fontSize: 40, fontWeight: 600, color: 'rgba(255,255,255,0.8)'}}>{lieu}</div>
        </div>
      );
    })}
  </div>,
  <div style={{display: 'flex', gap: 90}}>
    <div><Compteur valeur={48} /><div style={{fontSize: 42, fontWeight: 700}}>délégations</div></div>
    <div><Compteur valeur={22} couleur={ROUGE} /><div style={{fontSize: 42, fontWeight: 700}}>chefs d'État</div></div>
  </div>,
  <>
    <div style={{fontSize: 96, fontWeight: 900, position: 'relative', opacity: interpolate(frame, [18, 30], [1, 0.35], clamp)}}>
      WAGNER
      <div style={{position: 'absolute', left: 0, top: '52%', height: 10, background: ROUGE, width: `${interpolate(frame, [6, 18], [0, 100], clamp)}%`}} />
    </div>
    <div style={{fontSize: 92, fontWeight: 900, color: JAUNE, whiteSpace: 'nowrap', transform: `translateX(${interpolate(frame, [16, 30], [600, 0], {...clamp, easing: Easing.out(Easing.back(1.4))})}px)`}}>AFRICA CORPS</div>
    <div style={{fontSize: 36, fontWeight: 600, color: 'rgba(255,255,255,0.8)'}}>rattaché au ministère russe de la Défense</div>
  </>,
  <div style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 14, width: 980}}>
    {[['🇲🇱', 'Mali'], ['🇧🇫', 'Burkina Faso'], ['🇳🇪', 'Niger'], ['🇨🇫', 'Centrafrique'], ['🇱🇾', 'Libye']].map(([f, n], i) => {
      const s = interpolate(frame - i * 7, [6, 16], [0, 1], clamp);
      return <div key={n} style={{opacity: s, transform: `scale(${0.5 + 0.5 * s})`, fontSize: 42, fontWeight: 800, padding: '10px 20px',
        borderRadius: 40, background: 'rgba(229,56,59,0.22)', border: `3px solid ${ROUGE}`}}>{f} {n}</div>;
    })}
  </div>,
  <>
    <div style={{fontSize: 120, display: 'flex', alignItems: 'center', gap: 40}}>
      <span style={{opacity: interpolate(frame, [20, 40], [1, 0.3], clamp)}}>🇫🇷</span>
      <span style={{fontSize: 90, color: JAUNE, fontWeight: 900}}>→</span>
      <span style={{transform: `scale(${interpolate(frame, [20, 34], [0.3, 1], clamp)})`}}>🇷🇺</span>
    </div>
    <div style={{fontSize: 48, fontWeight: 800, marginTop: 12}}>Sahel : <span style={{color: BLEU}}>départ</span> de la France, <span style={{color: ROUGE}}>arrivée</span> de la Russie</div>
  </>,
  <>
    <div style={{fontSize: 40, fontWeight: 700, color: 'rgba(255,255,255,0.85)', marginBottom: 14}}>Armes importées par l'Afrique subsaharienne</div>
    <Barre label="🇨🇳 Chine" valeur={22} max={24} texte="22 %" couleur="#F2C94C" retard={4} />
    <Barre label="🇷🇺 Russie" valeur={12} max={24} texte="12 %" couleur={ROUGE} retard={12} />
    <Barre label="🇹🇷 Turquie" valeur={11} max={24} texte="11 %" couleur="#9FB4FF" retard={20} />
  </>,
  <>
    <Compteur valeur={27.8} decimales={1} suffixe=" Md$" taille={140} />
    <div style={{fontSize: 46, fontWeight: 700}}>d'échanges Russie-Afrique en 2025</div>
  </>,
  <>
    <Barre label="🇨🇳 Chine" valeur={348} max={348} texte="348 Md$" couleur="#F2C94C" retard={0} />
    <Barre label="🇷🇺 Russie" valeur={27.8} max={348} texte="28 Md$" couleur={ROUGE} retard={10} />
    <div style={{fontSize: 70, fontWeight: 900, color: JAUNE, marginTop: 10, opacity: interpolate(frame, [26, 36], [0, 1], clamp)}}>12 × moins</div>
  </>,
  <>
    <div style={{fontSize: 78, fontWeight: 900, lineHeight: 1.1}}>Partenaire ou <span style={{color: ROUGE}}>nouvelle influence</span> ?</div>
    <div style={{fontSize: 52, fontWeight: 700, color: JAUNE, marginTop: 20}}>👇 Dis-le en commentaire</div>
  </>,
];

const ScenePanneau: React.FC<{i: number}> = ({i}) => {
  const frame = useCurrentFrame();
  return <Panneau>{scenesPanneau(frame)[i]}</Panneau>;
};

export const Geo = () => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const {debuts} = useScenes();
  let scene = 0;
  debuts.forEach((d, i) => { if (frame >= d) scene = i; });
  const avance = frame / durationInFrames;
  return (
    <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 30%, #18213F 0%, #0B1020 70%)'}}>
      <Carte scene={scene} t={frame / fps} />
      <div style={{position: 'absolute', top: 80, left: 70, right: 70}}>
        <div style={{fontFamily: police, fontSize: 38, fontWeight: 800, letterSpacing: 6, color: 'rgba(255,255,255,0.9)', textAlign: 'center'}}>
          GÉOPOLITIQUE · RUSSIE × AFRIQUE
        </div>
        <div style={{height: 10, borderRadius: 5, background: 'rgba(255,255,255,0.18)', marginTop: 20}}>
          <div style={{height: 10, borderRadius: 5, width: `${avance * 100}%`, background: ROUGE}} />
        </div>
      </div>
      <Sequence from={Math.round(DECALAGE * fps)} layout="none"><Audio src={staticFile('voix-geo.wav')} /></Sequence>
      {debuts.map((d, i) => (
        <Sequence key={i} from={d} durationInFrames={(i < debuts.length - 1 ? debuts[i + 1] : durationInFrames) - d} layout="none">
          <ScenePanneau i={i} />
        </Sequence>
      ))}
      <div style={{position: 'absolute', top: 1672, left: 60, right: 60, textAlign: 'center', fontFamily: police, fontSize: 28,
        color: 'rgba(255,255,255,0.6)'}}>{SOURCES[scene]}</div>
    </AbsoluteFill>
  );
};
