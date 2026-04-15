#!/usr/bin/env python3
"""
TradesBySci — Add Day Pipeline (V3 Learning Builder)
=====================================
Uses your MASTER NotebookLM notebook and adds each new day as a source.
Generates Audio, Study Guide, Flashcards, Mind Map, Quiz, and Infographic concurrently.
Downloads them locally and updates days.json for the TradesBySci UI.

Usage:
  python add_day.py --day 2 --youtube "https://www.youtube.com/watch?v=VIDEO_ID"
                   --title "Your Day 2 Title"
                   --desc "English description"

After running, the website inline HTML data auto-updates.
"""

import os, sys, json, time, subprocess, re, argparse
from pathlib import Path

# Force UTF-8 output on Windows (avoids cp1252 UnicodeEncodeError)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── Config ──────────────────────────────────────────────────────────────────
SCRIPT_DIR      = Path(__file__).parent
DAYS_JSON       = SCRIPT_DIR / "days.json"
STUDIOS_DIR     = SCRIPT_DIR / "studios"
PYTHON          = sys.executable
SCRIPTS_PATH    = r"C:\Users\cesar\AppData\Local\Python\pythoncore-3.14-64\Scripts"

# YOUR MASTER NOTEBOOK
MASTER_NOTEBOOK = "8be24334-4293-41e0-a87d-cd20e67349ae"

ENV = {
    **os.environ,
    "PYTHONIOENCODING": "utf-8",
    "PATH": SCRIPTS_PATH + ";" + os.environ.get("PATH", "")
}

# ── Helpers ──────────────────────────────────────────────────────────────────
def nlm(args: list, timeout=600) -> str:
    """Run a notebooklm CLI command and return combined stdout+stderr as utf-8."""
    cmd = [PYTHON, "-m", "notebooklm"] + args
    result = subprocess.run(
        cmd, capture_output=True, env=ENV, timeout=timeout,
        encoding="utf-8", errors="replace"
    )
    return ((result.stdout or "") + (result.stderr or "")).strip()

def extract_id(text):
    matches = re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", text)
    return matches[0] if matches else None

def step(n, total, msg):
    print(f"\n[{n}/{total}] {msg}", flush=True)

