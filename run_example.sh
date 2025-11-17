#!/bin/bash

# Helper script to run the example evaluation

echo "=========================================="
echo "Candidate-Job Matching System - Example"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "No virtual environment found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        source .venv/bin/activate
    fi
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy env.example to .env and configure your API keys."
    exit 1
fi

# Run the example
echo "Running example evaluation..."
echo ""
python notebooks/example_evaluation.py

echo ""
echo "=========================================="
echo "Example complete!"
echo "=========================================="

