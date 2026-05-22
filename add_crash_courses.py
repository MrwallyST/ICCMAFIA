#!/usr/bin/env python3
"""
TradesBySci — Add Crash Courses & Master Synthesis Pipeline
===========================================================
Adds the 6 Crash Course videos as Days 101-106 and the All For One Crash Course Synthesis as Day 107.
Generates all 14 learning resources for each.
"""

import os, sys, json, time, subprocess, re
from pathlib import Path

# Force UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SCRIPT_DIR      = Path(__file__).parent
DAYS_JSON       = SCRIPT_DIR / "days.json"
STUDIOS_DIR     = SCRIPT_DIR / "studios"
PYTHON          = sys.executable
SCRIPTS_PATH    = r"C:\Users\cesar\AppData\Local\Python\pythoncore-3.14-64\Scripts"
MASTER_NOTEBOOK = "8be24334-4293-41e0-a87d-cd20e67349ae"

ENV = {
    **os.environ,
    "PYTHONIOENCODING": "utf-8",
    "PYTHONUTF8": "1",
    "PATH": SCRIPTS_PATH + ";" + os.environ.get("PATH", "")
}

CRASH_COURSES = [
    {"day": 101, "youtube_url": "https://www.youtube.com/watch?v=PYVr6O6p_V4", "title": "Day Trading Crash Course #1 ( +$4.5M Withdraw )", "desc": "Simple Day Trading Crash Course #1 - Introduction to the ICC Trading Strategy.", "takeaways": ["Introduction to the ICC framework (Indication, Correction, Continuation)", "The basic market structures: Uptrends, Downtrends, Consolidation", "Setting up charts and identifying major swing highs and lows"]},
    {"day": 102, "youtube_url": "https://www.youtube.com/watch?v=3NDqGuITSpk", "title": "Day Trading Crash Course #2 (Market Structure Rules)", "desc": "Simple Day Trading Crash Course #2 - Comprehensive rules of Market Structure.", "takeaways": ["Deep dive into Market Structure rules and mechanics", "How to identify valid Swing Breaks (Bos/Choch)", "Avoiding the trap of looking at minor internal structure"]},
    {"day": 103, "youtube_url": "https://www.youtube.com/watch?v=fDtZbxeNWyw", "title": "Day Trading Crash Course #3 (Indication & Correction)", "desc": "Simple Day Trading Crash Course #3 - Finding entry triggers using Indication and Correction.", "takeaways": ["The Indication: How momentum shift signals the trend", "The Correction: Rules for pullbacks to support/resistance", "Why impatience during corrections leads to losses"]},
    {"day": 104, "youtube_url": "https://www.youtube.com/watch?v=lcodvDq2jx4", "title": "Day Trading Crash Course #4 (Understanding Corrections)", "desc": "Simple Day Trading Crash Course #4 - Decoding and trading complex Correction phases.", "takeaways": ["Decoding complex corrections and market sweeps", "Identifying structural targets and liquidity pools", "Protecting capital by waiting for deep discount zones"]},
    {"day": 105, "youtube_url": "https://www.youtube.com/watch?v=NQY6xAL4SuU", "title": "Day Trading Crash Course #5 (Daily & 4H Combo)", "desc": "Simple Day Trading Crash Course #5 - Combining Daily & 4H timeframes for higher probability setups.", "takeaways": ["Timeframe alignment: combining Daily, 4H, and 1H charts", "How higher timeframe structure overrides lower timeframe noise", "Mapping the higher timeframe bias to execution"]},
    {"day": 106, "youtube_url": "https://www.youtube.com/watch?v=rVphir6Qi80", "title": "Day Trading Crash Course #6 (Breakdown Thoughts)", "desc": "Simple Day Trading Crash Course #6 - Chart walkthroughs, execution examples, and final breakdown thoughts.", "takeaways": ["Live chart execution walkthroughs and rules review", "Final breakdown thoughts on simple price action", "Creating a mechanical daily checklist for execution"]}
]

def nlm(args: list, timeout=600) -> str:
    cmd = [PYTHON, "-m", "notebooklm"] + args
    result = subprocess.run(
        cmd, capture_output=True, env=ENV, timeout=timeout,
        encoding="utf-8", errors="replace"
    )
    if result.returncode != 0:
        return ((result.stdout or "") + "\n" + (result.stderr or "")).strip()
    return (result.stdout or "").strip()

def extract_id(text):
    matches = re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", text)
    return matches[0] if matches else None

