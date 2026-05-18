#!/usr/bin/env python3
"""
TradesBySci — Add Day 14 Pipeline (Full Suite)
Adds Day 14 YouTube video as source, generates ALL artifacts,
updates days.json, rebuilds index.html, pushes to GitHub.
"""

import os, sys, json, time, subprocess, re
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── Config ───────────────────────────────────────────────────────────────────
SCRIPT_DIR      = Path(__file__).parent
DAYS_JSON       = SCRIPT_DIR / "days.json"
STUDIOS_DIR     = SCRIPT_DIR / "studios"
PYTHON          = sys.executable
SCRIPTS_PATH    = r"C:\Users\cesar\AppData\Local\Python\pythoncore-3.14-64\Scripts"
MASTER_NOTEBOOK = "8be24334-4293-41e0-a87d-cd20e67349ae"

DAY_NUM         = 14
YOUTUBE_URL     = "https://youtu.be/9ZGnRJxt0hY"
YOUTUBE_ID      = "9ZGnRJxt0hY"
TITLE           = "Day 14: The Complete ICC Playbook - Putting It All Together"
DESC            = "AI-decoded Trades by Sci lesson."
TAKEAWAYS       = [
    "Full ICC playbook applied from start to finish on a live chart",
    "How to combine Indications, Corrections & Continuations in real trades",
    "Multi-timeframe confluence: 1H/4H setup + 5M/15M precision entry",
    "Mindset, risk management & the trader's checklist for every session"
]

ENV = {**os.environ, "PYTHONIOENCODING": "utf-8",
       "PATH": SCRIPTS_PATH + ";" + os.environ.get("PATH", "")}

# ── Helpers ──────────────────────────────────────────────────────────────────
def nlm(args, timeout=600):
    cmd = [PYTHON, "-m", "notebooklm"] + args
    r = subprocess.run(cmd, capture_output=True, env=ENV, timeout=timeout,
                       encoding="utf-8", errors="replace")
    return ((r.stdout or "") + (r.stderr or "")).strip()

def extract_id(text):
    m = re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", text)
    return m[0] if m else None

def step(n, total, msg):
    print(f"\n[{n}/{total}] {msg}", flush=True)

