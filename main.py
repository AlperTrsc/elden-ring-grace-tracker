#!/usr/bin/env python3
"""
Elden Ring: Sites of Grace (Lütuf Noktaları) Gezgini & Takipçisi
Kullanım:
    python main.py         -> İnteraktif Web Uygulamasını Başlatır (Önerilen)
    python main.py --gui   -> Masaüstü Tkinter Arayüzünü Başlatır
"""

import sys
import os

def print_banner():
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

    banner = """
    =================================================================
             ELDEN RING: SITES OF GRACE EXPLORER
             Lütuf Noktalari Gezgini & Takipcisi
             
       * 408 Lütuf Noktasi (Ara Topraklar + Gölge Diyari DLC)
       * Interaktif Harita & Koordinat Görünümü
       * Bölge Bazli Ilerleme & Kesif Takipcisi
       * Fandom Wiki Baglantilari & Kisisel Not Defteri
    =================================================================
    """
    print(banner)

def main():
    print_banner()

    args = sys.argv[1:]

    if '--help' in args or '-h' in args:
        print("Kullanım Seçenekleri:")
        print("  python main.py         : İnteraktif Web Arayüzünü Başlatır (Önerilen)")
        print("  python main.py --gui   : Masaüstü Tkinter Penceresini Başlatır")
        print("  python main.py --port  : Özel port belirler (Örn: python main.py --port 8090)")
        sys.exit(0)

    if '--gui' in args:
        print("Masaüstü Tkinter Arayüzü başlatılıyor...")
        try:
            import gui
            gui.main()
        except Exception as e:
            print(f"Masaüstü arayüzü başlatılırken hata oluştu: {e}")
            print("Web sürümünü denemek için: python main.py")
    else:
        port = 8088
        if '--port' in args:
            try:
                p_idx = args.index('--port') + 1
                port = int(args[p_idx])
            except (ValueError, IndexError):
                pass

        print("İnteraktif Web Uygulaması başlatılıyor...")
        import app
        app.run_server(port=port, open_browser=True)

if __name__ == '__main__':
    main()
