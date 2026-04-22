# Agent-S Healthcare Wrapper (EHR -> CoverMyMeds)

This integration adds a stateful wrapper on top of Agent-S for prior authorization workflows.

It is designed for your requirement:
- You provide patient name as `LastName, FirstName`
- Agent-S uses the remembered EHR app as source until you explicitly change it
- Agent-S extracts demographic + diagnostic information
- Agent-S enters data into CoverMyMeds in a human-like pattern
- Agent-S stops before final submission and asks for explicit confirmation

## Script

- `agent_s_healthcare_wrapper.py`

## Remembered App State

State file path (override with env var):
- Default: `~/.agent_s_healthcare_state.json`
- Override: `AGENT_S_HEALTHCARE_STATE_PATH=/custom/path/state.json`

## Required Environment

You still need normal Agent-S runtime requirements:
- `agent_s` executable in `PATH`
- model credentials (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.)
- grounding endpoint, especially:
  - `AGENT_S_GROUND_URL`
  - `AGENT_S_GROUND_MODEL` (default `ui-tars-1.5-7b`)
  - `AGENT_S_GROUNDING_WIDTH` (default `1920`)
  - `AGENT_S_GROUNDING_HEIGHT` (default `1080`)

## Usage

Set the source EHR once (remembered until changed):

```bash
./integrations/healthcare_covermymeds/agent_s_healthcare_wrapper.py set-source-app "Epic Hyperspace"
```

Set the target app once:

```bash
./integrations/healthcare_covermymeds/agent_s_healthcare_wrapper.py set-target-app "CoverMyMeds"
```

Show current remembered state:

```bash
./integrations/healthcare_covermymeds/agent_s_healthcare_wrapper.py show-state
```

Run prior auth workflow for a patient:

```bash
./integrations/healthcare_covermymeds/agent_s_healthcare_wrapper.py run-patient "Doe, Jane" --max-steps 25
```

Run with optional case notes:

```bash
./integrations/healthcare_covermymeds/agent_s_healthcare_wrapper.py run-patient "Doe, Jane" \
  --case-notes "PA renewal for medication X. Include prior failure history." \
  --max-steps 25
```

## Safety Notes

- This wrapper enforces a "stop before final submit" instruction.
- It does not bypass CAPTCHA or security challenges.
- It should only be used in authorized clinical workflows and with validated source data.
