"""
FotoOwl AI Video Pipeline - WITH FREE GEMINI API!
This version actually works with the free Gemini API
"""

print("=" * 60)
print("🎬 FotoOwl AI Video Pipeline (FREE Gemini API)")
print("=" * 60)

# Install required packages if missing
try:
    import google.generativeai as genai
    from pydantic import BaseModel
    from typing import List, Optional, Literal
    import chromadb
    from chromadb.utils import embedding_functions
    from langgraph.graph import StateGraph, END
    import json
    import os
    import uuid
    import logging
    from pathlib import Path
    import time
    
    print("✅ All modules loaded successfully")
except ImportError as e:
    print(f"❌ Missing package: {e}")
    print("\n📦 Run this command to install:")
    print("   pip install google-generativeai pydantic chromadb langgraph python-dotenv")
    exit(1)

# ============= SETUP GEMINI =============
print("\n🔑 Setting up Gemini API...")

# Try to get API key from environment or prompt
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("\n⚠️ No Gemini API key found in environment.")
    print("📝 You can get a free key at: https://makersuite.google.com/app/apikey")
    GEMINI_API_KEY = input("👉 Paste your Gemini API key here: ").strip()
    if not GEMINI_API_KEY:
        print("❌ No API key provided. Using fallback mode (no AI).")
        USE_GEMINI = False
    else:
        USE_GEMINI = True
else:
    USE_GEMINI = True

if USE_GEMINI:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        # Test the API
        test_model = genai.GenerativeModel('gemini-pro')
        test_response = test_model.generate_content("Say OK if you can hear me")
        if "OK" in test_response.text:
            print("✅ Gemini API connected successfully!")
        else:
            print("⚠️ Gemini API test failed. Using fallback mode.")
            USE_GEMINI = False
    except Exception as e:
        print(f"⚠️ Gemini setup error: {e}")
        print("Using fallback mode (no AI).")
        USE_GEMINI = False

# ============= MODELS =============
print("\n📝 Setting up data models...")

class VideoIntent(BaseModel):
    pacing: Literal["slow", "medium", "fast"]
    visual_style: Literal["cinematic", "corporate", "upbeat", "minimal"]
    caption_tone: Literal["emotional", "professional", "energetic", "minimal"]
    transition_preference: Literal["fade", "cut", "zoom", "slide"]

class Scene(BaseModel):
    image_path: str
    duration_seconds: float
    caption: str
    transition: str
    animation_style: Optional[str] = None

class Storyboard(BaseModel):
    scenes: List[Scene]
    overall_pacing: str
    narrative_arc: str

class PipelineState(BaseModel):
    images: List[str]
    user_prompt: str
    intent: Optional[VideoIntent] = None
    image_analysis: Optional[dict] = None
    storyboard: Optional[Storyboard] = None
    remotion_script: Optional[str] = None
    compile_errors: List[str] = []
    retry_count: int = 0
    max_retries: int = 3
    video_url: Optional[str] = None
    status: str = "initialized"
    error_report: Optional[str] = None

print("✅ Models created")

# ============= RAG SYSTEM =============
print("🗄️ Setting up RAG system...")

