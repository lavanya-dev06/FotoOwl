import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

print("=" * 60)
print("🎬 FotoOwl AI Video Pipeline")
print("=" * 60)

# Now import and run
try:
    from src.main import main
    main()
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("💡 Try running this command first:")
    print("   $env:PYTHONPATH = '.'")
    print("   python src/main.py")