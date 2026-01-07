"""
Run all tests

Execute this file to run the complete test suite.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    print("\n" + "="*60)
    print("  World Director Test Suite")
    print("="*60)
    
    # Import and run test modules
    try:
        from tests.test_conditions import run_all_tests as run_conditions_tests
        run_conditions_tests()
    except Exception as e:
        print(f"❌ ConditionsEvaluator tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    try:
        from tests.test_director import run_all_tests as run_director_tests
        run_director_tests()
    except Exception as e:
        print(f"❌ DirectorService tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("="*60)
    print("  🎉 All tests passed successfully!")
    print("="*60 + "\n")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
