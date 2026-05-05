import markdown
import os

for d in ['9', '10']:
    md_file = f'studios/day-{d}/day{d}_slides.md'
    html_file = f'studios/day-{d}/day{d}_slides.html'
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            md_text = f.read()
        
        # Replace the literal page breaks with horizontal rules for better flow
        md_text = md_text.replace('---', '\n---\n')
        
        html = markdown.markdown(md_text)
        
        html_content = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Day {d} Slides</title>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&display=swap" rel="stylesheet">
<style>
  body {{
    font-family: 'Outfit', sans-serif;
    background-color: #07090f;
    color: #e2e8f0;
    padding: 40px;
    line-height: 1.6;
    max-width: 800px;
    margin: 0 auto;
  }}
  h1, h2, h3 {{
    color: #38bdf8;
    margin-top: 40px;
  }}
  h1 {{
    border-bottom: 2px solid rgba(56, 189, 248, 0.2);
    padding-bottom: 10px;
    font-size: 2.5em;
  }}
  h2 {{ font-size: 1.8em; }}
  hr {{
    border: 0;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    margin: 50px 0;
  }}
  ul {{ margin-top: 15px; font-size: 1.1em; }}
  li {{ margin-bottom: 12px; }}
  strong {{ color: #f8fafc; font-weight: 800; }}
</style>
</head>
<body>
{html}
</body>
</html>'''
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f'Created {html_file}')
    except Exception as e:
        print(f"Error on Day {d}: {e}")
