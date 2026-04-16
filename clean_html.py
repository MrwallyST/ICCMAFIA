import re

html_path = r"c:\Users\cesar\Documents\New folder\TradesBySci\index.html"
with open(html_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Remove standard Spanish elements
text = re.sub(r'<span class="es-text"[^>]*>.*?</span>', '', text)
text = re.sub(r'<div class="card-title es-title"[^>]*>.*?</div>', '', text)
text = re.sub(r'<h2 class="es-title"[^>]*>.*?</h2>', '', text)
text = re.sub(r'<p class="es-title"[^>]*>.*?</p>', '', text)
text = re.sub(r'<span class="es-title"[^>]*>.*?</span>', '', text)

# 2. Strip remaining wrapper classes
text = text.replace('class="en-text"', '')
text = text.replace('class="en-title"', '')
text = text.replace('class="card-title en-title"', 'class="card-title"')
text = text.replace('class="  "', ' ')
text = text.replace('class=""', '')

# 3. Clean up rBtn logic
# We change the function signatures
text = re.sub(r'function rBtn\(has, icon, enTitle, esTitle, enDesc, esDesc, onclickStr\)', 'function rBtn(has, icon, title, desc, onclickStr)', text)
text = re.sub(r'function rLink\(has, icon, enTitle, esTitle, enDesc, esDesc, href\)', 'function rLink(has, icon, title, desc, href)', text)

# Inside the functions, replace the complex spans with simple ones
text = re.sub(r'<span class="resource-title">.*?\$\{enTitle\}.*?</span>', r'<span class="resource-title">${title}</span>', text, flags=re.DOTALL)
text = re.sub(r'<span class="resource-desc">.*?\$\{enDesc\}.*?</span>', r'<span class="resource-desc">${desc}</span>', text, flags=re.DOTALL)
text = re.sub(r'<span class="resource-desc"[^>]*>.*?\$\{enDesc\}.*?</span>', r'<span class="resource-desc" style="color:var(--muted);">${desc}</span>', text, flags=re.DOTALL)
text = re.sub(r'<span class="resource-title">.*?\$\{enTitle\}.*?</span>', r'<span class="resource-title">${title}</span>', text, flags=re.DOTALL)

# Let's fix the calls to rBtn manually via regex. They look like:
# ${rBtn(hasStudy, '📖', 'Study Guide', 'Guía de Estudio', 'Interactive Report', 'Reporte Interactivo', `openResourceModal(...)`)}
# We want to keep arg 1, 2, 3, 5, 7.
text = re.sub(
    r'\$\{rBtn\(([^,]+),\s*(\'[^\']+\'),\s*(\'[^\']+\'),\s*(\'[^\']+\'),\s*(\'[^\']+\'),\s*(\'[^\']+\'),\s*(`[^`]+`)\)\}',
    r'${rBtn(\1, \2, \3, \5, \7)}',
    text
)

# 4. Clean up other specific leftovers
# `placeholder="${globalLang==='es'?'Escribe tus notas para este día...':'Write your notes for this day...'}"`
# => `placeholder="Write your notes for this day..."`
text = re.sub(r'placeholder="\$\{globalLang===\'es\'\?\'[^\']+\':\'([^\']+)\'\}"', r'placeholder="\1"', text)

# `data-avail-langs="${availLangs.join(',')}"` and the unused availLangs reference
text = re.sub(r' data-avail-langs="\$\{availLangs\.join\(\',\',?\)\}"', '', text)

with open(html_path, "w", encoding="utf-8") as f:
    f.write(text)