def wait_for_all(artifact_ids, max_wait=1200):
    pending = set(artifact_ids)
    print(f"   Waiting for {len(pending)} artifacts...", flush=True)
    for _ in range(max_wait // 15):
        if not pending:
            return True
        out = nlm(["artifact", "list", "-n", MASTER_NOTEBOOK], timeout=60)
        lines = out.splitlines()
        still = set()
        for aid in pending:
            rel = [l for l in lines if aid[:8] in l]
            if any("complete" in l.lower() or "ready" in l.lower() for l in rel):
                print(f"\n   ✓ {aid[:8]} done!")
            elif any("fail" in l.lower() or "error" in l.lower() for l in rel):
                print(f"\n   ✗ {aid[:8]} failed!")
            else:
                still.add(aid)
        pending = still
        if pending:
            print(".", end="", flush=True)
            time.sleep(15)
    print("\n   Timed out on some artifacts.")
    return False

def rebuild_html():
    html_path = SCRIPT_DIR / "index.html"
    if not html_path.exists() or not DAYS_JSON.exists():
        return
    days = json.loads(DAYS_JSON.read_text(encoding="utf-8"))
    days_str = json.dumps(days, ensure_ascii=False, separators=(',', ':'))
    html = html_path.read_text(encoding="utf-8")
    new_line = f'  const DAYS_DATA = {days_str};'
    html = re.sub(r'  const DAYS_DATA = \[.*?\];', new_line, html, flags=re.DOTALL)
    html_path.write_text(html, encoding="utf-8")
    print(f"   index.html updated with {len(days)} day(s) of data")

def quiz_json_to_md(json_path, md_path):
    """Convert NotebookLM quiz JSON to the Markdown format the site expects."""
    try:
        data = json.loads(Path(json_path).read_text(encoding="utf-8"))
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
        print(f"   Quiz converted to Markdown ✓")
        return True
    except Exception as e:
        print(f"   Quiz conversion warning: {e}")
        return False

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    TOTAL = 9
    day_dir = STUDIOS_DIR / f"day-{DAY_NUM}"
    day_dir.mkdir(parents=True, exist_ok=True)

    # 1. Set active notebook
    step(1, TOTAL, "Setting master notebook as active context...")
    nlm(["use", MASTER_NOTEBOOK])
    print("   ✓ Notebook set")

    # 2. Add Day 14 YouTube as source
    step(2, TOTAL, f"Adding Day {DAY_NUM} YouTube video as source...")
    out = nlm(["source", "add", YOUTUBE_URL, "-n", MASTER_NOTEBOOK], timeout=90)
    print(f"   Source add: {out[:120]}")
    print("   Waiting 30s for indexing...")
    time.sleep(30)

    # 3. Launch all generations in parallel
    step(3, TOTAL, f"Launching full learning suite for Day {DAY_NUM}...")
    tasks = {}

    print("   -> Audio Overview")
    audio_prompt = f"Create an engaging podcast-style Audio Overview for Day {DAY_NUM}: {TITLE}. Focus ONLY on Day {DAY_NUM} concepts."
    out = nlm(["generate", "audio", audio_prompt, "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['audio'] = extract_id(out)

    print("   -> Study Guide")
    study_prompt = f"FOCUS STRICTLY on Day {DAY_NUM}: {TITLE}. Generate a concise 2-page study guide covering only the concepts from this specific lesson."
    out = nlm(["generate", "report", study_prompt, "--format", "study-guide", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['study'] = extract_id(out)

    print("   -> Flashcards")
    out = nlm(["generate", "flashcards", f"FOCUS EXCLUSIVELY on Day {DAY_NUM}: {TITLE}. Generate 10 flashcards.", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['flash'] = extract_id(out)

    print("   -> Quiz")
    quiz_prompt = f"Create 10 multiple-choice questions EXCLUSIVELY about Day {DAY_NUM}: {TITLE}. Do NOT test on previous days."
    out = nlm(["generate", "quiz", quiz_prompt, "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['quiz'] = extract_id(out)

    print("   -> Infographic")
    info_prompt = f"Create a visual cheat-sheet infographic for Day {DAY_NUM}: {TITLE}. Include key rules, entry criteria, and concepts from this lesson only."
    out = nlm(["generate", "infographic", info_prompt, "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['info'] = extract_id(out)

    print("   -> Slide Deck")
    slide_prompt = f"Lesson slides for Day {DAY_NUM}: {TITLE}. One key idea per slide, bullet points, concise."
    out = nlm(["generate", "slide-deck", slide_prompt, "--length", "short", "--format", "presenter", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['slides'] = extract_id(out)

    print("   -> Data Table")
    out = nlm(["generate", "data-table", f"Key concepts, definitions, and examples from Day {DAY_NUM}: {TITLE}.", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['table'] = extract_id(out)

    print("   -> Blog Post")
    blog_prompt = f"SEO blog post for Day {DAY_NUM}: {TITLE}. Under 800 words, actionable takeaways. Credit Trades by Sci. CTA: mrwallyst.github.io/ICCMAFIA"
    out = nlm(["generate", "report", "--format", "blog-post", blog_prompt, "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['blog'] = extract_id(out)

    print("   -> YouTube Script")
    yt_prompt = (
        f"YouTube video script for Day {DAY_NUM}: {TITLE}. "
        f"Open with: 'Welcome to ICCMAFIA-AI, today we summarize Day {DAY_NUM} of the TradesbySci ICC course!' "
        "Break down all concepts clearly. CTA: mrwallyst.github.io/ICCMAFIA for free study tools. Credit Trades by Sci."
    )
    out = nlm(["generate", "report", "--format", "custom", "--append", yt_prompt, f"Day {DAY_NUM}: {TITLE}", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['ytscript'] = extract_id(out)

    print("   -> Twitter Thread")
    thread_prompt = f"Viral 10-post X/Thread for Day {DAY_NUM}: {TITLE}. Each post under 400 chars. Number them 1/10 to 10/10. First post mentions 'Day {DAY_NUM} of TradesbySci ICC Course'."
    out = nlm(["generate", "report", "--format", "custom", "--append", thread_prompt, f"Day {DAY_NUM}", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['twitter'] = extract_id(out)

    print("   -> Newsletter")
    news_prompt = f"Short email newsletter for Day {DAY_NUM}: {TITLE}. Under 400 words. Subject line, 3 bullet points, CTA to mrwallyst.github.io/ICCMAFIA."
    out = nlm(["generate", "report", "--format", "custom", "--append", news_prompt, f"Day {DAY_NUM}", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['newsletter'] = extract_id(out)

    print("   -> LinkedIn Carousel")
    li_prompt = f"5-slide LinkedIn carousel for Day {DAY_NUM}: {TITLE}. Slide 1=hook, 2-4=key concepts, 5=CTA to mrwallyst.github.io/ICCMAFIA. Credit Trades by Sci."
    out = nlm(["generate", "report", "--format", "custom", "--append", li_prompt, f"Day {DAY_NUM}", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['linkedin'] = extract_id(out)

    print("   -> FAQ Document")
    faq_prompt = f"8 Q&A pairs answering beginner questions about Day {DAY_NUM}: {TITLE}. Answers under 3 sentences each."
    out = nlm(["generate", "report", "--format", "custom", "--append", faq_prompt, f"Day {DAY_NUM}", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['faq'] = extract_id(out)

    active_tasks = {k: v for k, v in tasks.items() if v}
    print(f"   Launched {len(active_tasks)} parallel generations.")

    # 4. Wait
    step(4, TOTAL, "Waiting for all artifacts to complete...")
    wait_for_all(list(active_tasks.values()), max_wait=1200)

    # 5. Download
    step(5, TOTAL, "Downloading all artifacts...")
    p = {
        'audio':      day_dir / f"day{DAY_NUM}_en.mp3",
        'study':      day_dir / f"day{DAY_NUM}_study.md",
        'flash':      day_dir / f"day{DAY_NUM}_flashcards.json",
        'quiz_raw':   day_dir / f"day{DAY_NUM}_quiz_raw.json",
        'quiz':       day_dir / f"day{DAY_NUM}_quiz.md",
        'info':       day_dir / f"day{DAY_NUM}_infographic.png",
        'slides':     day_dir / f"day{DAY_NUM}_slides.pdf",
        'table':      day_dir / f"day{DAY_NUM}_datatable.md",
        'blog':       day_dir / f"day{DAY_NUM}_blog.md",
        'ytscript':   day_dir / f"day{DAY_NUM}_ytscript.md",
        'twitter':    day_dir / f"day{DAY_NUM}_twitter.md",
        'newsletter': day_dir / f"day{DAY_NUM}_newsletter.md",
        'linkedin':   day_dir / f"day{DAY_NUM}_linkedin.md",
        'faq':        day_dir / f"day{DAY_NUM}_faq.md",
        'ig':         day_dir / f"day{DAY_NUM}_ig.md",
        'tiktok':     day_dir / f"day{DAY_NUM}_tiktok.md",
    }

    def dl(key, kind, path):
        if key in active_tasks:
            print(f"   - {kind} -> {path.name}")
            nlm(["download", kind, str(path), "-a", active_tasks[key], "--force"])

    if 'audio' in active_tasks:
        print(f"   - audio -> {p['audio'].name}")
        nlm(["download", "audio", str(p['audio']), "-a", active_tasks['audio'], "--force"])
    dl('study',      "report",      p['study'])
    dl('flash',      "flashcards",  p['flash'])
    dl('info',       "infographic", p['info'])
    dl('slides',     "slide-deck",  p['slides'])
    dl('table',      "data-table",  p['table'])
    dl('blog',       "report",      p['blog'])
    dl('ytscript',   "report",      p['ytscript'])
    dl('twitter',    "report",      p['twitter'])
    dl('newsletter', "report",      p['newsletter'])
    dl('linkedin',   "report",      p['linkedin'])
    dl('faq',        "report",      p['faq'])

    # Download quiz as JSON then convert to MD
    if 'quiz' in active_tasks:
        print(f"   - quiz (json) -> {p['quiz_raw'].name}")
        nlm(["download", "quiz", str(p['quiz_raw']), "-a", active_tasks['quiz'], "--force"])
        if p['quiz_raw'].exists():
            quiz_json_to_md(p['quiz_raw'], p['quiz'])
        else:
            # Try downloading directly as markdown
            nlm(["download", "report", str(p['quiz']), "-a", active_tasks['quiz'], "--force"])

    # 6. Generate IG + TikTok locally from study guide content
    step(6, TOTAL, "Generating social assets (IG + TikTok)...")
    ig_content = f"""## 📸 IG Reel Caption — Day {DAY_NUM}

**Hook Line (First 2 lines — no hashtags, stop the scroll):**
This is Day {DAY_NUM} of the ICC course. The last lesson. Here's everything you need to know to actually execute. 👇

**Body:**
Day {DAY_NUM} is where everything clicks.

The ICC method isn't complicated. Three steps:

INDICATION — Price breaks a key swing level with a full candle body close. That's your signal.

CORRECTION — Price pulls back to where it launched. FOMO traders got wrecked here. You're still patient.

CONTINUATION — Structure breaks on the lower timeframe. NOW you enter. With conviction.

Stop overcomplicating trading. These three rules, applied consistently, are what separate funded traders from blown accounts.

**CTA:**
Full free course in bio — quizzes, flashcards, audio included. Zero cost. Link 👆

---

**Hashtags (paste as first comment):**
#DayTrading #FuturesTrading #ICCMethod #SmartMoney #TradingEducation #OrderFlow #NQ #GoldTrading #PropFirm #TopstepTrader #TradingStrategy #LearnToTrade #FuturesTrader #ICCFramework #TradesBySci
"""

    tiktok_content = f"""## 🎵 TikTok Script — Day {DAY_NUM}

**[0:00–0:03] HOOK — ON SCREEN TEXT + VOICEOVER:**
"Day {DAY_NUM}. The final lesson. Here's the full ICC playbook in 30 seconds."

**[0:03–0:10] STEP 1 — INDICATION:**
"Look for a full candle BODY — not a wick — to close past a swing high or low. That tells you where price wants to go next."

**[0:10–0:17] STEP 2 — CORRECTION:**
"Price comes back. This is where beginners panic and chase. Smart money waits right here at the key level."

**[0:17–0:24] STEP 3 — CONTINUATION:**
"On the 5 or 15 minute chart, you wait for a Change of Character. When structure breaks in your direction — that's your entry."

**[0:24–0:28] RESULT:**
"Two high-quality trades a week with a 1:3 risk-reward is all you need. That's the system."

**[0:28–0:30] CTA:**
"Free full course in my bio. Drop a 🔥 if this helped."

---

**TikTok Caption:**
The complete ICC trading system in 30 seconds. Day {DAY_NUM} — final lesson. All free 👇 #DayTrading #ICCMethod #FuturesTrader #SmartMoneyTrading #LearnToTrade #TradesBySci
"""

    p['ig'].write_text(ig_content, encoding="utf-8")
    p['tiktok'].write_text(tiktok_content, encoding="utf-8")
    print("   IG Caption ✓")
    print("   TikTok Script ✓")

    # 7. Update days.json
    step(7, TOTAL, "Updating days.json...")
    days = json.loads(DAYS_JSON.read_text(encoding="utf-8"))
    days = [d for d in days if d.get("day") != DAY_NUM]

    new_day = {
        "day": DAY_NUM,
        "title": TITLE,
        "description": DESC,
        "youtubeId": YOUTUBE_ID,
        "reelUrl": "",
        "audioUrl":        f"./studios/day-{DAY_NUM}/day{DAY_NUM}_en.mp3",
        "infographicUrl":  f"./studios/day-{DAY_NUM}/day{DAY_NUM}_infographic.png",
        "quizFile":        f"./studios/day-{DAY_NUM}/day{DAY_NUM}_quiz.md",
        "studyGuideUrl":   f"./studios/day-{DAY_NUM}/day{DAY_NUM}_study.md",
        "flashcardsUrl":   f"./studios/day-{DAY_NUM}/day{DAY_NUM}_flashcards.json",
        "mindMapUrl":      f"./studios/day-{DAY_NUM}/day{DAY_NUM}_mindmap.json",
        "slideDeckUrl":    f"./studios/day-{DAY_NUM}/day{DAY_NUM}_slides.pdf",
        "dataTableUrl":    f"./studios/day-{DAY_NUM}/day{DAY_NUM}_datatable.md",
        "blogPostUrl":     f"./studios/day-{DAY_NUM}/day{DAY_NUM}_blog.md",
        "youtubeScriptUrl":f"./studios/day-{DAY_NUM}/day{DAY_NUM}_ytscript.md",
        "igCaptionUrl":    f"./studios/day-{DAY_NUM}/day{DAY_NUM}_ig.md",
        "tiktokUrl":       f"./studios/day-{DAY_NUM}/day{DAY_NUM}_tiktok.md",
        "twitterThreadUrl":f"./studios/day-{DAY_NUM}/day{DAY_NUM}_twitter.md",
        "newsletterUrl":   f"./studios/day-{DAY_NUM}/day{DAY_NUM}_newsletter.md",
        "linkedinUrl":     f"./studios/day-{DAY_NUM}/day{DAY_NUM}_linkedin.md",
        "faqUrl":          f"./studios/day-{DAY_NUM}/day{DAY_NUM}_faq.md",
        "keyTakeaways": TAKEAWAYS,
        "notebookId": MASTER_NOTEBOOK
    }

    days.append(new_day)
    days.sort(key=lambda d: d["day"])
    DAYS_JSON.write_text(json.dumps(days, indent=2, ensure_ascii=False), encoding="utf-8")
    rebuild_html()

    # 8. Generate mind map synchronously
    step(8, TOTAL, "Generating Mind Map...")
    mind_path = day_dir / f"day{DAY_NUM}_mindmap.json"
    if not mind_path.exists():
        mm_out = nlm(["generate", "mind-map", f"Mind map for Day {DAY_NUM}: {TITLE}. Core concepts only.", "-n", MASTER_NOTEBOOK], timeout=180)
        mm_id = extract_id(mm_out)
        if mm_id:
            raw = nlm(["note", "get", mm_id, "-n", MASTER_NOTEBOOK], timeout=60)
            idx = raw.find('{')
            if idx >= 0:
                try:
                    data = json.loads(raw[idx:])
                    mind_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
                    print("   Mind Map ✓")
                except:
                    mind_path.write_text(raw, encoding="utf-8")
            else:
                mind_path.write_text(raw, encoding="utf-8")

    # 9. Git push
    step(9, TOTAL, "Pushing to GitHub Pages...")
    subprocess.run(["git", "add", "-A"], cwd=str(SCRIPT_DIR), env=ENV, timeout=30)
    subprocess.run(["git", "commit", "-m", f"Add Day {DAY_NUM}: {TITLE}"], cwd=str(SCRIPT_DIR), env=ENV, timeout=30)
    r = subprocess.run(["git", "push"], cwd=str(SCRIPT_DIR), env=ENV, timeout=60)
    if r.returncode == 0:
        print("   Pushed to GitHub! Site will update in ~60 seconds.")
    else:
        print("   Push failed. Run: git add -A && git commit -m 'Day 14' && git push")

    # Summary
    print("\n" + "="*60)
    print(f"🎉 Day {DAY_NUM} COMPLETE")
    for label, path in [
        ("🎧 Audio",       p['audio']),
        ("📖 Study",       p['study']),
        ("📇 Flashcards",  p['flash']),
        ("✅ Quiz",        p['quiz']),
        ("🖼️  Infographic", p['info']),
        ("🎞️  Slides",      p['slides']),
        ("📊 Data Table",  p['table']),
        ("📝 Blog Post",   p['blog']),
        ("🎬 YT Script",   p['ytscript']),
        ("🐦 Twitter",     p['twitter']),
        ("📧 Newsletter",  p['newsletter']),
        ("📱 LinkedIn",    p['linkedin']),
        ("❓ FAQ",         p['faq']),
        ("📸 IG Caption",  p['ig']),
        ("🎵 TikTok",      p['tiktok']),
    ]:
        print(f"  {label}: {'✅' if path.exists() else '❌'}")
    print(f"  🌐 Live at: https://mrwallyst.github.io/ICCMAFIA/")
    print("="*60)

if __name__ == "__main__":
    main()