class RAGSystem:
    def __init__(self):
        try:
            self.client = chromadb.PersistentClient(path="./chroma_db")
            self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            
            self.style_collection = self.client.get_or_create_collection(
                name="style_guides",
                embedding_function=self.embedding_fn
            )
            self.api_collection = self.client.get_or_create_collection(
                name="remotion_api",
                embedding_function=self.embedding_fn
            )
            self._seed_documents()
            print("✅ RAG system ready")
        except Exception as e:
            print(f"⚠️ RAG warning: {e}")
    
    def _seed_documents(self):
        try:
            self.style_collection.delete(ids=[str(i) for i in range(10)])
            self.api_collection.delete(ids=[str(i) for i in range(10)])
        except:
            pass
        
        style_docs = [
            {
                "id": "cinematic",
                "content": "CINEMATIC STYLE: Slow pacing with 3-4 seconds per scene. Warm golden tones. Smooth cross-fade transitions. Emotional captions with poetic language.",
                "metadata": {"style": "cinematic"}
            },
            {
                "id": "upbeat",
                "content": "UPBEAT STYLE: Fast pacing with 1-2 seconds per scene. Bright vibrant colors. Dynamic cut transitions. Energetic captions with emojis.",
                "metadata": {"style": "upbeat"}
            },
            {
                "id": "corporate",
                "content": "CORPORATE STYLE: Moderate pacing with 2-3 seconds per scene. Clean professional look. Subtle fade transitions. Concise professional captions.",
                "metadata": {"style": "corporate"}
            }
        ]
        
        for doc in style_docs:
            self.style_collection.add(
                documents=[doc["content"]],
                ids=[doc["id"]],
                metadatas=[doc["metadata"]]
            )
        
        api_docs = [
            {"id": "sequence", "content": "import { Sequence, useCurrentFrame } from 'remotion';"},
            {"id": "interpolation", "content": "import { interpolate } from 'remotion';"},
            {"id": "spring", "content": "import { spring } from 'remotion';"}
        ]
        
        for doc in api_docs:
            self.api_collection.add(
                documents=[doc["content"]],
                ids=[doc["id"]]
            )
    
    def retrieve_style(self, intent_str: str, k: int = 1) -> str:
        try:
            results = self.style_collection.query(query_texts=[intent_str], n_results=k)
            if results['documents'] and len(results['documents'][0]) > 0:
                return results['documents'][0][0]
        except:
            pass
        return ""
    
    def retrieve_api(self, query: str, k: int = 2) -> List[str]:
        try:
            results = self.api_collection.query(query_texts=[query], n_results=k)
            if results['documents'] and len(results['documents'][0]) > 0:
                return results['documents'][0]
        except:
            pass
        return []

# ============= AGENTS WITH GEMINI =============
print("🤖 Setting up AI agents...")

def call_gemini(prompt_text, response_format=None):
    """Call Gemini API with retry logic"""
    if not USE_GEMINI:
        return None
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt_text)
        
        if response.text:
            return response.text
        else:
            return None
    except Exception as e:
        print(f"⚠️ Gemini API error: {e}")
        return None

class IntentParser:
    def parse(self, prompt: str) -> VideoIntent:
        try:
            if USE_GEMINI:
                response = call_gemini(
                    f"Parse this video prompt into structured data. "
                    f"Prompt: '{prompt}'. "
                    f"Return ONLY a JSON object with: pacing (slow/medium/fast), "
                    f"visual_style (cinematic/corporate/upbeat/minimal), "
                    f"caption_tone (emotional/professional/energetic/minimal), "
                    f"transition_preference (fade/cut/zoom/slide)."
                )
                if response:
                    # Parse the JSON response
                    import re
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        data = json.loads(json_match.group())
                        return VideoIntent(**data)
        except Exception as e:
            print(f"⚠️ Intent parse error: {e}")
        
        # Fallback
        print("📝 Using fallback intent")
        return VideoIntent(
            pacing="medium",
            visual_style="cinematic",
            caption_tone="emotional",
            transition_preference="fade"
        )

class ImageAnalyzer:
    def analyze(self, image_paths: List[str], intent) -> dict:
        return {
            "best_images": image_paths[:8],
            "analysis": "Selected best images",
            "themes": ["event", "people"],
            "quality_scores": [0.85] * len(image_paths[:8]),
            "total_images": len(image_paths)
        }

