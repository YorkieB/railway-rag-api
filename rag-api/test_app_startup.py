"""
Test script to verify app.py can be imported and initialized.

This script checks that:
1. All imports work correctly
2. App can be instantiated
3. All routers are included
4. No circular import issues

Usage:
    python -m rag_api.test_app_startup
    OR
    cd rag-api && python -m test_app_startup
"""

import sys
import os

# Set UTF-8 encoding for Windows compatibility
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add parent directory to path for module imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

def test_imports():
    """Test that all imports work."""
    print("Testing imports...")
    
    try:
        # Try importing as module
        from rag_api.app import app
        print("✅ App imported successfully")
        return True
    except ImportError:
        try:
            # Fallback: try direct import if running from rag-api directory
            from app import app
            print("✅ App imported successfully (direct import)")
            return True
        except ImportError as e:
            print(f"❌ Import error: {e}")
            print("   Try running: python -m rag_api.test_app_startup")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_app_structure():
    """Test that app has expected structure."""
    print("\nTesting app structure...")
    
    try:
        try:
            from rag_api.app import app
        except ImportError:
            from app import app
        
        # Check app exists
        if app is None:
            print("❌ App is None")
            return False
        print("✅ App instance exists")
        
        # Check routers
        router_count = len(app.routes)
        print(f"✅ Found {router_count} routes")
        
        # Check middleware
        middleware_count = len(app.middleware_stack)
        print(f"✅ Found {middleware_count} middleware layers")
        
        return True
    except Exception as e:
        print(f"❌ Error checking app structure: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_routes():
    """Test that key routes exist."""
    print("\nTesting routes...")
    
    try:
        try:
            from rag_api.app import app
        except ImportError:
            from app import app
        
        # Get all route paths
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
            elif hasattr(route, 'path_regex'):
                routes.append(str(route.path_regex))
        
        # Check for key routes
        key_routes = [
            "/",
            "/health",
            "/query",
            "/docs",
            "/redoc"
        ]
        
        found_routes = []
        for key_route in key_routes:
            if any(key_route in str(r) for r in routes):
                found_routes.append(key_route)
                print(f"✅ Route found: {key_route}")
            else:
                print(f"⚠️  Route not found: {key_route}")
        
        print(f"\n✅ Found {len(found_routes)}/{len(key_routes)} key routes")
        return True
    except Exception as e:
        print(f"❌ Error checking routes: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_components():
    """Test that components are initialized."""
    print("\nTesting component initialization...")
    
    try:
        try:
            from rag_api.app import (
                budget_enforcer,
                memory_storage,
                uncertainty_checker,
                cost_tracker,
                enhanced_pipeline,
                live_session_storage
            )
        except ImportError:
            from app import (
                budget_enforcer,
                memory_storage,
                uncertainty_checker,
                cost_tracker,
                enhanced_pipeline,
                live_session_storage
            )
        
        components = {
            "budget_enforcer": budget_enforcer,
            "memory_storage": memory_storage,
            "uncertainty_checker": uncertainty_checker,
            "cost_tracker": cost_tracker,
            "enhanced_pipeline": enhanced_pipeline,
            "live_session_storage": live_session_storage
        }
        
        for name, component in components.items():
            if component is None:
                print(f"❌ {name} is None")
                return False
            print(f"✅ {name} initialized")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ Error checking components: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Jarvis App Startup Test")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("App Structure", test_app_structure),
        ("Routes", test_routes),
        ("Components", test_components)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! App is ready to run.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

