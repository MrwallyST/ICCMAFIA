#!/usr/bin/env python3
"""Download latest flashcards + quiz from NotebookLM for Day 14."""
import os, sys, json, subprocess, re, time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR   = Path(__file__).parent
PYTHON       = sys.executable
SCRIPTS_PATH = r"C:\Users\cesar\AppData\Local\Python\pythoncore-3.14-64\Scripts"
NB           = "8be24334-4293-41e0-a87d-cd20e67349ae"
DAY_NUM      = 14
day_dir      = SCRIPT_DIR / "studios" / f"day-{DAY_NUM}"
TITLE        = "Day 14: The Complete ICC Playbook - Putting It All Together"
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8",
       "PATH": SCRIPTS_PATH + ";" + os.environ.get("PATH", "")}

def nlm(args, timeout=300):
    cmd = [PYTHON, "-m", "notebooklm"] + args
    r = subprocess.run(cmd, capture_output=True, env=ENV, timeout=timeout,
                       encoding="utf-8", errors="replace")
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    return out

def extract_id(text):
    m = re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", text)
    return m[0] if m else None

def wait_done(aid, max_wait=300):
    print(f"   Polling {aid[:8]}...", flush=True)
    for _ in range(max_wait // 10):
        out = nlm(["artifact", "list", "-n", NB], timeout=60)
        for line in out.splitlines():
            if aid[:8] in line:
                if "complete" in line.lower() or "ready" in line.lower():
                    print(" ✓"); return True
                if "fail" in line.lower() or "error" in line.lower():
                    print(" ✗"); return False
        print(".", end="", flush=True)
        time.sleep(10)
    print(" timeout"); return False

def quiz_to_md(raw_path, md_path):
    """Try multiple strategies to convert quiz to working MD."""
    raw = Path(raw_path).read_text(encoding="utf-8", errors="replace")
    # Strategy 1: parse as JSON
    try:
        idx = raw.find('{')
        if idx >= 0:
            data = json.loads(raw[idx:])
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
            print(f"   Converted {len(data.get('questions',[]))} questions to MD ✓")
            return True
    except Exception as e:
        print(f"   JSON parse failed: {e}")
    # Strategy 2: the file might already be markdown
    if "## Question" in raw or "- [x]" in raw or "- [ ]" in raw:
        Path(md_path).write_text(raw, encoding="utf-8")
        print("   File already in MD format — copied ✓")
        return True
    print("   Could not convert quiz")
    return False

def rebuild_html():
    days_path = SCRIPT_DIR / "days.json"
    html_path = SCRIPT_DIR / "index.html"
    days = json.loads(days_path.read_text(encoding="utf-8"))
    days_str = json.dumps(days, ensure_ascii=False, separators=(',', ':'))
    html = html_path.read_text(encoding="utf-8")
    new_line = f'  const DAYS_DATA = {days_str};'
    html = re.sub(r'  const DAYS_DATA = \[.*?\];', new_line, html, flags=re.DOTALL)
    html_path.write_text(html, encoding="utf-8")
    print(f"   HTML rebuilt ({len(days)} days)")

def main():
    nlm(["use", NB])

    flash_path    = day_dir / f"day{DAY_NUM}_flashcards.json"
    quiz_raw_path = day_dir / f"day{DAY_NUM}_quiz_raw.json"
    quiz_md_path  = day_dir / f"day{DAY_NUM}_quiz.md"

    # ── FLASHCARDS ────────────────────────────────────────────────────────────
    print("\n=== FLASHCARDS ===")
    # Generate fresh set
    out = nlm(["generate", "flashcards",
               f"Create 10 flashcards ONLY for Day {DAY_NUM}: {TITLE}. Front=concept, Back=definition.",
               "-n", NB, "--no-wait"], timeout=60)
    fid = extract_id(out)
    print(f"   Generated ID: {fid}")
    if fid:
        wait_done(fid, max_wait=300)
        # Try download with artifact ID
        result = nlm(["download", "flashcards", str(flash_path), "-a", fid, "--force"], timeout=120)
        print(f"   Download result: {result[:100]}")
        if not flash_path.exists() or flash_path.stat().st_size < 100:
            # Try without -a, just grab latest
            print("   Trying latest flashcard download...")
            result = nlm(["download", "flashcards", str(flash_path), "--force"], timeout=120)
            print(f"   Result: {result[:100]}")
    print(f"   Flashcards: {'✅ ' + str(flash_path.stat().st_size) + ' bytes' if flash_path.exists() else '❌'}")

    # ── QUIZ ──────────────────────────────────────────────────────────────────
    print("\n=== QUIZ ===")
    out = nlm(["generate", "quiz",
               f"Create 10 multiple-choice questions ONLY for Day {DAY_NUM}: {TITLE}. 4 options each, one correct.",
               "-n", NB, "--no-wait"], timeout=60)
    qid = extract_id(out)
    print(f"   Generated ID: {qid}")
    if qid:
        wait_done(qid, max_wait=300)
        # Try download as JSON
        result = nlm(["download", "quiz", str(quiz_raw_path), "-a", qid, "--force"], timeout=120)
        print(f"   JSON download: {result[:100]}")
        if quiz_raw_path.exists() and quiz_raw_path.stat().st_size > 100:
            quiz_to_md(quiz_raw_path, quiz_md_path)
        else:
            # Try latest
            print("   Trying latest quiz download...")
            result = nlm(["download", "quiz", str(quiz_raw_path), "--force"], timeout=120)
            if quiz_raw_path.exists() and quiz_raw_path.stat().st_size > 100:
                quiz_to_md(quiz_raw_path, quiz_md_path)
            else:
                # Last resort: download as report/markdown
                print("   Trying report download as fallback...")
                result = nlm(["download", "report", str(quiz_md_path), "-a", qid, "--force"], timeout=120)
                print(f"   Report result: {result[:100]}")
    print(f"   Quiz MD: {'✅ ' + str(quiz_md_path.stat().st_size) + ' bytes' if quiz_md_path.exists() else '❌'}")

    # ── Update JSON + push ────────────────────────────────────────────────────
    print("\n=== Updating site + pushing ===")
    days_path = SCRIPT_DIR / "days.json"
    days = json.loads(days_path.read_text(encoding="utf-8"))
    for d in days:
        if d.get("day") == DAY_NUM:
            d["quizFile"]     = f"./studios/day-{DAY_NUM}/day{DAY_NUM}_quiz.md"
            d["flashcardsUrl"]= f"./studios/day-{DAY_NUM}/day{DAY_NUM}_flashcards.json"
    days_path.write_text(json.dumps(days, indent=2, ensure_ascii=False), encoding="utf-8")
    rebuild_html()

    subprocess.run(["git", "add", "-A"], cwd=str(SCRIPT_DIR), env=ENV, timeout=30)
    subprocess.run(["git", "commit", "-m", "Day 14: fix flashcards + quiz download"], cwd=str(SCRIPT_DIR), env=ENV, timeout=30)
    r = subprocess.run(["git", "push"], cwd=str(SCRIPT_DIR), env=ENV, timeout=60)

    print("\n" + "="*50)
    print(f"  📇 Flashcards : {'✅' if flash_path.exists() else '❌'}")
    print(f"  ✅ Quiz MD    : {'✅' if quiz_md_path.exists() else '❌'}")
    print(f"  🌐 GitHub     : {'pushed' if r.returncode==0 else 'FAILED'}")
    print("="*50)

if __name__ == "__main__":
    main()
