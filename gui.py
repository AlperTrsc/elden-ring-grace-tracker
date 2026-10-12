import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data', 'graces.json')
USER_SAVE_FILE = os.path.join(BASE_DIR, 'data', 'user_progress.json')

class EldenRingGraceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Elden Ring - Lütuf Noktaları (Sites of Grace Explorer)")
        self.root.geometry("1180x750")
        self.root.minsize(950, 600)
        self.root.configure(bg="#0f1115")

        self.graces = []
        self.progress = {"discovered": [], "favorites": [], "notes": {}}
        self.current_grace = None

        self.load_data()
        self.setup_styles()
        self.create_widgets()
        self.populate_regions()
        self.filter_graces()
        self.update_stats()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                self.graces = json.load(f)
        if os.path.exists(USER_SAVE_FILE):
            try:
                with open(USER_SAVE_FILE, 'r', encoding='utf-8') as f:
                    self.progress = json.load(f)
            except Exception:
                self.progress = {"discovered": [], "favorites": [], "notes": {}}

    def save_progress(self):
        os.makedirs(os.path.dirname(USER_SAVE_FILE), exist_ok=True)
        with open(USER_SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)
        self.update_stats()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.style.configure('.', background="#0f1115", foreground="#d8c59a")
        self.style.configure('Treeview',
                             background="#16181f",
                             foreground="#e0d6b9",
                             fieldbackground="#16181f",
                             rowheight=28,
                             font=('Segoe UI', 10))
        self.style.map('Treeview',
                       background=[('selected', '#3d321d')],
                       foreground=[('selected', '#ffdf80')])

        self.style.configure('Treeview.Heading',
                             background="#222530",
                             foreground="#c59b27",
                             font=('Segoe UI Semibold', 10))

        self.style.configure('Horizontal.TProgressbar',
                             background='#c59b27',
                             troughcolor='#1e2029')

    def create_widgets(self):
        # Header frame
        header = tk.Frame(self.root, bg="#161922", height=65)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        title_lbl = tk.Label(header, text="✦ ELDEN RING: SITES OF GRACE GEZGİNİ ✦",
                             font=('Cinzel', 16, 'bold'), fg="#f3d078", bg="#161922")
        title_lbl.pack(side=tk.LEFT, padx=20, pady=10)

        # Stats in header
        self.stats_lbl = tk.Label(header, text="Keşif: 0 / 0 (%0.0)",
                                  font=('Segoe UI', 11, 'bold'), fg="#ffd700", bg="#161922")
        self.stats_lbl.pack(side=tk.RIGHT, padx=20)

        self.progress_bar = ttk.Progressbar(header, orient="horizontal", length=220,
                                            mode="determinate", style='Horizontal.TProgressbar')
        self.progress_bar.pack(side=tk.RIGHT, padx=10)

        # Filter bar
        filter_bar = tk.Frame(self.root, bg="#1a1d26", pady=8, padx=15)
        filter_bar.pack(fill=tk.X, side=tk.TOP)

        tk.Label(filter_bar, text="Arama:", fg="#d8c59a", bg="#1a1d26", font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(0, 6))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.filter_graces())
        search_entry = tk.Entry(filter_bar, textvariable=self.search_var, bg="#262a38", fg="#ffffff",
                                insertbackground="#f3d078", font=('Segoe UI', 10), width=24)
        search_entry.pack(side=tk.LEFT, padx=(0, 15))

        tk.Label(filter_bar, text="Diyar:", fg="#d8c59a", bg="#1a1d26", font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(0, 6))
        self.realm_var = tk.StringVar(value="Tümü")
        realm_cb = ttk.Combobox(filter_bar, textvariable=self.realm_var, state="readonly", width=18,
                                values=["Tümü", "Ara Topraklar (Base)", "Gölge Diyarı (DLC)"])
        realm_cb.pack(side=tk.LEFT, padx=(0, 15))
        realm_cb.bind("<<ComboboxSelected>>", lambda e: self.on_realm_change())

        tk.Label(filter_bar, text="Durum:", fg="#d8c59a", bg="#1a1d26", font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(0, 6))
        self.status_var = tk.StringVar(value="Tümü")
        status_cb = ttk.Combobox(filter_bar, textvariable=self.status_var, state="readonly", width=14,
                                 values=["Tümü", "Keşfedildi", "Keşfedilmedi", "Favoriler"])
        status_cb.pack(side=tk.LEFT, padx=(0, 15))
        status_cb.bind("<<ComboboxSelected>>", lambda e: self.filter_graces())

        # Web App launcher button
        web_btn = tk.Button(filter_bar, text="🌐 İnteraktif Haritayı Aç", command=self.open_web_app,
                            bg="#382d16", fg="#f5d372", activebackground="#4f3f1e", activeforeground="#ffffff",
                            font=('Segoe UI Semibold', 9), padx=10, relief=tk.FLAT)
        web_btn.pack(side=tk.RIGHT, padx=5)

        # Main Split Content
        main_split = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#0f1115", sashwidth=4)
        main_split.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel: Regions
        left_frame = tk.Frame(main_split, bg="#16181f", width=240)
        main_split.add(left_frame)

        left_lbl = tk.Label(left_frame, text="Bölgeler & Konumlar", fg="#c59b27", bg="#16181f",
                            font=('Segoe UI Semibold', 11))
        left_lbl.pack(anchor="w", padx=10, pady=6)

        self.region_tree = ttk.Treeview(left_frame, show="tree", selectmode="browse")
        self.region_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        self.region_tree.bind("<<TreeviewSelect>>", lambda e: self.filter_graces())

        # Center panel: Grace List
        center_frame = tk.Frame(main_split, bg="#16181f", width=480)
        main_split.add(center_frame)

        columns = ("discovered", "name", "type", "region")
        self.grace_tree = ttk.Treeview(center_frame, columns=columns, show="headings", selectmode="browse")
        self.grace_tree.heading("discovered", text="Durum")
        self.grace_tree.heading("name", text="Lütuf Adı")
        self.grace_tree.heading("type", text="Tür")
        self.grace_tree.heading("region", text="Bölge")

        self.grace_tree.column("discovered", width=70, anchor="center")
        self.grace_tree.column("name", width=220)
        self.grace_tree.column("type", width=110)
        self.grace_tree.column("region", width=120)

        grace_scroll = ttk.Scrollbar(center_frame, orient="vertical", command=self.grace_tree.yview)
        self.grace_tree.configure(yscrollcommand=grace_scroll.set)
        self.grace_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        grace_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.grace_tree.bind("<<TreeviewSelect>>", self.on_grace_selected)
        self.grace_tree.bind("<Double-1>", self.on_grace_double_click)

        # Right panel: Details
        self.right_frame = tk.Frame(main_split, bg="#16181f", width=340, padx=15, pady=15)
        main_split.add(right_frame=self.right_frame)

        self.setup_detail_panel()

    def setup_detail_panel(self):
        self.detail_name = tk.Label(self.right_frame, text="Bir Lütuf Seçin", fg="#f3d078", bg="#16181f",
                                    font=('Cinzel', 14, 'bold'), wraplength=300, justify=tk.LEFT)
        self.detail_name.pack(anchor="w", pady=(0, 5))

        self.detail_region = tk.Label(self.right_frame, text="", fg="#9ea3b5", bg="#16181f",
                                      font=('Segoe UI', 10))
        self.detail_region.pack(anchor="w", pady=(0, 5))

        self.detail_type = tk.Label(self.right_frame, text="", fg="#c59b27", bg="#16181f",
                                    font=('Segoe UI Semibold', 10))
        self.detail_type.pack(anchor="w", pady=(0, 10))

        # Action buttons
        btn_box = tk.Frame(self.right_frame, bg="#16181f")
        btn_box.pack(fill=tk.X, pady=(0, 15))

        self.toggle_disc_btn = tk.Button(btn_box, text="✦ Keşfedildi Olarak İşaretle", command=self.toggle_discovered,
                                         bg="#332a18", fg="#f5d372", activebackground="#4f3f1e",
                                         font=('Segoe UI Semibold', 10), relief=tk.FLAT, pady=6)
        self.toggle_disc_btn.pack(fill=tk.X, pady=(0, 6))

        self.toggle_fav_btn = tk.Button(btn_box, text="★ Favorilere Ekle", command=self.toggle_favorite,
                                        bg="#242836", fg="#d8c59a", font=('Segoe UI', 9), relief=tk.FLAT, pady=4)
        self.toggle_fav_btn.pack(fill=tk.X, pady=(0, 6))

        self.wiki_btn = tk.Button(btn_box, text="📖 Wiki / Rehber Sayfasını Aç", command=self.open_wiki,
                                  bg="#222530", fg="#9ea3b5", font=('Segoe UI', 9), relief=tk.FLAT, pady=4)
        self.wiki_btn.pack(fill=tk.X)

        # Description
        tk.Label(self.right_frame, text="Bilgi & Açıklama:", fg="#c59b27", bg="#16181f",
                 font=('Segoe UI Semibold', 10)).pack(anchor="w", pady=(10, 4))
        self.detail_desc = tk.Label(self.right_frame, text="", fg="#d0d4e4", bg="#16181f",
                                    font=('Segoe UI', 9), wraplength=290, justify=tk.LEFT)
        self.detail_desc.pack(anchor="w", pady=(0, 10))

        # Personal notes
        tk.Label(self.right_frame, text="Kişisel Notlar:", fg="#c59b27", bg="#16181f",
                 font=('Segoe UI Semibold', 10)).pack(anchor="w", pady=(5, 4))
        self.notes_text = tk.Text(self.right_frame, height=5, bg="#20232e", fg="#ffffff",
                                  insertbackground="#ffd700", font=('Segoe UI', 9), relief=tk.FLAT)
        self.notes_text.pack(fill=tk.X, pady=(0, 6))
        self.notes_text.bind("<KeyRelease>", self.on_notes_changed)

    def populate_regions(self):
        self.region_tree.delete(*self.region_tree.get_children())
        self.region_tree.insert("", "end", "all", text="Tüm Bölgeler")

        realm_filter = self.realm_var.get()
        regions = sorted(list(set(g['region_tr'] for g in self.graces if self.match_realm(g, realm_filter))))
        for reg in regions:
            self.region_tree.insert("", "end", reg, text=reg)

        self.region_tree.selection_set("all")

    def match_realm(self, grace, realm_filter):
        if realm_filter == "Tümü":
            return True
        elif realm_filter == "Ara Topraklar (Base)" and grace['realm'] == 'The Lands Between':
            return True
        elif realm_filter == "Gölge Diyarı (DLC)" and grace['realm'] == 'Shadow of the Erdtree':
            return True
        return False

    def on_realm_change(self):
        self.populate_regions()
        self.filter_graces()

    def filter_graces(self):
        self.grace_tree.delete(*self.grace_tree.get_children())

        search_q = self.search_var.get().strip().lower()
        realm_filter = self.realm_var.get()
        status_filter = self.status_var.get()

        sel_region = "all"
        region_sel = self.region_tree.selection()
        if region_sel:
            sel_region = region_sel[0]

        disc_set = set(self.progress.get("discovered", []))
        fav_set = set(self.progress.get("favorites", []))

        for g in self.graces:
            gid = g['id']
            is_disc = gid in disc_set
            is_fav = gid in fav_set

            if not self.match_realm(g, realm_filter):
                continue

            if sel_region != "all" and g['region_tr'] != sel_region:
                continue

            if status_filter == "Keşfedildi" and not is_disc:
                continue
            elif status_filter == "Keşfedilmedi" and is_disc:
                continue
            elif status_filter == "Favoriler" and not is_fav:
                continue

            if search_q:
                text_to_search = f"{g['name']} {g['region_tr']} {g['subregion_tr']} {g['type_tr']}".lower()
                if search_q not in text_to_search:
                    continue

            status_str = "✓ Keşfedildi" if is_disc else "○ Keşfedilmedi"
            tag = "discovered" if is_disc else "undiscovered"

            item_id = self.grace_tree.insert("", "end", iid=gid,
                                             values=(status_str, g['name'], g['type_tr'], g['region_tr']),
                                             tags=(tag,))

        self.grace_tree.tag_configure("discovered", foreground="#ffd700")
        self.grace_tree.tag_configure("undiscovered", foreground="#b0b4c3")

    def on_grace_selected(self, event):
        sel = self.grace_tree.selection()
        if not sel:
            return
        gid = sel[0]
        grace = next((g for g in self.graces if g['id'] == gid), None)
        if not grace:
            return

        self.current_grace = grace
        disc_set = set(self.progress.get("discovered", []))
        fav_set = set(self.progress.get("favorites", []))
        is_disc = gid in disc_set
        is_fav = gid in fav_set

        self.detail_name.config(text=grace['name'])
        self.detail_region.config(text=f"{grace['realm_tr']} • {grace['region_tr']} ({grace['subregion_tr']})")
        self.detail_type.config(text=f"Tür: {grace['type_tr']}")
        self.detail_desc.config(text=grace['description_tr'])

        self.toggle_disc_btn.config(
            text="✕ Keşfedilmedi Yap" if is_disc else "✦ Keşfedildi Olarak İşaretle",
            bg="#4a2020" if is_disc else "#332a18",
            fg="#ffaaaa" if is_disc else "#f5d372"
        )
        self.toggle_fav_btn.config(
            text="★ Favorilerden Kaldır" if is_fav else "☆ Favorilere Ekle",
            fg="#ffd700" if is_fav else "#d8c59a"
        )

        notes = self.progress.get("notes", {}).get(gid, "")
        self.notes_text.delete("1.0", tk.END)
        self.notes_text.insert(tk.END, notes)

    def on_grace_double_click(self, event):
        self.toggle_discovered()

    def toggle_discovered(self):
        if not self.current_grace:
            return
        gid = self.current_grace['id']
        disc_set = set(self.progress.get("discovered", []))

        if gid in disc_set:
            disc_set.remove(gid)
        else:
            disc_set.add(gid)

        self.progress["discovered"] = list(disc_set)
        self.save_progress()
        self.filter_graces()
        self.grace_tree.selection_set(gid)

    def toggle_favorite(self):
        if not self.current_grace:
            return
        gid = self.current_grace['id']
        fav_set = set(self.progress.get("favorites", []))

        if gid in fav_set:
            fav_set.remove(gid)
        else:
            fav_set.add(gid)

        self.progress["favorites"] = list(fav_set)
        self.save_progress()
        self.on_grace_selected(None)

    def on_notes_changed(self, event):
        if not self.current_grace:
            return
        gid = self.current_grace['id']
        content = self.notes_text.get("1.0", tk.END).strip()
        if "notes" not in self.progress:
            self.progress["notes"] = {}
        self.progress["notes"][gid] = content
        self.save_progress()

    def open_wiki(self):
        if self.current_grace and self.current_grace.get('wiki_url'):
            webbrowser.open(self.current_grace['wiki_url'])

    def open_web_app(self):
        url = "http://127.0.0.1:8088"
        try:
            import urllib.request
            urllib.request.urlopen(url, timeout=0.5)
        except Exception:
            import threading
            import app
            threading.Thread(target=lambda: app.run_server(port=8088, open_browser=False), daemon=True).start()
        webbrowser.open(url)

    def update_stats(self):
        total = len(self.graces)
        disc_count = len(self.progress.get("discovered", []))
        pct = (disc_count / total * 100) if total > 0 else 0
        self.stats_lbl.config(text=f"Keşfedilen: {disc_count} / {total} (%{pct:.1f})")
        self.progress_bar['value'] = pct

def main():
    root = tk.Tk()
    app = EldenRingGraceApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
