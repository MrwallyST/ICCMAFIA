import json
from pathlib import Path
SCRIPT_DIR = Path(r"c:\Users\cesar\Documents\New folder\TradesBySci")
DAYS_JSON = SCRIPT_DIR / "days.json"
days = json.loads(DAYS_JSON.read_text(encoding="utf-8"))
for d in days:
    if d["day"] == 1:
        d["blogPostUrl"] = "./studios/day-1/day1_blog.md"
        d["youtubeScriptUrl"] = "./studios/day-1/day1_ytscript.md"
        d["twitterThreadUrl"] = "./studios/day-1/day1_twitter.md"
        d["newsletterUrl"] = "./studios/day-1/day1_newsletter.md"
        d["linkedinUrl"] = "./studios/day-1/day1_linkedin.md"
        d["faqUrl"] = "./studios/day-1/day1_faq.md"
DAYS_JSON.write_text(json.dumps(days, indent=2, ensure_ascii=False), encoding="utf-8")
import add_day
add_day.rebuild_html()
