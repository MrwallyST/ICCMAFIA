#!/usr/bin/env python3
"""
TradesBySci — Add Day Pipeline (v2)
=====================================
Uses your MASTER NotebookLM notebook and adds each new day as a source.
Generates per-day audio, quiz, and infographic, downloads them locally,
and updates days.json for the TradesBySci website.

Usage:
  python add_day.py --day 2 --youtube "https://www.youtube.com/watch?v=VIDEO_ID"
                   --title "Your Day 2 Title"
                   --title-es "Titulo en Espanol"
                   --desc "English description"
                   --desc-es "Descripcion en espanol"

After running, the website auto-updates. Push to GitHub -> Vercel deploys.
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

# YOUR MASTER NOTEBOOK — "Foundations of Simple Price Action Trading"
MASTER_NOTEBOOK = "8be24334-4293-41e0-a87d-cd20e67349ae"

ENV = {
    **os.environ,
    "PYTHONIOENCODING": "utf-8",
    "PATH": SCRIPTS_PATH + ";" + os.environ.get("PATH", "")
}

# ── Helpers ──────────────────────────────────────────────────────────────────
def nlm(args: list, timeout=300) -> str:
    """Run a notebooklm CLI command and return combined stdout+stderr as utf-8."""
    cmd = [PYTHON, "-m", "notebooklm"] + args
    result = subprocess.run(
        cmd, capture_output=True, env=ENV, timeout=timeout,
        encoding="utf-8", errors="replace"
    )
    return ((result.stdout or "") + (result.stderr or "")).strip()

def step(n, total, msg):
    print(f"\n[{n}/{total}] {msg}", flush=True)

def wait_for_artifact(artifact_id: str, label="artifact", max_wait=600) -> bool:
    """Poll artifact list until the given ID shows as complete."""
    print(f"   Waiting for {label} to finish generating...", end="", flush=True)
    for _ in range(max_wait // 15):
        out = nlm(["artifact", "list", "-n", MASTER_NOTEBOOK], timeout=30)
        relevant = [l for l in out.splitlines() if artifact_id[:8] in l]
        if any("complete" in l.lower() or "ready" in l.lower() for l in relevant):
            print(" done!")
            return True
        if any("fail" in l.lower() or "error" in l.lower() for l in relevant):
            print(" FAILED!")
            return False
        print(".", end="", flush=True)
        time.sleep(15)
    print(" timed out (may still be generating)")
    return False

def rebuild_html():
    """Embed the latest days.json data directly into index.html so it works on file://"""
    html_path = SCRIPT_DIR / "index.html"
    if not html_path.exists() or not DAYS_JSON.exists():
        return
    days = json.loads(DAYS_JSON.read_text(encoding="utf-8"))
    days_json_str = json.dumps(days, ensure_ascii=False, separators=(',', ':'))
    html = html_path.read_text(encoding="utf-8")
    # Replace the DAYS_DATA line
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
    TOTAL = 5
    day_dir = STUDIOS_DIR / f"day-{day_num}"
    day_dir.mkdir(parents=True, exist_ok=True)
    youtube_id = youtube_url.split("v=")[-1].split("&")[0] if "v=" in youtube_url else ""

    # ── Step 1: Set master notebook as active context ────────────────────────
    step(1, TOTAL, f"Setting master notebook as active context...")
    out = nlm(["use", MASTER_NOTEBOOK])
    print(f"   {out[:200]}")

    # ── Step 2: Add new YouTube video as source ──────────────────────────────
    step(2, TOTAL, f"Adding Day {day_num} YouTube video as source...")
    out = nlm(["source", "add", youtube_url, "-n", MASTER_NOTEBOOK], timeout=60)
    print(f"   {out[:300]}")
    if "error" in out.lower() and "already" not in out.lower():
        print("   Warning: source may not have been added. Continuing anyway.")
    else:
        print("   Source added. Waiting 10s for indexing...")
        time.sleep(10)

    # ── Step 3: Generate per-day audio ──────────────────────────────────────
    step(3, TOTAL, f"Generating Day {day_num} Audio Studio (English)...")
    out = nlm(["generate", "audio",
               f"Focus specifically on Day {day_num}: {title_en}. Key topics: {', '.join(takeaways_en[:3])}.",
               "-n", MASTER_NOTEBOOK, "--wait"],
              timeout=600)
    # Extract artifact ID from output
    artifact_id = None
    matches = re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", out)
    if matches:
        artifact_id = matches[0]
    print(f"   Started artifact: {artifact_id or 'unknown'}")
    print(f"   {out[:200]}")

    # Wait for completion
    if artifact_id:
        wait_for_artifact(artifact_id, label="audio", max_wait=600)

    # Download audio
    audio_path = day_dir / f"day{day_num}_en.mp3"
    print(f"   Downloading audio -> {audio_path}")
    out = nlm(["download", "audio", str(audio_path),
               "-n", MASTER_NOTEBOOK, "--force"], timeout=120)
    print(f"   {out[:300]}")
    audio_ok = audio_path.exists() and audio_path.stat().st_size > 1000
    print(f"   Audio: {'OK (' + str(audio_path.stat().st_size // 1024) + ' KB)' if audio_ok else 'NOT DOWNLOADED'}")

    # ── Step 4: Generate quiz ────────────────────────────────────────────────
    step(4, TOTAL, f"Generating Day {day_num} Quiz...")
    out = nlm(["generate", "quiz",
               f"8 questions specifically about Day {day_num}: {title_en}. Focus on: {', '.join(takeaways_en)}.",
               "-n", MASTER_NOTEBOOK, "--wait"],
              timeout=300)
    quiz_id = None
    matches = re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", out)
    if matches:
        quiz_id = matches[0]
    print(f"   Quiz artifact: {quiz_id or 'unknown'}")

    if quiz_id:
        wait_for_artifact(quiz_id, label="quiz", max_wait=300)
    quiz_path = day_dir / f"day{day_num}_quiz.md"
    out = nlm(["download", "quiz", str(quiz_path),
               "-n", MASTER_NOTEBOOK, "--format", "markdown"], timeout=60)
    print(f"   {out[:200]}")
    quiz_ok = quiz_path.exists()

    # ── Step 5: Update days.json ─────────────────────────────────────────────
    step(5, TOTAL, "Updating days.json for the website...")
    if DAYS_JSON.exists():
        days = json.loads(DAYS_JSON.read_text(encoding="utf-8"))
    else:
        days = []

    # Remove existing entry for this day if re-running
    days = [d for d in days if d.get("day") != day_num]

    new_day = {
        "day": day_num,
        "title": title_en,
        "titleEs": title_es,
        "description": desc_en,
        "descriptionEs": desc_es,
        "youtubeId": youtube_id,
        "reelUrl": "",
        "studios": {
            "en": {
                "audioUrl":   f"./studios/day-{day_num}/day{day_num}_en.mp3" if audio_ok else "",
                "audioLabel": f"Day {day_num} Audio Overview"
            },
            "es": {
                "audioUrl":   "",
                "audioLabel": f"Día {day_num} — Resumen en Español"
            }
        },
        "infographicUrl": "",
        "quizFile":       f"./studios/day-{day_num}/day{day_num}_quiz.md" if quiz_ok else "",
        "keyTakeaways":   takeaways_en,
        "keyTakeawaysEs": takeaways_es,
        "notebookId":     MASTER_NOTEBOOK
    }

    days.append(new_day)
    days.sort(key=lambda d: d["day"])
    DAYS_JSON.write_text(json.dumps(days, indent=2, ensure_ascii=False), encoding="utf-8")
    rebuild_html()

    # ── Summary ──────────────────────────────────────────────────────────────
    print("\n" + "="*60)
    print(f"Day {day_num} pipeline complete!")
    print(f"  Audio EN   : {'OK' if audio_ok else 'MISSING - check NotebookLM'}")
    print(f"  Quiz       : {'OK' if quiz_ok else 'MISSING'}")
    print(f"  days.json  : Updated")
    print(f"  index.html : Updated (open in Chrome to see changes)")
    print()
    print("NEXT STEPS:")
    print(f"  1. For Spanish audio: Generate it in NotebookLM, save to:")
    print(f"     studios/day-{day_num}/day{day_num}_es.mp3")
    print(f"     then run: python add_day.py --day {day_num} --patch-es")
    print(f"  2. Refresh index.html in Chrome (press F5)")
    print("="*60)


