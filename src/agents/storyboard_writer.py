from langchain_openai import ChatOpenAI
from src.rag.vector_store import RAGSystem
from src.models import Storyboard, Scene, VideoIntent
from typing import List

class StoryboardWriter:
    def __init__(self):
        self.model = ChatOpenAI(
            model="gpt-4o-mini",
            openai_api_base="https://keylessai.thryx.workers.dev/v1",
            openai_api_key="not-needed",
            temperature=0.7
        )
        self.rag = RAGSystem()
    
    def generate(self, images: List[str], analysis: dict, intent: VideoIntent) -> Storyboard:
        style_context = self.rag.retrieve_style(intent.visual_style)
        
        try:
            response = self.model.with_structured_output(Storyboard).invoke(
                f"Create a storyboard for {len(images)} images. "
                f"Style guide: {style_context}. "
                f"Intent: {intent}. "
                "Return scenes with image_path, duration_seconds (1-4), caption, and transition type."
            )
            return response
        except Exception as e:
            print(f"⚠️ API error, using fallback: {e}")
            return self._fallback_storyboard(images, intent)
    
    def _fallback_storyboard(self, images: List[str], intent: VideoIntent) -> Storyboard:
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
        
        return Storyboard(
            scenes=scenes,
            overall_pacing=intent.pacing,
            narrative_arc=f"A {intent.visual_style} journey"
        )