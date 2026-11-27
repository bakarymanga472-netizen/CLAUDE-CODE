import {Composition} from 'remotion';
import {Metier} from './Metier';
import {Journaliste, DUREE_JOURNALISTE} from './Journaliste';
export const RemotionRoot = () => (
  <>
    <Composition id="Metier" component={Metier} durationInFrames={900} fps={30} width={1080} height={1920} />
    <Composition id="Journaliste" component={Journaliste} durationInFrames={DUREE_JOURNALISTE} fps={30} width={1080} height={1920} />
  </>
);
