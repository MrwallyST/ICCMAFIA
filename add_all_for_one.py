#!/usr/bin/env python3
"""
TradesBySci — "All For One" Master Lesson Pipeline
Generates a comprehensive final module synthesizing ALL 14 course videos.
This is a special "Day 99" entry that ties the entire ICC curriculum together.
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

DAY_NUM         = 99  # Special ID for "All For One"
TITLE           = "🎯 ALL FOR ONE — The Complete ICC Trading Masterclass"
DESC            = "The ultimate synthesis of all 14 TradesBySci lessons. Every concept, every rule, every edge — in one place."
TAKEAWAYS       = [
    "Complete ICC Framework: Indications → Corrections → Continuations mastered",
    "Every lesson from Days 1–14 synthesized into one actionable playbook",
    "Full risk management system: position sizing, stop placement & R:R ratios",
    "The trader's mindset, psychology & daily routine for consistent profitability"
]

ALL_VIDEOS = [
    ("Day 1",  "https://youtu.be/DpY628SfdgM",  "The Foundation - ICC Framework Decoded Part 1"),
    ("Day 2",  "https://youtu.be/_W3VajeeY5Y",  "ICC Framework Part 2 - Support & Resistance"),
    ("Day 3",  "https://youtu.be/7eLDXUaav1E",  "ICC Framework Part 3 - Liquidity & Corrections"),
    ("Day 4",  "https://youtu.be/vYHD7Cs71MU",  "ICC Framework Part 4 - Continuations & The Entry Model"),
    ("Day 5",  "https://youtu.be/sqH6vqv6bMY",  "The 1 Secret 90% of Traders Don't Know"),
    ("Day 13", "https://youtu.be/Dqin6lHEwZg",  "Positioning & Psychology"),
    ("Day 14", "https://youtu.be/9ZGnRJxt0hY",  "The Complete ICC Playbook - Putting It All Together"),
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
    print("\n   Timed out.")
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
    print(f"   index.html updated with {len(days)} day(s)")

def quiz_json_to_md(json_path, md_path):
    try:
        data = json.loads(Path(json_path).read_text(encoding="utf-8"))
        md = f"# {data.get('title', 'Master Quiz')}\n\n"
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
        print(f"   Quiz conversion: {e}")

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    TOTAL = 9
    day_dir = STUDIOS_DIR / f"day-{DAY_NUM}"
    day_dir.mkdir(parents=True, exist_ok=True)

    step(1, TOTAL, "Setting master notebook as active context...")
    nlm(["use", MASTER_NOTEBOOK])
    print("   ✓ Notebook set (all 14 days already indexed as sources)")

    # 2. Add any missing videos as sources (idempotent)
    step(2, TOTAL, "Ensuring all course videos are indexed as sources...")
    for label, url, title in ALL_VIDEOS:
        print(f"   Adding {label}: {title[:50]}...")
        out = nlm(["source", "add", url, "-n", MASTER_NOTEBOOK], timeout=90)
        print(f"   {label}: {out[:80]}")
        time.sleep(5)
    print("   Waiting 30s for indexing...")
    time.sleep(30)

    # 3. Launch generations — ALL scoped to the FULL curriculum
    step(3, TOTAL, "Launching master synthesis artifacts (all 14 days)...")
    tasks = {}
    SCOPE = (
        "Draw from ALL 14 lessons in this notebook (Days 1-14 of the TradesBySci ICC course). "
        "IMPORTANT: You must heavily emphasize that the entire ICC trading framework (Indication -> Correction -> Continuation) "
        "is ultimately a mechanical safeguard designed to conquer human trading psychology pitfalls—specifically FOMO, greed, impatience, and fear. "
        "Stress that technical mastery is completely useless without disciplined emotional control and risk management; everything in trading "
        "ultimately comes back to psychology and self-regulation."
    )

    print("   -> Audio Overview (Master Podcast)")
    audio_prompt = (
        f"Create a comprehensive, podcast-style Audio Overview that synthesizes ALL 14 lessons of the TradesBySci ICC course. {SCOPE} "
        "Weave the narrative around the core theme: how each mechanical rule of ICC directly serves to protect a trader's psychology. "
        "This should feel like a complete, mind-shifting trading education in one listen."
    )
    out = nlm(["generate", "audio", audio_prompt, "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['audio'] = extract_id(out)

    print("   -> Master Study Guide")
    study_prompt = (
        f"Create the ULTIMATE study guide synthesizing all 14 lessons of the TradesBySci ICC course. {SCOPE} "
        "Organize by topic: Market Structure, ICC Framework, Entries, Exits, Risk Management, and Psychology. "
        "Showcase how every single step of the framework maps back to managing a trader's emotional state. Max 4 pages."
    )
    out = nlm(["generate", "report", study_prompt, "--format", "study-guide", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['study'] = extract_id(out)

    print("   -> Master Flashcards")
    out = nlm(["generate", "flashcards", f"Create 20 flashcards covering the most important concepts and psychological guardrails across ALL 14 lessons. {SCOPE}", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['flash'] = extract_id(out)

    print("   -> Master Quiz")
    quiz_prompt = (
        f"Create a 15-question comprehensive quiz covering ALL 14 lessons of the TradesBySci ICC course. {SCOPE} "
        "Include questions that test the mechanics of ICC and how those mechanics protect against emotional errors like chasing, FOMO, and overtrading."
    )
    out = nlm(["generate", "quiz", quiz_prompt, "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['quiz'] = extract_id(out)

    print("   -> Master Infographic")
    info_prompt = (
        f"Create the ultimate visual cheat-sheet infographic summarizing the complete ICC trading system. {SCOPE} "
        "Include: the 3-phase framework, entry rules, risk management, and a detailed psychology checklist showing how the mechanics prevent emotional mistakes."
    )
    out = nlm(["generate", "infographic", info_prompt, "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['info'] = extract_id(out)

    print("   -> Master Slide Deck")
    slide_prompt = (
        f"Create a comprehensive slide deck presenting the complete ICC trading system from all 14 lessons. {SCOPE} "
        "Dedicate slides to explaining the relationship between technical mechanics and trader psychology, proving why success is 90% psychological."
    )
    out = nlm(["generate", "slide-deck", slide_prompt, "--format", "presenter", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['slides'] = extract_id(out)

    print("   -> Master Data Table")
    out = nlm(["generate", "data-table", f"Create a comprehensive reference table of ALL key concepts, rules, setups, and emotional triggers from the complete 14-lesson ICC course. {SCOPE}", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['table'] = extract_id(out)

    print("   -> Master Blog Post")
    blog_prompt = (
        "Write a comprehensive SEO blog post titled 'The Complete ICC Trading Masterclass: Mechanics Meet Psychology'. "
        f"{SCOPE} Under 1200 words. Weave in the core message: trading is 90% psychology, and ICC is the mechanical framework designed to conquer the psychological traps of greed and fear. "
        "CTA: mrwallyst.github.io/ICCMAFIA for free tools. Credit TradesBySci."
    )
    out = nlm(["generate", "report", "--format", "blog-post", blog_prompt, "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['blog'] = extract_id(out)

    print("   -> Master YouTube Script")
    yt_prompt = (
        "Write an epic YouTube video script for a master compilation video. "
        f"Open with: 'Welcome to ICCMAFIA-AI! Today we break down the ENTIRE TradesBySci ICC course — all 14 lessons — in one video, and show why it all comes down back to psychology!' "
        f"{SCOPE} Structure: Introduction -> Market Structure -> ICC Framework -> Entries -> Risk Management -> Psychology (showing how mechanics serve mindset) -> CTA. "
        "CTA: mrwallyst.github.io/ICCMAFIA for ALL free study materials. Credit TradesBySci."
    )
    out = nlm(["generate", "report", "--format", "custom", "--append", yt_prompt, "All For One Masterclass", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['ytscript'] = extract_id(out)

    print("   -> Master Twitter Thread")
    thread_prompt = (
        "Write a viral 15-post X/Thread: 'The COMPLETE ICC Trading System — 14 lessons distilled into 15 tweets.' "
        f"{SCOPE} Make sure to emphasize how technical rules are actually psychological rules in disguise. "
        "Each post under 400 chars. Number 1/15 to 15/15. Post 1 must hook with the masterclass theme."
    )
    out = nlm(["generate", "report", "--format", "custom", "--append", thread_prompt, "All For One", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['twitter'] = extract_id(out)

    print("   -> Master Newsletter")
    news_prompt = (
        "Write a special email newsletter: 'The ICC Masterclass is Complete — Here's Why It All Comes Down to Psychology.' "
        f"{SCOPE} Under 500 words. Explain why technical mastery fails without the right psychology, and how the ICC framework helps automate discipline. "
        "Subject line, key highlights from all 14 days, CTA to mrwallyst.github.io/ICCMAFIA."
    )
    out = nlm(["generate", "report", "--format", "custom", "--append", news_prompt, "All For One", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['newsletter'] = extract_id(out)

    print("   -> Master LinkedIn Carousel")
    li_prompt = (
        "Write a 7-slide LinkedIn carousel: 'I studied 14 trading lessons. Here's the complete ICC system.' "
        f"{SCOPE} Focus on the transition from mechanics to mindset, showing why psychology is the ultimate foundation of success. "
        "Slide 1=hook, 2-6=key pillars (mechanics & psychology), 7=CTA to mrwallyst.github.io/ICCMAFIA."
    )
    out = nlm(["generate", "report", "--format", "custom", "--append", li_prompt, "All For One", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['linkedin'] = extract_id(out)

    print("   -> Master FAQ Document")
    faq_prompt = (
        f"Write a comprehensive FAQ with 12 Q&A pairs covering the most common questions about the entire ICC trading system. {SCOPE} "
        "Include several questions on trading psychology, emotional control, and how the ICC framework supports mental discipline. Answers under 4 sentences each."
    )
    out = nlm(["generate", "report", "--format", "custom", "--append", faq_prompt, "All For One", "-n", MASTER_NOTEBOOK, "--no-wait"], timeout=60)
    tasks['faq'] = extract_id(out)

    active_tasks = {k: v for k, v in tasks.items() if v}
    print(f"   Launched {len(active_tasks)} parallel generations.")

    step(4, TOTAL, "Waiting for all artifacts to complete...")
    wait_for_all(list(active_tasks.values()), max_wait=1200)

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
        'mind':       day_dir / f"day{DAY_NUM}_mindmap.json",
    }

    if 'audio' in active_tasks:
        print(f"   - audio -> {p['audio'].name}")
        nlm(["download", "audio", str(p['audio']), "-a", active_tasks['audio'], "--force"])

    for key, kind, path_key in [
        ('study',      "report",      'study'),
        ('flash',      "flashcards",  'flash'),
        ('info',       "infographic", 'info'),
        ('slides',     "slide-deck",  'slides'),
        ('table',      "data-table",  'table'),
        ('blog',       "report",      'blog'),
        ('ytscript',   "report",      'ytscript'),
        ('twitter',    "report",      'twitter'),
        ('newsletter', "report",      'newsletter'),
        ('linkedin',   "report",      'linkedin'),
        ('faq',        "report",      'faq'),
    ]:
        if key in active_tasks:
            print(f"   - {key} -> {p[path_key].name}")
            if kind == "flashcards":
                nlm(["download", kind, str(p[path_key]), "-a", active_tasks[key]])
            else:
                nlm(["download", kind, str(p[path_key]), "-a", active_tasks[key], "--force"])

    if 'quiz' in active_tasks:
        print(f"   - quiz -> {p['quiz_raw'].name}")
        nlm(["download", "quiz", str(p['quiz_raw']), "-a", active_tasks['quiz']])
        if p['quiz_raw'].exists():
            quiz_json_to_md(p['quiz_raw'], p['quiz'])

    # 6. Social assets
    step(6, TOTAL, "Writing IG + TikTok master assets...")
    ig_content = f"""## 📸 IG Reel Caption — ALL FOR ONE Masterclass

