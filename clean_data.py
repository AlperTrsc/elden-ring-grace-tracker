import json

with open('data/graces.json', 'r', encoding='utf-8') as f:
    graces = json.load(f)

reg_tr = {
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
    'Gravesite Plain': 'Mezarlık Ovası',
    'Castle Ensis': 'Ensis Kalesi',
    'Belurat, Tower Settlement': 'Belurat, Kule Yerleşimi',
    'Scadu Altus': 'Scadu Altus',
    'Shadow Keep': 'Gölge Kalesi',
    'Ancient Ruins of Rauh': 'Antik Rauh Harabeleri',
    'Rauh Base': 'Rauh Tabanı',
    'Cerulean Coast': 'Gök Mavisi Kıyı',
    "Charo's Hidden Grave": "Charo'nun Gizli Mezarı",
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

type_tr = {
    'Overworld': 'Açık Dünya Lütfu',
    'Legacy Dungeon': 'Ana Zindan Lütfu',
    'Dungeon': 'Zindan / Mağara Lütfu',
    'Underground': 'Yeraltı Lütfu',
    'Boss': 'Boss Arenası Lütfu'
}

for g in graces:
    realm_tr = 'Ara Topraklar' if g['realm'] == 'The Lands Between' else 'Gölge Diyarı (DLC)'
    g['realm_tr'] = realm_tr
    g['region_tr'] = reg_tr.get(g['region'], g['region'])
    g['subregion_tr'] = reg_tr.get(g['subregion'], g['subregion'])
    g['type_tr'] = type_tr.get(g['type'], 'Lütuf Noktası')
    g['description_tr'] = f"{realm_tr} - {g['region_tr']} ({g['subregion_tr']}) bölgesinde yer alan {g['type_tr']}."

with open('data/graces.json', 'w', encoding='utf-8') as f:
    json.dump(graces, f, ensure_ascii=False, indent=2)

print('Updated graces.json cleanly with proper Turkish characters!')
