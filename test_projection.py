import json
import re

# Load compass graces
with open('data/compass_graces.json', 'r', encoding='utf-8') as f:
    graces = json.load(f)

# Load legacy conv
with open('world-map-legacy-conv.ts', 'r', encoding='utf-8') as f:
    ts_data = f.read()

# Extract json array from ts_data
m = re.search(r'export const WORLD_MAP_LEGACY_CONV:.*?=\s*(\[.*?\]);', ts_data, re.DOTALL)
json_str = m.group(1)
json_str = re.sub(r',\s*\]', ']', json_str)
legacy_conv = json.loads(json_str)

# Group legacy conv by srcMapId
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
    if not block:
        return None
    points = legacy_by_block.get(block)
    if not points:
        return None
    best = None
    best_dist = float('inf')
    for p in points:
        dx = x - p['srcX']
        dz = z - p['srcZ']
        d = dx*dx + dz*dz
        if d < best_dist:
            best_dist = d
            best = p
    if not best:
        return None
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
        if tier > 2:
            return None
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

projected = []
for g in graces:
    res = marker_to_master(g['mapId'], g['x'], g['z'])
    if res:
        projected.append({
            'name': g.get('displayName') or g.get('name'),
            'mapId': g['mapId'],
            'master': res['master'],
            'px': res['px'],
            'py': res['py']
        })

print(f'Total graces: {len(graces)}, successfully projected: {len(projected)}')

# Let's inspect some key M00 graces
m00 = [p for p in projected if p['master'] == 'M00']
print(f'M00 graces: {len(m00)}')

key_names = ['The First Step', 'Church of Elleh', 'Gatefront', 'Castle Morne Rampart', 'Academy Gate Town', 'Main Academy Gate', 'Raya Lucaria Grand Library', 'Erdtree Sanctuary', 'Beside the Greatbridge']
for p in m00:
    for k in key_names:
        if k.lower() in p['name'].lower():
            print(f"{p['name']}: px={p['px']:.1f}, py={p['py']:.1f}")

# Min and max px, py in M00
min_px = min(p['px'] for p in m00)
max_px = max(p['px'] for p in m00)
min_py = min(p['py'] for p in m00)
max_py = max(p['py'] for p in m00)
print(f'M00 bounds: px=[{min_px:.1f}, {max_px:.1f}], py=[{min_py:.1f}, {max_py:.1f}]')
print(f'Span: width={max_px - min_px:.1f}, height={max_py - min_py:.1f}')
