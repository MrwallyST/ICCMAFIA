import json
from pathlib import Path
SCRIPT_DIR = Path(r"c:\Users\cesar\Documents\New folder\TradesBySci")
DAYS_JSON = SCRIPT_DIR / "days.json"
days = json.loads(DAYS_JSON.read_text(encoding="utf-8"))
for d in days:
    if d["day"] == 1:
        d["flashcardsUrl"] = "./studios/day-1/day1_flashcards.md"
        d["mindMapUrl"] = "./studios/day-1/day1_mindmap.json"

DAYS_JSON.write_text(json.dumps(days, indent=2, ensure_ascii=False), encoding="utf-8")
import add_day
add_day.rebuild_html()
