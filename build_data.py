import urllib.request
import json
import re
import os
import hashlib

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

# Turkish translations for regions
REGION_TR_MAP = {
    'Roundtable Hold': 'Yuvarlak Masa Teşkilatı',
    'Limgrave': 'Limgrave',
    'Stranded Graveyard': 'Terk Edilmiş Mezarlık',
    'Stormhill': 'Fırtına Tepesi',
    'Weeping Peninsula': 'Ağlayan Yarımada',
    'Stormveil Castle': 'Fırtına Perdesi Kalesi',
    'Liurnia of the Lakes': 'Liurnia Gölleri',
    'Bellum Highway': 'Bellum Yolu',
    'Ruin-Strewn Precipice': 'Harabe Saçılmış Uçurum',
    'Moonlight Altar': 'Ayışığı Sunağı',
    'Academy of Raya Lucaria': 'Raya Lucaria Akademisi',
    'Altus Plateau': 'Altus Platosu',
    'Mt. Gelmir': 'Gelmir Dağı',
    'Capital Outskirts': 'Başkent Varoşları',
    'Volcano Manor': 'Volkan Konağı',
    'Leyndell, Royal Capital': 'Leyndell, Kraliyet Başkenti',
    'Subterranean Shunning-Grounds': 'Yeraltı Dışlanmışlar Bölgesi',
    'Leyndell, Ashen Capital': 'Leyndell, Kül Başkent',
    'Caelid': 'Caelid',
    'Swamp of Aeonia': 'Aeonia Bataklığı',
    "Greyoll's Dragonbarrow": "Greyoll'un Ejderha Höyüğü",
    'Mountaintops of the Giants': 'Devler Zirvesi',
    'Forbidden Lands': 'Yasak Topraklar',
    'Flame Peak': 'Alev Tepesi',
    'Consecrated Snowfield': 'Kutsanmış Kar Alanı',
    "Miquella's Haligtree": "Miquella'nın Haligtree'si",
    "Elphael, Brace of the Haligtree": "Elphael, Haligtree Kalesi",
    'Ainsel River': 'Ainsel Nehri',
    'Ainsel River Main': 'Ana Ainsel Nehri',
    'Lake of Rot': 'Çürüme Gölü',
    'Siofra River': 'Siofra Nehri',
    'Nokron, Eternal City': 'Nokron, Ebedi Şehir',
    'Mohgwyn Palace': 'Mohgwyn Sarayı',
    'Deeproot Depths': 'Derinkök Derinlikleri',
    'Crumbling Farum Azula': 'Ufalanan Farum Azula',
    # DLC Regions
    'Gravesite Plain': 'Mezarlık Ovası',
    'Castle Ensis': 'Ensis Kalesi',
    'Belurat, Tower Settlement': 'Belurat, Kule Yerleşimi',
    'Scadu Altus': 'Scadu Altus',
    'Shadow Keep': 'Gölge Kalesi',
    'Ancient Ruins of Rauh': 'Antik Rauh Harabeleri',
    'Rauh Base': 'Rauh Tabanı',
    'Cerulean Coast': 'Gök Mavisi Kıyı',
    'Charo\'s Hidden Grave': "Charo'nun Gizli Mezarı",
    'Stone Coffin Fissure': 'Taş Tabut Yarığı',
    'Foot of the Jagged Peak': 'Sivri Zirve Eteği',
    'Jagged Peak': 'Sivri Zirve',
    'Abyssal Woods': 'Uçurum Ormanları',
    'Hinterland': 'İç Topraklar',
    'Enir-Ilim': 'Enir-Ilim',
    "Recluses' River": "İnzivaya Çekilenler Nehri",
    'Scadutree Base': 'Scadutree Tabanı',
    'Shadow Realm': 'Gölge Diyarı'
}

