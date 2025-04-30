#!/bin/bash

# Set up the environment
cd "$(dirname "$0")" # Change to the script's directory

# Ensure we're using the virtual environment
source .venv/bin/activate

# Add the current directory to PYTHONPATH 
export PYTHONPATH=$PWD:$PYTHONPATH

# Run the demo
python demo/DemoRunner.py
