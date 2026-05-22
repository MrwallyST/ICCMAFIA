import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main():
    content = open('index.html', 'r', encoding='utf-8').read()
    
    # Let's find renderCard function
    start_idx = content.find("function renderCard(day)")
    if start_idx >= 0:
        print(content[start_idx:start_idx+1800])
    else:
        print("function renderCard(day) not found")

if __name__ == "__main__":
    main()
