import os
import sys
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def check_assets():
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
        
    # 1. Check Day 14 Mind Map
    p_mind_14 = base_dir / "studios" / "day-14" / "day14_mindmap.json"
    if not p_mind_14.exists():
        print("Error: Day 14 mind map does not exist")
        sys.exit(1)
    elif p_mind_14.stat().st_size == 0:
        print("Error: Day 14 mind map is empty")
        sys.exit(1)
    else:
        try:
            with open(p_mind_14, "r", encoding="utf-8") as f:
                json.load(f)
            print("Day 14 mind map successfully verified!")
        except Exception as e:
            print(f"Error: Day 14 mind map is not valid JSON: {e}")
            sys.exit(1)

    # 2. Check Days 101-107 in days.json
    expected_days = list(range(101, 108))
    days_in_json = {d.get("day"): d for d in days}
    
    for day_num in expected_days:
        if day_num not in days_in_json:
            print(f"Error: Day {day_num} is missing from days.json")
            sys.exit(1)
        print(f"Found Day {day_num} entry in days.json: {days_in_json[day_num]['title']}")
        
    # 3. Check physical assets for Days 101-107
    for day_num in expected_days:
        day_dir = base_dir / "studios" / f"day-{day_num}"
        if not day_dir.exists():
            print(f"Error: Directory {day_dir} does not exist")
            sys.exit(1)
            
        expected_files = [
            f"day{day_num}_en.mp3",
            f"day{day_num}_study.md",
            f"day{day_num}_flashcards.json",
            f"day{day_num}_mindmap.json",
            f"day{day_num}_quiz.md",
            f"day{day_num}_quiz_raw.json",
            f"day{day_num}_infographic.png",
            f"day{day_num}_slides.pdf",
            f"day{day_num}_datatable.md",
            f"day{day_num}_blog.md",
            f"day{day_num}_ytscript.md",
            f"day{day_num}_twitter.md",
            f"day{day_num}_newsletter.md",
            f"day{day_num}_linkedin.md",
            f"day{day_num}_faq.md",
            f"day{day_num}_ig.md",
            f"day{day_num}_tiktok.md"
        ]
        
        missing = []
        for f in expected_files:
            path = day_dir / f
            if not path.exists():
                missing.append(f)
            elif path.stat().st_size == 0:
                missing.append(f"{f} (empty file)")
                
        if missing:
            print(f"Error: Missing or empty Day {day_num} files: {', '.join(missing)}")
            sys.exit(1)
            
        # Verify JSON validity for flashcards and mindmaps
        for json_f in [f"day{day_num}_flashcards.json", f"day{day_num}_mindmap.json"]:
            try:
                with open(day_dir / json_f, "r", encoding="utf-8") as f:
                    json.load(f)
            except Exception as e:
                print(f"Error: {json_f} is not valid JSON: {e}")
                sys.exit(1)
                
        print(f"All Day {day_num} assets successfully verified!")
        
    print("All checks passed successfully!")
    sys.exit(0)

if __name__ == "__main__":
    check_assets()
