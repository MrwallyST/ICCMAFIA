import sys, re

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main():
    content = open('index.html', 'r', encoding='utf-8').read()
    
    # Let's find lines with DAYS_DATA
    for i, line in enumerate(content.splitlines(), 1):
        if "DAYS_DATA" in line:
            # truncate long lines (like the declaration of DAYS_DATA)
            if len(line) > 120:
                print(f"Line {i}: {line[:120]}... [truncated]")
            else:
                print(f"Line {i}: {line}")
                
    # Let's find JavaScript functions that deal with rendering days
    print("\n--- JavaScript functions ---")
    matches = re.finditer(r'function\s+\w+\(.*?\)\s*\{', content)
    for m in matches:
        start_idx = m.start()
        # print the matched function signature and a bit of context
        print(content[start_idx:start_idx+150].replace('\n', ' '))

if __name__ == "__main__":
    main()
