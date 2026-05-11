import json

with open('studios/day-13/day13_quiz.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

md_content = '# ' + data.get('title', 'Trading Quiz') + '\n\n'

for i, q in enumerate(data['questions'], 1):
    md_content += f'## Question {i}\n'
    md_content += q['question'] + '\n\n'
    for opt in q['answerOptions']:
        mark = 'x' if opt['isCorrect'] else ' '
        md_content += f'- [{mark}] {opt["text"]}\n'
    md_content += '\n'
    if 'hint' in q:
        md_content += f'**Hint:** {q["hint"]}\n\n'

with open('studios/day-13/day13_quiz.md', 'w', encoding='utf-8') as f:
    f.write(md_content)
