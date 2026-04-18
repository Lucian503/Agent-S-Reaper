import os
import subprocess
import openai

def get_last_logs():
    if os.path.exists("logs/agent.log"):
        with open("logs/agent.log", "r") as f:
            return "".join(f.readlines()[-60:])
    return "No logs found."

def ask_for_fix(error_log):
    print("🤖 Analyzing failure and asking for a fix...")
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = f"The Agent-S Researcher failed with this log:\n\n{error_log}\n\nRewrite the 'run_s3_gemini_macos.sh' or '.github/workflows/autonomous_research.yml' to fix this. Return ONLY the full code of the file that needs changing. No prose."
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are a DevOps expert fixing Agent-S on GitHub Actions."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def apply_and_push(fix_code):
    filename = "run_s3_gemini_macos.sh" if "bin/bash" in fix_code else ".github/workflows/autonomous_research.yml"
    print(f"🛠️ Applying fix to {filename}...")
    with open(filename, "w") as f:
        f.write(fix_code.strip('`').replace('yaml', '').replace('bash', '').strip())
    
    subprocess.run(["git", "config", "user.name", "Self-Healer-Bot"])
    subprocess.run(["git", "config", "user.email", "bot@healer.com"])
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "Self-healing: Fixed crash/loop autonomously"])
    subprocess.run(["git", "push"])

if __name__ == "__main__":
    logs = get_last_logs()
    if "Error" in logs or "Traceback" in logs or "black" in logs:
        try:
            fix = ask_for_fix(logs)
            apply_and_push(fix)
        except Exception as e:
            print(f"Healer failed: {e}")
