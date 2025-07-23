#!/usr/bin/env python3
"""
Test runner for the Web Scraper test suite.
Provides easy commands for running different test categories.
"""

import sys
import os
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_command(cmd, description):
    """Run a command and display results."""
    print(f"\n🔍 {description}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test runner interface."""
    if len(sys.argv) < 2:
        print("""
🧪 Web Scraper Test Runner

Usage: python tests/run_tests.py <command>

Commands:
  unit         - Run unit tests only
  integration  - Run integration tests only  
  debug        - Run debug scripts
  all          - Run all tests
  contact      - Run contact-related tests
  storage      - Run storage-related tests
  api          - Run API tests
  
Examples:
  python tests/run_tests.py unit
  python tests/run_tests.py all  
  python tests/run_tests.py contact
        """)
        return

    command = sys.argv[1].lower()
    
    # Change to project root directory
    os.chdir(project_root)
    
    if command == "unit":
        run_command(f"python -m pytest tests/unit/ -v", "Running Unit Tests")
        
    elif command == "integration":
        run_command(f"python -m pytest tests/integration/ -v", "Running Integration Tests")
        
    elif command == "debug":
        print("\n🐛 Running Debug Scripts")
        print("=" * 60)
        
        debug_scripts = [
            "tests/debug/debug_contact_simple.py",
            "tests/debug/debug_storage_issue.py"
        ]
        
        for script in debug_scripts:
            if Path(script).exists():
                print(f"\n▶️  Running {script}")
                run_command(f"python {script}", f"Debug: {Path(script).name}")
            
    elif command == "all":
        print("\n🚀 Running Complete Test Suite")
        run_command(f"python -m pytest tests/ -v", "All Tests")
        
    elif command == "contact":
        print("\n📞 Running Contact-Related Tests")
        run_command(f"python -m pytest tests/unit/test_contact_extraction.py tests/integration/test_contact_with_real_website.py -v", "Contact Tests")
        
    elif command == "storage":
        print("\n💾 Running Storage-Related Tests")
        run_command(f"python -m pytest tests/unit/test_storage.py -v", "Storage Tests")
        
    elif command == "api":
        print("\n🌐 Running API Tests")
        run_command(f"python -m pytest tests/integration/test_api_integration.py tests/integration/test_simplified_api.py -v", "API Tests")
        
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python tests/run_tests.py' to see available commands")

if __name__ == "__main__":
    main() 