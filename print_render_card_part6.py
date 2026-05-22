import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def main():
    content = open('index.html', 'r', encoding='utf-8').read()
    
    # Let's find renderCard function part 6
    start_idx = content.find("return `\n      <div class=\"day-card\" id=\"day-${day.day}\">")
    if start_idx >= 0:
        print(content[start_idx:start_idx+1500])
    else:
        print("return div class=day-card not found")

if __name__ == "__main__":
    main()
