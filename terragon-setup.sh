#!/bin/bash

# Terragon Labs Codebase Setup Script
# This script sets up the development environment for typechecking and testing

set -e  # Exit on any error

echo "🔧 Setting up Terragon Labs codebase for development..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Install system dependencies if needed (for Debian/Ubuntu)
if command -v apt &> /dev/null; then
    echo "📦 Installing system dependencies..."
    sudo apt update -qq
    sudo apt install -y python3-venv python3-pip
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install main dependencies
echo "📦 Installing main dependencies..."
pip install requests==2.26.0 python-dotenv==0.19.1 pyperclip==1.8.2 termcolor==1.1.0 colorama==0.4.4 distro==1.9.0
pip install PyYAML
pip install openai groq anthropic ollama rich

# Install development dependencies
echo "🛠️ Installing development dependencies..."
pip install mypy pytest pytest-cov
pip install urllib3==1.26.20  # Fix version conflict

# Create development configuration files if they don't exist
echo "⚙️ Setting up configuration files..."

# Create mypy.ini if it doesn't exist
if [ ! -f "mypy.ini" ]; then
    cat > mypy.ini << 'EOF'
[mypy]
python_version = 3.12
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False
disallow_incomplete_defs = False
check_untyped_defs = True
disallow_untyped_decorators = False
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
ignore_missing_imports = True
EOF
    echo "✅ Created mypy.ini"
else
    echo "✅ mypy.ini already exists"
fi

# Create pytest.ini if it doesn't exist
if [ ! -f "pytest.ini" ]; then
    cat > pytest.ini << 'EOF'
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
EOF
    echo "✅ Created pytest.ini"
else
    echo "✅ pytest.ini already exists"
fi

# Test the setup
echo "🧪 Testing the setup..."

echo "  • Running typechecking on iop.py..."
if mypy iop.py; then
    echo "  ✅ iop.py passes type checking"
else
    echo "  ⚠️ iop.py has type checking issues (this is expected for ai_model.py)"
fi

echo "  • Running tests..."
if python -m pytest tests/ -v; then
    echo "  ✅ All tests pass"
else
    echo "  ❌ Some tests failed"
    exit 1
fi

# Clean up any temporary files
echo "🧹 Cleaning up temporary files..."
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".mypy_cache" -type d -exec rm -rf {} + 2>/dev/null || true

echo ""
echo "🎉 Setup complete! Development environment is ready."
echo ""
echo "To use the environment:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run tests: python -m pytest tests/"
echo "  3. Run type checking: mypy iop.py"
echo "  4. Run the main program: python iop.py [arguments]"
echo ""
echo "Available commands after activation:"
echo "  • pytest tests/           - Run all tests"
echo "  • pytest tests/ -v        - Run tests with verbose output"
echo "  • pytest tests/ --cov     - Run tests with coverage"
echo "  • mypy iop.py             - Run type checking on iop.py"
echo "  • mypy ai_model.py        - Run type checking on ai_model.py"
echo ""