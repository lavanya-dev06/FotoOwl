
import { Composition, Sequence } from 'remotion';

const fps = 30;

const VideoComponent = () => {
  return (
    <div style={
      flex: 1,
      backgroundColor: '#0f0f1a',
      justifyContent: 'center',
      alignItems: 'center',
      display: 'flex',
    }>
      
      <Sequence from={ 0 } durationInFrames={ 45 }>
        <div style={
          position: 'absolute',
          width: '100%',
          height: '100%',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          background: 'linear-gradient(135deg, #1a1a2e, #16213e, #0f3460)',
        }>
          <div style={
            fontSize: 72,
            color: '#ffffff',
            textShadow: '3px 3px 6px rgba(0,0,0,0.7)',
            textAlign: 'center',
            padding: '20px 40px',
            fontFamily: 'Georgia, serif',
            fontWeight: 'bold',
          }>
            Let's go!
          </div>
        </div>
      </Sequence>
      <Sequence from={ 30 } durationInFrames={ 45 }>
        <div style={
          position: 'absolute',
          width: '100%',
          height: '100%',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          background: 'linear-gradient(135deg, #1a1a2e, #16213e, #0f3460)',
        }>
          <div style={
            fontSize: 72,
            color: '#ffffff',
            textShadow: '3px 3px 6px rgba(0,0,0,0.7)',
            textAlign: 'center',
            padding: '20px 40px',
            fontFamily: 'Georgia, serif',
            fontWeight: 'bold',
          }>
            Amazing!
          </div>
        </div>
      </Sequence>
      <Sequence from={ 60 } durationInFrames={ 45 }>
        <div style={
          position: 'absolute',
          width: '100%',
          height: '100%',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          background: 'linear-gradient(135deg, #1a1a2e, #16213e, #0f3460)',
        }>
          <div style={
            fontSize: 72,
            color: '#ffffff',
            textShadow: '3px 3px 6px rgba(0,0,0,0.7)',
            textAlign: 'center',
            padding: '20px 40px',
            fontFamily: 'Georgia, serif',
            fontWeight: 'bold',
          }>
            Best day ever!
          </div>
        </div>
      </Sequence>
      <Sequence from={ 90 } durationInFrames={ 45 }>
        <div style={
          position: 'absolute',
          width: '100%',
          height: '100%',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          background: 'linear-gradient(135deg, #1a1a2e, #16213e, #0f3460)',
        }>
          <div style={
            fontSize: 72,
            color: '#ffffff',
            textShadow: '3px 3px 6px rgba(0,0,0,0.7)',
            textAlign: 'center',
            padding: '20px 40px',
            fontFamily: 'Georgia, serif',
            fontWeight: 'bold',
          }>
            So much fun!
          </div>
        </div>
      </Sequence>
      <Sequence from={ 120 } durationInFrames={ 45 }>
        <div style={
          position: 'absolute',
          width: '100%',
          height: '100%',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          background: 'linear-gradient(135deg, #1a1a2e, #16213e, #0f3460)',
        }>
          <div style={
            fontSize: 72,
            color: '#ffffff',
            textShadow: '3px 3px 6px rgba(0,0,0,0.7)',
            textAlign: 'center',
            padding: '20px 40px',
            fontFamily: 'Georgia, serif',
            fontWeight: 'bold',
          }>
            Let's go!
          </div>
        </div>
      </Sequence>
      <Sequence from={ 150 } durationInFrames={ 45 }>
        <div style={
          position: 'absolute',
          width: '100%',
          height: '100%',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          background: 'linear-gradient(135deg, #1a1a2e, #16213e, #0f3460)',
        }>
          <div style={
            fontSize: 72,
            color: '#ffffff',
            textShadow: '3px 3px 6px rgba(0,0,0,0.7)',
            textAlign: 'center',
            padding: '20px 40px',
            fontFamily: 'Georgia, serif',
            fontWeight: 'bold',
          }>
            Amazing!
          </div>
        </div>
      </Sequence>
      <Sequence from={ 180 } durationInFrames={ 45 }>
        <div style={
          position: 'absolute',
          width: '100%',
          height: '100%',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          background: 'linear-gradient(135deg, #1a1a2e, #16213e, #0f3460)',
        }>
          <div style={
            fontSize: 72,
            color: '#ffffff',
            textShadow: '3px 3px 6px rgba(0,0,0,0.7)',
            textAlign: 'center',
            padding: '20px 40px',
            fontFamily: 'Georgia, serif',
            fontWeight: 'bold',
          }>
            Best day ever!
          </div>
        </div>
      </Sequence>
      <Sequence from={ 210 } durationInFrames={ 45 }>
        <div style={
          position: 'absolute',
          width: '100%',
          height: '100%',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          background: 'linear-gradient(135deg, #1a1a2e, #16213e, #0f3460)',
        }>
          <div style={
            fontSize: 72,
            color: '#ffffff',
            textShadow: '3px 3px 6px rgba(0,0,0,0.7)',
            textAlign: 'center',
            padding: '20px 40px',
            fontFamily: 'Georgia, serif',
            fontWeight: 'bold',
          }>
            So much fun!
          </div>
        </div>
      </Sequence>
    </div>
  );
};

export const MyVideo = () => {
  return (
    <Composition
      id="MyVideo"
      component={VideoComponent}
      durationInFrames={ 270 }
      fps={fps}
      width={1920}
      height={1080}
    />
  );
};
