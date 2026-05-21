import os
import sys
import json
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def check_day_99_assets():
    base_dir = Path(r"C:\Users\cesar\Documents\New folder\TradesBySci")
    days_json_path = base_dir / "days.json"
    
    if not days_json_path.exists():
        print("Error: days.json not found")
        sys.exit(1)
        
    try:
        with open(days_json_path, "r", encoding="utf-8") as f:
            days = json.load(f)
    except Exception as e:
        print(f"Error loading days.json: {e}")
        sys.exit(1)
        
    day_99 = None
    for d in days:
        if d.get("day") == 99:
            day_99 = d
            break
            
    if not day_99:
        print("Error: Day 99 is missing from days.json")
        sys.exit(1)
        
    print(f"Found Day 99 entry: {day_99['title']}")
    
    # Check expected files
    day_dir = base_dir / "studios" / "day-99"
    if not day_dir.exists():
        print(f"Error: studios/day-99 directory does not exist")
        sys.exit(1)
        
    expected_files = [
        "day99_en.mp3",
        "day99_study.md",
        "day99_flashcards.json",
        "day99_quiz.md",
        "day99_infographic.png",
        "day99_slides.pdf",
        "day99_datatable.md",
        "day99_blog.md",
        "day99_ytscript.md",
        "day99_twitter.md",
        "day99_newsletter.md",
        "day99_linkedin.md",
        "day99_faq.md",
        "day99_ig.md",
        "day99_tiktok.md",
        "day99_mindmap.json",
    ]
    
    missing = []
    for f in expected_files:
        path = day_dir / f
        if not path.exists():
            missing.append(f)
        elif path.stat().st_size == 0:
            missing.append(f"{f} (empty file)")
            
    if missing:
        print(f"Error: Missing or empty Day 99 files: {', '.join(missing)}")
        sys.exit(1)
        
    print("All Day 99 assets successfully verified!")
    sys.exit(0)

if __name__ == "__main__":
    check_day_99_assets()
