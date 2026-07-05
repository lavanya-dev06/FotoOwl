from pydantic import BaseModel
from typing import List, Optional, Literal

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