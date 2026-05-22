import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

content = open('index.html', 'r', encoding='utf-8').read()

lines = content.splitlines()
start = -1
for i, line in enumerate(lines, 1):
    if 'class="giscus-wrap"' in line:
        start = i
        break

if start >= 0:
    print(f"Giscus wrap starts on line {start}")
    for idx in range(start - 2, start + 25):
        print(f"{idx}: {lines[idx-1]}")
else:
    print("Giscus wrap not found")
