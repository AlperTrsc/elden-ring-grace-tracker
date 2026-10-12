import urllib.request
import json
from collections import Counter

url = 'https://raw.githubusercontent.com/EthanShoeDev/elden-ring-compass/main/packages/data/src/generated/markers.ts'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
print('Streaming markers.ts...')

markers = []
with urllib.request.urlopen(req) as resp:
    for line_bytes in resp:
        line = line_bytes.decode('utf-8').strip()
        if line.startswith('{') and line.endswith('},'):
            item_json = line[:-1]
            try:
                markers.append(json.loads(item_json))
            except Exception:
                pass
        elif line.startswith('{') and line.endswith('}'):
            try:
                markers.append(json.loads(line))
            except Exception:
                pass

print(f'Successfully parsed {len(markers)} markers!')
cats = Counter(m.get('category') for m in markers)
print('Categories:', dict(cats))

graces = [m for m in markers if m.get('category') == 'grace']
print(f'Graces found: {len(graces)}')

# Save graces markers to json
with open('data/compass_graces.json', 'w', encoding='utf-8') as f:
    json.dump(graces, f, ensure_ascii=False, indent=2)

# Also save bosses and dungeons
bosses = [m for m in markers if m.get('category') == 'boss']
with open('data/compass_bosses.json', 'w', encoding='utf-8') as f:
    json.dump(bosses, f, ensure_ascii=False, indent=2)

print('Saved data/compass_graces.json and data/compass_bosses.json!')
