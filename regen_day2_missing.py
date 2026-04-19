import subprocess, sys, re, time, os
from pathlib import Path

PYTHON = sys.executable
SCRIPTS_PATH = r"C:\Users\cesar\AppData\Local\Python\pythoncore-3.14-64\Scripts"
ENV = {**os.environ, "PATH": SCRIPTS_PATH + ";" + os.environ.get("PATH", "")}
NB = "8be24334-4293-41e0-a87d-cd20e67349ae"
out_dir = Path(r"c:\Users\cesar\Documents\New folder\TradesBySci\studios\day-2")
out_dir.mkdir(parents=True, exist_ok=True)

def nlm(args, timeout=120):
    r = subprocess.run([PYTHON, "-m", "notebooklm"] + args, capture_output=True, text=True, env=ENV, timeout=timeout)
    return r.stdout + r.stderr

def extract_id(text):
    m = re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", text)
    return m[0] if m else None

def wait_for_artifact(tid):
    for i in range(60):
        s = nlm(["artifact", "list", "-n", NB])
        relevant = [l for l in s.splitlines() if tid[:8] in l]
        if relevant and any("complete" in l.lower() or "ready" in l.lower() for l in relevant):
            return True
        time.sleep(10)
    return False

# 1. Quiz
print("Generating Quiz...")
out = nlm(["generate", "quiz", "8 questions specifically about Day 2: ICC Framework Decoded Part 2 - Support & Resistance", "-n", NB, "--no-wait"])
tid = extract_id(out)
print(f"Quiz Task: {tid}")
if tid and wait_for_artifact(tid):
    print("Downloading Quiz...")
    os.environ['PYTHONIOENCODING'] = 'utf-8' # For safe downloading
    out = nlm(["download", "quiz", str(out_dir / "day2_quiz.md"), "-a", tid, "--force"])
    print(out[:300])

# 2. Flashcards
print("Generating Flashcards...")
out = nlm(["generate", "flashcards", "Focus on Day 2: ICC Framework Decoded Part 2 - Support & Resistance", "-n", NB, "--no-wait"])
tid = extract_id(out)
print(f"Flashcards Task: {tid}")
if tid and wait_for_artifact(tid):
    print("Downloading Flashcards...")
    out = nlm(["download", "flashcards", str(out_dir / "day2_flashcards.json"), "-a", tid, "--force"])
    print(out[:300])

print("DONE")
