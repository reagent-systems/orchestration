#!/usr/bin/env python3
"""
Interface Agent Launcher
Run from orchestration root directory
"""

import sys
from pathlib import Path

# Add interface-agent to path
interface_path = Path(__file__).parent / "interface-agent"
sys.path.insert(0, str(interface_path))

# Import and run the interface agent
from app.interface_agent.agent import main

if __name__ == "__main__":
    main() 