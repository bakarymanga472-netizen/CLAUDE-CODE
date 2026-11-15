import {Composition} from 'remotion';
import {Metier} from './Metier';
export const RemotionRoot = () => (
  <Composition id="Metier" component={Metier} durationInFrames={900} fps={30} width={1080} height={1920} />
);
