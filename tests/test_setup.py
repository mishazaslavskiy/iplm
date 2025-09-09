#!/usr/bin/env python3
"""
Test script to verify IPLM setup and basic functionality
"""
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from src import Process, IP, Type, ip_manager, db_manager
        print("✓ All main modules imported successfully")
        assert True, "All main modules imported successfully"
    except ImportError as e:
        print(f"✗ Import error: {e}")
        assert False, f"Import error: {e}"

def test_config():
    """Test configuration loading"""
    print("Testing configuration...")
    
    try:
        from config.settings import DATABASE_CONFIG, IP_STATUSES
        print(f"✓ Database config loaded: {DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}")
        print(f"✓ IP statuses: {IP_STATUSES}")
        assert True, "Configuration loaded successfully"
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        assert False, f"Configuration error: {e}"

def test_database_connection():
    """Test database connection (without actually connecting)"""
    print("Testing database setup...")
    
    try:
        from src.database import DatabaseManager
        db = DatabaseManager()
        print("✓ Database manager created successfully")
        print(f"✓ Database config: {db.config['host']}:{db.config['port']}")
        assert True, "Database manager created successfully"
    except Exception as e:
        print(f"✗ Database setup error: {e}")
        assert False, f"Database setup error: {e}"

def test_models():
    """Test model creation (without database)"""
    print("Testing model creation...")
    
    try:
        from src.models import Process
        from src.type_model import Type
        from src.ip_model import IP
        
        # Test Process creation
        process = Process(name="Test_Process", node="28nm", fab="TSMC", description="Test process")
        print("✓ Process model created successfully")
        
        # Test Type creation
        type_obj = Type(name="Test_Type", description="Test type")
        print("✓ Type model created successfully")
        
        # Test IP creation
        ip = IP(name="Test_IP", type_id=1, process_id=1, provider="Test_Provider")
        print("✓ IP model created successfully")
        
        assert True, "All models created successfully"
    except Exception as e:
        print(f"✗ Model creation error: {e}")
        assert False, f"Model creation error: {e}"

def main():
    """Run all tests"""
    print("IPLM Setup Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_database_connection,
        test_models
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {e}")
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! IPLM is ready to use.")
        print("\nNext steps:")
        print("1. Set up MySQL database")
        print("2. Update config/database.yaml with your database credentials")
        print("3. Run: python -m src.cli db init")
        print("4. Run: python examples/basic_usage.py")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
