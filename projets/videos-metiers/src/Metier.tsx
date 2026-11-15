import {AbsoluteFill, interpolate, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Audio} from '@remotion/media';
import phrases from './phrases-metier.json';

const DECALAGE = 0.2; // la voix démarre à 0,2 s
const JAUNE = '#FFD23F';
const police = 'Inter, "Helvetica Neue", Arial, sans-serif';

type Scene = {icone: string; etiquette?: string; valeur: string; detail?: string; couleur?: string; note?: boolean};
const SCENES: Scene[] = [
  {icone: '👩‍⚕️', valeur: 'INFIRMIÈRE', detail: "à l'hôpital : combien elle gagne vraiment ?"},
  {icone: '🎓', etiquette: 'Études', valeur: 'Bac +3', detail: '3 ans en institut de soins infirmiers'},
  {icone: '💶', etiquette: 'Début de carrière', valeur: '≈ 1 700 €', detail: 'net par mois*', note: true},
  {icone: '📈', etiquette: 'Fin de carrière', valeur: "jusqu'à ≈ 3 000 €", detail: 'net par mois*', note: true},
  {icone: '🌙', etiquette: 'Nuits & dimanches', valeur: '+200 à 500 €', detail: 'en plus par mois*', note: true},
  {icone: '🕐', etiquette: 'Horaires', valeur: "Jusqu'à 12 h", detail: 'par journée, même le week‑end'},
  {icone: '✅', etiquette: 'Le plus', valeur: 'Emploi stable et utile', couleur: '#5BE37D'},
  {icone: '❌', etiquette: 'Le moins', valeur: 'La fatigue', couleur: '#FF6B6B'},
  {icone: '👇', valeur: 'Et toi, tu ferais ce métier ?', detail: 'Dis-le en commentaire'},
];

const Carte = ({s, duree, index}: {s: Scene; duree: number; index: number}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const entree = spring({frame, fps, config: {damping: 13, mass: 0.8}});
  const pop = spring({frame: frame - 6, fps, config: {damping: 9}});
  const sortie = interpolate(frame, [duree - 5, duree], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const titre = index === 0;
  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', opacity: sortie}}>
      <div style={{width: 900, padding: '70px 60px', borderRadius: 48, textAlign: 'center',
        background: titre ? 'transparent' : 'rgba(255,255,255,0.10)', border: titre ? 'none' : '3px solid rgba(255,255,255,0.18)',
        transform: `translateY(${interpolate(entree, [0, 1], [140, 0])}px) scale(${interpolate(entree, [0, 1], [0.85, 1])})`}}>
        <div style={{fontSize: titre ? 230 : 150, transform: `scale(${interpolate(pop, [0, 1], [0.4, 1])})`}}>{s.icone}</div>
        {s.etiquette && <div style={{fontFamily: police, fontSize: 52, fontWeight: 700, letterSpacing: 4, textTransform: 'uppercase',
          color: 'rgba(255,255,255,0.75)', marginTop: 20}}>{s.etiquette}</div>}
        <div style={{fontFamily: police, fontWeight: 900, color: s.couleur ?? JAUNE, lineHeight: 1.08, marginTop: 18,
          fontSize: titre ? 128 : s.valeur.length > 14 ? 92 : s.valeur.length > 10 ? 108 : 132, whiteSpace: s.valeur.length > 14 ? 'normal' : 'nowrap', textShadow: '0 8px 30px rgba(0,0,0,.35)'}}>{s.valeur}</div>
        {s.detail && <div style={{fontFamily: police, fontSize: titre ? 62 : 54, fontWeight: 600, color: '#fff', marginTop: 24, lineHeight: 1.25}}>{s.detail}</div>}
      </div>
    </AbsoluteFill>
  );
};

export const Metier = () => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const avance = frame / durationInFrames;
  const actuelle = phrases.findIndex((p, i) => frame / fps >= p.debut + DECALAGE &&
    (i === phrases.length - 1 || frame / fps < phrases[i + 1].debut + DECALAGE));
  const note = actuelle >= 0 && SCENES[actuelle]?.note;
  return (
    <AbsoluteFill style={{background: 'radial-gradient(circle at 30% 20%, #2F6BFF 0%, #133A9E 45%, #071A4A 100%)'}}>
      {[0, 1, 2].map((i) => (
        <div key={i} style={{position: 'absolute', width: 520, height: 520, borderRadius: '50%', background: 'rgba(255,255,255,0.05)',
          left: [-120, 700, 260][i], top: [1400, 200, 1650][i] + Math.sin(frame / 40 + i) * 30}} />
      ))}
      <div style={{position: 'absolute', top: 120, left: 90, right: 90}}>
        <div style={{fontFamily: police, fontSize: 40, fontWeight: 800, letterSpacing: 6, color: 'rgba(255,255,255,0.85)', textAlign: 'center'}}>
          LE MÉTIER À LA LOUPE
        </div>
        <div style={{height: 12, borderRadius: 6, background: 'rgba(255,255,255,0.2)', marginTop: 26}}>
          <div style={{height: 12, borderRadius: 6, width: `${avance * 100}%`, background: JAUNE}} />
        </div>
      </div>
      <Sequence from={Math.round(DECALAGE * fps)} layout="none"><Audio src={staticFile('voix-metier.wav')} /></Sequence>
      {phrases.map((p, i) => {
        const debut = Math.round((p.debut + DECALAGE) * fps);
        const fin = i < phrases.length - 1 ? Math.round((phrases[i + 1].debut + DECALAGE) * fps) : durationInFrames;
        return (
          <Sequence key={i} from={debut} durationInFrames={fin - debut}>
            <Carte s={SCENES[i]} duree={fin - debut} index={i} />
          </Sequence>
        );
      })}
      <div style={{position: 'absolute', bottom: 330, left: 90, right: 90, textAlign: 'center', fontFamily: police, fontSize: 32,
        color: 'rgba(255,255,255,0.7)', opacity: note ? 1 : 0}}>
        *Estimations 2026, hôpital public, prime Ségur incluse
      </div>
    </AbsoluteFill>
  );
};
