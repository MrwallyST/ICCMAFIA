#!/usr/bin/env python3
"""Patch Day 14 — fix missing Flashcards and Quiz, then kick off All For One."""

import os, sys, json, time, subprocess, re
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR      = Path(__file__).parent
DAYS_JSON       = SCRIPT_DIR / "days.json"
PYTHON          = sys.executable
SCRIPTS_PATH    = r"C:\Users\cesar\AppData\Local\Python\pythoncore-3.14-64\Scripts"
MASTER_NOTEBOOK = "8be24334-4293-41e0-a87d-cd20e67349ae"
DAY_NUM         = 14
TITLE           = "Day 14: The Complete ICC Playbook - Putting It All Together"
day_dir         = SCRIPT_DIR / "studios" / f"day-{DAY_NUM}"

ENV = {**os.environ, "PYTHONIOENCODING": "utf-8",
       "PATH": SCRIPTS_PATH + ";" + os.environ.get("PATH", "")}

def nlm(args, timeout=600):
    cmd = [PYTHON, "-m", "notebooklm"] + args
    r = subprocess.run(cmd, capture_output=True, env=ENV, timeout=timeout,
                       encoding="utf-8", errors="replace")
    return ((r.stdout or "") + (r.stderr or "")).strip()

def extract_id(text):
    m = re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", text)
    return m[0] if m else None

def wait_for(artifact_id, max_wait=600):
    print(f"   Waiting for {artifact_id[:8]}...", flush=True)
    for _ in range(max_wait // 15):
        out = nlm(["artifact", "list", "-n", MASTER_NOTEBOOK], timeout=60)
        for line in out.splitlines():
            if artifact_id[:8] in line:
                if "complete" in line.lower() or "ready" in line.lower():
                    print(f"\n   ✓ Done!")
                    return True
                if "fail" in line.lower() or "error" in line.lower():
                    print(f"\n   ✗ Failed!")
                    return False
        print(".", end="", flush=True)
        time.sleep(15)
    print("\n   Timed out.")
    return False

def quiz_json_to_md(json_path, md_path):
    try:
        raw = Path(json_path).read_text(encoding="utf-8")
        # Handle both raw JSON and markdown-wrapped JSON
        idx = raw.find('{')
        if idx > 0:
            raw = raw[idx:]
        data = json.loads(raw)
        md = f"# {data.get('title', 'Trading Quiz')}\n\n"
        for i, q in enumerate(data.get("questions", []), 1):
            md += f"## Question {i}\n{q['question']}\n\n"
            for opt in q.get("answerOptions", []):
                mark = "x" if opt.get("isCorrect") else " "
                md += f"- [{mark}] {opt['text']}\n"
            md += "\n"
            if "hint" in q:
                md += f"**Hint:** {q['hint']}\n\n"
        Path(md_path).write_text(md, encoding="utf-8")
        print(f"   Quiz converted to Markdown ✓ ({len(data.get('questions',[]))} questions)")
        return True
    except Exception as e:
        print(f"   Quiz conversion error: {e}")
        return False

def rebuild_html():
    html_path = SCRIPT_DIR / "index.html"
    days = json.loads(DAYS_JSON.read_text(encoding="utf-8"))
    days_str = json.dumps(days, ensure_ascii=False, separators=(',', ':'))
    html = html_path.read_text(encoding="utf-8")
    new_line = f'  const DAYS_DATA = {days_str};'
    html = re.sub(r'  const DAYS_DATA = \[.*?\];', new_line, html, flags=re.DOTALL)
    html_path.write_text(html, encoding="utf-8")
    print(f"   index.html updated with {len(days)} day(s)")

def main():
    flash_path    = day_dir / f"day{DAY_NUM}_flashcards.json"
    quiz_raw_path = day_dir / f"day{DAY_NUM}_quiz_raw.json"
    quiz_md_path  = day_dir / f"day{DAY_NUM}_quiz.md"

    nlm(["use", MASTER_NOTEBOOK])

    # ── Fix Flashcards ────────────────────────────────────────────────────────
    print("\n[1/4] Generating Flashcards for Day 14...")
    out = nlm(["generate", "flashcards",
               f"FOCUS EXCLUSIVELY on Day {DAY_NUM}: {TITLE}. Generate 10 flashcards covering key concepts.",
               "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    flash_id = extract_id(out)
    print(f"   ID: {flash_id}")
    if flash_id and wait_for(flash_id):
        print(f"   Downloading flashcards...")
        nlm(["download", "flashcards", str(flash_path), "-a", flash_id, "--force"])
        print(f"   Flashcards: {'✅' if flash_path.exists() else '❌'}")
    else:
        print("   Flashcard generation failed — trying direct download of latest...")
        nlm(["download", "flashcards", str(flash_path), "--force"])

    # ── Fix Quiz ──────────────────────────────────────────────────────────────
    print("\n[2/4] Generating Quiz for Day 14...")
    out = nlm(["generate", "quiz",
               f"Create 10 multiple-choice questions EXCLUSIVELY about Day {DAY_NUM}: {TITLE}.",
               "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    quiz_id = extract_id(out)
    print(f"   ID: {quiz_id}")
    if quiz_id and wait_for(quiz_id):
        print(f"   Downloading quiz as JSON...")
        nlm(["download", "quiz", str(quiz_raw_path), "-a", quiz_id, "--force"])
        if quiz_raw_path.exists() and quiz_raw_path.stat().st_size > 100:
            quiz_json_to_md(quiz_raw_path, quiz_md_path)
        else:
            # Fallback: download as markdown directly
            print("   Trying markdown download fallback...")
            nlm(["download", "report", str(quiz_md_path), "-a", quiz_id, "--force"])
        print(f"   Quiz MD: {'✅' if quiz_md_path.exists() else '❌'}")

    # ── Update days.json to ensure quiz points to .md ─────────────────────────
    print("\n[3/4] Verifying days.json quiz pointer...")
    days = json.loads(DAYS_JSON.read_text(encoding="utf-8"))
    for d in days:
        if d.get("day") == DAY_NUM:
            d["quizFile"] = f"./studios/day-{DAY_NUM}/day{DAY_NUM}_quiz.md"
            d["flashcardsUrl"] = f"./studios/day-{DAY_NUM}/day{DAY_NUM}_flashcards.json"
            print(f"   ✓ Day {DAY_NUM} quiz → .md, flashcards → .json")
    DAYS_JSON.write_text(json.dumps(days, indent=2, ensure_ascii=False), encoding="utf-8")
    rebuild_html()

    # ── Git push ──────────────────────────────────────────────────────────────
    print("\n[4/4] Pushing to GitHub...")
    subprocess.run(["git", "add", "-A"], cwd=str(SCRIPT_DIR), env=ENV, timeout=30)
    subprocess.run(["git", "commit", "-m", "Fix Day 14: add flashcards + quiz"], cwd=str(SCRIPT_DIR), env=ENV, timeout=30)
    r = subprocess.run(["git", "push"], cwd=str(SCRIPT_DIR), env=ENV, timeout=60)

    print("\n" + "="*50)
    print("Day 14 Patch Complete:")
    print(f"  📇 Flashcards : {'✅' if flash_path.exists() else '❌'}")
    print(f"  ✅ Quiz (MD)  : {'✅' if quiz_md_path.exists() else '❌'}")
    if r.returncode == 0:
        print("  🌐 Pushed to GitHub — live in ~60s")
    print("="*50)

if __name__ == "__main__":
    main()
