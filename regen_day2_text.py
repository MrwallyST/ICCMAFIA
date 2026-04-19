import subprocess, sys, re, time, os
from pathlib import Path

PYTHON = sys.executable
SCRIPTS_PATH = r"C:\Users\cesar\AppData\Local\Python\pythoncore-3.14-64\Scripts"
ENV = {**os.environ, "PATH": SCRIPTS_PATH + ";" + os.environ.get("PATH", "")}
NB = "8be24334-4293-41e0-a87d-cd20e67349ae"
out_dir = Path(r"c:\Users\cesar\Documents\New folder\TradesBySci\studios\day-2")

def nlm(args, timeout=120):
    r = subprocess.run([PYTHON, "-m", "notebooklm"] + args, capture_output=True, text=True, env=ENV, timeout=timeout)
    return r.stdout + r.stderr

def extract_id(text):
    m = re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", text)
    return m[0] if m else None

def wait_for_artifact(tid):
    for i in range(60):
        s = nlm(["artifact", "list", "-n", NB])
        if s and tid[:8] in s and ("complete" in s.lower() or "ready" in s.lower()):
            return True
        time.sleep(10)
    return False

# 1. YouTube Script
print("Generating Day 2 YT Script...")
yt_prompt = (
    "Write an engaging, cinematic YouTube video script (video overview) covering these concepts. "
    "INTRO: The host MUST open by saying: 'Welcome to ICCMAFIA-AI, today we are summarizing Day 2 of the TradesbySci ICC course! We will be doing all of the course videos...' "
    "CORE: Break down all key trading concepts from the lesson clearly like teaching a complete beginner. "
    "BONUS: WEBSITE CTA: The script MUST enthusiastically instruct viewers to click the link in the description (mrwallyst.github.io/ICCMAFIA) to access their free Interactive Study Guide, Quiz, Mind Map, Flashcards, and Audio Podcast. "
    "OUTRO: End with a strong, cinematic Call to Action reminding viewers to like, comment, and subscribe to ICCMAFIA-AI. "
    "CREDIT: Give explicit credit to TradesbySci as the original course creator."
)
out = nlm(["generate", "report", "--format", "custom", "--append", yt_prompt, "Day 2: ICC Framework Decoded Part 2 - Support & Resistance", "-n", NB, "--no-wait"])
tid = extract_id(out)
if tid and wait_for_artifact(tid):
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    nlm(["download", "report", str(out_dir / "day2_ytscript.md"), "-a", tid, "--force"])
    print("YT Script downloaded.")

# 2. Twitter Thread
print("Generating Day 2 Twitter Thread...")
thread_prompt = "Write a viral 10-post Thread (optimized for X/Instagram Threads) summarizing Day 2 concepts. CRITICAL: Each individual post MUST be strictly under 400 characters so I can easily copy and paste them. Number each post (1/10, 2/10, etc.), include a punchy BOLD topic header for each post (e.g. 1/10 🚨 **TRADING VS. GAMBLING**), and make sure the first post explicitly states 'Day 2 of the TradesbySci ICC Course'."
out = nlm(["generate", "report", "--format", "custom", "--append", thread_prompt, "Day 2: ICC Framework Decoded Part 2 - Support & Resistance", "-n", NB, "--no-wait"])
tid = extract_id(out)
if tid and wait_for_artifact(tid):
    nlm(["download", "report", str(out_dir / "day2_twitter.md"), "-a", tid, "--force"])
    print("Twitter Thread downloaded.")
