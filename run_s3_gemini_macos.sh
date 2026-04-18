#!/bin/bash
APP_PATH=$(find . -name "cli_app.py" | head -n 1)
export PYTHONPATH=$PYTHONPATH:$(pwd)

TASK="Search GitHub for tools to improve my data scraping accuracy. Record what you learn in SKILLS.md."

# We pipe the task in and ensure the display is active
echo "$TASK" | python3 "$APP_PATH" \
  --provider "openai" \
  --model "gpt-4o" \
  --ground_provider "openai" \
  --ground_url "https://api.openai.com/v1" \
  --ground_model "gpt-4o" \
  --grounding_width 1280 \
  --grounding_height 1024 \
  --max_trajectory_length 20
