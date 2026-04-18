#!/bin/bash
# Find where cli_app.py is hiding
APP_PATH=$(find . -name "cli_app.py" | head -n 1)

if [ -z "$APP_PATH" ]; then
  echo "ERROR: cli_app.py not found!"
  exit 1
fi

echo "Found cli_app.py at: $APP_PATH"

# Set the Python Path to the current root directory
# This solves the "No module named gui_agents" error
export PYTHONPATH=$PYTHONPATH:$(pwd)

python3 "$APP_PATH" \
  --provider "openai" \
  --model "gpt-4o" \
  --ground_provider "openai" \
  --ground_model "gpt-4o" \
  --ground_url "https://api.openai.com/v1" \
  --grounding_width 1280 \
  --grounding_height 1024 \
  --max_trajectory_length 20 \
  --enable_local_env \
  "$@"
