#!/usr/bin/env bash
# Generate data and serve the visualization
set -e

echo "Generating data from ~/.claude/ ..."
python3 process_data.py

echo ""
echo "Starting server at http://localhost:8765"
echo "Press Ctrl+C to stop."
echo ""

python3 -m http.server 8765
