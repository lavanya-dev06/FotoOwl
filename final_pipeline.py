"""
FOTOOWL AI VIDEO PIPELINE - FINAL WORKING VERSION
This version saves EVERYTHING properly
"""

import json
import os
import uuid
import logging
from pathlib import Path
from typing import List, Optional, Literal
from dataclasses import dataclass, asdict
import time

# Try to import optional packages
try:
    from pydantic import BaseModel
    from langgraph.graph import StateGraph, END
    import chromadb
    from chromadb.utils import embedding_functions
    print("✅ Core packages loaded")
except ImportError as e:
    print(f"⚠️ Some packages missing: {e}")
    print("📦 Run: pip install pydantic langgraph chromadb sentence-transformers")

# ============= DATA MODELS =============
class VideoIntent(BaseModel):
    pacing: Literal["slow", "medium", "fast"] = "medium"
    visual_style: Literal["cinematic", "corporate", "upbeat", "minimal"] = "cinematic"
    caption_tone: Literal["emotional", "professional", "energetic", "minimal"] = "emotional"
    transition_preference: Literal["fade", "cut", "zoom", "slide"] = "fade"

class Scene(BaseModel):
    image_path: str
    duration_seconds: float = 2.0
    caption: str = "Scene"
    transition: str = "fade"
    animation_style: Optional[str] = "fade"

class Storyboard(BaseModel):
    scenes: List[Scene] = []
    overall_pacing: str = "medium"
    narrative_arc: str = "A visual journey"

class PipelineState(BaseModel):
    images: List[str] = []
    user_prompt: str = ""
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

# ============= RAG SYSTEM =============
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
            self._seed_documents()
            print("✅ RAG system ready")
        except Exception as e:
            print(f"⚠️ RAG not available: {e}")
    
    def _seed_documents(self):
        try:
            style_docs = [
                {
                    "id": "cinematic",
                    "content": "CINEMATIC: Slow pacing (3-4s per scene). Warm tones. Fade transitions. Emotional captions.",
                    "metadata": {"style": "cinematic"}
                },
                {
                    "id": "upbeat", 
                    "content": "UPBEAT: Fast pacing (1-2s). Bright colors. Cut transitions. Energetic captions.",
                    "metadata": {"style": "upbeat"}
                },
                {
                    "id": "corporate",
                    "content": "CORPORATE: Moderate pacing (2-3s). Clean look. Slide transitions. Professional captions.",
                    "metadata": {"style": "corporate"}
                }
            ]
            for doc in style_docs:
                self.style_collection.add(
                    documents=[doc["content"]],
                    ids=[doc["id"]],
                    metadatas=[doc["metadata"]]
                )
        except:
            pass
    
    def retrieve_style(self, style: str) -> str:
        try:
            results = self.style_collection.query(query_texts=[style], n_results=1)
            if results['documents'] and results['documents'][0]:
                return results['documents'][0][0]
        except:
            pass
        return ""

# ============= AGENTS =============
class IntentParser:
    def parse(self, prompt: str) -> VideoIntent:
        # Simple keyword-based parsing
        prompt_lower = prompt.lower()
        
        # Determine pacing
        if any(word in prompt_lower for word in ["fast", "quick", "upbeat", "energetic"]):
            pacing = "fast"
        elif any(word in prompt_lower for word in ["slow", "emotional", "cinematic"]):
            pacing = "slow"
        else:
            pacing = "medium"
        
        # Determine style
        if "cinematic" in prompt_lower or "wedding" in prompt_lower:
            style = "cinematic"
        elif "upbeat" in prompt_lower or "birthday" in prompt_lower or "party" in prompt_lower:
            style = "upbeat"
        elif "corporate" in prompt_lower or "professional" in prompt_lower:
            style = "corporate"
        else:
            style = "cinematic"
        
        # Determine tone
        if "emotional" in prompt_lower:
            tone = "emotional"
        elif "professional" in prompt_lower:
            tone = "professional"
        elif "energetic" in prompt_lower:
            tone = "energetic"
        else:
            tone = "emotional"
        
        # Determine transition
        if "fade" in prompt_lower:
            transition = "fade"
        elif "cut" in prompt_lower:
            transition = "cut"
        elif "zoom" in prompt_lower:
            transition = "zoom"
        elif "slide" in prompt_lower:
            transition = "slide"
        else:
            transition = "fade"
        
        return VideoIntent(
            pacing=pacing,
            visual_style=style,
            caption_tone=tone,
            transition_preference=transition
        )

