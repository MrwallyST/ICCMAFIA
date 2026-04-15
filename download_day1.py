#!/usr/bin/env python3
"""
Poll and download the Day 1 audio when it's ready.
Run: python download_day1.py
"""
import subprocess, sys, time, os
from pathlib import Path

ENV    = {**os.environ, "PYTHONIOENCODING": "utf-8",
          "PATH": r"C:\Users\cesar\AppData\Local\Python\pythoncore-3.14-64\Scripts;" + os.environ.get("PATH", "")}
PYTHON = sys.executable
ARTIFACT_ID = "73af3efb-71ea-4570-96b2-15d55eb08dc4"
OUTPUT      = Path(__file__).parent / "studios" / "day-1" / "day1_en.mp3"

def run(args):
    r = subprocess.run([PYTHON, "-m", "notebooklm"] + args,
                       capture_output=True, text=True, env=ENV,
                       encoding="utf-8", errors="replace")
    return ((r.stdout or "") + (r.stderr or "")).strip()

print("Polling for audio completion... (may take up to 10 min)")
for attempt in range(30):
    out = run(["artifact", "list"])
    if "complete" in out.lower() or "ready" in out.lower():
        print(f"\nAudio is READY! Downloading to {OUTPUT}...")
        break
    if "pending" in out.lower() or "in_progress" in out.lower():
        print(f"  [{attempt+1}/30] Still generating... waiting 30s", end="\r")
        time.sleep(30)
    else:
        print(out)
        break

# Try download regardless
print(f"\nAttempting download -> {OUTPUT}")
result = run(["download", "audio", "--output", str(OUTPUT)])
print(result)
if OUTPUT.exists():
    print(f"\n🎉 SUCCESS! Audio saved: {OUTPUT} ({OUTPUT.stat().st_size // 1024} KB)")
    # Now update days.json
    import json
    days_json = Path(__file__).parent / "days.json"
    days = json.loads(days_json.read_text(encoding="utf-8"))
    for d in days:
        if d["day"] == 1:
            d["studios"]["en"]["audioUrl"] = "./studios/day-1/day1_en.mp3"
            print("✅ days.json updated with audio URL!")
    days_json.write_text(json.dumps(days, indent=2, ensure_ascii=False), encoding="utf-8")
else:
    print("⚠ File not downloaded yet — try running again in a few minutes")
