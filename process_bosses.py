import json
import re

# Read compass_bosses_raw.ts
with open('data/compass_bosses_raw.ts', 'r', encoding='utf-8') as f:
    ts_data = f.read()

m = re.search(r'export const BOSSES:.*?=\s*(\[.*?\]);', ts_data, re.DOTALL)
bosses_raw = json.loads(re.sub(r',\s*\]', ']', m.group(1)))

# Load legacy conv
with open('world-map-legacy-conv.ts', 'r', encoding='utf-8') as f:
    ts_conv = f.read()
m2 = re.search(r'export const WORLD_MAP_LEGACY_CONV:.*?=\s*(\[.*?\]);', ts_conv, re.DOTALL)
legacy_conv = json.loads(re.sub(r',\s*\]', ']', m2.group(1)))
legacy_by_block = {}
for c in legacy_conv:
    src = c['srcMapId']
    if src not in legacy_by_block:
        legacy_by_block[src] = []
    legacy_by_block[src].append(c)

OFFSET_X = -7168
OFFSET_Y = 16640

def dungeon_block(map_id):
    m = re.match(r'^(m\d\d_\d\d_\d\d)_', map_id)
    return m.group(1) if m else None

def dungeon_marker_to_master(map_id, x, z):
    block = dungeon_block(map_id)
    if not block: return None
    points = legacy_by_block.get(block)
    if not points: return None
    best = None
    best_dist = float('inf')
    for p in points:
        dx = x - p['srcX']
        dz = z - p['srcZ']
        d = dx*dx + dz*dz
        if d < best_dist:
            best_dist = d
            best = p
    if not best: return None
    world_x = x + best['addX']
    world_z = z + best['addZ']
    return {
        'master': best['master'],
        'px': world_x + OFFSET_X,
        'py': OFFSET_Y - world_z
    }

def marker_to_master(map_id, x, z):
    m = re.match(r'^m(60|61)_(\d+)_(\d+)_\d(\d)$', map_id)
    if m:
        prefix = m.group(1)
        tier = int(m.group(4))
        if tier > 2: return None
        size = 256 * (2 ** tier)
        col = int(m.group(2))
        row = int(m.group(3))
        world_x = col * size + size / 2.0 + x
        world_z = row * size + size / 2.0 + z
        master = 'M00' if prefix == '60' else 'M10'
        return {
            'master': master,
            'px': world_x + OFFSET_X,
            'py': OFFSET_Y - world_z
        }
    return dungeon_marker_to_master(map_id, x, z)

W_M00 = 9728.0
H_M00 = 9216.0
W_M10 = 4879.0
H_M10 = 5940.0
SCALE_M10 = 1.124
OFF_X_M10 = -3704.0
OFF_Y_M10 = -2722.0

boss_list = []
seen = set()

for b in bosses_raw:
    name = b.get('name')
    if not name or name in seen:
        continue
    
    proj = marker_to_master(b['mapId'], b['x'], b['z'])
    if not proj:
        continue

    master = proj['master']
    px = proj['px']
    py = proj['py']

    if master == 'M00':
        mx = round((px / W_M00) * 100.0, 2)
        my = round((py / H_M00) * 100.0, 2)
        realm = 'The Lands Between'
    elif master == 'M10':
        img_x = px * SCALE_M10 + OFF_X_M10
        img_y = py * SCALE_M10 + OFF_Y_M10
        mx = round((img_x / W_M10) * 100.0, 2)
        my = round((img_y / H_M10) * 100.0, 2)
        realm = 'Shadow of the Erdtree'
    else:
        # M01 underground
        mx = round((px / W_M00) * 100.0, 2)
        my = round((py / H_M00) * 100.0, 2)
        realm = 'The Lands Between'

    if 0 <= mx <= 100 and 0 <= my <= 100:
        seen.add(name)
        boss_list.append({
            'id': f"boss-{b['defeatFlagId']}",
            'name': name,
            'realm': realm,
            'map_coords': {'x': mx, 'y': my},
            'runes': b.get('runes', 0),
            'type': 'Boss',
            'defeated': False
        })

print(f"Total bosses projected: {len(boss_list)}")
with open('data/bosses.json', 'w', encoding='utf-8') as f:
    json.dump(boss_list, f, ensure_ascii=False, indent=2)

print("Saved data/bosses.json successfully!")
