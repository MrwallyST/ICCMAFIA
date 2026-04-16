import json
from pathlib import Path
SCRIPT_DIR = Path(r"c:\Users\cesar\Documents\New folder\TradesBySci")
DAYS_JSON = SCRIPT_DIR / "days.json"
days = json.loads(DAYS_JSON.read_text(encoding="utf-8"))
for d in days:
    if "titleEs" in d: del d["titleEs"]
    if "descriptionEs" in d: del d["descriptionEs"]
    if "keyTakeawaysEs" in d: del d["keyTakeawaysEs"]
    if "studios" in d:
        if "en" in d["studios"]:
            d["audioUrl"] = d["studios"]["en"]["audioUrl"]
        del d["studios"]
DAYS_JSON.write_text(json.dumps(days, indent=2, ensure_ascii=False), encoding="utf-8")
import add_day
add_day.rebuild_html()