def wait_for_all(artifact_ids, max_wait=900):
    """Poll artifact list until all given IDs show as complete."""
    pending = set(artifact_ids)
    print(f"   Waiting for {len(pending)} artifacts to complete...", flush=True)
    for i in range(max_wait // 15):
        if not pending:
            return True
        out = nlm(["artifact", "list", "-n", MASTER_NOTEBOOK], timeout=60)
        lines = out.splitlines()
        
        still_pending = set()
        for a_id in pending:
            # Look for this artifact in the list output
            relevant = [l for l in lines if a_id[:8] in l]
            if any("complete" in l.lower() or "ready" in l.lower() for l in relevant):
                print(f"\n   ✓ Artifact {a_id[:8]} completed!")
            elif any("fail" in l.lower() or "error" in l.lower() for l in relevant):
                print(f"\n   ✗ Artifact {a_id[:8]} failed!")
            else:
                still_pending.add(a_id)
        
        pending = still_pending
        if pending:
            print(".", end="", flush=True)
            time.sleep(15)
            
    print("\n   Timed out waiting for some artifacts.")
    return False

def rebuild_html():
    """Embed the latest days.json data directly into index.html so it works on file://"""
    html_path = SCRIPT_DIR / "index.html"
    if not html_path.exists() or not DAYS_JSON.exists():
        return
    days = json.loads(DAYS_JSON.read_text(encoding="utf-8"))
    days_json_str = json.dumps(days, ensure_ascii=False, separators=(',', ':'))
    html = html_path.read_text(encoding="utf-8")
    import re as _re
    new_line = f'  const DAYS_DATA = {days_json_str};'
    html = _re.sub(r'  const DAYS_DATA = \[.*?\];', new_line, html, flags=_re.DOTALL)
    html_path.write_text(html, encoding="utf-8")
    print(f"   index.html updated with {len(days)} day(s) of data")

# ── Main pipeline ─────────────────────────────────────────────────────────────
def run_pipeline(
    day_num: int,
    youtube_url: str,
    title_en: str,
    title_es: str,
    desc_en: str,
    desc_es: str,
    takeaways_en: list,
    takeaways_es: list,
):
    TOTAL = 6
    day_dir = STUDIOS_DIR / f"day-{day_num}"
    day_dir.mkdir(parents=True, exist_ok=True)
    youtube_id = youtube_url.split("v=")[-1].split("&")[0] if "v=" in youtube_url else ""

    # 1. Active context
    step(1, TOTAL, "Setting master notebook as active context...")
    out = nlm(["use", MASTER_NOTEBOOK])
    
    # 2. Add source
    step(2, TOTAL, f"Adding Day {day_num} YouTube video as source...")
    out = nlm(["source", "add", youtube_url, "-n", MASTER_NOTEBOOK], timeout=60)
    print("   Source requested. Waiting 15s for indexing...")
    time.sleep(15)

    # 3. Fire parallel generations
    step(3, TOTAL, f"Requesting full learning suite for Day {day_num}...")
    
    tasks = {}

    print("   -> Audio Overview")
    out = nlm(["generate", "audio", 
               f"Focus specifically on Day {day_num}: {title_en}. Key topics: {', '.join(takeaways_en[:3])}. IMPORTANT INSTRUCTION: Make sure to explicitly tell the listener 'Click the link in bio to get more information on Day {day_num}' and say that the learning materials are entirely free.", 
               "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['audio'] = extract_id(out)

    print("   -> Study Guide")
    out = nlm(["generate", "report", f"Focus on Day {day_num}: {title_en}", "--format", "study-guide", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['study'] = extract_id(out)

    print("   -> Flashcards")
    out = nlm(["generate", "flashcards", f"Focus on Day {day_num}: {title_en}", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['flash'] = extract_id(out)

    print("   -> Mind Map")
    out = nlm(["generate", "mind-map", f"Focus on Day {day_num}: {title_en}", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['mind'] = extract_id(out)

    print("   -> Quiz")
    out = nlm(["generate", "quiz", f"8 questions specifically about Day {day_num}: {title_en}", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['quiz'] = extract_id(out)

    print("   -> Infographic")
    out = nlm(["generate", "infographic", f"Visual overview of Day {day_num}: {title_en}", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['info'] = extract_id(out)

    print("   -> Slide Deck")
    out = nlm(["generate", "slide-deck", f"Lesson slides for Day {day_num}: {title_en}. Cover all key concepts as a structured presentation.", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['slides'] = extract_id(out)

    print("   -> Data Table")
    out = nlm(["generate", "data-table", f"Organize key concepts, definitions, and examples from Day {day_num}: {title_en} into a structured reference table.", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['table'] = extract_id(out)

    # Clean None values in case of failure
    active_tasks = {k: v for k, v in tasks.items() if v}
    print(f"   Successfully launched {len(active_tasks)} parallel generations.")

    # 4. Wait for all
    step(4, TOTAL, "Waiting for all NotebookLM artifacts to finish generating...")
    wait_for_all(list(active_tasks.values()), max_wait=900)

    # 5. Download all
    step(5, TOTAL, "Downloading completed resources...")
    paths = {
        'audio':  day_dir / f"day{day_num}_en.mp3",
        'study':  day_dir / f"day{day_num}_study.md",
        'flash':  day_dir / f"day{day_num}_flashcards.json",
        'mind':   day_dir / f"day{day_num}_mindmap.json",
        'quiz':   day_dir / f"day{day_num}_quiz.md",
        'info':   day_dir / f"day{day_num}_infographic.png",
        'slides': day_dir / f"day{day_num}_slides.pdf",
        'table':  day_dir / f"day{day_num}_datatable.md",
    }
    
    if 'audio' in active_tasks:
        print(f"   - Audio -> {paths['audio'].name}")
        nlm(["download", "audio", str(paths['audio']), "-a", active_tasks['audio'], "--force"])
    if 'study' in active_tasks:
        print(f"   - Study Guide -> {paths['study'].name}")
        # Note: --format markdown doesn't apply when picking with -a usually, but we use positional download report
        nlm(["download", "report", str(paths['study']), "-a", active_tasks['study'], "--force"])
    if 'flash' in active_tasks:
        print(f"   - Flashcards -> {paths['flash'].name}")
        nlm(["download", "flashcards", str(paths['flash']), "-a", active_tasks['flash'], "--force"])
    if 'mind' in active_tasks:
        print(f"   - Mind Map -> {paths['mind'].name}")
        nlm(["download", "mind-map", str(paths['mind']), "-a", active_tasks['mind'], "--force"])
    if 'quiz' in active_tasks:
        print(f"   - Quiz -> {paths['quiz'].name}")
        nlm(["download", "quiz", str(paths['quiz']), "-a", active_tasks['quiz'], "--force"])
    if 'info' in active_tasks:
        print(f"   - Infographic -> {paths['info'].name}")
        nlm(["download", "infographic", str(paths['info']), "-a", active_tasks['info'], "--force"])
    if 'slides' in active_tasks:
        print(f"   - Slide Deck -> {paths['slides'].name}")
        nlm(["download", "slide-deck", str(paths['slides']), "-a", active_tasks['slides'], "--force"])
    if 'table' in active_tasks:
        print(f"   - Data Table -> {paths['table'].name}")
        nlm(["download", "data-table", str(paths['table']), "-a", active_tasks['table'], "--force"])

    # 6. Update JSON
    step(6, TOTAL, "Updating website data...")
    if DAYS_JSON.exists():
        days = json.loads(DAYS_JSON.read_text(encoding="utf-8"))
    else:
        days = []

    days = [d for d in days if d.get("day") != day_num]

    new_day = {
        "day": day_num,
        "title": title_en, "titleEs": title_es,
        "description": desc_en, "descriptionEs": desc_es,
        "youtubeId": youtube_id,
        "reelUrl": "",
        "studios": {
            "en": {
                "audioUrl":   f"./studios/day-{day_num}/{paths['audio'].name}" if paths['audio'].exists() else "",
                "audioLabel": f"Day {day_num} Audio Overview"
            },
            "es": {"audioUrl": "", "audioLabel": f"Día {day_num} — Resumen en Español"}
        },
        "infographicUrl": f"./studios/day-{day_num}/{paths['info'].name}" if paths['info'].exists() else "",
        "quizFile":       f"./studios/day-{day_num}/{paths['quiz'].name}" if paths['quiz'].exists() else "",
        "studyGuideUrl":  f"./studios/day-{day_num}/{paths['study'].name}" if paths['study'].exists() else "",
        "flashcardsUrl":  f"./studios/day-{day_num}/{paths['flash'].name}" if paths['flash'].exists() else "",
        "mindMapUrl":     f"./studios/day-{day_num}/{paths['mind'].name}" if paths['mind'].exists() else "",
        "slideDeckUrl":   f"./studios/day-{day_num}/{paths['slides'].name}" if paths['slides'].exists() else "",
        "dataTableUrl":   f"./studios/day-{day_num}/{paths['table'].name}" if paths['table'].exists() else "",
        "keyTakeaways":   takeaways_en,
        "keyTakeawaysEs": takeaways_es,
        "notebookId":     MASTER_NOTEBOOK
    }

    days.append(new_day)
    days.sort(key=lambda d: d["day"])
    DAYS_JSON.write_text(json.dumps(days, indent=2, ensure_ascii=False), encoding="utf-8")
    rebuild_html()

    print("\n" + "="*60)
    print(f"Day {day_num} Learning Modules Platform complete!")
    print(f"  Audio      : {'OK' if paths['audio'].exists() else 'MISSING'}")
    print(f"  Study Guide: {'OK' if paths['study'].exists() else 'MISSING'}")
    print(f"  Flashcards : {'OK' if paths['flash'].exists() else 'MISSING'}")
    print(f"  Mind Map   : {'OK' if paths['mind'].exists() else 'MISSING'}")
    print(f"  Quiz       : {'OK' if paths['quiz'].exists() else 'MISSING'}")
    print(f"  Infographic: {'OK' if paths['info'].exists() else 'MISSING'}")
    print(f"  Slide Deck : {'OK' if paths['slides'].exists() else 'MISSING'}")
    print(f"  Data Table : {'OK' if paths['table'].exists() else 'MISSING'}")
    print(f"  index.html : Updated (open in Chrome to see changes)")
    print("="*60)

# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(description="Add a TradesBySci day + full learning suite")
    p.add_argument("--day",       type=int,  required=True)
    p.add_argument("--youtube",   default="")
    p.add_argument("--title",     default="")
    p.add_argument("--title-es",  default="")
    p.add_argument("--desc",      default="")
    p.add_argument("--desc-es",   default="")
    args = p.parse_args()

    if not args.youtube:
        print("Error: --youtube is required")
        sys.exit(1)

    takeaways_en = ["ICC Framework: Indications, Corrections, Continuations", "How to read order flow and identify liquidity zones", "The 3 market phases every futures trader must know", "Real trade setups from the Trades by Sci curriculum"]
    takeaways_es = ["Marco ICC: Indicaciones, Correcciones, Continuaciones", "Como leer el flujo de ordenes e identificar zonas de liquidez", "Las 3 fases del mercado para futuros", "Setups reales del curriculo de Trades by Sci"]

    run_pipeline(
        day_num    = args.day,
        youtube_url= args.youtube,
        title_en   = args.title  or f"TradesBySci Day {args.day}",
        title_es   = args.title_es or f"TradesBySci Dia {args.day}",
        desc_en    = args.desc   or "AI-decoded Trades by Sci lesson.",
        desc_es    = args.desc_es or "Leccion decodificada con IA.",
        takeaways_en = takeaways_en,
        takeaways_es = takeaways_es,
    )

if __name__ == "__main__":
    main()
