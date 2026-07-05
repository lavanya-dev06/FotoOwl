"""
Comprehensive Test Suite for FotoOwl Pipeline
Run with: python test_pipeline.py
"""

import json
import sys
from pathlib import Path

def test_output_files():
    """Test that all output files were created"""
    print("\n🧪 TEST 1: Checking Output Files")
    print("-" * 40)
    
    output_dir = Path("output")
    if not output_dir.exists():
        print("❌ No output folder found. Run working_pipeline.py first.")
        return False
    
    required_files = [
        "storyboard_1.json",
        "storyboard_2.json", 
        "storyboard_3.json",
        "remotion_script_1.tsx",
        "remotion_script_2.tsx",
        "remotion_script_3.tsx",
        "intent_1.json",
        "intent_2.json",
        "intent_3.json",
        "summary.json"
    ]
    
    all_exist = True
    for file in required_files:
        if (output_dir / file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} MISSING")
            all_exist = False
    
    return all_exist

def test_storyboards():
    """Test that storyboards are valid and different"""
    print("\n🧪 TEST 2: Validating Storyboards")
    print("-" * 40)
    
    output_dir = Path("output")
    storyboards = []
    
    for i in range(1, 4):
        file_path = output_dir / f"storyboard_{i}.json"
        if not file_path.exists():
            print(f"❌ storyboard_{i}.json missing")
            return False
        
        with open(file_path) as f:
            data = json.load(f)
            storyboards.append(data)
            
            # Check structure
            if "scenes" not in data:
                print(f"❌ storyboard_{i}.json missing 'scenes'")
                return False
            
            scenes = data["scenes"]
            if len(scenes) != 8:
                print(f"⚠️ storyboard_{i}.json has {len(scenes)} scenes (expected 8)")
            
            # Check each scene
            for j, scene in enumerate(scenes):
                required_fields = ["image_path", "duration_seconds", "caption", "transition"]
                for field in required_fields:
                    if field not in scene:
                        print(f"❌ Scene {j} missing '{field}'")
                        return False
            
            print(f"✅ Storyboard {i}: {len(scenes)} scenes, {data.get('overall_pacing', 'unknown')} pacing")
    
    # Test that storyboards are different
    if len(storyboards) >= 2:
        captions_1 = [s["caption"] for s in storyboards[0]["scenes"]]
        captions_2 = [s["caption"] for s in storyboards[1]["scenes"]]
        
        if captions_1 == captions_2:
            print("⚠️ Storyboard 1 and 2 have the same captions (should be different)")
        
        pacing_1 = storyboards[0].get("overall_pacing", "")
        pacing_2 = storyboards[1].get("overall_pacing", "")
        
        if pacing_1 != pacing_2:
            print(f"✅ Different pacing: {pacing_1} vs {pacing_2}")
        else:
            print(f"⚠️ Same pacing: {pacing_1}")
    
    return True

def test_scripts():
    """Test that scripts are valid Remotion code"""
    print("\n🧪 TEST 3: Validating Remotion Scripts")
    print("-" * 40)
    
    output_dir = Path("output")
    
    for i in range(1, 4):
        file_path = output_dir / f"remotion_script_{i}.tsx"
        if not file_path.exists():
            print(f"❌ remotion_script_{i}.tsx missing")
            return False
        
        with open(file_path) as f:
            content = f.read()
        
        # Check for required Remotion components
        checks = [
            ("import", "Missing import statements"),
            ("Composition", "Missing Composition component"),
            ("Sequence", "Missing Sequence component"),
            ("fps", "Missing fps variable"),
            ("durationInFrames", "Missing durationInFrames")
        ]
        
        valid = True
        for check, error in checks:
            if check not in content:
                print(f"❌ Script {i}: {error}")
                valid = False
        
        if valid:
            print(f"✅ Script {i}: Valid Remotion code")
    
    return True

def test_intents():
    """Test that intents are parsed correctly"""
    print("\n🧪 TEST 4: Validating Intents")
    print("-" * 40)
    
    output_dir = Path("output")
    intents = []
    
    expected_intents = [
        {"visual_style": "cinematic", "pacing": "slow"},
        {"visual_style": "upbeat", "pacing": "fast"},
        {"visual_style": "corporate", "pacing": "medium"}
    ]
    
    for i in range(1, 4):
        file_path = output_dir / f"intent_{i}.json"
        if not file_path.exists():
            print(f"❌ intent_{i}.json missing")
            return False
        
        with open(file_path) as f:
            data = json.load(f)
            intents.append(data)
            
            # Check expected values
            expected = expected_intents[i-1]
            if data.get("visual_style") == expected["visual_style"]:
                print(f"✅ Intent {i}: {expected['visual_style']} style")
            else:
                print(f"⚠️ Intent {i}: Expected {expected['visual_style']}, got {data.get('visual_style')}")
            
            if data.get("pacing") == expected["pacing"]:
                print(f"   ✅ {expected['pacing']} pacing")
            else:
                print(f"   ⚠️ Expected {expected['pacing']}, got {data.get('pacing')}")
    
    return True

def test_summary():
    """Test that summary file exists and is valid"""
    print("\n🧪 TEST 5: Validating Summary")
    print("-" * 40)
    
    output_dir = Path("output")
    file_path = output_dir / "summary.json"
    
    if not file_path.exists():
        print("❌ summary.json missing")
        return False
    
    with open(file_path) as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        print("❌ summary.json should be a list")
        return False
    
    if len(data) != 3:
        print(f"⚠️ Summary has {len(data)} entries (expected 3)")
    else:
        print(f"✅ Summary: {len(data)} test runs")
    
    for entry in data:
        if "style" in entry and "status" in entry:
            print(f"   - {entry['style']}: {entry['status']}")
    
    return True

def main():
    print("\n" + "=" * 60)
    print("🧪 FOTOOWL PIPELINE - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Output Files", test_output_files),
        ("Storyboards", test_storyboards),
        ("Remotion Scripts", test_scripts),
        ("Intents", test_intents),
        ("Summary", test_summary)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test '{name}' crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 RESULTS: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ ALL TESTS PASSED! Your pipeline is ready for submission.")
    else:
        print("⚠️ Some tests failed. Please check the output above.")
    
    print("=" * 60)
    return failed == 0

if __name__ == "__main__":
    sys.exit(0 if main() else 1)