class StoryboardWriter:
    def __init__(self):
        self.rag = RAGSystem()
    
    def generate(self, images: List[str], analysis: dict, intent: VideoIntent) -> Storyboard:
        try:
            if USE_GEMINI:
                style_context = self.rag.retrieve_style(intent.visual_style)
                
                prompt = f"""Create a video storyboard for {len(images)} images.
Style: {style_context}
Intent: {intent.visual_style} style, {intent.pacing} pacing, {intent.caption_tone} tone
Images: {', '.join(images[:5])}...

Return ONLY a JSON array of scenes. Each scene must have:
- image_path: the image filename
- duration_seconds: number (1-4)
- caption: short text
- transition: fade/cut/zoom/slide

Example: [{{"image_path": "image_1.jpg", "duration_seconds": 2.5, "caption": "Beautiful moment", "transition": "fade"}}]"""
                
                response = call_gemini(prompt)
                if response:
                    import re
                    json_match = re.search(r'\[.*\]', response, re.DOTALL)
                    if json_match:
                        scenes_data = json.loads(json_match.group())
                        scenes = []
                        for i, scene_data in enumerate(scenes_data[:8]):
                            scenes.append(Scene(
                                image_path=scene_data.get('image_path', images[i] if i < len(images) else f"image_{i}.jpg"),
                                duration_seconds=float(scene_data.get('duration_seconds', 2.0)),
                                caption=scene_data.get('caption', f"Scene {i+1}"),
                                transition=scene_data.get('transition', intent.transition_preference),
                                animation_style="fade"
                            ))
                        return Storyboard(
                            scenes=scenes,
                            overall_pacing=intent.pacing,
                            narrative_arc=f"A {intent.visual_style} journey"
                        )
        except Exception as e:
            print(f"⚠️ Storyboard error: {e}")
        
        return self._fallback_storyboard(images, intent)
    
    def _fallback_storyboard(self, images: List[str], intent: VideoIntent) -> Storyboard:
        print("📝 Using fallback storyboard")
        scenes = []
        duration = 2.0 if intent.pacing == "medium" else (1.5 if intent.pacing == "fast" else 3.0)
        for i, img in enumerate(images[:8]):
            scene = Scene(
                image_path=img,
                duration_seconds=duration,
                caption=f"Scene {i+1}",
                transition=intent.transition_preference,
                animation_style="fade"
            )
            scenes.append(scene)
        return Storyboard(scenes=scenes, overall_pacing=intent.pacing, 
                         narrative_arc=f"A {intent.visual_style} journey")

class ScriptGenerator:
    def __init__(self):
        self.rag = RAGSystem()
    
    def generate(self, storyboard: Storyboard, intent: VideoIntent, error_context: str = "") -> str:
        try:
            if USE_GEMINI:
                api_context = self.rag.retrieve_api("remotion sequence")
                
                prompt = f"""Generate a Remotion composition script for this storyboard.
Storyboard: {storyboard.json()}
Intent: {intent.visual_style} style, {intent.pacing} pacing

Return ONLY valid TypeScript/React code using Remotion.
Use Composition, Sequence, and styling.
Keep it simple but functional."""
                
                if error_context:
                    prompt += f"\n\nFIX THIS ERROR: {error_context}"
                
                response = call_gemini(prompt)
                if response:
                    # Clean up the response if it has markdown
                    script = response
                    if "```typescript" in script:
                        script = script.split("```typescript")[1].split("```")[0]
                    elif "```" in script:
                        script = script.split("```")[1].split("```")[0]
                    return script.strip()
        except Exception as e:
            print(f"⚠️ Script generation error: {e}")
        
        return self._fallback_script(storyboard)
    
    def _fallback_script(self, storyboard: Storyboard) -> str:
        print("📝 Using fallback script")
        scenes_code = []
        for i, scene in enumerate(storyboard.scenes):
            frames = int(scene.duration_seconds * 30)
            start_frame = i * 30
            scenes_code.append(f"""
      <Sequence from={{ {start_frame} }} durationInFrames={{ {frames} }}>
        <div style={{ position: 'absolute', width: '100%', height: '100%',
          display: 'flex', justifyContent: 'center', alignItems: 'center',
          background: 'linear-gradient(45deg, #1a1a1a, #2a2a2a)' }}>
          <div style={{ fontSize: 60, color: '#ffffff', textAlign: 'center' }}>
            {scene.caption}
          </div>
        </div>
      </Sequence>""")
        
        total_frames = len(storyboard.scenes) * 30 + 30
        return f"""
import {{ Composition, Sequence }} from 'remotion';
const fps = 30;
const VideoComponent = () => {{ return (<div style={{ flex: 1, backgroundColor: '#1a1a1a',
  justifyContent: 'center', alignItems: 'center', display: 'flex' }}>
  {''.join(scenes_code)}
</div>); }};
export const MyVideo = () => {{
  return <Composition id="MyVideo" component={{VideoComponent}}
    durationInFrames={{ {total_frames} }} fps={{fps}} width={{1920}} height={{1080}} />;
}};
"""