**Hook Line:**
14 trading lessons. One system. Zero cost. But the real battle is in your mind. 👇

**Body:**
The ICC method is the simplest trading system you'll ever learn.

Three steps. That's it.

📊 INDICATION — A full candle body breaks a swing level. Price showed its hand.

↩️ CORRECTION — Price retraces. Every amateur chases here and gets stopped out.

▶️ CONTINUATION — Lower timeframe structure breaks in your direction. You enter with edge.

🧠 But here's the absolute truth: the mechanics are only 10% of the game. The other 90%? Psychology.
The entire ICC framework is designed as a mechanical safeguard to protect you from YOURSELF. 

It eliminates FOMO. It stops you from chasing wicks. It forces you to wait for the pullback.
If you can't manage your emotions, no technical system in the world will save your account.

Days 1 through 14. Free. Interactive quizzes, flashcards, mind maps, audio and more.

**CTA:**
Full free masterclass in bio — zero cost, zero email required. Link 👆

---

**Hashtags:**
#DayTrading #FuturesTrading #TradingPsychology #ICCMethod #SmartMoney #TradingEducation #TradesBySci #PropFirm #TopstepTrader #LearnToTrade #FuturesTrader #ICCFramework #TradingMasterclass #NQFutures #GoldTrading #OrderFlow #Mindset
"""

    tiktok_content = f"""## 🎵 TikTok Script — ALL FOR ONE Masterclass

