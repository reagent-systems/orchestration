#!/bin/bash

# Read-Write App Setup Script
# This script sets up the read-write app with ADK and A2A integration

set -e

echo "🚀 Setting up Read-Write App with A2A Integration"
echo "=================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "⚠️  Git is not installed. Git operations will be disabled."
else
    echo "✅ Git found: $(git --version)"
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f "app/.env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp app/env.example app/.env
    echo "✅ .env file created"
    echo "⚠️  Please edit app/.env and add your API keys and git settings"
else
    echo "✅ .env file already exists"
fi

# Create workspace directory
echo "📁 Creating workspace directory..."
mkdir -p workspace
echo "✅ Workspace directory created"

# Test the setup
echo "🧪 Testing setup..."
python test_setup.py

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit app/.env and add your Google API key"
echo "2. Configure git settings in app/.env (optional)"
echo "3. Run: cd app && adk web"
echo "4. Open http://localhost:8000 in your browser"
echo "5. Select 'enhanced_file_operations_agent' to start"
echo ""
echo "Available agents:"
echo "- enhanced_file_operations_agent (main agent)"
echo "- file_analysis_workflow (sequential workflow)"
echo "- file_creation_workflow (sequential workflow)"
echo "- parallel_file_operations (parallel workflow)"
echo "- git_management_loop (loop workflow)"
echo ""
echo "For A2A integration:"
echo "1. Install A2A SDK: pip install a2a-sdk"
echo "2. Configure A2A settings in app/.env"
echo "3. Start your A2A agent registry"
echo ""
echo "Happy coding! 🚀" 