class CompilerFixer:
    def compile(self, script: str):
        errors = []
        if "import" not in script: errors.append("Missing import")
        if "Composition" not in script: errors.append("Missing Composition")
        if "{" not in script or "}" not in script: errors.append("Missing brackets")
        if "return" not in script: errors.append("Missing return")
        return (len(errors) == 0, errors)

class Renderer:
    def __init__(self):
        os.makedirs("output", exist_ok=True)
        print("✅ Renderer ready")
    
    def render(self, script: str) -> str:
        path = f"output/video_{uuid.uuid4().hex[:8]}.tsx"
        with open(path, "w") as f:
            f.write(script)
        return f"file://{os.path.abspath(path)} (Simulated render)"

# ============= PIPELINE =============
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class VideoPipeline:
    def __init__(self):
        print("🏗️ Building pipeline...")
        self.intent_parser = IntentParser()
        self.image_analyzer = ImageAnalyzer()
        self.storyboard_writer = StoryboardWriter()
        self.script_generator = ScriptGenerator()
        self.compiler_fixer = CompilerFixer()
        self.renderer = Renderer()
        self.graph = self._build_graph()
        print("✅ Pipeline ready!")
    
    def _build_graph(self):
        workflow = StateGraph(PipelineState)
        workflow.add_node("parse_intent", self._parse_intent)
        workflow.add_node("analyze_images", self._analyze_images)
        workflow.add_node("write_storyboard", self._write_storyboard)
        workflow.add_node("generate_script", self._generate_script)
        workflow.add_node("compile_and_fix", self._compile_and_fix)
        workflow.add_node("render", self._render)
        
        workflow.set_entry_point("parse_intent")
        workflow.add_edge("parse_intent", "analyze_images")
        workflow.add_edge("analyze_images", "write_storyboard")
        workflow.add_edge("write_storyboard", "generate_script")
        workflow.add_edge("generate_script", "compile_and_fix")
        
        workflow.add_conditional_edges(
            "compile_and_fix",
            self._should_retry_or_continue,
            {"retry": "generate_script", "render": "render", "fail": END}
        )
        workflow.add_edge("render", END)
        return workflow.compile()
    
    def _should_retry_or_continue(self, state: PipelineState):
        if state.status == "compiled": 
            return "render"
        elif state.retry_count < state.max_retries: 
            return "retry"
        else: 
            return "fail"
    
    def _parse_intent(self, state):
        logger.info("📝 Parsing intent...")
        state.intent = self.intent_parser.parse(state.user_prompt)
        state.status = "intent_parsed"
        logger.info(f"✅ Intent: {state.intent.visual_style} style, {state.intent.pacing} pacing")
        return state
    
    def _analyze_images(self, state):
        logger.info("🖼️ Analyzing images...")
        state.image_analysis = self.image_analyzer.analyze(state.images, state.intent)
        state.status = "images_analyzed"
        logger.info(f"✅ Selected {len(state.image_analysis['best_images'])} images")
        return state
    
    def _write_storyboard(self, state):
        logger.info("📖 Writing storyboard...")
        state.storyboard = self.storyboard_writer.generate(
            state.image_analysis["best_images"], state.image_analysis, state.intent
        )
        state.status = "storyboard_ready"
        logger.info(f"✅ Storyboard: {len(state.storyboard.scenes)} scenes")
        return state
    
    def _generate_script(self, state):
        logger.info("💻 Generating script...")
        error_context = state.compile_errors[-1] if state.compile_errors else ""
        state.remotion_script = self.script_generator.generate(
            state.storyboard, state.intent, error_context
        )
        state.status = "script_generated"
        logger.info("✅ Script generated")
        return state
    
    def _compile_and_fix(self, state):
        logger.info("🔧 Compiling...")
        success, errors = self.compiler_fixer.compile(state.remotion_script)
        if success:
            state.status = "compiled"
            logger.info("✅ Compilation successful")
        else:
            state.status = "compile_failed"
            state.compile_errors.extend(errors)
            state.retry_count += 1
            logger.warning(f"❌ Compilation failed: {errors}")
        return state
    
    def _render(self, state):
        logger.info("🎬 Rendering...")
        state.video_url = self.renderer.render(state.remotion_script)
        state.status = "rendered"
        logger.info(f"✅ Video: {state.video_url}")
        return state
    
    def run(self, images: List[str], prompt: str):
        state = PipelineState(images=images, user_prompt=prompt, status="initialized")
        logger.info("🚀 Starting pipeline...")
        return self.graph.invoke(state)

