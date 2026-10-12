import json

with open('data/graces.json', 'r', encoding='utf-8') as f:
    graces_old = json.load(f)
with open('data/compass_graces.json', 'r', encoding='utf-8') as f:
    graces_comp = json.load(f)

def clean(s):
    return s.lower().replace("'", "").replace(",", "").replace("-", " ").strip()

comp_map = {clean(g.get('displayName', '')): g for g in graces_comp}

matched = 0
unmatched_old = []
for g in graces_old:
    name = clean(g['name'])
    if name in comp_map:
        matched += 1
    else:
        # Partial match
        found = any(name in cn or cn in name for cn in comp_map)
        if found:
            matched += 1
        else:
            unmatched_old.append(g['name'])

print(f"Total old graces: {len(graces_old)}, Matched: {matched}")
print(f"Unmatched old ({len(unmatched_old)}):", unmatched_old)
