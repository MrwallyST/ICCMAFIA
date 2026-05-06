"""
Full audit of TradesBySci Studios vs index.html data.
Checks every URL referenced in the JS data array and reports 404s vs OK.
"""
import re, os, sys

# Force UTF-8 output for emoji support
sys.stdout.reconfigure(encoding='utf-8')

BASE = r"C:\Users\cesar\Documents\New folder\TradesBySci"
INDEX = os.path.join(BASE, "index.html")

with open(INDEX, encoding="utf-8") as f:
    content = f.read()

# Extract individual lesson JSON objects using regex
lesson_pattern = re.compile(r'\{[^{}]*"day"\s*:\s*\d+[^{}]*\}', re.DOTALL)
raw_lessons = lesson_pattern.findall(content)

print(f"Found {len(raw_lessons)} lesson entries in index.html\n")
print("=" * 80)

URL_FIELDS = [
    ("youtubeId", False),
    ("audioUrl", True),
    ("infographicUrl", True),
    ("quizFile", True),
    ("studyGuideUrl", True),
    ("flashcardsUrl", True),
    ("mindMapUrl", True),
    ("slideDeckUrl", True),
    ("dataTableUrl", True),
    ("blogPostUrl", True),
    ("youtubeScriptUrl", True),
    ("igCaptionUrl", True),
    ("twitterThreadUrl", True),
    ("newsletterUrl", True),
    ("podcastUrl", True),
    ("faqUrl", True),
    ("tiktokUrl", True),
    ("reelUrl", True),
]

all_issues = []

for raw in raw_lessons:
    day_match = re.search(r'"day"\s*:\s*(\d+)', raw)
    if not day_match:
        continue
    day = int(day_match.group(1))
    
    title_match = re.search(r'"title"\s*:\s*"([^"]*)"', raw)
    title = title_match.group(1) if title_match else "Unknown"
    
    if "comingSoonDate" in raw:
        print(f"Day {day:2d}: [{title}] -- COMING SOON (skipped)")
        continue
    
    print(f"\nDay {day:2d}: {title}")
    day_issues = []
    
    for field, is_file in URL_FIELDS:
        val_match = re.search(rf'"{field}"\s*:\s*"([^"]*)"', raw)
        val = val_match.group(1) if val_match else ""
        
        if field == "youtubeId":
            status = "OK" if val else "EMPTY"
            print(f"  {field:22s}: [{status}] {val[:60] if val else ''}")
            if not val:
                day_issues.append(f"  {field}: MISSING YouTube ID")
            continue
        
        if not val:
            print(f"  {field:22s}: [EMPTY] not in index.html")
            day_issues.append(f"  {field}: EMPTY -- not linked in index.html")
            continue
        
        if not is_file:
            continue
        
        rel = val.replace("./", "").replace("/", os.sep)
        abs_path = os.path.join(BASE, rel)
        
        if os.path.exists(abs_path):
            size = os.path.getsize(abs_path)
            if size > 0:
                print(f"  {field:22s}: [OK]  ({size:,} bytes)")
            else:
                print(f"  {field:22s}: [EMPTY FILE]")
                day_issues.append(f"  {field}: FILE IS EMPTY -> {rel}")
        else:
            print(f"  {field:22s}: [404] FILE MISSING -> {rel}")
            day_issues.append(f"  {field}: FILE NOT ON DISK -> {rel}")
    
    if day_issues:
        all_issues.extend([f"Day {day} ({title}):"] + day_issues + [""])

print("\n" + "=" * 80)
print("FINAL AUDIT SUMMARY")
print("=" * 80)
if all_issues:
    print(f"Issues Found:\n")
    for line in all_issues:
        print(line)
else:
    print("ALL ASSETS VERIFIED -- No issues found!")
