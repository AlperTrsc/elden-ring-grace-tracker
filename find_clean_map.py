import urllib.request
import json
import re

# Search GitHub repositories for clean map images
headers = {'User-Agent': 'Mozilla/5.0'}

repos = [
    'elden-ring-compass/web',
    'elpwc/EldenRingOnlineMap',
    'NikVince/nightreign-map-router',
    '251dream/elden-ring-crud-boss-tracker',
    'F3T1W/EldenTracker'
]

for repo in repos:
    try:
        url = f'https://api.github.com/repos/{repo}/git/trees/main?recursive=1'
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            map_files = [f['path'] for f in data.get('tree', []) if any(k in f['path'].lower() for k in ['map', 'world']) and any(f['path'].lower().endswith(ext) for ext in ['.png', '.jpg', '.webp'])]
            print(f"[{repo}] map files:", map_files[:10])
    except Exception as e:
        # Try master branch
        try:
            url = f'https://api.github.com/repos/{repo}/git/trees/master?recursive=1'
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read())
                map_files = [f['path'] for f in data.get('tree', []) if any(k in f['path'].lower() for k in ['map', 'world']) and any(f['path'].lower().endswith(ext) for ext in ['.png', '.jpg', '.webp'])]
                print(f"[{repo}] map files (master):", map_files[:10])
        except Exception as e2:
            print(f"[{repo}] Err:", e2)