# ── Patch ES audio URL only ───────────────────────────────────────────────────
def patch_es_audio(day_num: int):
    es_path = STUDIOS_DIR / f"day-{day_num}" / f"day{day_num}_es.mp3"
    if not es_path.exists():
        print(f"File not found: {es_path}")
        sys.exit(1)
    days = json.loads(DAYS_JSON.read_text(encoding="utf-8"))
    for d in days:
        if d["day"] == day_num:
            d["studios"]["es"]["audioUrl"] = f"./studios/day-{day_num}/day{day_num}_es.mp3"
            print(f"Updated Day {day_num} Spanish audio in days.json")
    DAYS_JSON.write_text(json.dumps(days, indent=2, ensure_ascii=False), encoding="utf-8")
    rebuild_html()
    print("index.html updated — refresh Chrome (F5)")


# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    p = argparse.ArgumentParser(description="Add a new TradesBySci day to the website")
    p.add_argument("--day",       type=int,  required=True)
    p.add_argument("--youtube",   default="")
    p.add_argument("--title",     default="")
    p.add_argument("--title-es",  default="")
    p.add_argument("--desc",      default="")
    p.add_argument("--desc-es",   default="")
    p.add_argument("--patch-es",  action="store_true",
                   help="Only update Spanish audio URL in days.json")
    args = p.parse_args()

    if args.patch_es:
        patch_es_audio(args.day)
        return

    if not args.youtube:
        print("Error: --youtube is required")
        sys.exit(1)

    takeaways_en = [
        "ICC Framework: Indications, Corrections, Continuations",
        "How to read order flow and identify liquidity zones",
        "The 3 market phases every futures trader must know",
        "Real trade setups from the Trades by Sci curriculum"
    ]
    takeaways_es = [
        "Marco ICC: Indicaciones, Correcciones, Continuaciones",
        "Como leer el flujo de ordenes e identificar zonas de liquidez",
        "Las 3 fases del mercado para futuros",
        "Setups reales del curriculo de Trades by Sci"
    ]

    run_pipeline(
        day_num    = args.day,
        youtube_url= args.youtube,
        title_en   = args.title  or f"TradesBySci Day {args.day}",
        title_es   = getattr(args, 'title_es', '') or f"TradesBySci Dia {args.day}",
        desc_en    = args.desc   or "AI-decoded Trades by Sci lesson.",
        desc_es    = getattr(args, 'desc_es', '') or "Leccion decodificada con IA.",
        takeaways_en = takeaways_en,
        takeaways_es = takeaways_es,
    )

if __name__ == "__main__":
    main()
