import json
import re

# Load existing graces
with open('data/graces.json', 'r', encoding='utf-8') as f:
    graces_old = json.load(f)

# Load compass graces
with open('data/compass_graces.json', 'r', encoding='utf-8') as f:
    graces_comp = json.load(f)

# Load legacy conv
with open('world-map-legacy-conv.ts', 'r', encoding='utf-8') as f:
    ts_data = f.read()

m = re.search(r'export const WORLD_MAP_LEGACY_CONV:.*?=\s*(\[.*?\]);', ts_data, re.DOTALL)
legacy_conv = json.loads(re.sub(r',\s*\]', ']', m.group(1)))

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

def clean(s):
    return s.lower().replace("'", "").replace(",", "").replace("-", " ").strip()

# Build compass grace map by clean name
comp_lookup = {}
for g in graces_comp:
    disp = g.get('displayName') or g.get('name')
    comp_lookup[clean(disp)] = g

# Also special manual aliases if needed
aliases = {
    clean('Beside the Crater-Pocked  Glade'): clean('Beside the Crater-Pocked Glade'),
    clean("Giants' Mountaintops Catacombs"): clean("Giant-Conquering Hero's Grave")
}

# Image dimensions
# Lands Between (M00): 9728 x 9216
W_M00 = 9728.0
H_M00 = 9216.0

# Shadow Realm (M10): 4879 x 5940
W_M10 = 4879.0
H_M10 = 5940.0
SCALE_M10 = 1.124
OFF_X_M10 = -3704.0
OFF_Y_M10 = -2722.0

calibrated_count = 0
for g in graces_old:
    name_clean = clean(g['name'])
    if name_clean in aliases:
        name_clean = aliases[name_clean]

    # Special case: Roundtable Hold
    if 'roundtable' in g.get('region', '').lower() or 'roundtable' in g['name'].lower():
        g['map_coords'] = {'x': 8.5, 'y': 88.0}
        calibrated_count += 1
        continue

    cg = comp_lookup.get(name_clean)
    if not cg:
        # Try substring search
        for k, v in comp_lookup.items():
            if name_clean == k or name_clean in k or k in name_clean:
                cg = v
                break

    if cg:
        proj = marker_to_master(cg['mapId'], cg['x'], cg['z'])
        if proj:
            master = proj['master']
            px = proj['px']
            py = proj['py']

            if master == 'M00':
                mx = round((px / W_M00) * 100.0, 2)
                my = round((py / H_M00) * 100.0, 2)
                g['map_coords'] = {'x': mx, 'y': my}
                g['master'] = 'M00'
                calibrated_count += 1
            elif master == 'M10':
                # DLC
                img_x = px * SCALE_M10 + OFF_X_M10
                img_y = py * SCALE_M10 + OFF_Y_M10
                mx = round((img_x / W_M10) * 100.0, 2)
                my = round((img_y / H_M10) * 100.0, 2)
                g['map_coords'] = {'x': mx, 'y': my}
                g['master'] = 'M10'
                calibrated_count += 1
            elif master == 'M01':
                # Underground - on M00 surface or underground
                mx = round((px / W_M00) * 100.0, 2)
                my = round((py / H_M00) * 100.0, 2)
                g['map_coords'] = {'x': mx, 'y': my}
                g['master'] = 'M01'
                calibrated_count += 1

print(f"Total graces: {len(graces_old)}, Calibrated with exact MSB coords: {calibrated_count}")

# Verify key graces in updated list
for g in graces_old:
    if g['name'] in ['The First Step', 'Church of Elleh', 'Gatefront', 'Godrick the Grafted', 'Rennala, Queen of the Full Moon', 'Castle Morne Rampart']:
        print(f"  {g['name']}: map_coords = {g['map_coords']}")

with open('data/graces.json', 'w', encoding='utf-8') as f:
    json.dump(graces_old, f, ensure_ascii=False, indent=2)

print("Saved calibrated data/graces.json successfully!")
