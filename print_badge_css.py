import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main():
    content = open('index.html', 'r', encoding='utf-8').read()
    
    # Search for day-num-badge styling
    idx = content.find(".day-num-badge")
    if idx >= 0:
        print(content[idx:idx+1000])
    else:
        print("styling not found")

if __name__ == "__main__":
    main()