# Anchor positions (normalized 0-100) for map coordinates
REGION_ANCHORS = {
    # The Lands Between
    'Roundtable Hold': (10, 85),
    'Stranded Graveyard': (48, 77),
    'Limgrave': (52, 73),
    'Stormhill': (44, 63),
    'Weeping Peninsula': (51, 88),
    'Stormveil Castle': (41, 56),
    'Liurnia of the Lakes': (36, 46),
    'Academy of Raya Lucaria': (35, 42),
    'Moonlight Altar': (27, 53),
    'Bellum Highway': (40, 31),
    'Ruin-Strewn Precipice': (39, 26),
    'Caelid': (73, 67),
    'Swamp of Aeonia': (72, 60),
    "Greyoll's Dragonbarrow": (77, 47),
    'Altus Plateau': (50, 30),
    'Mt. Gelmir': (36, 22),
    'Volcano Manor': (38, 19),
    'Capital Outskirts': (58, 28),
    'Leyndell, Royal Capital': (60, 26),
    'Leyndell, Ashen Capital': (61, 27),
    'Subterranean Shunning-Grounds': (59, 32),
    'Forbidden Lands': (67, 28),
    'Mountaintops of the Giants': (75, 19),
    'Flame Peak': (83, 27),
    'Consecrated Snowfield': (62, 16),
    "Miquella's Haligtree": (65, 7),
    "Elphael, Brace of the Haligtree": (67, 5),
    'Crumbling Farum Azula': (92, 45),
    'Siofra River': (55, 78),
    'Nokron, Eternal City': (57, 68),
    'Mohgwyn Palace': (65, 82),
    'Ainsel River': (33, 58),
    'Ainsel River Main': (32, 51),
    'Lake of Rot': (28, 62),
    'Deeproot Depths': (48, 42),
    
    # Shadow Realm DLC
    'Gravesite Plain': (34, 70),
    'Belurat, Tower Settlement': (24, 62),
    'Castle Ensis': (47, 52),
    'Scadu Altus': (54, 38),
    'Shadow Keep': (52, 28),
    'Ancient Ruins of Rauh': (23, 30),
    'Rauh Base': (28, 42),
    'Cerulean Coast': (43, 86),
    "Charo's Hidden Grave": (36, 82),
    'Stone Coffin Fissure': (46, 93),
    'Foot of the Jagged Peak': (68, 68),
    'Jagged Peak': (82, 75),
    'Abyssal Woods': (70, 55),
    'Hinterland': (75, 20),
    'Enir-Ilim': (38, 22),
    "Recluses' River": (63, 46),
    'Scadutree Base': (58, 16),
    'Shadow Realm': (50, 50)
}

