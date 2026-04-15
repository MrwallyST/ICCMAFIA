#!/usr/bin/env python3
"""
TradesBySci — Add Day Pipeline (V4 Full Suite)
=====================================
Uses your MASTER NotebookLM notebook and adds each new day as a source.
Generates 8 English artifacts + 1 Spanish audio concurrently.
Downloads them locally, updates days.json, rebuilds index.html, and pushes to GitHub.

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

def _clean_mind_map(file_path):
    """Strip NotebookLM metadata prefix and clean invalid control characters from mind map JSON."""
    try:
        raw = open(file_path, 'rb').read().decode('utf-8-sig', errors='replace')
        raw = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', ' ', raw)
        idx = raw.find('{')
        if idx >= 0:
            data = json.loads(raw[idx:], strict=False)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"   Mind map cleaned: {data.get('name', 'unknown')}")
    except Exception as e:
        print(f"   Mind map cleanup warning: {e}")

# ── Main pipeline ─────────────────────────────────────────────────────────────
def run_pipeline(
    day_num: int,
    youtube_url: str,
    title_en: str,
    desc_en: str,
    takeaways_en: list,
):
    TOTAL = 8
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
    out = nlm(["generate", "mind-map", "-n", MASTER_NOTEBOOK], timeout=120)
    # Mind map returns note ID directly, not an artifact ID
    mind_note_id = extract_id(out)
    tasks['mind'] = mind_note_id

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

    print("   -> Blog Post")
    out = nlm(["generate", "report", "--format", "blog-post", f"Write a comprehensive blog post for Day {day_num}: {title_en}", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['blog'] = extract_id(out)

    print("   -> YouTube Script")
    out = nlm(["generate", "report", "--format", "custom", "--append", "Write an engaging YouTube video script (video overview) covering these concepts.", f"Day {day_num}: {title_en}", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['ytscript'] = extract_id(out)

    print("   -> Twitter Thread")
    out = nlm(["generate", "report", "--format", "custom", "--append", "Write a viral 10-tweet Twitter thread summarizing the key concepts.", f"Day {day_num}: {title_en}", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['twitter'] = extract_id(out)

    print("   -> Newsletter")
    out = nlm(["generate", "report", "--format", "custom", "--append", "Write an engaging email newsletter summarizing this lesson.", f"Day {day_num}: {title_en}", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['newsletter'] = extract_id(out)

    print("   -> LinkedIn Carousel")
    out = nlm(["generate", "report", "--format", "custom", "--append", "Write the text copy for a 5-slide LinkedIn carousel post.", f"Day {day_num}: {title_en}", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['linkedin'] = extract_id(out)

    print("   -> FAQ Document")
    out = nlm(["generate", "report", "--format", "custom", "--append", "Write a Frequently Asked Questions (FAQ) document answering common beginner queries.", f"Day {day_num}: {title_en}", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['faq'] = extract_id(out)

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
        'blog':   day_dir / f"day{day_num}_blog.md",
        'ytscript': day_dir / f"day{day_num}_ytscript.md",
        'twitter': day_dir / f"day{day_num}_twitter.md",
        'newsletter': day_dir / f"day{day_num}_newsletter.md",
        'linkedin': day_dir / f"day{day_num}_linkedin.md",
        'faq':    day_dir / f"day{day_num}_faq.md",
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
        nlm(["note", "get", active_tasks['mind'], "-n", MASTER_NOTEBOOK], timeout=60)
        # mind-map is done synchronously, save it via note get
        mm_out = nlm(["note", "get", active_tasks['mind'], "-n", MASTER_NOTEBOOK], timeout=60)
        with open(paths['mind'], 'w', encoding='utf-8') as f:
            f.write(mm_out)
        # Clean the JSON: strip metadata prefix
        _clean_mind_map(paths['mind'])
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
    if 'blog' in active_tasks:
        print(f"   - Blog Post -> {paths['blog'].name}")
        nlm(["download", "report", str(paths['blog']), "-a", active_tasks['blog'], "--force"])
    if 'ytscript' in active_tasks:
        print(f"   - YouTube Script -> {paths['ytscript'].name}")
        nlm(["download", "report", str(paths['ytscript']), "-a", active_tasks['ytscript'], "--force"])
    if 'twitter' in active_tasks:
        print(f"   - Twitter Thread -> {paths['twitter'].name}")
        nlm(["download", "report", str(paths['twitter']), "-a", active_tasks['twitter'], "--force"])
    if 'newsletter' in active_tasks:
        print(f"   - Newsletter -> {paths['newsletter'].name}")
        nlm(["download", "report", str(paths['newsletter']), "-a", active_tasks['newsletter'], "--force"])
    if 'linkedin' in active_tasks:
        print(f"   - LinkedIn Carousel -> {paths['linkedin'].name}")
        nlm(["download", "report", str(paths['linkedin']), "-a", active_tasks['linkedin'], "--force"])
    if 'faq' in active_tasks:
        print(f"   - FAQ Document -> {paths['faq'].name}")
        nlm(["download", "report", str(paths['faq']), "-a", active_tasks['faq'], "--force"])

    # 6. Update JSON
    step(6, TOTAL, "Updating website data...")
    if DAYS_JSON.exists():
        days = json.loads(DAYS_JSON.read_text(encoding="utf-8"))
    else:
        days = []

    days = [d for d in days if d.get("day") != day_num]

    new_day = {
        "day": day_num,
        "title": title_en,
        "description": desc_en,
        "youtubeId": youtube_id,
        "reelUrl": "",
        "audioUrl": f"./studios/day-{day_num}/{paths['audio'].name}" if paths['audio'].exists() else "",
        "infographicUrl": f"./studios/day-{day_num}/{paths['info'].name}" if paths['info'].exists() else "",
        "quizFile":       f"./studios/day-{day_num}/{paths['quiz'].name}" if paths['quiz'].exists() else "",
        "studyGuideUrl":  f"./studios/day-{day_num}/{paths['study'].name}" if paths['study'].exists() else "",
        "flashcardsUrl":  f"./studios/day-{day_num}/{paths['flash'].name}" if paths['flash'].exists() else "",
        "mindMapUrl":     f"./studios/day-{day_num}/{paths['mind'].name}" if paths['mind'].exists() else "",
        "slideDeckUrl":   f"./studios/day-{day_num}/{paths['slides'].name}" if paths['slides'].exists() else "",
        "dataTableUrl":   f"./studios/day-{day_num}/{paths['table'].name}" if paths['table'].exists() else "",
        "blogPostUrl":       f"./studios/day-{day_num}/{paths['blog'].name}" if paths['blog'].exists() else "",
        "youtubeScriptUrl":  f"./studios/day-{day_num}/{paths['ytscript'].name}" if paths['ytscript'].exists() else "",
        "twitterThreadUrl":  f"./studios/day-{day_num}/{paths['twitter'].name}" if paths['twitter'].exists() else "",
        "newsletterUrl":     f"./studios/day-{day_num}/{paths['newsletter'].name}" if paths['newsletter'].exists() else "",
        "linkedinUrl":       f"./studios/day-{day_num}/{paths['linkedin'].name}" if paths['linkedin'].exists() else "",
        "faqUrl":            f"./studios/day-{day_num}/{paths['faq'].name}" if paths['faq'].exists() else "",
        "keyTakeaways":   takeaways_en,
        "notebookId":     MASTER_NOTEBOOK
    }

    days.append(new_day)
    days.sort(key=lambda d: d["day"])
    DAYS_JSON.write_text(json.dumps(days, indent=2, ensure_ascii=False), encoding="utf-8")
    rebuild_html()

    # 8. Git push
    step(8, TOTAL, "Pushing to GitHub Pages...")
    try:
        subprocess.run(["git", "add", "-A"], cwd=str(SCRIPT_DIR), env=ENV, timeout=30)
        subprocess.run(["git", "commit", "-m", f"Day {day_num}: {title_en} — full learning suite"], cwd=str(SCRIPT_DIR), env=ENV, timeout=30)
        subprocess.run(["git", "push"], cwd=str(SCRIPT_DIR), env=ENV, timeout=60)
        print("   Pushed to GitHub! Site will update in ~60 seconds.")
    except Exception as e:
        print(f"   Git push failed: {e}. Push manually with: git add -A && git commit -m 'Day {day_num}' && git push")

    print("\n" + "="*60)
    print(f"🎉 Day {day_num} COMPLETE — Full Learning Suite")
    print(f"  🎧 Audio     : {'✅' if paths['audio'].exists() else '❌'}")
    print(f"  📖 Study     : {'✅' if paths['study'].exists() else '❌'}")
    print(f"  📇 Flashcards: {'✅' if paths['flash'].exists() else '❌'}")
    print(f"  🗺️  Mind Map  : {'✅' if paths['mind'].exists() else '❌'}")
    print(f"  ✅ Quiz      : {'✅' if paths['quiz'].exists() else '❌'}")
    print(f"  🖼️  Infograph : {'✅' if paths['info'].exists() else '❌'}")
    print(f"  🎞️  Slides    : {'✅' if paths['slides'].exists() else '❌'}")
    print(f"  📊 Data Table: {'✅' if paths['table'].exists() else '❌'}")
    print(f"  📝 Blog Post : {'✅' if paths['blog'].exists() else '❌'}")
    print(f"  🎬 YT Script : {'✅' if paths['ytscript'].exists() else '❌'}")
    print(f"  🐦 Twitter   : {'✅' if paths['twitter'].exists() else '❌'}")
    print(f"  📧 Newsletter: {'✅' if paths['newsletter'].exists() else '❌'}")
    print(f"  📱 LinkedIn  : {'✅' if paths['linkedin'].exists() else '❌'}")
    print(f"  ❓ FAQ Doc   : {'✅' if paths['faq'].exists() else '❌'}")
    print(f"  🌐 Live at   : https://mrwallyst.github.io/ICCMAFIA/")
    print("="*60)

# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(description="Add a TradesBySci day + full learning suite")
    p.add_argument("--day",       type=int,  required=True)
    p.add_argument("--youtube",   default="")
    p.add_argument("--title",     default="")
    p.add_argument("--desc",      default="")
    args = p.parse_args()

    if not args.youtube:
        print("Error: --youtube is required")
        sys.exit(1)

    takeaways_en = ["ICC Framework: Indications, Corrections, Continuations", "How to read order flow and identify liquidity zones", "The 3 market phases every futures trader must know", "Real trade setups from the Trades by Sci curriculum"]

    run_pipeline(
        day_num    = args.day,
        youtube_url= args.youtube,
        title_en   = args.title  or f"TradesBySci Day {args.day}",
        desc_en    = args.desc   or "AI-decoded Trades by Sci lesson.",
        takeaways_en = takeaways_en
    )

if __name__ == "__main__":
    main()
