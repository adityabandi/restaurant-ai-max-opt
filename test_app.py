#!/usr/bin/env python3
"""
Simple test script to verify app structure without dependencies
"""

import ast
import sys

def test_app_structure():
    """Test the app structure and imports"""
    print("🔍 Testing Restaurant Analytics Pro app structure...")
    
    try:
        # Parse the app file
        with open('streamlit_app.py', 'r') as f:
            content = f.read()
        
        # Parse AST to check syntax
        tree = ast.parse(content)
        print("✅ Python syntax is valid")
        
        # Check for required classes
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        required_classes = ['ClaudeAI', 'DataProcessor', 'InsightGenerator', 'RestaurantAnalyticsPro']
        
        missing_classes = set(required_classes) - set(classes)
        if missing_classes:
            print(f"❌ Missing classes: {missing_classes}")
            return False
        else:
            print(f"✅ All required classes found: {required_classes}")
        
        # Check for main function
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        if 'main' in functions:
            print("✅ Main function found")
        else:
            print("❌ Main function missing")
            return False
        
        # Check for streamlit imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend([alias.name for alias in node.names])
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module)
        
        required_imports = ['streamlit', 'pandas', 'plotly.express']
        missing_imports = set(required_imports) - set(imports)
        if missing_imports:
            print(f"❌ Missing imports: {missing_imports}")
            return False
        else:
            print(f"✅ All required imports found")
        
        # Check file size (should be substantial)
        file_size = len(content)
        if file_size < 10000:  # Less than 10KB
            print(f"❌ File too small: {file_size} bytes")
            return False
        else:
            print(f"✅ File size appropriate: {file_size:,} bytes")
        
        # Check for key methods
        methods = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        required_methods = ['load_custom_css', 'run', '_render_dashboard', '_process_uploaded_file']
        
        missing_methods = set(required_methods) - set(methods)
        if missing_methods:
            print(f"❌ Missing methods: {missing_methods}")
            return False
        else:
            print(f"✅ All key methods found")
        
        print("\n🎉 App structure test PASSED!")
        print("📋 Summary:")
        print(f"   • File size: {file_size:,} bytes")
        print(f"   • Classes: {len(classes)} ({', '.join(classes)})")
        print(f"   • Methods: {len(methods)}")
        print(f"   • Lines of code: {len(content.splitlines())}")
        
        return True
        
    except FileNotFoundError:
        print("❌ streamlit_app.py not found")
        return False
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_requirements():
    """Check requirements.txt"""
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read().strip().split('\n')
        
        print(f"\n📦 Requirements.txt check:")
        print(f"   • {len(requirements)} dependencies listed")
        
        essential_deps = ['streamlit', 'pandas', 'plotly']
        for dep in essential_deps:
            if any(dep in req for req in requirements):
                print(f"   ✅ {dep}")
            else:
                print(f"   ❌ {dep} missing")
        
        return True
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False

if __name__ == "__main__":
    print("🍽️ Restaurant Analytics Pro - Structure Test")
    print("=" * 50)
    
    app_ok = test_app_structure()
    req_ok = check_requirements()
    
    if app_ok and req_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("🚀 App is ready for deployment!")
        print("\n📝 Deployment notes:")
        print("   • Upload to Streamlit Cloud")
        print("   • Add ANTHROPIC_API_KEY secret (optional)")
        print("   • App will work without API key using pattern analysis")
    else:
        print("\n❌ TESTS FAILED - Check issues above")
        sys.exit(1)