def wait_for_all(artifact_ids, max_wait=900):
    pending = set(artifact_ids)
    print(f"   Waiting for {len(pending)} artifacts to complete...", flush=True)
    for i in range(max_wait // 15):
        if not pending:
            return True
        out = nlm(["artifact", "list", "-n", MASTER_NOTEBOOK, "--json"], timeout=60)
        try:
            data = json.loads(out)
            artifacts = data.get("artifacts", [])
        except Exception as e:
            print(f"\n   Error parsing JSON from list command: {e}. Raw: {out[:200]}")
            artifacts = []
            
        still_pending = set()
        for a_id in pending:
            found = False
            for art in artifacts:
                if art.get("id") == a_id or art.get("id", "").startswith(a_id[:8]):
                    found = True
                    status = art.get("status", "").lower()
                    if "complete" in status or "ready" in status or status == "completed":
                        print(f"\n   ✓ Artifact {a_id[:8]} completed!")
                    elif "fail" in status or "error" in status or status == "failed":
                        print(f"\n   ✗ Artifact {a_id[:8]} failed!")
                    else:
                        still_pending.add(a_id)
                    break
            if not found:
                still_pending.add(a_id)
        
        pending = still_pending
        if pending:
            print(".", end="", flush=True)
            time.sleep(15)
            
    print("\n   Timed out waiting for some artifacts.")
    return False

def quiz_json_to_md(json_path, md_path):
    try:
        data = json.loads(Path(json_path).read_text(encoding="utf-8"))
        md = f"# {data.get('title', 'Knowledge Quiz')}\n\n"
        for i, q in enumerate(data.get("questions", []), 1):
            md += f"## Question {i}\n{q['question']}\n\n"
            for opt in q.get("answerOptions", []):
                mark = "x" if opt.get("isCorrect") else " "
                md += f"- [{mark}] {opt['text']}\n"
            md += "\n"
            if "hint" in q:
                md += f"**Hint:** {q['hint']}\n\n"
        Path(md_path).write_text(md, encoding="utf-8")
        print("   Quiz converted to Markdown ✓")
    except Exception as e:
        # Fallback to copying raw json or printing error
        print(f"   Quiz conversion error: {e}")

def _clean_mind_map(file_path):
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

def rebuild_html():
    html_path = SCRIPT_DIR / "index.html"
    if not html_path.exists() or not DAYS_JSON.exists():
        return
    days = json.loads(DAYS_JSON.read_text(encoding="utf-8"))
    days_json_str = json.dumps(days, ensure_ascii=False, separators=(',', ':'))
    html = html_path.read_text(encoding="utf-8")
    new_line = f'  const DAYS_DATA = {days_json_str};'
    html = re.sub(r'  const DAYS_DATA = \[.*?\];', new_line, html, flags=re.DOTALL)
    html_path.write_text(html, encoding="utf-8")
    print(f"   index.html updated with {len(days)} day(s) of data")

def add_sources_if_missing():
    print("Checking existing sources in master notebook...")
    out = nlm(["source", "list", "-n", MASTER_NOTEBOOK, "--json"])
    try:
        data = json.loads(out)
        sources = data.get("sources", [])
    except Exception as e:
        print(f"Failed to parse source list: {e}. Output was: {out[:300]}")
        sources = []

    # Map sources by title (or index)
    source_map = {}
    for cc in CRASH_COURSES:
        day_num = cc["day"]
        match_str = f"Crash Course #{day_num - 100}"
        found_src = None
        for s in sources:
            if match_str in s.get("title", ""):
                found_src = s
                break
        
        if found_src:
            print(f"   Crash Course #{day_num - 100} already indexed under Source ID: {found_src['id']}")
            source_map[day_num] = found_src["id"]
        else:
            print(f"   Crash Course #{day_num - 100} is missing. Adding URL: {cc['youtube_url']}")
            out = nlm(["source", "add", cc["youtube_url"], "-n", MASTER_NOTEBOOK], timeout=90)
            print(f"   Add requested. Output: {out[:120]}")
            print("   Waiting 20s for indexing...")
            time.sleep(20)
            
            # Fetch source list again to get ID
            new_out = nlm(["source", "list", "-n", MASTER_NOTEBOOK, "--json"])
            try:
                new_data = json.loads(new_out)
                for s in new_data.get("sources", []):
                    if match_str in s.get("title", ""):
                        source_map[day_num] = s["id"]
                        print(f"   Indexed! Source ID: {s['id']}")
                        break
            except Exception as ex:
                print(f"   Failed to retrieve new source ID: {ex}")
                
    return source_map

def generate_day(day_num, title_en, desc_en, takeaways_en, source_id):
    print(f"\n=================== Day {day_num} ===================")
    day_dir = STUDIOS_DIR / f"day-{day_num}"
    day_dir.mkdir(parents=True, exist_ok=True)
    youtube_url = [cc["youtube_url"] for cc in CRASH_COURSES if cc["day"] == day_num][0]
    youtube_id = youtube_url.split("v=")[-1].split("&")[0]

    p = {
        'audio':  day_dir / f"day{day_num}_en.mp3",
        'study':  day_dir / f"day{day_num}_study.md",
        'flash':  day_dir / f"day{day_num}_flashcards.json",
        'mind':   day_dir / f"day{day_num}_mindmap.json",
        'quiz':   day_dir / f"day{day_num}_quiz.md",
        'quiz_raw': day_dir / f"day{day_num}_quiz_raw.json",
        'info':   day_dir / f"day{day_num}_infographic.png",
        'slides': day_dir / f"day{day_num}_slides.pdf",
        'table':  day_dir / f"day{day_num}_datatable.md",
        'blog':   day_dir / f"day{day_num}_blog.md",
        'ytscript': day_dir / f"day{day_num}_ytscript.md",
        'twitter': day_dir / f"day{day_num}_twitter.md",
        'newsletter': day_dir / f"day{day_num}_newsletter.md",
        'linkedin': day_dir / f"day{day_num}_linkedin.md",
        'faq':    day_dir / f"day{day_num}_faq.md",
        'ig':     day_dir / f"day{day_num}_ig.md",
        'tiktok':  day_dir / f"day{day_num}_tiktok.md"
    }

    tasks = {}
    
    # 1. Concurrently trigger learning resources scoped to specific source ID
    # Audio
    if not p['audio'].exists() or p['audio'].stat().st_size == 0:
        audio_prompt = (
            f"Focus specifically on Day {day_num}: {title_en}. "
            f"Key topics: {', '.join(takeaways_en[:3])}. "
            "STYLE: Real cinematic style, in-depth explainer format. "
            "INTRO: You MUST open by saying: 'Welcome to ICCMAFIA-AI, summarizing the Tradesbysci ICC course! We will be doing all of the course videos...' "
            "CORE: Automatically identify and explain the most important trading concepts from today's lesson. Break them down clearly as if teaching a complete beginner. "
            "BONUS: Announce to the audience that a free, downloadable infographic summarizing today's topics is available at the link in bio. "
            "WEBSITE CTA: Tell listeners to visit mrwallyst.github.io/ICCMAFIA to access the free interactive Study Guide, Quiz, Mind Map, Flashcards, and Audio Podcast for this lesson. "
            "OUTRO: End with a strong, cinematic Call to Action reminding listeners to like, comment, and subscribe to the ICCMAFIA-AI channel. "
            "CREDIT: Give explicit credit to Trades by Sci as the original course creator."
        )
        print("   Launching Audio Overview...")
        out = nlm(["generate", "audio", audio_prompt, "-n", MASTER_NOTEBOOK, "-s", source_id, "--no-wait"], timeout=60)
        tasks['audio'] = extract_id(out)
    else:
        print("   [Skip] Audio already exists.")

    # Study Guide
    if not p['study'].exists() or p['study'].stat().st_size == 0:
        print("   Launching Study Guide...")
        study_prompt = f"IGNORE ALL PREVIOUS DAYS. Focus STRICTLY on Day {day_num}: {title_en}. Only cover concepts explicitly mentioned in the Day {day_num} video. Keep it concise — max 2 pages."
        out = nlm(["generate", "report", study_prompt, "--format", "study-guide", "-n", MASTER_NOTEBOOK, "-s", source_id, "--no-wait"], timeout=60)
        tasks['study'] = extract_id(out)
    else:
        print("   [Skip] Study Guide already exists.")

    # Flashcards
    if not p['flash'].exists() or p['flash'].stat().st_size == 0:
        print("   Launching Flashcards...")
        out = nlm(["generate", "flashcards", f"IGNORE PREVIOUS LESSONS. Focus EXCLUSIVELY on Day {day_num}: {title_en}.", "-n", MASTER_NOTEBOOK, "-s", source_id, "--no-wait"], timeout=60)
        tasks['flash'] = extract_id(out)
    else:
        print("   [Skip] Flashcards already exists.")

    # Mind Map (Returns note ID directly)
    if not p['mind'].exists() or p['mind'].stat().st_size == 0:
        print("   Launching Mind Map...")
        out = nlm(["generate", "mind-map", "-n", MASTER_NOTEBOOK, "-s", source_id], timeout=120)
        tasks['mind'] = extract_id(out)
    else:
        print("   [Skip] Mind Map already exists.")

    # Quiz
    if not p['quiz'].exists() or p['quiz'].stat().st_size == 0:
        print("   Launching Quiz...")
        out = nlm(["generate", "quiz", f"Create 8 questions EXCLUSIVELY about Day {day_num}: {title_en}. Do NOT test on Day 1 or previous material.", "-n", MASTER_NOTEBOOK, "-s", source_id, "--no-wait"], timeout=60)
        tasks['quiz'] = extract_id(out)
    else:
        print("   [Skip] Quiz already exists.")

    # Infographic
    if not p['info'].exists() or p['info'].stat().st_size == 0:
        print("   Launching Infographic...")
        info_prompt = (
            f"Visual overview of Day {day_num}: {title_en}. "
            "Create a clear, beginner-friendly visual breakdown of the exact core concepts discussed in today's lesson. "
            "BRANDING: Prominently feature the channel name 'ICCMAFIA-AI' on the image. "
            "CREDIT: Explicitly give credit to 'Trades by Sci' on the image. "
            "WEBSITE: Include the URL mrwallyst.github.io/ICCMAFIA somewhere on the infographic."
        )
        out = nlm(["generate", "infographic", info_prompt, "-n", MASTER_NOTEBOOK, "-s", source_id, "--no-wait"], timeout=60)
        tasks['info'] = extract_id(out)
    else:
        print("   [Skip] Infographic already exists.")

    # Slide Deck
    if not p['slides'].exists() or p['slides'].stat().st_size == 0:
        print("   Launching Slide Deck...")
        slide_prompt = f"Lesson slides for Day {day_num}: {title_en}. Cover only the essential concepts with bullet points. One key idea per slide."
        out = nlm(["generate", "slide-deck", slide_prompt, "--length", "short", "--format", "presenter", "-n", MASTER_NOTEBOOK, "-s", source_id, "--no-wait"], timeout=60)
        tasks['slides'] = extract_id(out)
    else:
        print("   [Skip] Slide Deck already exists.")

    # Data Table
    if not p['table'].exists() or p['table'].stat().st_size == 0:
        print("   Launching Data Table...")
        out = nlm(["generate", "data-table", f"Organize key concepts, definitions, and examples from Day {day_num}: {title_en} into a structured reference table.", "-n", MASTER_NOTEBOOK, "-s", source_id, "--no-wait"], timeout=60)
        tasks['table'] = extract_id(out)
    else:
        print("   [Skip] Data Table already exists.")

    # Blog Post
    if not p['blog'].exists() or p['blog'].stat().st_size == 0:
        print("   Launching Blog Post...")
        blog_prompt = f"Write a concise, SEO-optimized blog post for Day {day_num}: {title_en}. Keep it under 800 words. Focus on actionable takeaways, not fluff. Credit Trades by Sci. End with a CTA to visit mrwallyst.github.io/ICCMAFIA for free study materials."
        out = nlm(["generate", "report", "--format", "blog-post", blog_prompt, "-n", MASTER_NOTEBOOK, "-s", source_id, "--no-wait"], timeout=60)
        tasks['blog'] = extract_id(out)
    else:
        print("   [Skip] Blog Post already exists.")

    # YouTube Script
    if not p['ytscript'].exists() or p['ytscript'].stat().st_size == 0:
        print("   Launching YouTube Script...")
        yt_prompt = (
            "Write an engaging, cinematic YouTube video script (video overview) covering these concepts. "
            f"INTRO: The host MUST open by saying: 'Welcome to ICCMAFIA-AI, today we are summarizing Day {day_num} of the TradesbySci ICC course! We will be doing all of the course videos...' "
            "CORE: Break down all key trading concepts from the lesson clearly like teaching a complete beginner. "
            "BONUS: WEBSITE CTA: The script MUST enthusiastically instruct viewers to click the link in the description (mrwallyst.github.io/ICCMAFIA) to access their free Interactive Study Guide, Quiz, Mind Map, Flashcards, and Audio Podcast. "
            "OUTRO: End with a strong, cinematic Call to Action reminding viewers to like, comment, and subscribe to ICCMAFIA-AI. "
            "CREDIT: Give explicit credit to TradesbySci as the original course creator."
        )
        out = nlm(["generate", "report", "--format", "custom", "--append", yt_prompt, f"Day {day_num}: {title_en}", "-n", MASTER_NOTEBOOK, "-s", source_id, "--no-wait"], timeout=60)
        tasks['ytscript'] = extract_id(out)
    else:
        print("   [Skip] YouTube Script already exists.")

    # Twitter Thread
    if not p['twitter'].exists() or p['twitter'].stat().st_size == 0:
        print("   Launching Twitter Thread...")
        thread_prompt = f"Write a viral 10-post Thread (optimized for X/Instagram Threads) summarizing Day {day_num} concepts. CRITICAL: Each individual post MUST be strictly under 400 characters so I can easily copy and paste them. Number each post (1/10, 2/10, etc.), include a punchy BOLD topic header for each post (e.g. 1/10 🚨 **TRADING VS. GAMBLING**), and make sure the first post explicitly states 'Day {day_num} of the TradesbySci ICC Course'."
        out = nlm(["generate", "report", "--format", "custom", "--append", thread_prompt, f"Day {day_num}: {title_en}", "-n", MASTER_NOTEBOOK, "-s", source_id, "--no-wait"], timeout=60)
        tasks['twitter'] = extract_id(out)
    else:
        print("   [Skip] Twitter Thread already exists.")

    # Newsletter
    if not p['newsletter'].exists() or p['newsletter'].stat().st_size == 0:
        print("   Launching Newsletter...")
        news_prompt = "Write a short, punchy email newsletter summarizing this lesson in under 400 words. Include a subject line, 3 key bullet points, and a CTA linking to mrwallyst.github.io/ICCMAFIA for free resources."
        out = nlm(["generate", "report", "--format", "custom", "--append", news_prompt, f"Day {day_num}: {title_en}", "-n", MASTER_NOTEBOOK, "-s", source_id, "--no-wait"], timeout=60)
        tasks['newsletter'] = extract_id(out)
    else:
        print("   [Skip] Newsletter already exists.")

    # LinkedIn
    if not p['linkedin'].exists() or p['linkedin'].stat().st_size == 0:
        print("   Launching LinkedIn Carousel...")
        li_prompt = "Write the text copy for a 5-slide LinkedIn carousel post. Each slide must be under 150 words. Slide 1 = hook, Slides 2-4 = key concepts, Slide 5 = CTA to mrwallyst.github.io/ICCMAFIA. Credit Trades by Sci."
        out = nlm(["generate", "report", "--format", "custom", "--append", li_prompt, f"Day {day_num}: {title_en}", "-n", MASTER_NOTEBOOK, "-s", source_id, "--no-wait"], timeout=60)
        tasks['linkedin'] = extract_id(out)
    else:
        print("   [Skip] LinkedIn Carousel already exists.")

    # FAQ
    if not p['faq'].exists() or p['faq'].stat().st_size == 0:
        print("   Launching FAQ Document...")
        faq_prompt = "Write a Frequently Asked Questions (FAQ) document with exactly 8 Q&A pairs answering the most common beginner queries about this lesson. Keep answers under 3 sentences each."
        out = nlm(["generate", "report", "--format", "custom", "--append", faq_prompt, f"Day {day_num}: {title_en}", "-n", MASTER_NOTEBOOK, "-s", source_id, "--no-wait"], timeout=60)
        tasks['faq'] = extract_id(out)
    else:
        print("   [Skip] FAQ Document already exists.")

    active_tasks = {k: v for k, v in tasks.items() if v}
    print(f"   Successfully launched {len(active_tasks)} parallel generations.")

    # 2. Wait for completions (exclude mind map since it is a note and completes synchronously)
    async_task_ids = [v for k, v in active_tasks.items() if k != 'mind']
    if async_task_ids:
        wait_for_all(async_task_ids, max_wait=900)

    # 3. Download
    if 'audio' in active_tasks:
        print(f"   Downloading Audio -> {p['audio'].name}")
        nlm(["download", "audio", str(p['audio']), "-a", active_tasks['audio'], "--force"])
    if 'study' in active_tasks:
        print(f"   Downloading Study Guide -> {p['study'].name}")
        nlm(["download", "report", str(p['study']), "-a", active_tasks['study'], "--force"])
    if 'flash' in active_tasks:
        print(f"   Downloading Flashcards -> {p['flash'].name}")
        nlm(["download", "flashcards", str(p['flash']), "-a", active_tasks['flash']])
    if 'mind' in active_tasks:
        print(f"   Downloading Mind Map -> {p['mind'].name}")
        mm_out = nlm(["note", "get", active_tasks['mind'], "-n", MASTER_NOTEBOOK], timeout=60)
        with open(p['mind'], 'w', encoding='utf-8') as f:
            f.write(mm_out)
        _clean_mind_map(p['mind'])
    if 'quiz' in active_tasks:
        print(f"   Downloading Quiz -> {p['quiz_raw'].name}")
        nlm(["download", "quiz", str(p['quiz_raw']), "-a", active_tasks['quiz']])
        if p['quiz_raw'].exists() and p['quiz_raw'].stat().st_size > 100:
            quiz_json_to_md(p['quiz_raw'], p['quiz'])
    if 'info' in active_tasks:
        print(f"   Downloading Infographic -> {p['info'].name}")
        nlm(["download", "infographic", str(p['info']), "-a", active_tasks['info'], "--force"])
    if 'slides' in active_tasks:
        print(f"   Downloading Slide Deck -> {p['slides'].name}")
        nlm(["download", "slide-deck", str(p['slides']), "-a", active_tasks['slides'], "--force"])
    if 'table' in active_tasks:
        print(f"   Downloading Data Table -> {p['table'].name}")
        nlm(["download", "data-table", str(p['table']), "-a", active_tasks['table'], "--force"])
    if 'blog' in active_tasks:
        print(f"   Downloading Blog -> {p['blog'].name}")
        nlm(["download", "report", str(p['blog']), "-a", active_tasks['blog'], "--force"])
    if 'ytscript' in active_tasks:
        print(f"   Downloading YouTube Script -> {p['ytscript'].name}")
        nlm(["download", "report", str(p['ytscript']), "-a", active_tasks['ytscript'], "--force"])
    if 'twitter' in active_tasks:
        print(f"   Downloading Twitter Thread -> {p['twitter'].name}")
        nlm(["download", "report", str(p['twitter']), "-a", active_tasks['twitter'], "--force"])
    if 'newsletter' in active_tasks:
        print(f"   Downloading Newsletter -> {p['newsletter'].name}")
        nlm(["download", "report", str(p['newsletter']), "-a", active_tasks['newsletter'], "--force"])
    if 'linkedin' in active_tasks:
        print(f"   Downloading LinkedIn Carousel -> {p['linkedin'].name}")
        nlm(["download", "report", str(p['linkedin']), "-a", active_tasks['linkedin'], "--force"])
    if 'faq' in active_tasks:
        print(f"   Downloading FAQ -> {p['faq'].name}")
        nlm(["download", "report", str(p['faq']), "-a", active_tasks['faq'], "--force"])

    # Write social media copies manually
    ig_content = f"""## 📸 IG Reel Caption — Day {day_num}
    
**Hook:** Simple price action secrets from Day {day_num} of the TradesBySci Crash Course. 👇

**Takeaway:**
{chr(10).join(f"- {t}" for t in takeaways_en)}

**CTA:**
Get the free interactive study guide, quiz, mind map, slides, and podcast summary at mrwallyst.github.io/ICCMAFIA/ 🔗
"""
    tiktok_content = f"""## 🎵 TikTok Script — Day {day_num}

**Hook:** "Here's what you missed in Day {day_num} of the TradesBySci Day Trading Crash Course..."
**Core:** Explain how market structure, indication, and correction are key to finding the trend.
**CTA:** "Access all free study guides, quizzes, and flashcards at the link in my bio!"
"""
    p['ig'].write_text(ig_content, encoding="utf-8")
    p['tiktok'].write_text(tiktok_content, encoding="utf-8")

    # Update days.json
    days = json.loads(DAYS_JSON.read_text(encoding="utf-8"))
    days = [d for d in days if d.get("day") != day_num]
    
    new_day = {
        "day": day_num,
        "title": title_en,
        "description": desc_en,
        "youtubeId": youtube_id,
        "reelUrl": "",
        "audioUrl": f"./studios/day-{day_num}/{p['audio'].name}" if p['audio'].exists() else "",
        "infographicUrl": f"./studios/day-{day_num}/{p['info'].name}" if p['info'].exists() else "",
        "quizFile":       f"./studios/day-{day_num}/{p['quiz'].name}" if p['quiz'].exists() else "",
        "studyGuideUrl":  f"./studios/day-{day_num}/{p['study'].name}" if p['study'].exists() else "",
        "flashcardsUrl":  f"./studios/day-{day_num}/{p['flash'].name}" if p['flash'].exists() else "",
        "mindMapUrl":     f"./studios/day-{day_num}/{p['mind'].name}" if p['mind'].exists() else "",
        "slideDeckUrl":   f"./studios/day-{day_num}/{p['slides'].name}" if p['slides'].exists() else "",
        "dataTableUrl":   f"./studios/day-{day_num}/{p['table'].name}" if p['table'].exists() else "",
        "blogPostUrl":       f"./studios/day-{day_num}/{p['blog'].name}" if p['blog'].exists() else "",
        "youtubeScriptUrl":  f"./studios/day-{day_num}/{p['ytscript'].name}" if p['ytscript'].exists() else "",
        "igCaptionUrl":      f"./studios/day-{day_num}/{p['ig'].name}" if p['ig'].exists() else "",
        "tiktokUrl":         f"./studios/day-{day_num}/{p['tiktok'].name}" if p['tiktok'].exists() else "",
        "twitterThreadUrl":  f"./studios/day-{day_num}/{p['twitter'].name}" if p['twitter'].exists() else "",
        "newsletterUrl":     f"./studios/day-{day_num}/{p['newsletter'].name}" if p['newsletter'].exists() else "",
        "linkedinUrl":       f"./studios/day-{day_num}/{p['linkedin'].name}" if p['linkedin'].exists() else "",
        "faqUrl":            f"./studios/day-{day_num}/{p['faq'].name}" if p['faq'].exists() else "",
        "keyTakeaways":   takeaways_en,
        "notebookId":     MASTER_NOTEBOOK,
        "isCrashCourse":  True
    }
    days.append(new_day)
    days.sort(key=lambda d: d["day"])
    DAYS_JSON.write_text(json.dumps(days, indent=2, ensure_ascii=False), encoding="utf-8")
    rebuild_html()
    print(f"✓ Day {day_num} finished and integrated!")

def generate_crash_all_for_one(source_ids):
    print("\n=================== Generating All For One Crash Course Synthesis (Day 107) ===================")
    day_num = 107
    title = "🎯 ALL FOR ONE — The Complete Simple Day Trading Crash Course"
    desc = "The ultimate synthesis of the 6-part TradesBySci Simple Day Trading Crash Course. Every structure rule, every bias checklist in one place."
    takeaways = [
        "Complete Crash Course Playbook: Market structure, trend alignment & execution synthesized",
        "Multi-timeframe rules: combining Daily, 4H & 1H charts into a single mechanical system",
        "Mechanical checklists for scanning levels, sweeping liquidity & choosing entry triggers",
        "The discipline blueprint: managing drawdown, rules adherence & daily charting routine"
    ]
    
    day_dir = STUDIOS_DIR / f"day-{day_num}"
    day_dir.mkdir(parents=True, exist_ok=True)
    
    p = {
        'audio':      day_dir / f"day{day_num}_en.mp3",
        'study':      day_dir / f"day{day_num}_study.md",
        'flash':      day_dir / f"day{day_num}_flashcards.json",
        'mind':       day_dir / f"day{day_num}_mindmap.json",
        'quiz':       day_dir / f"day{day_num}_quiz.md",
        'quiz_raw':   day_dir / f"day{day_num}_quiz_raw.json",
        'info':       day_dir / f"day{day_num}_infographic.png",
        'slides':     day_dir / f"day{day_num}_slides.pdf",
        'table':      day_dir / f"day{day_num}_datatable.md",
        'blog':       day_dir / f"day{day_num}_blog.md",
        'ytscript':   day_dir / f"day{day_num}_ytscript.md",
        'twitter':    day_dir / f"day{day_num}_twitter.md",
        'newsletter': day_dir / f"day{day_num}_newsletter.md",
        'linkedin':   day_dir / f"day{day_num}_linkedin.md",
        'faq':        day_dir / f"day{day_num}_faq.md",
        'ig':         day_dir / f"day{day_num}_ig.md",
        'tiktok':     day_dir / f"day{day_num}_tiktok.md"
    }

    # Scoping string specifying ALL 6 sources
    scope_args = []
    for s_id in source_ids:
        scope_args.extend(["-s", s_id])
        
    tasks = {}
    
    if not p['audio'].exists() or p['audio'].stat().st_size == 0:
        print("   Launching Audio Overview...")
        audio_prompt = (
            "Create a comprehensive, podcast-style Audio Overview that synthesizes the entire 6-part TradesBySci Day Trading Crash Course. "
            "Weave the narrative around the core theme: how simple price action rules (market structure, indication, correction, timeframe combo) "
            "eliminate emotional errors and build a mechanical edge. Outro with CTA for mrwallyst.github.io/ICCMAFIA."
        )
        out = nlm(["generate", "audio", audio_prompt, "-n", MASTER_NOTEBOOK] + scope_args + ["--no-wait"], timeout=60)
        tasks['audio'] = extract_id(out)
    else:
        print("   [Skip] Audio already exists.")

    if not p['study'].exists() or p['study'].stat().st_size == 0:
        print("   Launching Study Guide...")
        study_prompt = (
            "Create a master study guide summarizing all 6 crash course lessons. "
            "Organize by: 1) Market Structure Rules, 2) Indication & Correction, 3) Higher Timeframe bias (Daily/4H), and 4) Final breakdown and execution thoughts. Max 4 pages."
        )
        out = nlm(["generate", "report", study_prompt, "--format", "study-guide", "-n", MASTER_NOTEBOOK] + scope_args + ["--no-wait"], timeout=60)
        tasks['study'] = extract_id(out)
    else:
        print("   [Skip] Study Guide already exists.")

    if not p['flash'].exists() or p['flash'].stat().st_size == 0:
        print("   Launching Flashcards...")
        out = nlm(["generate", "flashcards", "Create 15 flashcards covering all key definitions and mechanical rules from the 6 crash course lessons.", "-n", MASTER_NOTEBOOK] + scope_args + ["--no-wait"], timeout=60)
        tasks['flash'] = extract_id(out)
    else:
        print("   [Skip] Flashcards already exists.")

    if not p['mind'].exists() or p['mind'].stat().st_size == 0:
        print("   Launching Mind Map...")
        out = nlm(["generate", "mind-map", "-n", MASTER_NOTEBOOK] + scope_args, timeout=240)
        tasks['mind'] = extract_id(out)
    else:
        print("   [Skip] Mind Map already exists.")

    if not p['quiz'].exists() or p['quiz'].stat().st_size == 0:
        print("   Launching Quiz...")
        quiz_prompt = "Create a 12-question multiple-choice comprehensive test covering all 6 crash course lessons. 4 options each, one correct."
        out = nlm(["generate", "quiz", quiz_prompt, "-n", MASTER_NOTEBOOK] + scope_args + ["--no-wait"], timeout=60)
        tasks['quiz'] = extract_id(out)
    else:
        print("   [Skip] Quiz already exists.")

    if not p['info'].exists() or p['info'].stat().st_size == 0:
        print("   Launching Infographic...")
        info_prompt = "Create a visual cheat-sheet infographic summarizing the rules, bias combinations, and entry formulas of the crash course. Brand with ICCMAFIA-AI."
        out = nlm(["generate", "infographic", info_prompt, "-n", MASTER_NOTEBOOK] + scope_args + ["--no-wait"], timeout=60)
        tasks['info'] = extract_id(out)
    else:
        print("   [Skip] Infographic already exists.")

    if not p['slides'].exists() or p['slides'].stat().st_size == 0:
        print("   Launching Slide Deck...")
        slide_prompt = "Create a presentation slide deck for the complete crash course playbook. Cover structure rules, timeframe combo, and execution."
        out = nlm(["generate", "slide-deck", slide_prompt, "--format", "presenter", "-n", MASTER_NOTEBOOK] + scope_args + ["--no-wait"], timeout=60)
        tasks['slides'] = extract_id(out)
    else:
        print("   [Skip] Slide Deck already exists.")

    if not p['table'].exists() or p['table'].stat().st_size == 0:
        print("   Launching Data Table...")
        out = nlm(["generate", "data-table", "Create a comprehensive reference data table summarizing the 6 crash course lessons.", "-n", MASTER_NOTEBOOK] + scope_args + ["--no-wait"], timeout=60)
        tasks['table'] = extract_id(out)
    else:
        print("   [Skip] Data Table already exists.")

    if not p['blog'].exists() or p['blog'].stat().st_size == 0:
        print("   Launching Blog Post...")
        blog_prompt = "Write a comprehensive SEO blog post: 'The Complete Day Trading Crash Course Playbook: Rules & Execution'. Under 1000 words. CTA to mrwallyst.github.io/ICCMAFIA."
        out = nlm(["generate", "report", "--format", "blog-post", blog_prompt, "-n", MASTER_NOTEBOOK] + scope_args + ["--no-wait"], timeout=60)
        tasks['blog'] = extract_id(out)
    else:
        print("   [Skip] Blog Post already exists.")

    if not p['ytscript'].exists() or p['ytscript'].stat().st_size == 0:
        print("   Launching YouTube Script...")
        yt_prompt = (
            "Write an epic YouTube compilation script titled 'Simple Day Trading Crash Course: ALL FOR ONE Compilation'. "
            "Open with: 'Welcome to ICCMAFIA-AI! Today we break down the COMPLETE TradesBySci Day Trading Crash Course — all 6 parts in one video!' "
            "Walk through rules of structure, indication vs correction, timeframe alignment, and live execution. CTA to mrwallyst.github.io/ICCMAFIA."
        )
        out = nlm(["generate", "report", "--format", "custom", "--append", yt_prompt, "All For One Crash Course Compilation", "-n", MASTER_NOTEBOOK] + scope_args + ["--no-wait"], timeout=60)
        tasks['ytscript'] = extract_id(out)
    else:
        print("   [Skip] YouTube Script already exists.")

    if not p['twitter'].exists() or p['twitter'].stat().st_size == 0:
        print("   Launching Twitter Thread...")
        thread_prompt = "Write a viral 12-post Twitter Thread summarizing the complete 6 crash course lessons. Under 400 characters each."
        out = nlm(["generate", "report", "--format", "custom", "--append", thread_prompt, "All For One Crash Course", "-n", MASTER_NOTEBOOK] + scope_args + ["--no-wait"], timeout=60)
        tasks['twitter'] = extract_id(out)
    else:
        print("   [Skip] Twitter Thread already exists.")

    if not p['newsletter'].exists() or p['newsletter'].stat().st_size == 0:
        print("   Launching Newsletter...")
        news_prompt = "Write a special email newsletter: 'The Complete Day Trading Crash Course Playbook is Live!'. Under 400 words. CTA link to mrwallyst.github.io/ICCMAFIA."
        out = nlm(["generate", "report", "--format", "custom", "--append", news_prompt, "All For One Crash Course", "-n", MASTER_NOTEBOOK] + scope_args + ["--no-wait"], timeout=60)
        tasks['newsletter'] = extract_id(out)
    else:
        print("   [Skip] Newsletter already exists.")

    if not p['linkedin'].exists() or p['linkedin'].stat().st_size == 0:
        print("   Launching LinkedIn Carousel...")
        li_prompt = "Write text copy for a 6-slide LinkedIn carousel: 'I studied 6 parts of a day trading crash course. Here is the mechanical playbook.' Under 150 words per slide."
        out = nlm(["generate", "report", "--format", "custom", "--append", li_prompt, "All For One Crash Course", "-n", MASTER_NOTEBOOK] + scope_args + ["--no-wait"], timeout=60)
        tasks['linkedin'] = extract_id(out)
    else:
        print("   [Skip] LinkedIn Carousel already exists.")

    if not p['faq'].exists() or p['faq'].stat().st_size == 0:
        print("   Launching FAQ...")
        faq_prompt = "Write a FAQ document with exactly 10 Q&A pairs covering structure, timeframe combo, and execution rules from the crash course."
        out = nlm(["generate", "report", "--format", "custom", "--append", faq_prompt, "All For One Crash Course", "-n", MASTER_NOTEBOOK] + scope_args + ["--no-wait"], timeout=60)
        tasks['faq'] = extract_id(out)
    else:
        print("   [Skip] FAQ already exists.")

    active_tasks = {k: v for k, v in tasks.items() if v}
    print(f"   Successfully launched {len(active_tasks)} parallel All-For-One generations.")

    # Wait for completions (exclude mind map since it is a note and completes synchronously)
    async_task_ids = [v for k, v in active_tasks.items() if k != 'mind']
    if async_task_ids:
        wait_for_all(async_task_ids, max_wait=1200)

    # Download
    if 'audio' in active_tasks:
        print(f"   Downloading Audio -> {p['audio'].name}")
        nlm(["download", "audio", str(p['audio']), "-a", active_tasks['audio'], "--force"])
    if 'study' in active_tasks:
        print(f"   Downloading Study Guide -> {p['study'].name}")
        nlm(["download", "report", str(p['study']), "-a", active_tasks['study'], "--force"])
    if 'flash' in active_tasks:
        print(f"   Downloading Flashcards -> {p['flash'].name}")
        nlm(["download", "flashcards", str(p['flash']), "-a", active_tasks['flash']])
    if 'mind' in active_tasks:
        print(f"   Downloading Mind Map -> {p['mind'].name}")
        mm_out = nlm(["note", "get", active_tasks['mind'], "-n", MASTER_NOTEBOOK], timeout=60)
        with open(p['mind'], 'w', encoding='utf-8') as f:
            f.write(mm_out)
        _clean_mind_map(p['mind'])
    if 'quiz' in active_tasks:
        print(f"   Downloading Quiz -> {p['quiz_raw'].name}")
        nlm(["download", "quiz", str(p['quiz_raw']), "-a", active_tasks['quiz']])
        if p['quiz_raw'].exists() and p['quiz_raw'].stat().st_size > 100:
            quiz_json_to_md(p['quiz_raw'], p['quiz'])
    if 'info' in active_tasks:
        print(f"   Downloading Infographic -> {p['info'].name}")
        nlm(["download", "infographic", str(p['info']), "-a", active_tasks['info'], "--force"])
    if 'slides' in active_tasks:
        print(f"   Downloading Slide Deck -> {p['slides'].name}")
        nlm(["download", "slide-deck", str(p['slides']), "-a", active_tasks['slides'], "--force"])
    if 'table' in active_tasks:
        print(f"   Downloading Data Table -> {p['table'].name}")
        nlm(["download", "data-table", str(p['table']), "-a", active_tasks['table'], "--force"])
    if 'blog' in active_tasks:
        print(f"   Downloading Blog -> {p['blog'].name}")
        nlm(["download", "report", str(p['blog']), "-a", active_tasks['blog'], "--force"])
    if 'ytscript' in active_tasks:
        print(f"   Downloading YouTube Script -> {p['ytscript'].name}")
        nlm(["download", "report", str(p['ytscript']), "-a", active_tasks['ytscript'], "--force"])
    if 'twitter' in active_tasks:
        print(f"   Downloading Twitter Thread -> {p['twitter'].name}")
        nlm(["download", "report", str(p['twitter']), "-a", active_tasks['twitter'], "--force"])
    if 'newsletter' in active_tasks:
        print(f"   Downloading Newsletter -> {p['newsletter'].name}")
        nlm(["download", "report", str(p['newsletter']), "-a", active_tasks['newsletter'], "--force"])
    if 'linkedin' in active_tasks:
        print(f"   Downloading LinkedIn Carousel -> {p['linkedin'].name}")
        nlm(["download", "report", str(p['linkedin']), "-a", active_tasks['linkedin'], "--force"])
    if 'faq' in active_tasks:
        print(f"   Downloading FAQ -> {p['faq'].name}")
        nlm(["download", "report", str(p['faq']), "-a", active_tasks['faq'], "--force"])

    # Write social media copies manually
    ig_content = f"""## 📸 IG Reel Caption — All For One Crash Course Compilation
    
**Hook:** The complete 6-part TradesBySci Day Trading Crash Course synthesized into ONE mechanical playbook. 👇

**Takeaway:**
{chr(10).join(f"- {t}" for t in takeaways)}

**CTA:**
Get the free interactive study guide, quiz, mind map, slides, and podcast summary at mrwallyst.github.io/ICCMAFIA/ 🔗
"""
    tiktok_content = f"""## 🎵 TikTok Script — All For One Crash Course Compilation

**Hook:** "I study all 6 parts of the TradesBySci Day Trading Crash Course so you don't have to..."
**Core:** Explain how structure rules, indication vs correction, timeframe alignment, and execution are synthesized.
**CTA:** "Access all free study guides, quizzes, and flashcards at the link in my bio!"
"""
    p['ig'].write_text(ig_content, encoding="utf-8")
    p['tiktok'].write_text(tiktok_content, encoding="utf-8")

    # Update days.json
    days = json.loads(DAYS_JSON.read_text(encoding="utf-8"))
    days = [d for d in days if d.get("day") != day_num]
    
    new_day = {
        "day": day_num,
        "title": title,
        "description": desc,
        "youtubeId": "",
        "reelUrl": "",
        "audioUrl": f"./studios/day-{day_num}/{p['audio'].name}" if p['audio'].exists() else "",
        "infographicUrl": f"./studios/day-{day_num}/{p['info'].name}" if p['info'].exists() else "",
        "quizFile":       f"./studios/day-{day_num}/{p['quiz'].name}" if p['quiz'].exists() else "",
        "studyGuideUrl":  f"./studios/day-{day_num}/{p['study'].name}" if p['study'].exists() else "",
        "flashcardsUrl":  f"./studios/day-{day_num}/{p['flash'].name}" if p['flash'].exists() else "",
        "mindMapUrl":     f"./studios/day-{day_num}/{p['mind'].name}" if p['mind'].exists() else "",
        "slideDeckUrl":   f"./studios/day-{day_num}/{p['slides'].name}" if p['slides'].exists() else "",
        "dataTableUrl":   f"./studios/day-{day_num}/{p['table'].name}" if p['table'].exists() else "",
        "blogPostUrl":       f"./studios/day-{day_num}/{p['blog'].name}" if p['blog'].exists() else "",
        "youtubeScriptUrl":  f"./studios/day-{day_num}/{p['ytscript'].name}" if p['ytscript'].exists() else "",
        "igCaptionUrl":      f"./studios/day-{day_num}/{p['ig'].name}" if p['ig'].exists() else "",
        "tiktokUrl":         f"./studios/day-{day_num}/{p['tiktok'].name}" if p['tiktok'].exists() else "",
        "twitterThreadUrl":  f"./studios/day-{day_num}/{p['twitter'].name}" if p['twitter'].exists() else "",
        "newsletterUrl":     f"./studios/day-{day_num}/{p['newsletter'].name}" if p['newsletter'].exists() else "",
        "linkedinUrl":       f"./studios/day-{day_num}/{p['linkedin'].name}" if p['linkedin'].exists() else "",
        "faqUrl":            f"./studios/day-{day_num}/{p['faq'].name}" if p['faq'].exists() else "",
        "keyTakeaways":   takeaways,
        "notebookId":     MASTER_NOTEBOOK,
        "isCrashCourse":  True
    }
    days.append(new_day)
    days.sort(key=lambda d: d["day"])
    DAYS_JSON.write_text(json.dumps(days, indent=2, ensure_ascii=False), encoding="utf-8")
    rebuild_html()
    print("✓ All For One Crash Course finished and integrated!")

def fix_day_14_mindmap():
    p_mind = STUDIOS_DIR / "day-14" / "day14_mindmap.json"
    if p_mind.exists() and p_mind.stat().st_size > 0:
        print("   [Skip] Day 14 Mind Map already exists.")
        return
    print("\n=================== Generating Missing Day 14 Mind Map ===================")
    day_num = 14
    # Find Day 14 source ID
    out = nlm(["source", "list", "-n", MASTER_NOTEBOOK, "--json"])
    source_id = None
    try:
        data = json.loads(out)
        for s in data.get("sources", []):
            if "Day 14" in s.get("title", "") or "Day 14" in s.get("title", ""):
                source_id = s["id"]
                break
    except Exception as e:
         print(f"Failed to find Day 14 source ID: {e}")
         
    if not source_id:
         # Fallback to hardcoded verified source ID from console output
         source_id = "05464e97-d7eb-4dfc-b6d5-2a34319b0d03"

    print(f"Using source ID {source_id} for Day 14 Mind Map")
    out = nlm(["generate", "mind-map", "-n", MASTER_NOTEBOOK, "-s", source_id], timeout=120)
    mind_id = extract_id(out)
    if mind_id:
        mm_out = nlm(["note", "get", mind_id, "-n", MASTER_NOTEBOOK], timeout=60)
        with open(p_mind, 'w', encoding='utf-8') as f:
            f.write(mm_out)
        _clean_mind_map(p_mind)
        print("✓ Day 14 Mind Map generated and saved!")
    else:
        print("✗ Failed to extract Day 14 mind map ID")

def main():
    nlm(["use", MASTER_NOTEBOOK])
    source_map = add_sources_if_missing()
    
    # Check if we got all source IDs
    all_found = True
    for cc in CRASH_COURSES:
        if cc["day"] not in source_map:
            print(f"Error: Missing source ID for Day {cc['day']}")
            all_found = False
            
    if not all_found:
        print("Cannot proceed: Some crash course sources are missing. Please retry.")
        sys.exit(1)
        
    # Generate Days 101-106 sequentially
    for cc in CRASH_COURSES:
        generate_day(
            day_num=cc["day"],
            title_en=cc["title"],
            desc_en=cc["desc"],
            takeaways_en=cc["takeaways"],
            source_id=source_map[cc["day"]]
        )
        
    # Generate Day 107 (All For One)
    generate_crash_all_for_one(list(source_map.values()))
    
    # Fix Day 14 Mind Map
    fix_day_14_mindmap()
    
    # Final rebuild and push
    rebuild_html()
    
    # Commit and push
    print("\nPushing changes to GitHub Pages...")
    try:
        subprocess.run(["git", "add", "-A"], cwd=str(SCRIPT_DIR), env=ENV, timeout=30)
        subprocess.run(["git", "commit", "-m", "Integrate Crash Courses Days 101-106 + Day 107 All For One + Day 14 mindmap fix"], cwd=str(SCRIPT_DIR), env=ENV, timeout=30)
        subprocess.run(["git", "push"], cwd=str(SCRIPT_DIR), env=ENV, timeout=60)
        print("Push complete!")
    except Exception as e:
        print(f"Git push failed: {e}")

if __name__ == "__main__":
    main()