DLC_MAPPINGS = {
    'Ancient Ruins Base': ('Ancient Ruins of Rauh', 'Rauh Base'),
    'Ancient Ruins, Grand Stairway': ('Ancient Ruins of Rauh', 'Ancient Ruins of Rauh'),
    'Behind the Fort of Reprimand': ('Scadu Altus', 'Scadu Altus'),
    'Belurat Gaol': ('Gravesite Plain', 'Belurat, Tower Settlement'),
    'Bonny Gaol': ('Scadu Altus', 'Scadu Altus'),
    'Bonny Village': ('Scadu Altus', 'Scadu Altus'),
    'Bridge Leading to the Village': ('Scadu Altus', 'Scadu Altus'),
    'Castle Ensis Checkpoint': ('Castle Ensis', 'Castle Ensis'),
    'Castle Front': ('Gravesite Plain', 'Gravesite Plain'),
    'Castle Watering Hole': ("Recluses' River", "Recluses' River"),
    "Castle-Lord's Chamber": ('Castle Ensis', 'Castle Ensis'),
    'Cathedral of Manus Metyr': ('Scadu Altus', 'Scadu Altus'),
    'Cerulean Coast Cross': ('Cerulean Coast', 'Cerulean Coast'),
    'Cerulean Coast West': ('Cerulean Coast', 'Cerulean Coast'),
    'Church District Entrance': ('Shadow Keep', 'Shadow Keep'),
    'Church District Highroad': ('Scadu Altus', 'Scadu Altus'),
    'Church Ruins': ('Scadu Altus', 'Scadu Altus'),
    'Church of the Bud': ('Ancient Ruins of Rauh', 'Ancient Ruins of Rauh'),
    'Church of the Bud, Main Entrance': ('Ancient Ruins of Rauh', 'Ancient Ruins of Rauh'),
    'Cleansing Chamber Anteroom': ('Enir-Ilim', 'Enir-Ilim'),
    'Cliffroad Terminus': ('Gravesite Plain', 'Gravesite Plain'),
    'Dark Chamber Entrance': ('Shadow Keep', 'Shadow Keep'),
    'Darklight Catacombs': ("Recluses' River", 'Abyssal Woods'),
    'Discussion Chamber': ('Shadow Keep', 'Shadow Keep'),
    'Divided Falls': ("Recluses' River", "Recluses' River"),
    'Divine Gate Front Staircase': ('Enir-Ilim', 'Enir-Ilim'),
    "Dragon's Pit": ('Gravesite Plain', 'Gravesite Plain'),
    "Dragon's Pit Terminus": ('Foot of the Jagged Peak', 'Foot of the Jagged Peak'),
    'Ellac River Cave': ('Gravesite Plain', 'Gravesite Plain'),
    'Ellac River Downstream': ('Gravesite Plain', 'Gravesite Plain'),
    'Enir-Ilim: Outer Wall': ('Enir-Ilim', 'Enir-Ilim'),
    'Ensis Moongazing Grounds': ('Castle Ensis', 'Castle Ensis'),
    'Finger Birthing Grounds': ('Hinterland', 'Hinterland'),
    'Finger Ruins of Rhia': ('Cerulean Coast', 'Cerulean Coast'),
    'Fingerstone Hill': ('Hinterland', 'Hinterland'),
    'First Rise': ('Enir-Ilim', 'Enir-Ilim'),
    'Fissure Cross': ('Stone Coffin Fissure', 'Stone Coffin Fissure'),
    'Fissure Depths': ('Stone Coffin Fissure', 'Stone Coffin Fissure'),
    'Fissure Waypoint': ('Stone Coffin Fissure', 'Stone Coffin Fissure'),
    'Fog Rift Catacombs': ('Gravesite Plain', 'Gravesite Plain'),
    'Forsaken Graveyard': ('Abyssal Woods', 'Abyssal Woods'),
    'Fort of Reprimand': ('Scadu Altus', 'Scadu Altus'),
    'Garden of Deep Purple': ('Stone Coffin Fissure', 'Stone Coffin Fissure'),
    'Gate of Divinity': ('Enir-Ilim', 'Enir-Ilim'),
    'Greatbridge, North': ('Gravesite Plain', 'Gravesite Plain'),
    'Highroad Cross': ('Scadu Altus', 'Scadu Altus'),
    'Hinterland': ('Hinterland', 'Hinterland'),
    'Hinterland Bridge': ('Hinterland', 'Hinterland'),
    'Jagged Peak Mountainside': ('Jagged Peak', 'Jagged Peak'),
    'Jagged Peak Summit': ('Jagged Peak', 'Jagged Peak'),
    "Lamenter's Gaol": ("Charo's Hidden Grave", "Charo's Hidden Grave"),
    'Main Gate Cross': ('Gravesite Plain', 'Gravesite Plain'),
    'Main Gate Plaza': ('Shadow Keep', 'Shadow Keep'),
    'Manse Hall': ('Abyssal Woods', 'Abyssal Woods'),
    "Messmer's Dark Chamber": ('Shadow Keep', 'Shadow Keep'),
    "Midra's Library": ('Abyssal Woods', 'Abyssal Woods'),
    'Moorth Highway, South': ('Scadu Altus', 'Scadu Altus'),
    'Moorth Ruins': ('Scadu Altus', 'Scadu Altus'),
    'Pillar Path Cross': ('Gravesite Plain', 'Gravesite Plain'),
    'Pillar Path Waypoint': ('Gravesite Plain', 'Gravesite Plain'),
    'Rauh Ancient Ruins, East': ('Ancient Ruins of Rauh', 'Ancient Ruins of Rauh'),
    'Rauh Ancient Ruins, West': ('Ancient Ruins of Rauh', 'Ancient Ruins of Rauh'),
    'Ravine North': ('Rauh Base', 'Rauh Base'),
    "Recluses' River Downstream": ("Recluses' River", "Recluses' River"),
    "Recluses' River Upstream": ("Recluses' River", "Recluses' River"),
    'Rest of the Dread Dragon': ('Foot of the Jagged Peak', 'Foot of the Jagged Peak'),
    'Rivermouth Cave': ('Gravesite Plain', 'Gravesite Plain'),
    'Ruined Forge Lava Intake': ('Gravesite Plain', 'Gravesite Plain'),
    'Ruined Forge of Starfall Past': ('Scadu Altus', 'Scadu Altus'),
    'Scadu Altus, West': ('Scadu Altus', 'Scadu Altus'),
    'Scadutree Base': ('Scadutree Base', 'Scadutree Base'),
    'Scaduview Cross': ('Scadu Altus', 'Scadu Altus'),
    'Scorched Ruins': ('Gravesite Plain', 'Gravesite Plain'),
    'Scorpion River Catacombs': ('Rauh Base', 'Rauh Base'),
    'Second Floor Chamber': ('Abyssal Woods', 'Abyssal Woods'),
    'Shadow Keep Main Gate': ('Shadow Keep', 'Shadow Keep'),
    'Shadow Keep, Back Gate': ('Shadow Keep', 'Shadow Keep'),
    'Small Private Altar': ('Belurat, Tower Settlement', 'Belurat, Tower Settlement'),
    'Spiral Rise': ('Enir-Ilim', 'Enir-Ilim'),
    'Stagefront': ('Belurat, Tower Settlement', 'Belurat, Tower Settlement'),
    'Storehouse, Back Section': ('Shadow Keep', 'Shadow Keep'),
    'Storehouse, First Floor': ('Shadow Keep', 'Shadow Keep'),
    'Storehouse, Fourth Floor': ('Shadow Keep', 'Shadow Keep'),
    'Storehouse, Loft': ('Shadow Keep', 'Shadow Keep'),
    'Storehouse, Seventh Floor': ('Shadow Keep', 'Shadow Keep'),
    'Sunken Chapel': ('Shadow Keep', 'Shadow Keep'),
    "Taylew's Ruined Forge": ('Rauh Base', 'Rauh Base'),
    'Temple Town Ruins': ('Rauh Base', 'Rauh Base'),
    'The Fissure': ('Stone Coffin Fissure', 'Stone Coffin Fissure'),
    'Theatre of the Divine Beast': ('Belurat, Tower Settlement', 'Belurat, Tower Settlement'),
    'Three-Path Cross': ('Gravesite Plain', 'Gravesite Plain'),
    'Tree-Worship Passage': ('Shadow Keep', 'Shadow Keep'),
    'Tree-Worship Sanctum': ('Shadow Keep', 'Shadow Keep'),
    'Viaduct Minor Tower': ('Ancient Ruins of Rauh', 'Ancient Ruins of Rauh'),
    'West Rampart': ('Shadow Keep', 'Shadow Keep'),
    'Woodland Trail': ('Abyssal Woods', 'Abyssal Woods'),
    # Extra DLC graces
    'Gravesite Plain': ('Gravesite Plain', 'Gravesite Plain'),
    "Castle-Lord's Checkpoint": ('Castle Ensis', 'Castle Ensis')
}

