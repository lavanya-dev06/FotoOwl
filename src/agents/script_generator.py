from langchain_openai import ChatOpenAI
from src.rag.vector_store import RAGSystem
from src.models import Storyboard, VideoIntent

class ScriptGenerator:
    def __init__(self):
        self.model = ChatOpenAI(
            model="gpt-4o-mini",
            openai_api_base="https://keylessai.thryx.workers.dev/v1",
            openai_api_key="not-needed",
            temperature=0.3
        )
        self.rag = RAGSystem()
    
    def generate(self, storyboard: Storyboard, intent: VideoIntent, error_context: str = "") -> str:
        api_context = self.rag.retrieve_api("remotion sequence interpolation spring")
        
        try:
            response = self.model.invoke(
                f"Generate a Remotion composition script for this storyboard. "
                f"Storyboard: {storyboard}. "
                f"Intent: {intent}. "
                f"API Examples: {api_context}. "
                f"{f'Previous error to fix: {error_context}' if error_context else ''}"
            )
            return response.content
        except Exception as e:
            print(f"⚠️ API error, using fallback: {e}")
            return self._fallback_script(storyboard)
    
    def _fallback_script(self, storyboard: Storyboard) -> str:
        scenes_code = []
        for i, scene in enumerate(storyboard.scenes):
            frames = int(scene.duration_seconds * 30)
            start_frame = i * 30
            scene_code = f"""
      <Sequence from={{ {start_frame} }} durationInFrames={{ {frames} }}>
        <div style={{
          position: 'absolute',
          width: '100%',
          height: '100%',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          background: 'linear-gradient(45deg, #1a1a1a, #2a2a2a)',
        }}>
          <div style={{
            fontSize: 60,
            color: '#ffffff',
            textShadow: '2px 2px 4px rgba(0,0,0,0.5)',
            textAlign: 'center',
            padding: 20,
          }}>
            {scene.caption}
          </div>
        </div>
      </Sequence>"""
            scenes_code.append(scene_code)
        
        total_frames = len(storyboard.scenes) * 30 + 30
        
        return f"""
import {{ Composition, Sequence }} from 'remotion';

const fps = 30;

const VideoComponent = () => {{
  return (
    <div style={{
      flex: 1,
      backgroundColor: '#1a1a1a',
      justifyContent: 'center',
      alignItems: 'center',
      display: 'flex',
    }}>
      {''.join(scenes_code)}
    </div>
  );
}};

export const MyVideo = () => {{
  return (
    <Composition
      id="MyVideo"
      component={{VideoComponent}}
      durationInFrames={{ {total_frames} }}
      fps={{fps}}
      width={{1920}}
      height={{1080}}
    />
  );
}};
"""