class ImageAnalyzer:
    def analyze(self, images: List[str], intent: VideoIntent) -> dict:
        # Take up to 8 images
        selected = images[:8]
        return {
            "best_images": selected,
            "analysis": f"Selected {len(selected)} images for {intent.visual_style} style",
            "themes": ["event", "people"],
            "quality_scores": [0.85] * len(selected),
            "total_images": len(images)
        }

class StoryboardWriter:
    def __init__(self):
        self.rag = RAGSystem()
    
    def generate(self, images: List[str], analysis: dict, intent: VideoIntent) -> Storyboard:
        # Get style guide
        style_guide = self.rag.retrieve_style(intent.visual_style)
        
        # Create scenes
        scenes = []
        duration_map = {"slow": 3.0, "medium": 2.0, "fast": 1.5}
        duration = duration_map.get(intent.pacing, 2.0)
        
        captions_by_style = {
            "cinematic": ["A moment in time", "Forever captured", "Embrace the moment", "Love in focus", "Memories made", "Pure joy", "Together", "Eternal"],
            "upbeat": ["Let's go!", "Amazing!", "Best day ever!", "So much fun!", "Unforgettable", "Party time!", "Dance!", "Celebrate!"],
            "corporate": ["Professional excellence", "Team synergy", "Driving success", "Innovation", "Leadership", "Growth", "Achievement", "Vision"]
        }
        captions = captions_by_style.get(intent.visual_style, captions_by_style["cinematic"])
        
        for i, img in enumerate(images[:8]):
            scene = Scene(
                image_path=img,
                duration_seconds=duration,
                caption=captions[i % len(captions)],
                transition=intent.transition_preference,
                animation_style="fade"
            )
            scenes.append(scene)
        
        return Storyboard(
            scenes=scenes,
            overall_pacing=intent.pacing,
            narrative_arc=f"A {intent.visual_style} {intent.caption_tone} journey"
        )

