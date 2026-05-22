import json
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main():
    print("Fetching artifact list...")
    res = subprocess.run(
        ["python", "-m", "notebooklm", "artifact", "list", "-n", "8be24334-4293-41e0-a87d-cd20e67349ae", "--json"],
        capture_output=True, text=True
    )
    if res.returncode != 0:
        print("Failed to run artifact list:", res.stderr)
        return
        
    try:
        data = json.loads(res.stdout)
    except Exception as e:
        print("Failed to parse JSON:", e)
        print("Stdout:", res.stdout[:500])
        return

    artifacts = data.get("artifacts", [])
    print(f"Total artifacts: {len(artifacts)}")
    
    # Filter for today's date
    print("\n--- Recent Artifacts (created today/yesterday) ---")
    count = 0
    for a in artifacts:
        created = a.get("created_at", "")
        # Check if created in May 2026 or similar (recent)
        if "2026-05-2" in created or "2026-05-22" in created:
            print(f"ID: {a['id'][:8]} | Type: {a['type']:<20} | Status: {a['status']:<12} | Title: {a['title']}")
            count += 1
            
    print(f"Listed {count} recent artifacts.")

if __name__ == "__main__":
    main()
