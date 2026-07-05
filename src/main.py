import json
import sys
from pathlib import Path
from src.graph.state_graph import VideoPipeline

def main():
    # Create output directory
    Path("output").mkdir(exist_ok=True)
    
    # Create dummy image files if they don't exist
    for i in range(1, 11):
        img_path = f"image_{i}.jpg"
        if not Path(img_path).exists():
            with open(img_path, "w") as f:
                f.write(f"Dummy image {i}")
    
    # Sample images
    images = [f"image_{i}.jpg" for i in range(1, 11)]
    
    # Try different prompts
    prompts = [
        "Cinematic wedding reel, slow and emotional, warm tones",
        "Upbeat birthday reel, fast cuts, bold captions, energetic",
        "Clean corporate highlights, professional tone, subtle transitions"
    ]
    
    print("🎬 FotoOwl AI Video Pipeline (FREE - No API Key!)")
    print("=" * 60)
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n📝 Running prompt {i}: {prompt}")
        print("-" * 50)
        
        pipeline = VideoPipeline()
        result = pipeline.run(images, prompt)
        
        # Save outputs
        storyboard_path = f"output/storyboard_{i}.json"
        script_path = f"output/remotion_script_{i}.tsx"
        
        if result.storyboard:
            with open(storyboard_path, "w") as f:
                f.write(result.storyboard.json(indent=2))
            print(f"📄 Storyboard: {storyboard_path}")
        
        if result.remotion_script:
            with open(script_path, "w") as f:
                f.write(result.remotion_script)
            print(f"📄 Script: {script_path}")
        
        print(f"✅ Status: {result.status}")
        if result.video_url:
            print(f"🎥 Video: {result.video_url}")
        
        # Save state
        state_path = f"output/final_state_{i}.json"
        with open(state_path, "w") as f:
            json.dump({
                "status": result.status,
                "retry_count": result.retry_count,
                "error_report": result.error_report,
                "video_url": result.video_url
            }, f, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ DONE! Check the output folder for results.")

if __name__ == "__main__":
    main()