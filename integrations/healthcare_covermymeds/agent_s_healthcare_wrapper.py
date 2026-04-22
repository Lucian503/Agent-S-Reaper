#!/usr/bin/env python3
"""
Healthcare workflow wrapper for Agent-S.

This wrapper adds persistent app context for EHR -> CoverMyMeds prior auth work.
It remembers the active source app until changed and builds a structured task when
provided a patient name in "LastName, FirstName" format.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from typing import Dict, Any

STATE_PATH = os.environ.get(
    "AGENT_S_HEALTHCARE_STATE_PATH",
    os.path.expanduser("~/.agent_s_healthcare_state.json"),
)

DEFAULT_STATE: Dict[str, Any] = {
    "source_app": "EHR",
    "target_app": "CoverMyMeds",
    "confirm_before_submit": True,
    "human_like_entry": True,
}


def load_state() -> Dict[str, Any]:
    if not os.path.exists(STATE_PATH):
        return DEFAULT_STATE.copy()

    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            loaded = json.load(f)
            if not isinstance(loaded, dict):
                return DEFAULT_STATE.copy()
            state = DEFAULT_STATE.copy()
            state.update(loaded)
            return state
    except Exception:
        return DEFAULT_STATE.copy()


def save_state(state: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    tmp_path = f"{STATE_PATH}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp_path, STATE_PATH)


def is_valid_patient_name(name: str) -> bool:
    return bool(re.match(r"^[^,]+,\s*[^,]+$", name.strip()))


def build_prior_auth_task(patient_name: str, state: Dict[str, Any], case_notes: str) -> str:
    source_app = state["source_app"]
    target_app = state["target_app"]

    optional_notes = ""
    if case_notes.strip():
        optional_notes = f"\nCase notes from user:\n{case_notes.strip()}\n"

    return textwrap.dedent(
        f"""
        You are executing a healthcare prior authorization workflow with strict safety and data quality controls.

        Workflow context to remember for this run:
        - Active source application: {source_app}
        - Active target application: {target_app}
        - Patient search input: {patient_name.strip()}

        Required workflow:
        1. In {source_app}, search the patient using exactly "LastName, FirstName" format.
        2. If multiple matching patients appear, stop and request a disambiguator (DOB or MRN) instead of guessing.
        3. Extract demographics from the chart:
           full legal name, DOB, sex, phone, address, subscriber/member identifiers, payer fields when present.
        4. Extract diagnosis information from the chart:
           ICD-10 codes, diagnosis text, problem-list context relevant to the requested medication.
        5. Open or switch to {target_app} and navigate to the relevant prior authorization case/form.
        6. Enter extracted values into matching form fields throughout {target_app}.
        7. Perform human-like data entry behavior:
           click into each field before typing, type in natural chunks, use realistic pauses, and review each section.
           Do not dump all fields as one paste unless the field is explicitly multiline free text.
        8. Validate entered values against extracted source data before moving to the next section.
        9. If required data is missing, pause and explicitly list what is missing.
        10. Before any final "Submit" action, stop and request explicit user confirmation.

        Safety requirements:
        - Never invent clinical details.
        - Never submit a final prior authorization without explicit user approval.
        - If blocked by CAPTCHA or hard security challenge, pause and hand off to the user.
        {optional_notes}
        Completion standard for this run:
        - Report which demographic fields were populated.
        - Report which diagnostic fields were populated.
        - Report whether the case is ready for final submit (without submitting).
        """
    ).strip()


def run_agent_s(task: str, max_steps: int, enable_reflection: bool, enable_local_env: bool) -> Dict[str, Any]:
    agent_s_path = os.environ.get("AGENT_S_PATH") or shutil.which("agent_s")
    if not agent_s_path:
        return {
            "status": "error",
            "message": "agent_s executable not found in PATH.",
            "hint": "Install with: pip install gui-agents",
        }

    provider = os.environ.get("AGENT_S_PROVIDER", "openai")
    model = os.environ.get("AGENT_S_MODEL", "gpt-5-2025-08-07")
    model_temperature = os.environ.get("AGENT_S_MODEL_TEMPERATURE", "")

    ground_url = os.environ.get("AGENT_S_GROUND_URL", "")
    ground_api_key = os.environ.get("AGENT_S_GROUND_API_KEY", "")
    ground_model = os.environ.get("AGENT_S_GROUND_MODEL", "ui-tars-1.5-7b")
    grounding_width = os.environ.get("AGENT_S_GROUNDING_WIDTH", "1920")
    grounding_height = os.environ.get("AGENT_S_GROUNDING_HEIGHT", "1080")
    ground_provider = os.environ.get("AGENT_S_GROUND_PROVIDER", "huggingface")

    if not ground_url:
        return {
            "status": "error",
            "message": "Grounding endpoint is missing.",
            "hint": "Set AGENT_S_GROUND_URL before running healthcare automation.",
        }

    cmd = [
        agent_s_path,
        "--provider",
        provider,
        "--model",
        model,
        "--max_trajectory_length",
        str(max_steps),
        "--task",
        task,
        "--ground_provider",
        ground_provider,
        "--ground_url",
        ground_url,
        "--ground_model",
        ground_model,
        "--grounding_width",
        grounding_width,
        "--grounding_height",
        grounding_height,
    ]

    if model_temperature:
        cmd.extend(["--model_temperature", model_temperature])

    if ground_api_key:
        cmd.extend(["--ground_api_key", ground_api_key])

    if enable_reflection:
        cmd.append("--enable_reflection")

    if enable_local_env:
        cmd.append("--enable_local_env")

    try:
        result = subprocess.run(cmd, text=True, timeout=1200)
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "Agent-S timed out after 20 minutes.",
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": f"Failed to execute Agent-S: {exc}",
        }

    if result.returncode == 0:
        return {
            "status": "success",
            "message": "Agent-S run completed.",
        }

    return {
        "status": "error",
        "message": f"Agent-S exited with return code {result.returncode}.",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Stateful EHR -> CoverMyMeds workflow wrapper for Agent-S"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    set_source = subparsers.add_parser("set-source-app", help="Set remembered source app")
    set_source.add_argument("app", type=str, help="Example: Epic Hyperspace")

    set_target = subparsers.add_parser("set-target-app", help="Set remembered target app")
    set_target.add_argument("app", type=str, help="Example: CoverMyMeds")

    subparsers.add_parser("show-state", help="Show current remembered app state")

    run_patient = subparsers.add_parser(
        "run-patient",
        help="Run EHR -> CoverMyMeds workflow using a patient LastName, FirstName",
    )
    run_patient.add_argument("patient_name", type=str, help='Format: "LastName, FirstName"')
    run_patient.add_argument(
        "--case-notes",
        type=str,
        default="",
        help="Optional notes to include in this run",
    )
    run_patient.add_argument("--max-steps", type=int, default=20)
    run_patient.add_argument("--no-reflection", action="store_true")
    run_patient.add_argument("--enable-local-env", action="store_true")
    run_patient.add_argument("--json", action="store_true")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    state = load_state()

    if args.command == "set-source-app":
        state["source_app"] = args.app.strip()
        save_state(state)
        print(f"source_app set to: {state['source_app']}")
        return

    if args.command == "set-target-app":
        state["target_app"] = args.app.strip()
        save_state(state)
        print(f"target_app set to: {state['target_app']}")
        return

    if args.command == "show-state":
        print(json.dumps(state, indent=2))
        return

    if args.command == "run-patient":
        patient_name = args.patient_name.strip()
        if not is_valid_patient_name(patient_name):
            print(
                "Error: patient_name must be in 'LastName, FirstName' format.",
                file=sys.stderr,
            )
            sys.exit(2)

        task = build_prior_auth_task(patient_name, state, args.case_notes)
        result = run_agent_s(
            task=task,
            max_steps=args.max_steps,
            enable_reflection=not args.no_reflection,
            enable_local_env=args.enable_local_env,
        )

        if args.json:
            print(json.dumps({"state": state, "result": result}, indent=2))
        else:
            print(f"Using source app: {state['source_app']}")
            print(f"Using target app: {state['target_app']}")
            print(result["message"])

        if result["status"] != "success":
            sys.exit(1)
        return


if __name__ == "__main__":
    main()
