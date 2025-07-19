#!/usr/bin/env python3
"""
Backend test script for Job Planner Assistant
"""

import sys
import os
import time
import requests
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import fastapi
        print("✓ FastAPI imported successfully")
    except ImportError as e:
        print(f"✗ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✓ Uvicorn imported successfully")
    except ImportError as e:
        print(f"✗ Uvicorn import failed: {e}")
        return False
    
    try:
        import sqlalchemy
        print("✓ SQLAlchemy imported successfully")
    except ImportError as e:
        print(f"✗ SQLAlchemy import failed: {e}")
        return False
    
    try:
        import openai
        print("✓ OpenAI imported successfully")
    except ImportError as e:
        print(f"✗ OpenAI import failed: {e}")
        return False
    
    try:
        import pydantic
        print("✓ Pydantic imported successfully")
    except ImportError as e:
        print(f"✗ Pydantic import failed: {e}")
        return False
    
    return True

def test_backend_modules():
    """Test if backend modules can be imported"""
    print("\nTesting backend modules...")
    
    try:
        from backend.config import settings
        print("✓ Config module imported successfully")
    except ImportError as e:
        print(f"✗ Config module import failed: {e}")
        return False
    
    try:
        from backend.database import init_database
        print("✓ Database module imported successfully")
    except ImportError as e:
        print(f"✗ Database module import failed: {e}")
        return False
    
    try:
        from backend.services import llm_service
        print("✓ Services module imported successfully")
    except ImportError as e:
        print(f"✗ Services module import failed: {e}")
        return False
    
    try:
        from backend.agents import search_agent
        print("✓ Agents module imported successfully")
    except ImportError as e:
        print(f"✗ Agents module import failed: {e}")
        return False
    
    try:
        from backend.api import router
        print("✓ API module imported successfully")
    except ImportError as e:
        print(f"✗ API module import failed: {e}")
        return False
    
    return True

def test_database_init():
    """Test database initialization"""
    print("\nTesting database initialization...")
    
    try:
        from backend.database import init_database
        init_database()
        print("✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False

def test_app_creation():
    """Test FastAPI app creation"""
    print("\nTesting FastAPI app creation...")
    
    try:
        from backend.main import app
        print("✓ FastAPI app created successfully")
        return True
    except Exception as e:
        print(f"✗ FastAPI app creation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Job Planner Assistant Backend Test ===\n")
    
    # Create data directories
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/chromadb", exist_ok=True)
    
    tests = [
        test_imports,
        test_backend_modules,
        test_database_init,
        test_app_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"=== Test Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("✓ All tests passed! Backend is ready to run.")
        return True
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