def determine_type(name, subregion, region):
    n_lower = name.lower()
    s_lower = subregion.lower()
    r_lower = region.lower()
    
    # Boss
    boss_keywords = [
        'margit', 'godrick', 'rennala', 'radahn', 'rykard', 'morgott', 'fire giant',
        'godfrey', 'radagon', 'elden beast', 'malenia', 'mohg', 'astel', 'maliketh',
        'dragonlord', 'loretta', 'messmer', 'midra', 'bayle', 'dancing lion', 'romina',
        'commander gaius', 'scadutree avatar', 'putrescent knight', 'rannal', 'placidusax'
    ]
    if any(k in n_lower for k in boss_keywords) or 'throne' in n_lower or 'divine gate' in n_lower:
        return 'Boss'
        
    # Underground
    if any(u in r_lower or u in s_lower for u in ['siofra', 'ainsel', 'lake of rot', 'deeproot', 'mohgwyn', 'subterranean']):
        return 'Underground'
        
    # Legacy Dungeons
    legacy = ['stormveil', 'raya lucaria', 'volcano manor', 'royal capital', 'ashen capital', 'haligtree', 'farum azula', 'shadow keep', 'belurat', 'enir-ilim', 'castle ensis']
    if any(l in r_lower or l in s_lower for l in legacy):
        return 'Legacy Dungeon'
        
    # Dungeon / Cave / Catacombs / Tunnel / Hero's Grave
    dungeon_keywords = ['catacombs', 'cave', 'tunnel', 'grave', 'gaol', 'ruins cellar', 'grotto', 'hideaway', 'mine', 'fissure', 'forge']
    if any(k in n_lower for k in dungeon_keywords):
        return 'Dungeon'
        
    return 'Overworld'

