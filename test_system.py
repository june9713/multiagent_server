"""
Quick test script to verify MCP system components
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all core modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from core.base_agent import BaseAgent
        print("  ✓ BaseAgent imported")
        
        from core.agent_loader import AgentLoader
        print("  ✓ AgentLoader imported")
        
        from core.history_manager import HistoryManager
        print("  ✓ HistoryManager imported")
        
        from core.context_manager import ContextManager
        print("  ✓ ContextManager imported")
        
        from agents.master_agent.agent import MasterAgent
        print("  ✓ MasterAgent imported")
        
        from agents.finance_agent.agent import FinanceAgent
        print("  ✓ FinanceAgent imported")
        
        from agents.schedule_agent.agent import ScheduleAgent
        print("  ✓ ScheduleAgent imported")
        
        print("\n✅ All imports successful!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {str(e)}\n")
        return False


def test_config():
    """Test agentconfig.json loading"""
    print("🧪 Testing configuration...")
    
    try:
        import json
        config_path = Path(__file__).parent / "agentconfig.json"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"  ✓ Config loaded")
        print(f"  ✓ Project: {config['project']['name']}")
        print(f"  ✓ Agents defined: {len(config['agents'])}")
        
        for agent in config['agents']:
            print(f"    - {agent['name']} ({agent['id']})")
        
        print("\n✅ Configuration valid!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Config test failed: {str(e)}\n")
        return False


def test_directories():
    """Test that required directories exist"""
    print("🧪 Testing directory structure...")
    
    base_dir = Path(__file__).parent
    required_dirs = [
        "core",
        "server",
        "agents",
        "cli",
        "data",
        "config"
    ]
    
    all_exist = True
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            print(f"  ✓ {dir_name}/ exists")
        else:
            print(f"  ✗ {dir_name}/ missing")
            all_exist = False
    
    if all_exist:
        print("\n✅ All directories present!\n")
    else:
        print("\n❌ Some directories missing!\n")
    
    return all_exist


def main():
    """Run all tests"""
    print("\n" + "="*50)
    print("  MCP Multi-Agent System - Quick Test")
    print("="*50 + "\n")
    
    results = []
    
    results.append(("Directory Structure", test_directories()))
    results.append(("Configuration", test_config()))
    results.append(("Module Imports", test_imports()))
    
    print("\n" + "="*50)
    print("  Test Summary")
    print("="*50 + "\n")
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! System is ready.\n")
        print("Next steps:")
        print("  1. Set GEMINI_API_KEY in .env file")
        print("  2. Run: python server/main.py")
        print("  3. Test: python cli/agent_cli.py list\n")
    else:
        print("\n⚠️  Some tests failed. Please review errors above.\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
