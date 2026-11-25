import {Composition} from 'remotion';
import {Enquete, DUREE_ENQUETE} from './Enquete';
import {Afrique, DUREE_AFRIQUE} from './Afrique';
export const RemotionRoot = () => (
  <>
    <Composition id="Enquete" component={Enquete} durationInFrames={DUREE_ENQUETE} fps={30} width={1080} height={1920} />
    <Composition id="Afrique" component={Afrique} durationInFrames={DUREE_AFRIQUE} fps={30} width={1080} height={1920} />
  </>
);
