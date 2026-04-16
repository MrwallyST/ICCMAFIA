import subprocess
import time
import re

print("Requesting new thread...")
out = subprocess.check_output(
    ["nlm", "generate", "report", "--format", "custom", "--append", 
     "Write a viral 10-post Thread (optimized for X/Instagram Threads) summarizing the key concepts. CRITICAL: Each individual post MUST be strictly under 400 characters so I can easily copy and paste them as single messages. Number each post (1/10, 2/10, etc.) and include a strong hook in the first post.", 
     "Day 1: The Foundation - ICC Framework Decoded Part 1", "-n", "8be24334-4293-41e0-a87d-cd20e67349ae", "--no-wait"],
    shell=True
).decode()

task_id_match = re.findall(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', out)
if not task_id_match:
    print("Failed to get task ID:", out)
    exit(1)

task_id = task_id_match[0]
print(f"Task started: {task_id}")

while True:
    status = subprocess.check_output(["nlm", "artifact", "list", "-n", "8be24334-4293-41e0-a87d-cd20e67349ae"], shell=True).decode()
    relevant = [l for l in status.splitlines() if task_id[:8] in l]
    if relevant and any("complete" in l.lower() or "ready" in l.lower() for l in relevant):
        print("Task completed!")
        break
    time.sleep(10)
    print("Waiting...")

print("Downloading...")
subprocess.run(["nlm", "download", "report", "./studios/day-1/day1_twitter.md", "-a", task_id, "--force"], shell=True)
print("Done!")
