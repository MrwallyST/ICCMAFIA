import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main():
    content = open('index.html', 'r', encoding='utf-8').read()
    
    # Search for days-container
    idx = content.find("id=\"days-container\"")
    if idx >= 0:
        print(content[idx-500:idx+1500])
    else:
        print("days-container not found")

if __name__ == "__main__":
    main()
