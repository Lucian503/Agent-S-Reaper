#!/bin/bash
# Agent-S Reaper Execution Script

python3 cli_app.py \
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