**[0:00–0:03] HOOK:**
"14 lessons. One trading system. But if you don't control your mind, you'll still fail."

**[0:03–0:08] THE SYSTEM:**
"This is the ICC method. Indication, Correction, Continuation. But it's actually a psychology cheat code."

**[0:08–0:15] STEP BY STEP:**
"Step 1: Indication. Price breaks a swing level. Do you chase? No. That's FOMO. You wait."

**[0:15–0:21] STEP 2:**
"Step 2: Correction. Price pulls back. This is where the impatient get trapped. Smart money waits for the level."

**[0:21–0:27] STEP 3:**
"Step 3: Continuation. Change of Character on the LTF. You enter. The rules do the thinking, so your emotions don't have to."

**[0:27–0:30] CTA:**
"The entire 14-day masterclass is free. Quizzes, flashcards, mind maps, all focused on psychology and mechanics. Link in bio."

---

**TikTok Caption:**
Trading is 90% psychology. Here is how the ICC method keeps you disciplined 👇 #DayTrading #TradingPsychology #ICCMethod #FuturesTrader #SmartMoneyTrading #LearnToTrade #TradesBySci #TradingMasterclass
"""

    p['ig'].write_text(ig_content, encoding="utf-8")
    p['tiktok'].write_text(tiktok_content, encoding="utf-8")
    print("   IG Caption ✓  TikTok ✓")

    # 7. Mind map
    step(7, TOTAL, "Generating Master Mind Map...")
    mm_out = nlm(["generate", "mind-map", "-n", MASTER_NOTEBOOK, "--json"], timeout=240)
    idx = mm_out.find('{')
    if idx >= 0:
        try:
            data = json.loads(mm_out[idx:])
            p['mind'].write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            print("   Mind Map ✓")
        except Exception as e:
            print(f"   Mind Map JSON Parse Error: {e}")
            p['mind'].write_text(mm_out, encoding="utf-8")
    else:
        print("   Mind Map Empty/Invalid output")

    # 8. Update days.json
    step(8, TOTAL, "Updating days.json with ALL FOR ONE entry...")
    days = json.loads(DAYS_JSON.read_text(encoding="utf-8"))
    days = [d for d in days if d.get("day") != DAY_NUM]

    new_day = {
        "day": DAY_NUM,
        "title": TITLE,
        "description": DESC,
        "youtubeId": "",
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

    # 9. Git push
    step(9, TOTAL, "Pushing to GitHub Pages...")
    subprocess.run(["git", "add", "-A"], cwd=str(SCRIPT_DIR), env=ENV, timeout=30)
    subprocess.run(["git", "commit", "-m", "Add ALL FOR ONE Master Lesson (Day 99)"], cwd=str(SCRIPT_DIR), env=ENV, timeout=30)
    r = subprocess.run(["git", "push"], cwd=str(SCRIPT_DIR), env=ENV, timeout=60)
    print("   Pushed!" if r.returncode == 0 else "   Push failed — push manually.")

    print("\n" + "="*60)
    print("🏆 ALL FOR ONE MASTERCLASS COMPLETE")
    for label, path_key in [
        ("🎧 Audio",      'audio'), ("📖 Study",    'study'),
        ("📇 Flashcards", 'flash'), ("✅ Quiz",     'quiz'),
        ("🖼️  Infographic",'info'),  ("🎞️  Slides",   'slides'),
        ("📊 Data Table", 'table'), ("📝 Blog",     'blog'),
        ("🎬 YT Script",  'ytscript'),("🐦 Twitter", 'twitter'),
        ("📧 Newsletter", 'newsletter'),("📱 LinkedIn",'linkedin'),
        ("❓ FAQ",        'faq'),   ("🗺️  Mind Map", 'mind'),
        ("📸 IG Caption", 'ig'),    ("🎵 TikTok",   'tiktok'),
    ]:
        print(f"  {label}: {'✅' if p[path_key].exists() else '❌'}")
    print(f"  🌐 Live at: https://mrwallyst.github.io/ICCMAFIA/")
    print("="*60)

if __name__ == "__main__":
    main()