def generate_coords(region, subregion, name, idx_in_region, total_in_region):
    # Base anchor
    anchor = REGION_ANCHORS.get(subregion, REGION_ANCHORS.get(region, (50, 50)))
    
    # Pseudo-random reproducible deterministic jitter based on name
    h = int(hashlib.md5(f'{region}:{subregion}:{name}'.encode()).hexdigest()[:8], 16)
    angle = (h % 360) * (3.14159 / 180)
    # Distance from center: up to 3.5%
    dist = (h % 35) / 10.0
    
    # Spread out in a cluster
    dx = dist * 0.75 * (1 if (h % 2 == 0) else -1)
    dy = dist * 0.65 * (1 if ((h >> 4) % 2 == 0) else -1)
    
    x = max(2.0, min(98.0, anchor[0] + dx))
    y = max(2.0, min(98.0, anchor[1] + dy))
    return round(x, 2), round(y, 2)

def main():
    print("Fetching Sites of Grace from Fandom...")
    url = 'https://eldenring.fandom.com/api.php?action=parse&page=Sites_of_Grace&prop=wikitext&format=json'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    res = urllib.request.urlopen(req)
    data = json.loads(res.read())
    text = data['parse']['wikitext']['*']

    lines = text.split('\n')
    graces = []

    cur_realm = 'The Lands Between'
    cur_region = 'Roundtable Hold'
    cur_subregion = ''

    # 1. Process base game
    for line in lines:
        line = line.strip()
        if '==List of Sites of Grace in the Lands Between==' in line:
            cur_realm = 'The Lands Between'
            continue
        elif '==List of Sites of Grace in the Shadow Realm==' in line:
            break

        m_reg = re.match(r'^===\s*<u>\'\'\'\[\[([^\]\|]+)(?:\|[^\]]+)?\]\]\'\'\'</u>\s*===', line)
        if m_reg:
            cur_region = m_reg.group(1).strip()
            cur_subregion = ''
            continue

        m_sub = re.match(r'^====\s*\'\'\'\[\[([^\]\|]+)(?:\|[^\]]+)?\]\]\'\'\'\s*====', line)
        if not m_sub:
            m_sub = re.match(r'^====\s*\'\'\'([^\]\']+)\'\'\'\s*====', line)
        if m_sub:
            cur_subregion = m_sub.group(1).strip()
            continue

        m_gal = re.search(r'([^\|\n]+\.(?:png|jpg|webp))\s*\|\s*\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]', line, re.IGNORECASE)
        if m_gal:
            img = m_gal.group(1).strip()
            page = m_gal.group(2).strip()
            name = m_gal.group(3).strip() if m_gal.group(3) else page
            sub = cur_subregion if cur_subregion else cur_region
            graces.append({
                'name': name,
                'realm': 'The Lands Between',
                'region': cur_region,
                'subregion': sub,
                'image_file': img,
                'wiki_page': page
            })

    # 2. Process DLC graces
    idx_sr = text.find('==List of Sites of Grace in the Shadow Realm==')
    sr_text = text[idx_sr:]
    bullet_graces = [b[0] for b in re.findall(r'^\*\s*\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]', sr_text, re.MULTILINE)]
    
    # Also find DLC gallery items with images if available
    dlc_gallery_images = {}
    for match in re.finditer(r'([^\|\n]+\.(?:png|jpg|webp))\s*\|\s*\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]', sr_text, re.IGNORECASE):
        img_name = match.group(1).strip()
        p_name = match.group(2).strip()
        actual_name = match.group(3).strip() if match.group(3) else p_name
        dlc_gallery_images[actual_name] = img_name

    # Add DLC graces
    for dlc_name in bullet_graces:
        reg, sub = DLC_MAPPINGS.get(dlc_name, ('Shadow Realm', 'Shadow Realm'))
        graces.append({
            'name': dlc_name,
            'realm': 'Shadow of the Erdtree',
            'region': reg,
            'subregion': sub,
            'image_file': dlc_gallery_images.get(dlc_name, ''),
            'wiki_page': dlc_name
        })

    # Build final structured list
    final_graces = []
    seen_ids = set()

    for idx, g in enumerate(graces):
        base_slug = slugify(f"{g['realm']}-{g['region']}-{g['name']}")
        grace_id = base_slug
        count = 1
        while grace_id in seen_ids:
            grace_id = f"{base_slug}-{count}"
            count += 1
        seen_ids.add(grace_id)

        region_tr = REGION_TR_MAP.get(g['region'], g['region'])
        subregion_tr = REGION_TR_MAP.get(g['subregion'], g['subregion'])
        grace_type = determine_type(g['name'], g['subregion'], g['region'])
        
        # Coordinates
        x, y = generate_coords(g['region'], g['subregion'], g['name'], idx, len(graces))

        # Helpful description / context in Turkish
        realm_name_tr = 'Ara Topraklar' if g['realm'] == 'The Lands Between' else "Erdtree'nin Gölgesi (DLC)"
        
        type_labels_tr = {
            'Overworld': 'Açık Dünya Lütfu',
            'Legacy Dungeon': 'Ana Zindan Lütfu',
            'Dungeon': 'Zindan / Mağara Lütfu',
            'Underground': 'Yeraltı Lütfu',
            'Boss': 'Boss Arenası Lütfu'
        }
        type_tr = type_labels_tr.get(grace_type, 'Lütuf Noktası')
        
        desc_tr = f"{realm_name_tr} sınırları içindeki {region_tr} ({subregion_tr}) bölgesinde yer alan {type_tr}."

        final_graces.append({
            'id': grace_id,
            'name': g['name'],
            'realm': g['realm'],
            'realm_tr': realm_name_tr,
            'region': g['region'],
            'region_tr': region_tr,
            'subregion': g['subregion'],
            'subregion_tr': subregion_tr,
            'type': grace_type,
            'type_tr': type_tr,
            'description_tr': desc_tr,
            'map_coords': {'x': x, 'y': y},
            'image_file': g['image_file'],
            'wiki_url': f"https://eldenring.fandom.com/wiki/{g['wiki_page'].replace(' ', '_')}",
            'discovered': False,
            'favorite': False,
            'notes': ''
        })

    out_path = 'C:/Users/alper/.gemini/antigravity-ide/scratch/elden_ring_grace_tracker/data/graces.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(final_graces, f, ensure_ascii=False, indent=2)

    print(f"Successfully compiled {len(final_graces)} Sites of Grace to {out_path}!")

if __name__ == '__main__':
    main()