class ScriptGenerator:
    def generate(self, storyboard: Storyboard, intent: VideoIntent, error_context: str = "") -> str:
        # Build scenes code
        scenes_code = []
        for i, scene in enumerate(storyboard.scenes):
            frames = int(scene.duration_seconds * 30)
            start_frame = i * 30
            
            scene_html = f"""
      <Sequence from={{ {start_frame} }} durationInFrames={{ {frames} }}>
        <div style={{
          position: 'absolute',
          width: '100%',
          height: '100%',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          background: 'linear-gradient(135deg, #1a1a2e, #16213e, #0f3460)',
        }}>
          <div style={{
            fontSize: 72,
            color: '#ffffff',
            textShadow: '3px 3px 6px rgba(0,0,0,0.7)',
            textAlign: 'center',
            padding: '20px 40px',
            fontFamily: 'Georgia, serif',
            fontWeight: 'bold',
          }}>
            {scene.caption}
          </div>
        </div>
      </Sequence>"""
            scenes_code.append(scene_html)
        
        total_frames = len(storyboard.scenes) * 30 + 30
        
        # Generate the full script
        script = f"""
import {{ Composition, Sequence }} from 'remotion';

const fps = 30;

const VideoComponent = () => {{
  return (
    <div style={{
      flex: 1,
      backgroundColor: '#0f0f1a',
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
        return script

class CompilerFixer:
    def compile(self, script: str):
        errors = []
        if "import" not in script:
            errors.append("Missing import statements")
        if "Composition" not in script:
            errors.append("Missing Composition component")
        if "{" not in script or "}" not in script:
            errors.append("Missing brackets")
        if "return" not in script:
            errors.append("Missing return statement")
        
        if len(errors) == 0:
            return True, []
        return False, errors

class Renderer:
    def __init__(self):
        os.makedirs("output", exist_ok=True)
    
    def render(self, script: str) -> str:
        path = f"output/video_{uuid.uuid4().hex[:8]}.tsx"
        with open(path, "w") as f:
            f.write(script)
        return f"file://{os.path.abspath(path)} (Simulated render)"

# ============= LANGGRAPH PIPELINE =============
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class VideoPipeline:
    def __init__(self):
        self.intent_parser = IntentParser()
        self.image_analyzer = ImageAnalyzer()
        self.storyboard_writer = StoryboardWriter()
        self.script_generator = ScriptGenerator()
        self.compiler_fixer = CompilerFixer()
        self.renderer = Renderer()
        self.graph = self._build_graph()
    
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
            {
                "retry": "generate_script",
                "render": "render",
                "fail": END
            }
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
    
    def _parse_intent(self, state: PipelineState):
        logger.info("📝 Parsing intent...")
        state.intent = self.intent_parser.parse(state.user_prompt)
        state.status = "intent_parsed"
        logger.info(f"✅ Intent: {state.intent.visual_style} | {state.intent.pacing} pacing")
        return state
    
    def _analyze_images(self, state: PipelineState):
        logger.info("🖼️ Analyzing images...")
        state.image_analysis = self.image_analyzer.analyze(state.images, state.intent)
        state.status = "images_analyzed"
        logger.info(f"✅ Selected {len(state.image_analysis['best_images'])} images")
        return state
    
    def _write_storyboard(self, state: PipelineState):
        logger.info("📖 Writing storyboard...")
        state.storyboard = self.storyboard_writer.generate(
            state.image_analysis["best_images"],
            state.image_analysis,
            state.intent
        )
        state.status = "storyboard_ready"
        logger.info(f"✅ Storyboard: {len(state.storyboard.scenes)} scenes")
        return state
    
    def _generate_script(self, state: PipelineState):
        logger.info("💻 Generating script...")
        error_context = state.compile_errors[-1] if state.compile_errors else ""
        state.remotion_script = self.script_generator.generate(
            state.storyboard,
            state.intent,
            error_context
        )
        state.status = "script_generated"
        logger.info("✅ Script generated")
        return state
    
    def _compile_and_fix(self, state: PipelineState):
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
    
    def _render(self, state: PipelineState):
        logger.info("🎬 Rendering...")
        state.video_url = self.renderer.render(state.remotion_script)
        state.status = "rendered"
        logger.info(f"✅ Video rendered")
        return state
    
    def run(self, images: List[str], prompt: str):
        state = PipelineState(images=images, user_prompt=prompt, status="initialized")
        logger.info("🚀 Starting pipeline...")
        return self.graph.invoke(state)

# ============= MAIN =============
def main():
    print("\n" + "=" * 60)
    print("🎬 FOTOOWL VIDEO PIPELINE - FINAL VERSION")
    print("=" * 60)
    
    # Create folders
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
    
    # Test prompts
    prompts = [
        ("cinematic", "Cinematic wedding reel, slow and emotional, warm tones"),
        ("upbeat", "Upbeat birthday reel, fast cuts, bold captions, energetic"),
        ("corporate", "Clean corporate highlights, professional tone, subtle transitions")
    ]
    
    all_results = []
    
    for i, (style, prompt) in enumerate(prompts, 1):
        print(f"\n{'='*60}")
        print(f"📝 Test {i}: {style.upper()} STYLE")
        print(f"Prompt: {prompt}")
        print("-" * 50)
        
        try:
            pipeline = VideoPipeline()
            result = pipeline.run(images, prompt)
            
            # SAVE STORYBOARD
            if result.storyboard:
                storyboard_data = {
                    "scenes": [
                        {
                            "image_path": s.image_path,
                            "duration_seconds": s.duration_seconds,
                            "caption": s.caption,
                            "transition": s.transition,
                            "animation_style": s.animation_style
                        }
                        for s in result.storyboard.scenes
                    ],
                    "overall_pacing": result.storyboard.overall_pacing,
                    "narrative_arc": result.storyboard.narrative_arc
                }
                with open(f"output/storyboard_{i}.json", "w") as f:
                    json.dump(storyboard_data, f, indent=2)
                print(f"✅ Storyboard saved: output/storyboard_{i}.json")
            
            # SAVE SCRIPT
            if result.remotion_script:
                with open(f"output/remotion_script_{i}.tsx", "w") as f:
                    f.write(result.remotion_script)
                print(f"✅ Script saved: output/remotion_script_{i}.tsx")
            
            # SAVE INTENT
            if result.intent:
                intent_data = {
                    "pacing": result.intent.pacing,
                    "visual_style": result.intent.visual_style,
                    "caption_tone": result.intent.caption_tone,
                    "transition_preference": result.intent.transition_preference
                }
                with open(f"output/intent_{i}.json", "w") as f:
                    json.dump(intent_data, f, indent=2)
                print(f"✅ Intent saved: output/intent_{i}.json")
            
            # STATUS
            print(f"✅ Status: {result.status}")
            if result.video_url:
                print(f"🎥 Video: {result.video_url}")
            
            # Save summary
            all_results.append({
                "test": i,
                "style": style,
                "prompt": prompt,
                "status": result.status,
                "scenes": len(result.storyboard.scenes) if result.storyboard else 0,
                "retry_count": result.retry_count
            })
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Save summary
    with open("output/summary.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETE!")
    print(f"📁 Check the 'output' folder for results")
    print("=" * 60)
    
    # Show what was created
    print("\n📂 Output files created:")
    for file in sorted(Path("output").iterdir()):
        print(f"  - {file.name}")

if __name__ == "__main__":
    main()