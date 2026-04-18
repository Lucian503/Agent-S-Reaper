#!/bin/bash
APP_PATH=$(find . -name "cli_app.py" | head -n 1)
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Force window focus to Chromium so the agent isn't clicking the desktop
xdotool search --onlyvisible --name "chromium" windowactivate

TASK="You are currently in the GitHub editor for SKILLS.md. Your ONLY goal is to type the following into the text area: 'Scraping Tools Identified: Playwright, Requests, BeautifulSoup4.' and then click the green 'Commit changes' button at the bottom."

echo "$TASK" | python3 "$APP_PATH" \
  --provider "openai" \
  --model "gpt-4o" \
  --ground_provider "openai" \
  --ground_model "gpt-4o" \
  --grounding_width 1280 \
  --grounding_height 1024 \
  --max_trajectory_length 30
