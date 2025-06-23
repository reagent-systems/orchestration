#!/usr/bin/env python3
"""
Orchestration Interface Launcher
Launch the sophisticated Textual-based live orchestration control center
"""

import os
import sys
from pathlib import Path

def main():
    """Launch the orchestration interface"""
    print("🎛️ Launching Orchestration Control Center...")
    print("=" * 60)
    
    # Check if workspace exists
    workspace_path = Path("./workspace")
    if not workspace_path.exists():
        print("📁 Creating workspace directory...")
        workspace_path.mkdir(exist_ok=True)
        (workspace_path / "current_tasks").mkdir(exist_ok=True)
        (workspace_path / "agent_logs").mkdir(exist_ok=True)
        (workspace_path / "agent_signals").mkdir(exist_ok=True)
    
    # Check environment
    if not os.path.exists(".env"):
        print("⚠️  Warning: .env file not found!")
        print("Please ensure environment variables are configured.")
    
    print("🚀 Starting Textual-based Interface Agent...")
    print("\nKeyboard shortcuts:")
    print("- N: New Task")
    print("- E: Edit Selected Task") 
    print("- D: Delete Selected Task")
    print("- R: Refresh Data")
    print("- Q: Quit")
    print("- Arrow Keys: Navigate")
    print("=" * 60)
    
    # Launch the interface
    try:
        # Add interface-agent to Python path
        interface_path = Path("interface-agent/app")
        sys.path.insert(0, str(interface_path))
        
        from interface_agent.agent import OrchestrationInterface
        
        app = OrchestrationInterface()
        app.run()
        
    except KeyboardInterrupt:
        print("\n👋 Interface closed by user")
    except Exception as e:
        print(f"❌ Error launching interface: {e}")
        print("Please check that all dependencies are installed:")
        print("  cd interface-agent && pip install -r requirements.txt")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 