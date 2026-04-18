#!/bin/bash
APP_PATH=$(find . -name "cli_app.py" | head -n 1)
export PYTHONPATH=$PYTHONPATH:$(pwd)

# DIRECT MISSION: We send the agent straight to the file it needs to edit.
# Replace [YOUR_BRANCH] with main
TARGET_URL="https://github.com/Lucian503/Agent-S-Reaper/edit/main/SKILLS.md"
TASK="The browser is open to the EDIT page of SKILLS.md. Type 'Identified Scraping Tools: Requests, Playwright, BeautifulSoup4' into the text area, scroll down, and click the 'Commit changes' button."

echo "$TASK" | python3 "$APP_PATH" \
  --provider "openai" \
  --model "gpt-4o" \
  --ground_provider "openai" \
  --ground_url "https://api.openai.com/v1" \
  --ground_model "gpt-4o" \
  --grounding_width 1280 \
  --grounding_height 1024 \
  --max_trajectory_length 30
