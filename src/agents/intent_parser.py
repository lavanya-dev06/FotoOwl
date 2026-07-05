from langchain_openai import ChatOpenAI
from src.models import VideoIntent

class IntentParser:
    def __init__(self):
        self.model = ChatOpenAI(
            model="gpt-4o-mini",
            openai_api_base="https://keylessai.thryx.workers.dev/v1",
            openai_api_key="not-needed",
            temperature=0.1
        )
    
    def parse(self, prompt: str) -> VideoIntent:
        try:
            response = self.model.with_structured_output(VideoIntent).invoke(
                f"Parse this video style prompt into structured intent: '{prompt}'. "
                "Extract pacing (slow/medium/fast), visual_style (cinematic/corporate/upbeat/minimal), "
                "caption_tone (emotional/professional/energetic/minimal), and transition_preference (fade/cut/zoom/slide)."
            )
            return response
        except Exception as e:
            print(f"⚠️ API error, using default: {e}")
            return VideoIntent(
                pacing="medium",
                visual_style="cinematic",
                caption_tone="emotional",
                transition_preference="fade"
            )