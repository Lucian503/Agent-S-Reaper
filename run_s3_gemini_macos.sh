#!/bin/bash
APP_PATH=$(find . -name "cli_app.py" | head -n 1)
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Since the browser is already open to GitHub, we just give the agent its goal
TASK="The browser is already open to your repository. Analyze the existing files, search GitHub for scraping tools, and update SKILLS.md."

echo "$TASK" | python3 "$APP_PATH" \
  --provider "openai" \
  --model "gpt-4o" \
  --ground_provider "openai" \
  --ground_url "https://api.openai.com/v1" \
  --ground_model "gpt-4o" \
  --grounding_width 1280 \
  --grounding_height 1024 \
  --max_trajectory_length 20
