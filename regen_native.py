import subprocess, sys, re, time, os
from pathlib import Path

PYTHON = sys.executable
SCRIPTS_PATH = r"C:\Users\cesar\AppData\Local\Python\pythoncore-3.14-64\Scripts"
ENV = {**os.environ, "PATH": SCRIPTS_PATH + ";" + os.environ.get("PATH", "")}
NB = "8be24334-4293-41e0-a87d-cd20e67349ae"

def nlm(args, timeout=120):
    r = subprocess.run([PYTHON, "-m", "notebooklm"] + args, capture_output=True, text=True, env=ENV, timeout=timeout)
    out = r.stdout + r.stderr
    print(f"  CMD: nlm {' '.join(args[:3])}... -> {out[:200]}")
    return out

def extract_id(text):
    m = re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", text)
    return m[0] if m else None

def wait_for(tid, label):
    print(f"  Waiting for {label} ({tid[:8]})...")
    for i in range(60):
        s = nlm(["artifact", "list", "-n", NB])
        relevant = [l for l in s.splitlines() if tid[:8] in l]
        if relevant and any("complete" in l.lower() or "ready" in l.lower() for l in relevant):
            print(f"  ✓ {label} completed!")
            return True
        if relevant and any("fail" in l.lower() or "error" in l.lower() for l in relevant):
            print(f"  ✗ {label} FAILED!")
            return False
        time.sleep(10)
    print(f"  ⏰ {label} timed out")
    return False

OUT = Path(r"c:\Users\cesar\Documents\New folder\TradesBySci\studios\day-1")

# 1. Slides (SHORT)
print("\n=== SLIDE DECK (--length short) ===")
out = nlm(["generate", "slide-deck", 
    "Lesson slides for Day 1: The Foundation - ICC Framework Decoded Part 1. Cover only the most essential concepts. One key idea per slide. Keep it SHORT.",
    "--length", "short", "--format", "presenter", "-n", NB, "--no-wait"])
tid = extract_id(out)
if tid and wait_for(tid, "Slides"):
    dest = str(OUT / "day1_slides.pdf")
    print(f"  Downloading to {dest}")
    dlout = nlm(["download", "slide-deck", dest, "-a", tid, "--force"])
    print(f"  Download result: {dlout[:300]}")
    sz = Path(dest).stat().st_size if Path(dest).exists() else 0
    print(f"  File size: {sz:,} bytes")

# 2. Infographic (BRANDED)
print("\n=== INFOGRAPHIC (branded) ===")
out = nlm(["generate", "infographic",
    "Visual overview of Day 1: The Foundation - ICC Framework Decoded Part 1. Create a clear, beginner-friendly visual breakdown. BRANDING: Feature 'ICCMAFIA-AI' prominently. CREDIT: Give credit to 'Trades by Sci'. WEBSITE: Include mrwallyst.github.io/ICCMAFIA",
    "-n", NB, "--no-wait"])
tid = extract_id(out)
if tid and wait_for(tid, "Infographic"):
    dest = str(OUT / "day1_infographic.png")
    dlout = nlm(["download", "infographic", dest, "-a", tid, "--force"])
    print(f"  Download: {dlout[:200]}")

# 3. Quiz (8 questions)
print("\n=== QUIZ (8 questions) ===")
out = nlm(["generate", "quiz",
    "8 questions specifically about Day 1: The Foundation - ICC Framework Decoded Part 1",
    "-n", NB, "--no-wait"])
tid = extract_id(out)
if tid and wait_for(tid, "Quiz"):
    dest = str(OUT / "day1_quiz.md")
    dlout = nlm(["download", "quiz", dest, "-a", tid, "--force"])
    print(f"  Download: {dlout[:200]}")

# 4. Flashcards
print("\n=== FLASHCARDS ===")
out = nlm(["generate", "flashcards",
    "Focus on Day 1: The Foundation - ICC Framework Decoded Part 1",
    "-n", NB, "--no-wait"])
tid = extract_id(out)
if tid and wait_for(tid, "Flashcards"):
    dest = str(OUT / "day1_flashcards.json")
    dlout = nlm(["download", "flashcards", dest, "-a", tid, "--force"])
    print(f"  Download: {dlout[:200]}")

print("\n=== ALL DONE ===")
