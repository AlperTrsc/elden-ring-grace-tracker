# ✦ Elden Ring: Sites of Grace & Discoveries Explorer ✦

Python tabanlı, hem **zengin modern web arayüzü** hem de **masaüstü GUI** sunan interaktif Elden Ring Lütuf Noktaları (Sites of Grace), Boss Arenaları ve Kişiselleştirilebilir Harita Keşif Gezgini.

---

## 🌟 Öne Çıkan Özellikler

1. **Sayısız & Orijinal Temiz Harita:**
   - Harita üzerindeki tüm koordinat/modlama ızgaraları ve sayılar kaldırılmıştır.
   - Ara Topraklar ve Shadow of the Erdtree'nin resmi, yüksek çözünürlüklü ve kristal netliğindeki harita görselleri entegre edilmiştir.

2. **Oyun İçi MSB Koordinatlarıyla Doğrulanmış Konumlar:**
   - Tüm 408 lütuf noktası ve 141 boss arenası FromSoftware'in gerçek MSB dünya koordinatları ve `WorldMapLegacyConvParam` legacy zindan dönüşümleriyle piksel piksel kalibre edilmiştir.
   - The First Step, Church of Elleh, Gatefront, Stormveil, Raya Lucaria vb. tüm noktalar tam binaların ve yolların merkezinde konumlanır.

3. **Özel Keşif / İşaret Ekleme & Kaldırma:**
   - **`[➕ İşaret Ekle]`** modu ile haritanın istenilen noktasına tıklanarak yeni keşifler oluşturulabilir.
   - Kategoriler: *🌟 Lütuf Noktası*, *⚔️ Boss / Düşman*, *🗝️ Zindan / Mağara*, *💎 Hazine / Eşya*, *👤 NPC / Tüccar*, *🔍 Gizem*, *📝 Not*.
   - Renk paleti seçimi (Altın, Kırmızı, Mavi, Zümrüt, Mor, Turuncu) ve kişisel ipucu notları.
   - Haritadaki herhangi bir işarete tıklanarak **`[🗑️ Haritadan Kaldır / Sil]`** ile güvenle silinebilir veya **`[✏️ Düzenle]`** ile güncellenebilir.
   - **`[📋 İşaretlerim]`** paneli ile tüm eklenen işaretler topluca yönetilebilir.

4. **Keşif Katmanı Filtreleri:**
   - `[🌟 Lütuflar]`: Lütuf noktalarını gösterir / gizler.
   - `[⚔️ Bosslar]`: 141 adet boss arenası ve rün ödüllerini gösterir; mağlup edilenler işaretlenebilir.
   - `[📍 Keşiflerim]`: Kendi eklediğiniz özel işaretleri gösterir / gizler.
   - `[👁️ Keşfedilmemişler]`: Henüz açılmamış içerikleri filtreler.

5. **Gelişmiş Liste & Kart Gezgini:**
   - Anlık arama (İsim, bölge, boss veya kişisel notlar üzerinden).
   - Bölge filtreleri (32 bölge).
   - Toplu keşfetme / sıfırlama.

6. **İlerleme Raporu & İstatistikler:**
   - Tamamlanma yüzdesi ve sayaçlar.
   - Bölge bazlı ilerleme çubukları.
   - JSON dışa aktarma (Export) ve içe aktarma (Import) yedekleme desteği.

---

## 🚀 Çalıştırma

Terminal veya komut istemcisinde (PowerShell / CMD) proje klasörüne gidin:

```powershell
cd C:\Users\alper\.gemini\antigravity-ide\scratch\elden_ring_grace_tracker
```

### 1. Web Arayüzünü Başlatma (Önerilen)
```powershell
python main.py
# veya
python app.py
```
*Otomatik olarak varsayılan internet tarayıcınızda `http://127.0.0.1:8088` adresini açar.*

### 2. Masaüstü GUI Başlatma
```powershell
python main.py --gui
```

---

## 📁 Proje Yapısı

```
elden_ring_grace_tracker/
├── main.py              # Birleşik başlatıcı (Web veya GUI seçimi)
├── app.py               # Yerleşik Python HTTP sunucusu & REST API
├── gui.py               # Tkinter tabanlı masaüstü GUI arayüzü
├── data/
│   ├── graces.json      # 408 Lütuf Noktası veri tabanı (Kalibre koordinatlı)
│   ├── bosses.json      # 141 Boss Arenası veri tabanı
│   └── user_progress.json # Kullanıcının keşif ilerlemesi, özel işaretleri ve notları
├── web/
│   ├── index.html       # Web arayüzü HTML yapısı
│   ├── style.css        # Elden Ring temalı altın/obsidyen stil sayfası
│   ├── app.js           # İnteraktif harita, işaret ekleme/çıkarma ve durum motoru
│   └── assets/
│       ├── map_lands_between.jpg / .webp # Sayısız temiz Ara Topraklar haritası
│       ├── map_shadow_realm.webp        # Sayısız temiz DLC Gölge Diyarı haritası
│       └── map_underground.webp         # Yeraltı haritası
└── README.md
```
