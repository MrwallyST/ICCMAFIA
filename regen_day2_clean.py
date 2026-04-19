import subprocess, sys, re, time, os, json
from pathlib import Path

PYTHON = sys.executable
SCRIPTS_PATH = r"C:\Users\cesar\AppData\Local\Python\pythoncore-3.14-64\Scripts"
ENV = {**os.environ, "PATH": SCRIPTS_PATH + ";" + os.environ.get("PATH", ""), "PYTHONIOENCODING": "utf-8"}
NB_URL = "https://www.youtube.com/watch?v=IGIxQD8PBMo"
out_dir = Path(r"c:\Users\cesar\Documents\New folder\TradesBySci\studios\day-2")

def nlm(args, timeout=120):
    r = subprocess.run([PYTHON, "-m", "notebooklm"] + args, capture_output=True, text=True, env=ENV, timeout=timeout)
    return r.stdout + r.stderr

def extract_id(text):
    m = re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", text)
    return m[0] if m else None

def _clean_mind_map(file_path):
    try:
        content = file_path.read_text(encoding='utf-8')
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*$', '', content)
        file_path.write_text(content.strip(), encoding='utf-8')
    except Exception as e:
        print(f"Error cleaning JSON: {e}")

# 1. Create Isolated Notebook
print("1. Creating isolated Notebook for Day 2...")
nb_out = nlm(["create", "TradesBySci Day 2 (Isolated)"])
m = re.search(r"Created notebook:\s*([a-f0-9-]+)", nb_out)
if not m:
    print("Failed to create notebook", nb_out)
    sys.exit(1)
notebook_id = m.group(1)
print(f"   -> Notebook ID: {notebook_id}")

print("2. Adding Day 2 source...")
nlm(["source", "add", NB_URL, "-n", notebook_id])
time.sleep(20)

tasks = {}
day_num = 2
title_en = "ICC Framework Decoded Part 2 - Support & Resistance"

print("3. Firing generations...")

out = nlm(["generate", "mind-map", "-n", notebook_id], timeout=120)
tasks['mind'] = extract_id(out)

out = nlm(["generate", "flashcards", f"Focus on Day {day_num}: {title_en}", "-n", notebook_id, "--no-wait"], timeout=60)
tasks['flash'] = extract_id(out)

out = nlm(["generate", "quiz", f"8 questions specifically about Day {day_num}: {title_en}", "-n", notebook_id, "--no-wait"], timeout=60)
tasks['quiz'] = extract_id(out)

info_prompt = f"Visual overview of Day 2: {title_en}. Create a clear visual breakdown of the support and resistance concepts discussed. Output ONLY Markdown."
out = nlm(["generate", "infographic", info_prompt, "-n", notebook_id, "--no-wait"], timeout=60)
tasks['info'] = extract_id(out)

out = nlm(["generate", "report", f"Focus on Day {day_num}: {title_en}. Keep it concise — max 2 pages.", "--format", "study-guide", "-n", notebook_id, "--no-wait"], timeout=60)
tasks['study'] = extract_id(out)

print("4. Waiting for complete...")
# Mind map is sync
if tasks['mind']:
    mm_out = nlm(["note", "get", tasks['mind'], "-n", notebook_id], timeout=60)
    out_dir.joinpath("day2_mindmap.json").write_text(mm_out, encoding='utf-8')
    _clean_mind_map(out_dir.joinpath("day2_mindmap.json"))

time.sleep(60)

print("5. Downloading...")
paths = {
    'flash': out_dir / "day2_flashcards.json",
    'quiz': out_dir / "day2_quiz.md",
    'info': out_dir / "day2_infographic.png",
    'study': out_dir / "day2_study.md"
}

for k, p in paths.items():
    if k in tasks and tasks[k]:
        args = ["download", "report" if k == 'study' else k, str(p), "-a", tasks[k], "--force"]
        print(f"Downloading {k}...")
        nlm(args)

# Lastly, update days.json to point to the new notebookId
days_path = Path(r"c:\Users\cesar\Documents\New folder\TradesBySci\days.json")
days = json.loads(days_path.read_text(encoding='utf-8'))
for d in days:
    if d['day'] == 2:
        d['notebookId'] = notebook_id
        break
days_path.write_text(json.dumps(days, indent=2), encoding='utf-8')

print("DONE!")
