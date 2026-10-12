import urllib.request
import json
from collections import Counter

url = 'https://raw.githubusercontent.com/EthanShoeDev/elden-ring-compass/main/packages/data/src/generated/markers.ts'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
print('Fetching markers.ts...')

markers = []
with urllib.request.urlopen(req) as resp:
    for line_bytes in resp:
        line = line_bytes.decode('utf-8').strip()
        if line.endswith(','):
            line = line[:-1]
        if line.startswith('{') and line.endswith('}'):
            try:
                markers.append(json.loads(line))
            except Exception:
                pass

print(f'Parsed {len(markers)} markers.')
cats = Counter(m.get('category') for m in markers)
print('Categories:', cats)
kinds = Counter(m.get('kind') for m in markers)
print('Kinds:', kinds)
