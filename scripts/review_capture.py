"""Print bounded, line-numbered visible evidence from a saved collector capture.

Read-only. Usage: review_capture.py capture.json index [needle [context_lines]]
No network, seller selection or repository mutation.
"""
import json
import sys
from pathlib import Path

items = json.loads(Path(sys.argv[1]).read_text())
item = items[int(sys.argv[2])]
print('SOURCE:', item['url'], '\nHTTP:', item.get('http'), '\nTIME:', item.get('retrieved_at'))
print('TITLE:', item.get('title'), '\nERROR:', item.get('error'))
lines = item.get('text', '').splitlines()
needle = sys.argv[3] if len(sys.argv) > 3 else ''
context = int(sys.argv[4]) if len(sys.argv) > 4 else 25
indices = [i for i, line in enumerate(lines) if needle.casefold() in line.casefold()] if needle else [0]
selected = set()
for index in indices[:12]:
    selected.update(range(max(0, index-context), min(len(lines), index+context+1)))
for index in sorted(selected):
    print(f'{index+1}: {lines[index]}')
print(f'Matching anchors: {len(indices)}; visible text lines: {len(lines)}')
