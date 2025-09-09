#!/bin/bash
# IPLM Installation Script

echo "IPLM Installation Script"
echo "========================"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Test installation
echo "Testing installation..."
python test_setup.py

echo ""
echo "Installation completed!"
echo ""
echo "To use IPLM:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Set up your MySQL database: mysql -u root < setup_database.sql"
echo "3. Update config/database.yaml with your database credentials"
echo "4. Initialize the database: python -m src.cli db init"
echo "5. Run the example: python examples/basic_usage.py"
