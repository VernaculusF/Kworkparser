import sys

# Заменяем pick на reword для коммитов с кракозябрами (первые 6 из 8)
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    lines = f.readlines()

# reword первые 6 коммитов (те что с кракозябрами)
result = []
for i, line in enumerate(lines):
    if i < 6 and line.startswith('pick '):
        result.append('reword ' + line[5:])
    else:
        result.append(line)

with open(sys.argv[1], 'w', encoding='utf-8') as f:
    f.writelines(result)
