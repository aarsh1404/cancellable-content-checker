#!/usr/bin/env python3
"""
Test script to verify the Cancellable Content Checker setup
"""

import sys
import importlib

def test_imports():
    """Test if all required packages can be imported"""
    required_packages = [
        'streamlit',
        'groq',
        'requests',
        'bs4',
        'PyPDF2',
        'docx',
        'PIL',
        'pytesseract',
        'lxml'
    ]
    
    print("Testing package imports...")
    failed_imports = []
    
    for package in required_packages:
        try:
            if package == 'bs4':
                importlib.import_module('bs4')
            elif package == 'PIL':
                importlib.import_module('PIL')
            else:
                importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    return failed_imports

def test_groq_connection():
    """Test Groq API connection"""
    try:
        from groq import Groq
        import os
        
        # Try to get API key from Streamlit secrets first, then environment
        api_key = None
        try:
            import streamlit as st
            # This won't work in a script context, so we'll try environment
            api_key = os.getenv("GROQ_API_KEY")
        except:
            pass
        
        # Try to read from secrets file directly
        if not api_key:
            try:
                import toml
                secrets_path = ".streamlit/secrets.toml"
                if os.path.exists(secrets_path):
                    with open(secrets_path, 'r') as f:
                        secrets = toml.load(f)
                        api_key = secrets.get("GROQ_API_KEY")
            except ImportError:
                pass
        
        if not api_key:
            print("⚠️  GROQ_API_KEY not found")
            print("   Make sure to set it in .streamlit/secrets.toml")
            return False
        
        client = Groq(api_key=api_key)
        
        # Test connection with a simple request
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Hello"}],
            model="llama-3.1-8b-instant",
            max_tokens=10
        )
        
        print("✅ Groq API connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Groq API connection failed: {e}")
        return False

def test_local_modules():
    """Test if local modules can be imported"""
    print("\nTesting local modules...")
    
    try:
        from analyzer import ContentAnalyzer
        print("✅ analyzer.py")
    except ImportError as e:
        print(f"❌ analyzer.py: {e}")
        return False
    
    try:
        from extractors import ContentExtractor
        print("✅ extractors.py")
    except ImportError as e:
        print(f"❌ extractors.py: {e}")
        return False
    
    try:
        from prompts import get_analysis_prompt
        print("✅ prompts.py")
    except ImportError as e:
        print(f"❌ prompts.py: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚨 Cancellable Content Checker - Setup Test")
    print("=" * 50)
    
    # Test imports
    failed_imports = test_imports()
    
    # Test local modules
    local_modules_ok = test_local_modules()
    
    # Test Groq connection
    groq_ok = test_groq_connection()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    if failed_imports:
        print(f"❌ Failed imports: {', '.join(failed_imports)}")
        print("   Run: pip install -r requirements.txt")
    else:
        print("✅ All package imports successful")
    
    if not local_modules_ok:
        print("❌ Local module imports failed")
        print("   Check that all Python files are in the same directory")
    else:
        print("✅ Local modules imported successfully")
    
    if not groq_ok:
        print("❌ Groq API connection failed")
        print("   Check your API key in .streamlit/secrets.toml")
    else:
        print("✅ Groq API connection successful")
    
    if not failed_imports and local_modules_ok and groq_ok:
        print("\n🎉 All tests passed! You're ready to run the app.")
        print("   Run: streamlit run app.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
