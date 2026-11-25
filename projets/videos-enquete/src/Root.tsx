import {Composition} from 'remotion';
import {Enquete, DUREE_ENQUETE} from './Enquete';
export const RemotionRoot = () => (
  <Composition id="Enquete" component={Enquete} durationInFrames={DUREE_ENQUETE} fps={30} width={1080} height={1920} />
);
