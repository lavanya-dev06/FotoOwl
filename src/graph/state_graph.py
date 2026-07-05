from langgraph.graph import StateGraph, END
from typing import Literal
from src.models import PipelineState
from src.agents.intent_parser import IntentParser
from src.agents.image_analyzer import ImageAnalyzer
from src.agents.storyboard_writer import StoryboardWriter
from src.agents.script_generator import ScriptGenerator
from src.agents.compiler_fixer import CompilerFixer
from src.agents.renderer import Renderer
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
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
    
    def _should_retry_or_continue(self, state: PipelineState) -> Literal["retry", "render", "fail"]:
        if state.status == "compiled":
            logger.info("✅ Compilation successful")
            return "render"
        elif state.retry_count < state.max_retries:
            logger.info(f"🔄 Retry {state.retry_count + 1}/{state.max_retries}")
            return "retry"
        else:
            logger.error(f"❌ Max retries exceeded")
            state.error_report = f"Compilation failed after {state.max_retries} retries"
            return "fail"
    
    def _parse_intent(self, state: PipelineState):
        logger.info("Parsing user intent...")
        state.intent = self.intent_parser.parse(state.user_prompt)
        state.status = "intent_parsed"
        logger.info(f"✅ Intent parsed")
        return state
    
    def _analyze_images(self, state: PipelineState):
        logger.info("Analyzing images...")
        state.image_analysis = self.image_analyzer.analyze(state.images, state.intent)
        state.status = "images_analyzed"
        logger.info(f"✅ Analyzed {len(state.image_analysis['best_images'])} images")
        return state
    
    def _write_storyboard(self, state: PipelineState):
        logger.info("Writing storyboard...")
        state.storyboard = self.storyboard_writer.generate(
            state.image_analysis["best_images"],
            state.image_analysis,
            state.intent
        )
        state.status = "storyboard_ready"
        logger.info(f"✅ Storyboard with {len(state.storyboard.scenes)} scenes")
        return state
    
    def _generate_script(self, state: PipelineState):
        logger.info("Generating Remotion script...")
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
        logger.info("Compiling script...")
        success, errors = self.compiler_fixer.compile(state.remotion_script)
        
        if success:
            state.status = "compiled"
            logger.info("✅ Compilation successful")
        else:
            state.status = "compile_failed"
            state.compile_errors.extend(errors)
            state.retry_count += 1
            logger.warning(f"❌ Compilation failed")
        
        return state
    
    def _render(self, state: PipelineState):
        logger.info("Rendering video...")
        state.video_url = self.renderer.render(state.remotion_script)
        state.status = "rendered"
        logger.info(f"✅ Video rendered")
        return state
    
    def run(self, images: List[str], prompt: str):
        initial_state = PipelineState(
            images=images,
            user_prompt=prompt,
            status="initialized"
        )
        
        logger.info("🚀 Starting pipeline...")
        final_state = self.graph.invoke(initial_state)
        return final_state