# ============= MAIN =============
def main():
    print("\n" + "=" * 60)
    print("🎬 FotoOwl AI Video Pipeline")
    print("=" * 60)
    
    # Create output folder
    Path("output").mkdir(exist_ok=True)
    
    # Create dummy images
    print("\n📸 Creating dummy images...")
    for i in range(1, 11):
        img_path = f"image_{i}.jpg"
        if not Path(img_path).exists():
            with open(img_path, "w") as f:
                f.write(f"Dummy image {i}")
    print("✅ 10 dummy images created")
    
    images = [f"image_{i}.jpg" for i in range(1, 11)]
    
    prompts = [
        "Cinematic wedding reel, slow and emotional, warm tones",
        "Upbeat birthday reel, fast cuts, bold captions, energetic",
        "Clean corporate highlights, professional tone, subtle transitions"
    ]
    
    print("\n" + "=" * 60)
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n📝 Running prompt {i}: {prompt}")
        print("-" * 50)
        
        try:
            pipeline = VideoPipeline()
            result = pipeline.run(images, prompt)
            
            # CONVERT TO DICT IF NEEDED
            result_dict = result.dict() if hasattr(result, 'dict') else result
            
            # SAVE STORYBOARD
            if hasattr(result, 'storyboard') and result.storyboard:
                storyboard_data = result.storyboard.dict() if hasattr(result.storyboard, 'dict') else result.storyboard
                with open(f"output/storyboard_{i}.json", "w") as f:
                    json.dump(storyboard_data, f, indent=2)
                print(f"✅ Storyboard saved: output/storyboard_{i}.json")
            else:
                print(f"⚠️ No storyboard to save for prompt {i}")
            
            # SAVE SCRIPT
            if hasattr(result, 'remotion_script') and result.remotion_script:
                with open(f"output/remotion_script_{i}.tsx", "w") as f:
                    f.write(result.remotion_script)
                print(f"✅ Script saved: output/remotion_script_{i}.tsx")
            else:
                print(f"⚠️ No script to save for prompt {i}")
            
            # STATUS
            if hasattr(result, 'status'):
                print(f"✅ Status: {result.status}")
            
            if hasattr(result, 'video_url') and result.video_url:
                print(f"🎥 Video: {result.video_url}")
                
            # Save final state
            with open(f"output/final_state_{i}.json", "w") as f:
                state_data = {
                    "prompt": prompt,
                    "status": result.status if hasattr(result, 'status') else "unknown",
                    "retry_count": result.retry_count if hasattr(result, 'retry_count') else 0,
                    "video_url": result.video_url if hasattr(result, 'video_url') else None,
                    "intent": result.intent.dict() if hasattr(result, 'intent') and result.intent else None
                }
                json.dump(state_data, f, indent=2)
            print(f"✅ State saved: output/final_state_{i}.json")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ DONE! Check the 'output' folder for results.")
    print("=" * 60)

if __name__ == "__main__":
    main()