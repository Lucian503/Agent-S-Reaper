#!/bin/bash
APP_PATH=$(find . -name "cli_app.py" | head -n 1)
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 1. HARD-FIX: We force the Python script to use our edit link as the starting point
# We search for any URL in cli_app.py and swap it for our target
sed -i "s|https://github.com/.*'|https://github.com/Lucian503/Agent-S-Reaper/edit/main/SKILLS.md'|g" "$APP_PATH"

# 2. DEFINITIVE TASK
TASK="You are now on the EDIT page for SKILLS.md. 1. Click inside the text editor. 2. Type 'Tools found: Playwright, Requests, OpenAI, Anthropic'. 3. Scroll to the bottom. 4. Click the green 'Commit changes' button."

echo "$TASK" | python3 "$APP_PATH" \
  --provider "openai" \
  --model "gpt-4o" \
  --ground_provider "openai" \
  --ground_url "https://api.openai.com/v1" \
  --ground_model "gpt-4o" \
  --grounding_width 1280 \
  --grounding_height 1024 \
  --max_trajectory_length 30
