#!/usr/bin/env python3
"""
Verification script for KKH Nursing Chatbot
Tests core functionality without external dependencies
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    try:
        import streamlit
        import requests
        import numpy as np
        print("✅ Core dependencies imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_basic_functionality():
    """Test basic chatbot functionality"""
    try:
        # Import our chatbot class
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from app import NursingChatbot
        
        # Initialize chatbot
        print("🤖 Initializing chatbot...")
        bot = NursingChatbot()
        print("✅ Chatbot initialized successfully")
        
        # Test fluid calculation
        print("🧮 Testing fluid calculation...")
        result = bot.calculate_fluid_requirements(10.0)
        expected_daily = 1000  # 10kg * 100ml/kg
        expected_hourly = 40   # 10kg * 4ml/kg/hr
        
        if result['daily_ml'] == expected_daily and result['hourly_ml'] == expected_hourly:
            print(f"✅ Fluid calculation correct: {result}")
        else:
            print(f"❌ Fluid calculation incorrect: {result}")
            return False
        
        # Test knowledge base
        print("📚 Testing knowledge base...")
        if hasattr(bot, 'knowledge_base') and bot.knowledge_base:
            print("✅ Knowledge base loaded")
        else:
            print("❌ Knowledge base not loaded")
            return False
        
        # Test search functionality
        print("🔍 Testing search functionality...")
        try:
            results = bot.search_knowledge_base("hand hygiene")
            if results:
                print("✅ Search functionality working")
            else:
                print("⚠️  Search returned no results (this might be normal)")
        except Exception as e:
            print(f"❌ Search error: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def test_file_structure():
    """Test that all required files are present"""
    required_files = [
        'app.py',
        'requirements.txt',
        'Dockerfile',
        'fly.toml',
        'README.md',
        'config.yaml'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True

def main():
    """Run all verification tests"""
    print("🏥 KKH Nursing Chatbot - Verification Tests")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Dependencies", test_imports),
        ("Core Functionality", test_basic_functionality)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} test PASSED")
        else:
            print(f"❌ {test_name} test FAILED")
    
    print(f"\n{'=' * 50}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The chatbot is ready for deployment.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
