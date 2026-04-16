import re

py_path = r"c:\Users\cesar\Documents\New folder\TradesBySci\add_day.py"
with open(py_path, "r", encoding="utf-8") as f:
    text = f.read()

# Remove Step 6: Generate Spanish Audio block
text = re.sub(r'# 6\. Generate Spanish Audio.*?# 7\. Update JSON', '# 6. Update JSON', text, flags=re.DOTALL)

# Update run_pipeline signature
text = re.sub(r'def run_pipeline\(.*?def ', 'def ', text, flags=re.DOTALL) # wait, that would delete the whole function body!

with open(py_path, "w", encoding="utf-8") as f:
    f.write(text)
