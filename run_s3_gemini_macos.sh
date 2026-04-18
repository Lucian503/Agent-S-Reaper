#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [[ -d "../venv_agent_s" ]]; then
  # shellcheck disable=SC1091
  source "../venv_agent_s/bin/activate"
fi

export PYTHONPATH="$ROOT_DIR"

# Remove potentially conflicting auth/base-url variables.
unset GEMINI_API_KEY || true
unset GOOGLE_API_KEY || true
unset ZAI_API_KEY || true
unset GEMINI_ENDPOINT_URL || true
unset OPENAI_BASE_URL || true
unset OPENAI_API_BASE || true

if [[ -f ".env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "ERROR: OPENAI_API_KEY is not set. Export your OpenAI API key first."
  exit 1
fi

TASK="${1:-Open Chrome and search for 'latest autonomous AI agent news'}"
OPENAI_ENDPOINT_URL="${OPENAI_ENDPOINT_URL:-https://api.openai.com/v1}"
OPENAI_MAIN_MODEL="${OPENAI_MAIN_MODEL:-gpt-4o}"
OPENAI_GROUND_MODEL="${OPENAI_GROUND_MODEL:-gpt-4o}"
GROUNDING_WIDTH="${GROUNDING_WIDTH:-1280}"
GROUNDING_HEIGHT="${GROUNDING_HEIGHT:-720}"
PYTHON_BIN="$(command -v python3 || command -v python)"

"${PYTHON_BIN}" gui_agents/s3/cli_app.py \
  --provider "openai" \
  --model "${OPENAI_MAIN_MODEL}" \
  --model_url "${OPENAI_ENDPOINT_URL}" \
  --ground_provider "openai" \
  --ground_model "${OPENAI_GROUND_MODEL}" \
  --ground_url "${OPENAI_ENDPOINT_URL}" \
  --grounding_width "${GROUNDING_WIDTH}" \
  --grounding_height "${GROUNDING_HEIGHT}" \
  --task "$TASK"
