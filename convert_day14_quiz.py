import json, pathlib, re

raw = pathlib.Path('studios/day-14/day14_quiz_raw.json').read_text(encoding='utf-8')
idx = raw.find('{')
data = json.loads(raw[idx:] if idx >= 0 else raw)

md = '# ' + data.get('title', 'Trading Quiz') + '\n\n'
for i, q in enumerate(data.get('questions', []), 1):
    md += f'## Question {i}\n'
    md += q['question'] + '\n\n'
    for opt in q.get('answerOptions', []):
        mark = 'x' if opt.get('isCorrect') else ' '
        md += f'- [{mark}] ' + opt['text'] + '\n'
    md += '\n'
    if 'hint' in q:
        md += '**Hint:** ' + q['hint'] + '\n\n'

pathlib.Path('studios/day-14/day14_quiz.md').write_text(md, encoding='utf-8')
print(f'Quiz converted: {len(data.get("questions",[]))} questions -> day14_quiz.md')
