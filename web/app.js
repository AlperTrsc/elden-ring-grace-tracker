/**
 * ELDEN RING: SITES OF GRACE EXPLORER & DISCOVERIES TRACKER
 * Features:
 * - Ultra-accurate verified in-game coordinates
 * - Official clean high-res Lands Between & Shadow Realm maps
 * - Custom Discoveries (Add, Edit, Remove any marker on map)
 * - Bosses & Dungeons discovery tracking
 * - Content Layer toggles (Lütuflar, Bosslar, Özel Keşiflerim)
 * - Audio Chimes, Embers, Offline Storage, JSON Import/Export
 */

(function () {
  'use strict';

  // State Management
  const state = {
    graces: [],
    bosses: [],
    customMarkers: [],
    discoveredSet: new Set(),
    favoriteSet: new Set(),
    defeatedBossesSet: new Set(),
    notesMap: {},
    audioEnabled: true,
    activeView: 'map',
    activeRealm: 'The Lands Between',
    activeStatus: 'all',
    activeType: 'all',
    activeRegion: 'all',
    mapMode: 'real',
    searchQuery: '',
    sortOrder: 'default',
    mapZoom: 0.85,
    mapPan: { x: 0, y: 0 },
    isDraggingMap: false,
    dragStart: { x: 0, y: 0 },
    selectedItem: null, // can be grace, boss, or custom marker
    selectedItemType: null, // 'grace' | 'boss' | 'custom'
    showUndiscoveredOnMap: true,
    layers: {
      graces: true,
      bosses: true,
      custom: true,
      undiscovered: true
    },
    addMarkerMode: false,
    audioCtx: null
  };

  // Category Icon & Label Map
  const CATEGORY_MAP = {
    grace: { icon: '🌟', label: 'Lütuf Noktası', defaultColor: '#ecbd4a' },
    boss: { icon: '⚔️', label: 'Boss / Düşman', defaultColor: '#e24a4a' },
    dungeon: { icon: '🗝️', label: 'Zindan / Mağara', defaultColor: '#f97316' },
    treasure: { icon: '💎', label: 'Hazine / Eşya', defaultColor: '#38bdf8' },
    npc: { icon: '👤', label: 'NPC / Tüccar', defaultColor: '#10b981' },
    secret: { icon: '🔍', label: 'Gizem / Geçit', defaultColor: '#a855f7' },
    note: { icon: '📝', label: 'Not / İpucu', defaultColor: '#ecbd4a' }
  };

  // DOM Cache
  const dom = {
    // Header & Nav
    btnViewMap: document.getElementById('btn-view-map'),
    btnViewList: document.getElementById('btn-view-list'),
    btnViewStats: document.getElementById('btn-view-stats'),
    viewMap: document.getElementById('view-map'),
    viewList: document.getElementById('view-list'),
    viewStats: document.getElementById('view-stats'),
    statTotalCount: document.getElementById('stat-total-count'),
    statTotalPct: document.getElementById('stat-total-pct'),
    statTotalBar: document.getElementById('stat-total-bar'),
    btnAudioToggle: document.getElementById('btn-audio-toggle'),
    audioIcon: document.getElementById('audio-icon'),
    btnSaveManual: document.getElementById('btn-save-manual'),

    // Map View Controls
    mapViewport: document.getElementById('map-viewport'),
    mapWorld: document.getElementById('map-world'),
    mapImageLayer: document.getElementById('map-image-layer'),
    mapCanvas: document.getElementById('map-canvas'),
    pinsContainer: document.getElementById('pins-container'),
    mapSearchInput: document.getElementById('map-search-input'),
    mapToggleUndiscovered: document.getElementById('map-toggle-undiscovered'),
    mapRealmTabs: document.getElementById('map-realm-tabs'),
    mapModeTabs: document.getElementById('map-mode-tabs'),
    btnZoomIn: document.getElementById('btn-zoom-in'),
    btnZoomOut: document.getElementById('btn-zoom-out'),
    btnZoomReset: document.getElementById('btn-zoom-reset'),
    btnFullscreenMap: document.getElementById('btn-fullscreen-map'),

    // Content Layer Toggles
    toggleLayerGraces: document.getElementById('toggle-layer-graces'),
    toggleLayerBosses: document.getElementById('toggle-layer-bosses'),
    toggleLayerCustom: document.getElementById('toggle-layer-custom'),

    // Marker Action Controls
    btnAddMarkerMode: document.getElementById('btn-add-marker-mode'),
    btnManageCustomMarkers: document.getElementById('btn-manage-custom-markers'),
    customMarkerCount: document.getElementById('custom-marker-count'),
    addMarkerBanner: document.getElementById('add-marker-banner'),
    btnCancelAddMarkerMode: document.getElementById('btn-cancel-add-marker-mode'),

    // Custom Marker Modal
    modalMarkerBackdrop: document.getElementById('modal-marker-backdrop'),
    modalMarkerTitleHeading: document.getElementById('modal-marker-title-heading'),
    btnCloseMarkerModal: document.getElementById('btn-close-marker-modal'),
    formCustomMarker: document.getElementById('form-custom-marker'),
    markerFormId: document.getElementById('marker-form-id'),
    markerFormX: document.getElementById('marker-form-x'),
    markerFormY: document.getElementById('marker-form-y'),
    markerFormRealm: document.getElementById('marker-form-realm'),
    markerFormTitle: document.getElementById('marker-form-title'),
    markerFormCategory: document.getElementById('marker-form-category'),
    markerFormRegion: document.getElementById('marker-form-region'),
    markerFormColor: document.getElementById('marker-form-color'),
    markerColorPalette: document.getElementById('marker-color-palette'),
    markerFormNotes: document.getElementById('marker-form-notes'),
    markerCoordsReadout: document.getElementById('marker-coords-readout'),
    markerFormDiscovered: document.getElementById('marker-form-discovered'),
    btnCancelMarkerForm: document.getElementById('btn-cancel-marker-form'),

    // Manage Markers Modal
    modalManageBackdrop: document.getElementById('modal-manage-backdrop'),
    btnCloseManageModal: document.getElementById('btn-close-manage-modal'),
    manageMarkersCountLabel: document.getElementById('manage-markers-count-label'),
    manageMarkersList: document.getElementById('manage-markers-list'),
    btnClearAllCustomMarkers: document.getElementById('btn-clear-all-custom-markers'),

    // List Explorer
    listSearchInput: document.getElementById('list-search-input'),
    btnClearSearch: document.getElementById('btn-clear-search'),
    pillsRealm: document.getElementById('pills-realm'),
    pillsStatus: document.getElementById('pills-status'),
    pillsType: document.getElementById('pills-type'),
    selectRegion: document.getElementById('select-region'),
    selectSort: document.getElementById('select-sort'),
    cardsResultsCount: document.getElementById('cards-results-count'),
    cardsGrid: document.getElementById('cards-grid'),
    emptyState: document.getElementById('empty-state'),
    btnResetFilters: document.getElementById('btn-reset-filters'),
    btnBatchDiscover: document.getElementById('btn-batch-discover-filtered'),
    btnBatchReset: document.getElementById('btn-batch-reset-filtered'),

    // Stats
    dashTotalVal: document.getElementById('dash-total-val'),
    dashTotalPct: document.getElementById('dash-total-pct'),
    dashBaseVal: document.getElementById('dash-base-val'),
    dashBasePct: document.getElementById('dash-base-pct'),
    dashDlcVal: document.getElementById('dash-dlc-val'),
    dashDlcPct: document.getElementById('dash-dlc-pct'),
    dashBossVal: document.getElementById('dash-boss-val'),
    dashBossPct: document.getElementById('dash-boss-pct'),
    regionsProgressGrid: document.getElementById('regions-progress-grid'),
    btnExportSave: document.getElementById('btn-export-save'),
    inputImportSave: document.getElementById('input-import-save'),
    btnResetAll: document.getElementById('btn-reset-all'),

    // Drawer / Modal
    modalBackdrop: document.getElementById('modal-backdrop'),
    graceDrawer: document.getElementById('grace-drawer'),
    btnCloseDrawer: document.getElementById('btn-close-drawer'),
    drawerRealm: document.getElementById('drawer-realm'),
    drawerName: document.getElementById('drawer-name'),
    drawerRegion: document.getElementById('drawer-region'),
    drawerType: document.getElementById('drawer-type'),
    drawerStatus: document.getElementById('drawer-status'),
    drawerDesc: document.getElementById('drawer-desc'),
    drawerCoords: document.getElementById('drawer-coords'),
    drawerNotes: document.getElementById('drawer-notes'),
    drawerBtnToggleDisc: document.getElementById('drawer-btn-toggle-disc'),
    drawerBtnToggleFav: document.getElementById('drawer-btn-toggle-fav'),
    drawerBtnEditCustom: document.getElementById('drawer-btn-edit-custom'),
    drawerBtnDeleteCustom: document.getElementById('drawer-btn-delete-custom'),
    drawerBtnWiki: document.getElementById('drawer-btn-wiki'),

    // Toast & Embers
    toast: document.getElementById('toast'),
    embersCanvas: document.getElementById('embers-canvas')
  };

  // ==========================================
  // INITIALIZATION
  // ==========================================
  async function init() {
    initEmbers();
    setupEventListeners();
    await loadData();
    populateRegionDropdown();
    updateMapRealm('The Lands Between');
    renderCards();
    updateStats();
    updateCustomMarkerCounter();
  }

  // ==========================================
  // AUDIO SYNTHESIZER (Grace Chime)
  // ==========================================
  function playGraceChime() {
    if (!state.audioEnabled) return;
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!state.audioCtx) {
        state.audioCtx = new AudioContext();
      }
      if (state.audioCtx.state === 'suspended') {
        state.audioCtx.resume();
      }

      const now = state.audioCtx.currentTime;
      // High-pitched crystal bell harmonics: 523Hz (C5), 784Hz (G5), 1046Hz (C6), 1318Hz (E6)
      const freqs = [523.25, 783.99, 1046.5, 1318.51];

      freqs.forEach((freq, i) => {
        const osc = state.audioCtx.createOscillator();
        const gain = state.audioCtx.createGain();

        osc.type = i % 2 === 0 ? 'sine' : 'triangle';
        osc.frequency.setValueAtTime(freq, now + i * 0.04);

        gain.gain.setValueAtTime(0, now);
        gain.gain.linearRampToValueAtTime(0.09 / (i + 1), now + 0.05 + i * 0.04);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 1.8 + i * 0.2);

        osc.connect(gain);
        gain.connect(state.audioCtx.destination);

        osc.start(now + i * 0.04);
        osc.stop(now + 2.2);
      });
    } catch (e) {
      console.warn('Audio play failed:', e);
    }
  }

  // ==========================================
  // DATA LOADING & SAVING
  // ==========================================
  async function loadData() {
    // 1. Load Graces
    try {
      const res = await fetch('/api/graces');
      if (res.ok) {
        state.graces = await res.json();
      }
    } catch (err) {
      console.warn('Could not fetch graces from server:', err);
      state.graces = [];
    }

    // 2. Load Bosses
    try {
      const res = await fetch('/api/bosses');
      if (res.ok) {
        state.bosses = await res.json();
      }
    } catch (err) {
      console.warn('Could not fetch bosses from server:', err);
      state.bosses = [];
    }

    // 3. Load User Progress & Custom Markers
    state.discoveredSet.clear();
    state.favoriteSet.clear();
    state.defeatedBossesSet.clear();
    state.customMarkers = [];
    state.notesMap = {};

    try {
      const res = await fetch('/api/progress');
      if (res.ok) {
        const p = await res.json();
        if (p.discovered) p.discovered.forEach(id => state.discoveredSet.add(id));
        if (p.favorites) p.favorites.forEach(id => state.favoriteSet.add(id));
        if (p.defeated_bosses) p.defeated_bosses.forEach(id => state.defeatedBossesSet.add(id));
        if (p.custom_markers) state.customMarkers = p.custom_markers;
        if (p.notes) Object.assign(state.notesMap, p.notes);
      }
    } catch (err) {
      console.warn('Could not fetch user progress:', err);
    }

    // Sync with localStorage as additional safeguard
    const localSaved = localStorage.getItem('er_grace_progress');
    if (localSaved) {
      try {
        const parsed = JSON.parse(localSaved);
        if (parsed.discovered) parsed.discovered.forEach(id => state.discoveredSet.add(id));
        if (parsed.favorites) parsed.favorites.forEach(id => state.favoriteSet.add(id));
        if (parsed.defeated_bosses) parsed.defeated_bosses.forEach(id => state.defeatedBossesSet.add(id));
        if (parsed.custom_markers && state.customMarkers.length === 0) {
          state.customMarkers = parsed.custom_markers;
        }
        if (parsed.notes) Object.assign(state.notesMap, parsed.notes);
      } catch (e) {}
    }
  }

  let saveDebounceTimer = null;
  function triggerSave(showToastNotice = false) {
    clearTimeout(saveDebounceTimer);
    saveDebounceTimer = setTimeout(async () => {
      const payload = {
        discovered: Array.from(state.discoveredSet),
        favorites: Array.from(state.favoriteSet),
        defeated_bosses: Array.from(state.defeatedBossesSet),
        custom_markers: state.customMarkers,
        notes: state.notesMap
      };

      // Save to localStorage
      localStorage.setItem('er_grace_progress', JSON.stringify(payload));

      // Save to Server
      try {
        const res = await fetch('/api/save', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (res.ok && showToastNotice) {
          showToast('İlerlemeniz başarıyla kaydedildi! 💾');
        }
      } catch (e) {
        if (showToastNotice) {
          showToast('Tarayıcıya kaydedildi (Çevrimdışı)');
        }
      }
    }, 250);
  }

  function showToast(msg) {
    dom.toast.textContent = msg;
    dom.toast.classList.add('show');
    setTimeout(() => dom.toast.classList.remove('show'), 2800);
  }

  // ==========================================
  // REGION POPULATION
  // ==========================================
  function populateRegionDropdown() {
    const regions = new Map();
    state.graces.forEach(g => {
      const reg = g.region_tr;
      regions.set(reg, (regions.get(reg) || 0) + 1);
    });

    const sortedRegions = Array.from(regions.entries()).sort((a, b) => a[0].localeCompare(b[0], 'tr'));

    dom.selectRegion.innerHTML = `<option value="all">Tüm Bölgeler (${state.graces.length})</option>`;
    sortedRegions.forEach(([name, count]) => {
      const opt = document.createElement('option');
      opt.value = name;
      opt.textContent = `${name} (${count})`;
      dom.selectRegion.appendChild(opt);
    });
  }

  // ==========================================
  // VIEW NAVIGATION
  // ==========================================
  function switchView(viewName) {
    state.activeView = viewName;

    [dom.btnViewMap, dom.btnViewList, dom.btnViewStats].forEach(b => b.classList.remove('active'));
    [dom.viewMap, dom.viewList, dom.viewStats].forEach(v => v.classList.remove('active'));

    if (viewName === 'map') {
      dom.btnViewMap.classList.add('active');
      dom.viewMap.classList.add('active');
      centerMap();
      renderMapPins();
    } else if (viewName === 'list') {
      dom.btnViewList.classList.add('active');
      dom.viewList.classList.add('active');
      renderCards();
    } else if (viewName === 'stats') {
      dom.btnViewStats.classList.add('active');
      dom.viewStats.classList.add('active');
      renderStatsDashboard();
    }
  }

  // ==========================================
  // MAP REALM & GEOMETRY
  // ==========================================
  function updateMapRealm(realm) {
    state.activeRealm = realm;

    if (realm === 'Shadow of the Erdtree') {
      dom.mapImageLayer.src = 'assets/map_shadow_realm.webp';
      // 4879 x 5940 aspect ratio
      dom.mapWorld.style.width = '2200px';
      dom.mapWorld.style.height = '2679px';
      dom.mapCanvas.width = 2200;
      dom.mapCanvas.height = 2679;
    } else {
      dom.mapImageLayer.src = 'assets/map_lands_between.jpg';
      // 9728 x 9216 aspect ratio: 9216 / 9728 * 2600 = 2463px
      dom.mapWorld.style.width = '2600px';
      dom.mapWorld.style.height = '2463px';
      dom.mapCanvas.width = 2600;
      dom.mapCanvas.height = 2463;
    }

    renderMapPins();
    if (state.mapMode === 'parchment') {
      renderMapCanvas();
    }
    centerMap();
  }

  function renderMapCanvas() {
    const canvas = dom.mapCanvas;
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    ctx.clearRect(0, 0, width, height);

    // Parchment texture background
    const bgGrad = ctx.createRadialGradient(width / 2, height / 2, 200, width / 2, height / 2, width * 0.7);
    bgGrad.addColorStop(0, '#1c1712');
    bgGrad.addColorStop(0.7, '#130f0c');
    bgGrad.addColorStop(1, '#0a0806');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, width, height);

    // Grid lines (subtle cartography aesthetic)
    ctx.strokeStyle = 'rgba(212, 169, 66, 0.05)';
    ctx.lineWidth = 1;
    const step = 150;
    for (let x = 0; x < width; x += step) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = 0; y < height; y += step) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Stylized Erdtree Tree Icon at Capital (Lands Between)
    if (state.activeRealm === 'The Lands Between') {
      const erdtreeX = width * 0.45;
      const erdtreeY = height * 0.40;
      const grad = ctx.createRadialGradient(erdtreeX, erdtreeY, 20, erdtreeX, erdtreeY, 600);
      grad.addColorStop(0, 'rgba(255, 235, 140, 0.22)');
      grad.addColorStop(0.3, 'rgba(212, 169, 66, 0.12)');
      grad.addColorStop(1, 'transparent');
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(erdtreeX, erdtreeY, 600, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  // ==========================================
  // MAP PINS RENDERING (Graces, Bosses, Custom)
  // ==========================================
  function renderMapPins() {
    dom.pinsContainer.innerHTML = '';

    const query = dom.mapSearchInput.value.trim().toLowerCase();
    const showUndisc = state.layers.undiscovered;

    // 1. SITES OF GRACE
    if (state.layers.graces) {
      state.graces.forEach(g => {
        const isDisc = state.discoveredSet.has(g.id);
        const isFav = state.favoriteSet.has(g.id);

        if (state.activeRealm !== 'all' && g.realm !== state.activeRealm) return;
        if (!isDisc && !showUndisc) return;

        if (query) {
          const fullText = `${g.name} ${g.region_tr} ${g.subregion_tr} ${g.type_tr}`.toLowerCase();
          if (!fullText.includes(query)) return;
        }

        const pin = document.createElement('div');
        pin.className = 'grace-pin';
        if (isDisc) pin.classList.add('discovered');
        if (g.type === 'Boss') pin.classList.add('boss');
        if (isFav) pin.classList.add('favorite');

        pin.style.left = `${g.map_coords.x}%`;
        pin.style.top = `${g.map_coords.y}%`;
        pin.dataset.id = g.id;

        pin.innerHTML = `
          <div class="pin-spark"></div>
          <div class="grace-pin-tooltip">
            ${isDisc ? '✦ ' : '○ '}${g.name} (${g.region_tr})
          </div>
        `;

        pin.addEventListener('click', (e) => {
          e.stopPropagation();
          openItemDrawer(g, 'grace');
        });

        dom.pinsContainer.appendChild(pin);
      });
    }

    // 2. BOSSES & ENCOUNTERS
    if (state.layers.bosses) {
      state.bosses.forEach(b => {
        const isDefeated = state.defeatedBossesSet.has(b.id);

        if (state.activeRealm !== 'all' && b.realm !== state.activeRealm) return;
        if (!isDefeated && !showUndisc) return;

        if (query) {
          const fullText = `${b.name} boss`.toLowerCase();
          if (!fullText.includes(query)) return;
        }

        const pin = document.createElement('div');
        pin.className = 'boss-pin';
        if (isDefeated) pin.classList.add('defeated');

        pin.style.left = `${b.map_coords.x}%`;
        pin.style.top = `${b.map_coords.y}%`;
        pin.dataset.id = b.id;

        pin.innerHTML = `
          <div class="boss-spark">⚔️</div>
          <div class="grace-pin-tooltip" style="border-color: rgba(226, 74, 74, 0.7);">
            ${isDefeated ? '✓ ' : '⚔️ '}${b.name} (Boss)
          </div>
        `;

        pin.addEventListener('click', (e) => {
          e.stopPropagation();
          openItemDrawer(b, 'boss');
        });

        dom.pinsContainer.appendChild(pin);
      });
    }

    // 3. CUSTOM USER MARKERS
    if (state.layers.custom) {
      state.customMarkers.forEach(cm => {
        if (state.activeRealm !== 'all' && cm.realm !== state.activeRealm) return;
        if (!cm.discovered && !showUndisc) return;

        if (query) {
          const fullText = `${cm.title} ${cm.region || ''} ${cm.notes || ''}`.toLowerCase();
          if (!fullText.includes(query)) return;
        }

        const catInfo = CATEGORY_MAP[cm.category] || CATEGORY_MAP.note;
        const pin = document.createElement('div');
        pin.className = 'custom-pin';
        if (cm.discovered) pin.classList.add('discovered');

        pin.style.left = `${cm.coords.x}%`;
        pin.style.top = `${cm.coords.y}%`;
        pin.dataset.id = cm.id;

        const pinColor = cm.color || catInfo.defaultColor;

        pin.innerHTML = `
          <div class="custom-pin-icon" style="color: ${pinColor}; border-color: ${pinColor};">
            ${catInfo.icon}
          </div>
          <div class="grace-pin-tooltip" style="border-color: ${pinColor};">
            ${cm.discovered ? '✓ ' : '✦ '}${cm.title} [${catInfo.label}]
          </div>
        `;

        pin.addEventListener('click', (e) => {
          e.stopPropagation();
          openItemDrawer(cm, 'custom');
        });

        dom.pinsContainer.appendChild(pin);
      });
    }
  }

  // Map Pan & Zoom
  function updateMapTransform() {
    dom.mapWorld.style.transform = `translate(${state.mapPan.x}px, ${state.mapPan.y}px) scale(${state.mapZoom})`;
  }

  function centerMap(targetX = 50, targetY = 50) {
    const vpRect = dom.mapViewport.getBoundingClientRect();
    const worldW = parseFloat(dom.mapWorld.style.width) || 2600;
    const worldH = parseFloat(dom.mapWorld.style.height) || 2463;

    const pixelTargetX = worldW * (targetX / 100);
    const pixelTargetY = worldH * (targetY / 100);

    state.mapPan.x = vpRect.width / 2 - pixelTargetX * state.mapZoom;
    state.mapPan.y = vpRect.height / 2 - pixelTargetY * state.mapZoom;
    updateMapTransform();
  }

  // ==========================================
  // CUSTOM MARKER CREATION & MANAGEMENT
  // ==========================================
  function setAddMarkerMode(active) {
    state.addMarkerMode = active;
    if (active) {
      dom.btnAddMarkerMode.classList.add('active');
      dom.addMarkerBanner.style.display = 'flex';
      dom.mapViewport.classList.add('adding-marker');
      showToast('📍 Haritada işaret eklemek istediğiniz noktaya tıklayın');
    } else {
      dom.btnAddMarkerMode.classList.remove('active');
      dom.addMarkerBanner.style.display = 'none';
      dom.mapViewport.classList.remove('adding-marker');
    }
  }

  function openCreateMarkerModal(pctX, pctY) {
    setAddMarkerMode(false);

    dom.markerFormId.value = '';
    dom.markerFormX.value = pctX.toFixed(2);
    dom.markerFormY.value = pctY.toFixed(2);
    dom.markerFormRealm.value = state.activeRealm;
    dom.markerFormTitle.value = '';
    dom.markerFormCategory.value = 'treasure';
    dom.markerFormNotes.value = '';
    dom.markerFormDiscovered.checked = false;

    // Detect closest region name based on nearby grace
    let closestRegion = 'Limgrave';
    let minDist = Infinity;
    state.graces.forEach(g => {
      if (g.realm === state.activeRealm) {
        const dx = g.map_coords.x - pctX;
        const dy = g.map_coords.y - pctY;
        const d = dx * dx + dy * dy;
        if (d < minDist) {
          minDist = d;
          closestRegion = g.region_tr;
        }
      }
    });
    dom.markerFormRegion.value = closestRegion;

    dom.markerCoordsReadout.textContent = `X: ${pctX.toFixed(2)}%, Y: ${pctY.toFixed(2)}%`;
    dom.modalMarkerTitleHeading.textContent = '✦ YENİ KEŞİF / İŞARET EKLE';

    // Reset color swatch
    selectColorSwatch('#ecbd4a');

    dom.modalMarkerBackdrop.style.display = 'flex';
    setTimeout(() => dom.markerFormTitle.focus(), 80);
  }

  function openEditMarkerModal(marker) {
    dom.modalBackdrop.classList.remove('open'); // close drawer

    dom.markerFormId.value = marker.id;
    dom.markerFormX.value = marker.coords.x;
    dom.markerFormY.value = marker.coords.y;
    dom.markerFormRealm.value = marker.realm;
    dom.markerFormTitle.value = marker.title;
    dom.markerFormCategory.value = marker.category;
    dom.markerFormRegion.value = marker.region || '';
    dom.markerFormNotes.value = marker.notes || '';
    dom.markerFormDiscovered.checked = !!marker.discovered;

    dom.markerCoordsReadout.textContent = `X: ${marker.coords.x}%, Y: ${marker.coords.y}%`;
    dom.modalMarkerTitleHeading.textContent = '✦ İŞARETİ DÜZENLE';

    selectColorSwatch(marker.color || '#ecbd4a');

    dom.modalMarkerBackdrop.style.display = 'flex';
    setTimeout(() => dom.markerFormTitle.focus(), 80);
  }

  function selectColorSwatch(color) {
    dom.markerFormColor.value = color;
    dom.markerColorPalette.querySelectorAll('.color-swatch').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.color.toLowerCase() === color.toLowerCase());
    });
  }

  function closeMarkerModal() {
    dom.modalMarkerBackdrop.style.display = 'none';
  }

  function handleSaveCustomMarker(e) {
    e.preventDefault();

    const title = dom.markerFormTitle.value.trim();
    if (!title) return;

    const id = dom.markerFormId.value || `custom-${Date.now()}`;
    const x = parseFloat(dom.markerFormX.value) || 50;
    const y = parseFloat(dom.markerFormY.value) || 50;
    const realm = dom.markerFormRealm.value || state.activeRealm;
    const category = dom.markerFormCategory.value;
    const region = dom.markerFormRegion.value.trim();
    const color = dom.markerFormColor.value || '#ecbd4a';
    const notes = dom.markerFormNotes.value.trim();
    const discovered = dom.markerFormDiscovered.checked;

    const markerData = {
      id,
      title,
      category,
      region,
      color,
      notes,
      coords: { x, y },
      realm,
      discovered,
      created_at: new Date().toISOString()
    };

    const existingIndex = state.customMarkers.findIndex(m => m.id === id);
    if (existingIndex >= 0) {
      state.customMarkers[existingIndex] = markerData;
      showToast(`✦ "${title}" güncellendi!`);
    } else {
      state.customMarkers.push(markerData);
      showToast(`✦ Yeni keşif eklendi: "${title}"`);
    }

    closeMarkerModal();
    triggerSave();
    renderMapPins();
    updateCustomMarkerCounter();
  }

  function deleteCustomMarker(markerId) {
    const idx = state.customMarkers.findIndex(m => m.id === markerId);
    if (idx < 0) return;

    const title = state.customMarkers[idx].title;
    state.customMarkers.splice(idx, 1);

    triggerSave();
    renderMapPins();
    updateCustomMarkerCounter();
    closeGraceDrawer();
    renderManageMarkersList();
    showToast(`🗑️ "${title}" haritadan kaldırıldı.`);
  }

  function updateCustomMarkerCounter() {
    if (dom.customMarkerCount) {
      dom.customMarkerCount.textContent = state.customMarkers.length;
    }
  }

  function openManageMarkersModal() {
    renderManageMarkersList();
    dom.modalManageBackdrop.style.display = 'flex';
  }

  function closeManageMarkersModal() {
    dom.modalManageBackdrop.style.display = 'none';
  }

  function renderManageMarkersList() {
    dom.manageMarkersList.innerHTML = '';
    dom.manageMarkersCountLabel.textContent = `Toplam ${state.customMarkers.length} özel işaret`;

    if (state.customMarkers.length === 0) {
      dom.manageMarkersList.innerHTML = `
        <div style="text-align:center; padding: 30px; color: var(--text-dim); font-size: 13px;">
          Henüz hiç özel işaret eklemediniz.<br>
          Harita üzerindeki <strong>[➕ İşaret Ekle]</strong> butonu ile istediğiniz yere işaret koyabilirsiniz!
        </div>
      `;
      return;
    }

    state.customMarkers.forEach(cm => {
      const cat = CATEGORY_MAP[cm.category] || CATEGORY_MAP.note;
      const item = document.createElement('div');
      item.className = 'manage-marker-item';

      item.innerHTML = `
        <div class="marker-item-info">
          <div class="marker-item-icon" style="color: ${cm.color || cat.defaultColor}; border-color: ${cm.color || cat.defaultColor};">
            ${cat.icon}
          </div>
          <div>
            <div class="marker-item-title">${cm.title}</div>
            <div class="marker-item-meta">${cat.label} • ${cm.region || 'Bölge'} (X: ${cm.coords.x}%, Y: ${cm.coords.y}%)</div>
          </div>
        </div>
        <div class="marker-item-actions">
          <button class="btn btn-subtle-sm btn-focus-marker" title="Haritada Göster">📍 Git</button>
          <button class="btn btn-danger-sm btn-del-marker" title="Haritadan Sil">🗑️ Sil</button>
        </div>
      `;

      item.querySelector('.btn-focus-marker').addEventListener('click', () => {
        closeManageMarkersModal();
        switchView('map');
        if (state.activeRealm !== cm.realm) {
          updateMapRealm(cm.realm);
          const realmBtn = dom.mapRealmTabs.querySelector(`[data-realm="${cm.realm}"]`);
          if (realmBtn) {
            dom.mapRealmTabs.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            realmBtn.classList.add('active');
          }
        }
        centerMap(cm.coords.x, cm.coords.y);
        setTimeout(() => openItemDrawer(cm, 'custom'), 250);
      });

      item.querySelector('.btn-del-marker').addEventListener('click', () => {
        if (confirm(`"${cm.title}" işaretini haritadan silmek istediğinize emin misiniz?`)) {
          deleteCustomMarker(cm.id);
        }
      });

      dom.manageMarkersList.appendChild(item);
    });
  }

  // ==========================================
  // DRAWER / MODAL HANDLING (Graces, Bosses, Custom)
  // ==========================================
  function openItemDrawer(item, itemType) {
    state.selectedItem = item;
    state.selectedItemType = itemType;

    // Reset visibility of type-specific buttons
    dom.drawerBtnEditCustom.style.display = 'none';
    dom.drawerBtnDeleteCustom.style.display = 'none';
    dom.drawerBtnWiki.style.display = 'inline-flex';

    if (itemType === 'grace') {
      dom.drawerRealm.textContent = item.realm_tr;
      dom.drawerName.textContent = item.name;
      dom.drawerRegion.textContent = `${item.region_tr} • ${item.subregion_tr}`;
      dom.drawerType.textContent = item.type_tr;
      dom.drawerType.className = `type-badge ${item.type.toLowerCase().replace(' ', '-')}`;
      dom.drawerDesc.textContent = item.description_tr;
      dom.drawerCoords.textContent = `Harita Koordinatları: X: ${item.map_coords.x}%, Y: ${item.map_coords.y}%`;

      const note = state.notesMap[item.id] || '';
      dom.drawerNotes.value = note;
      dom.drawerBtnWiki.href = item.wiki_url || `https://eldenring.fandom.com/wiki/${encodeURIComponent(item.name.replace(/ /g, '_'))}`;

      updateDrawerStatus();
      updateDrawerFavorite();

    } else if (itemType === 'boss') {
      dom.drawerRealm.textContent = item.realm === 'The Lands Between' ? 'Ara Topraklar' : 'Gölge Diyarı (DLC)';
      dom.drawerName.textContent = item.name;
      dom.drawerRegion.textContent = 'Boss Karşılaşması';
      dom.drawerType.textContent = '⚔️ Boss Arenası';
      dom.drawerType.className = 'type-badge boss';
      dom.drawerDesc.textContent = item.runes ? `Zafer Ödülü: ${item.runes.toLocaleString()} Rün` : 'Güçlü düşman arenası.';
      dom.drawerCoords.textContent = `Harita Koordinatları: X: ${item.map_coords.x}%, Y: ${item.map_coords.y}%`;

      const note = state.notesMap[item.id] || '';
      dom.drawerNotes.value = note;
      dom.drawerBtnWiki.href = `https://eldenring.fandom.com/wiki/${encodeURIComponent(item.name.replace(/ /g, '_'))}`;

      const isDefeated = state.defeatedBossesSet.has(item.id);
      dom.drawerStatus.textContent = isDefeated ? '✓ Mağlup Edildi' : '⚔️ Bekliyor';
      dom.drawerStatus.className = `status-badge ${isDefeated ? 'disc' : ''}`;
      dom.drawerBtnToggleDisc.textContent = isDefeated ? '✕ Mağlup Edilmedi Olarak İşaretle' : '⚔️ Boss Mağlup Edildi!';
      dom.drawerBtnToggleDisc.className = isDefeated ? 'btn btn-subtle' : 'btn btn-gold-lg';
      dom.drawerBtnToggleFav.style.display = 'none';

    } else if (itemType === 'custom') {
      const cat = CATEGORY_MAP[item.category] || CATEGORY_MAP.note;
      dom.drawerRealm.textContent = item.realm === 'The Lands Between' ? 'Ara Topraklar' : 'Gölge Diyarı (DLC)';
      dom.drawerName.textContent = item.title;
      dom.drawerRegion.textContent = item.region || 'Özel Keşif';
      dom.drawerType.textContent = `${cat.icon} ${cat.label}`;
      dom.drawerType.className = 'type-badge custom';
      dom.drawerDesc.textContent = item.notes || 'Bu işaret için özel açıklama girilmedi.';
      dom.drawerCoords.textContent = `Harita Koordinatları: X: ${item.coords.x}%, Y: ${item.coords.y}%`;

      dom.drawerNotes.value = item.notes || '';
      dom.drawerBtnWiki.style.display = 'none';

      const isDisc = !!item.discovered;
      dom.drawerStatus.textContent = isDisc ? '✓ Keşfedildi / Temizlendi' : '○ Keşfedilmedi';
      dom.drawerStatus.className = `status-badge ${isDisc ? 'disc' : ''}`;
      dom.drawerBtnToggleDisc.textContent = isDisc ? '✕ Keşfedilmedi Yap' : '✦ Keşfedildi Olarak İşaretle';
      dom.drawerBtnToggleDisc.className = isDisc ? 'btn btn-subtle' : 'btn btn-gold-lg';
      dom.drawerBtnToggleFav.style.display = 'none';

      // Show Custom Actions
      dom.drawerBtnEditCustom.style.display = 'inline-flex';
      dom.drawerBtnDeleteCustom.style.display = 'inline-flex';
    }

    dom.modalBackdrop.classList.add('open');
  }

  function closeGraceDrawer() {
    dom.modalBackdrop.classList.remove('open');
    state.selectedItem = null;
    state.selectedItemType = null;
  }

  function updateDrawerStatus() {
    if (!state.selectedItem) return;

    if (state.selectedItemType === 'grace') {
      const isDisc = state.discoveredSet.has(state.selectedItem.id);
      dom.drawerStatus.textContent = isDisc ? '✓ Keşfedildi' : '○ Keşfedilmedi';
      dom.drawerStatus.className = `status-badge ${isDisc ? 'disc' : ''}`;
      dom.drawerBtnToggleDisc.textContent = isDisc ? '✕ Keşfedilmedi Olarak İşaretle' : '✦ Keşfedildi Olarak İşaretle';
      dom.drawerBtnToggleDisc.className = isDisc ? 'btn btn-subtle' : 'btn btn-gold-lg';
      dom.drawerBtnToggleFav.style.display = 'inline-flex';
    }
  }

  function updateDrawerFavorite() {
    if (!state.selectedItem || state.selectedItemType !== 'grace') return;
    const isFav = state.favoriteSet.has(state.selectedItem.id);
    dom.drawerBtnToggleFav.textContent = isFav ? '★ Favorilerden Kaldır' : '☆ Favorilere Ekle';
  }

  function toggleDrawerItemStatus() {
    if (!state.selectedItem) return;

    if (state.selectedItemType === 'grace') {
      toggleDiscovered(state.selectedItem.id);
    } else if (state.selectedItemType === 'boss') {
      const bId = state.selectedItem.id;
      if (state.defeatedBossesSet.has(bId)) {
        state.defeatedBossesSet.delete(bId);
      } else {
        state.defeatedBossesSet.add(bId);
        playGraceChime();
      }
      triggerSave();
      renderMapPins();
      openItemDrawer(state.selectedItem, 'boss');
      showToast(state.defeatedBossesSet.has(bId) ? '⚔️ Boss mağlup edildi!' : 'Boss durumu sıfırlandı.');
    } else if (state.selectedItemType === 'custom') {
      state.selectedItem.discovered = !state.selectedItem.discovered;
      triggerSave();
      renderMapPins();
      openItemDrawer(state.selectedItem, 'custom');
      showToast(state.selectedItem.discovered ? '✦ Keşfedildi olarak işaretlendi!' : 'Keşif durumu güncellendi.');
    }
  }

  // ==========================================
  // LIST / CARD EXPLORER RENDERING
  // ==========================================
  function getFilteredGraces() {
    let filtered = [...state.graces];

    // Realm
    if (state.activeRealm !== 'all') {
      filtered = filtered.filter(g => g.realm === state.activeRealm);
    }

    // Status
    if (state.activeStatus === 'discovered') {
      filtered = filtered.filter(g => state.discoveredSet.has(g.id));
    } else if (state.activeStatus === 'undiscovered') {
      filtered = filtered.filter(g => !state.discoveredSet.has(g.id));
    } else if (state.activeStatus === 'favorite') {
      filtered = filtered.filter(g => state.favoriteSet.has(g.id));
    }

    // Region
    if (state.activeRegion !== 'all') {
      filtered = filtered.filter(g => g.region_tr === state.activeRegion);
    }

    // Type
    if (state.activeType !== 'all') {
      filtered = filtered.filter(g => g.type === state.activeType);
    }

    // Search query
    if (state.searchQuery) {
      const q = state.searchQuery.toLowerCase();
      filtered = filtered.filter(g => {
        return (
          g.name.toLowerCase().includes(q) ||
          g.region_tr.toLowerCase().includes(q) ||
          g.subregion_tr.toLowerCase().includes(q) ||
          g.type_tr.toLowerCase().includes(q) ||
          (state.notesMap[g.id] && state.notesMap[g.id].toLowerCase().includes(q))
        );
      });
    }

    // Sorting
    if (state.sortOrder === 'name') {
      filtered.sort((a, b) => a.name.localeCompare(b.name, 'tr'));
    } else if (state.sortOrder === 'region') {
      filtered.sort((a, b) => a.region_tr.localeCompare(b.region_tr, 'tr'));
    }

    return filtered;
  }

  function renderCards() {
    const graces = getFilteredGraces();
    dom.cardsResultsCount.textContent = `(${graces.length} Lütuf)`;
    dom.cardsGrid.innerHTML = '';

    if (graces.length === 0) {
      dom.emptyState.style.display = 'block';
      return;
    }
    dom.emptyState.style.display = 'none';

    graces.forEach(g => {
      const isDisc = state.discoveredSet.has(g.id);
      const isFav = state.favoriteSet.has(g.id);
      const hasNote = !!state.notesMap[g.id];

      const card = document.createElement('div');
      card.className = `grace-card ${isDisc ? 'discovered' : ''}`;
      card.dataset.id = g.id;

      card.innerHTML = `
        <div class="card-status-indicator"></div>
        <div class="card-header">
          <div class="card-title-box">
            <span class="card-realm">${g.realm_tr}</span>
            <h3 class="card-title">${g.name}</h3>
            <span class="card-region">📍 ${g.region_tr} • ${g.subregion_tr}</span>
          </div>
          <button class="card-fav-btn ${isFav ? 'active' : ''}" title="${isFav ? 'Favorilerden çıkar' : 'Favorilere ekle'}">
            ${isFav ? '★' : '☆'}
          </button>
        </div>

        <div class="card-badges">
          <span class="type-badge ${g.type.toLowerCase().replace(' ', '-')}">${g.type_tr}</span>
          ${hasNote ? '<span class="type-badge" style="background:rgba(212,169,66,0.18); color:var(--gold-light);">📝 Not var</span>' : ''}
        </div>

        <p class="card-desc">${g.description_tr}</p>

        <div class="card-footer">
          <div class="card-coords">X: ${g.map_coords.x}%, Y: ${g.map_coords.y}%</div>
          <div class="card-actions">
            <button class="btn btn-outline-sm btn-map-focus" title="Haritada Konumu Göster">🗺️ Haritada Gör</button>
            <button class="btn ${isDisc ? 'btn-subtle-sm' : 'btn-gold-sm'} btn-card-toggle">
              ${isDisc ? '✓ Keşfedildi' : '✦ Keşfet'}
            </button>
          </div>
        </div>
      `;

      card.querySelector('.card-fav-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        toggleFavorite(g.id);
      });

      card.querySelector('.btn-card-toggle').addEventListener('click', (e) => {
        e.stopPropagation();
        toggleDiscovered(g.id);
      });

      card.querySelector('.btn-map-focus').addEventListener('click', (e) => {
        e.stopPropagation();
        focusOnMap(g);
      });

      card.addEventListener('click', () => {
        openItemDrawer(g, 'grace');
      });

      dom.cardsGrid.appendChild(card);
    });
  }

  // ==========================================
  // DISCOVERY & FAVORITE ACTIONS
  // ==========================================
  function toggleDiscovered(id) {
    if (state.discoveredSet.has(id)) {
      state.discoveredSet.delete(id);
    } else {
      state.discoveredSet.add(id);
      playGraceChime();
    }

    triggerSave();
    updateStats();

    if (state.activeView === 'list') {
      renderCards();
    } else if (state.activeView === 'map') {
      renderMapPins();
    }

    if (state.selectedItem && state.selectedItem.id === id) {
      updateDrawerStatus();
    }
  }

  function toggleFavorite(id) {
    if (state.favoriteSet.has(id)) {
      state.favoriteSet.delete(id);
    } else {
      state.favoriteSet.add(id);
    }

    triggerSave();
    if (state.activeView === 'list') {
      renderCards();
    }
    if (state.selectedItem && state.selectedItem.id === id) {
      updateDrawerFavorite();
    }
  }

  function focusOnMap(grace) {
    switchView('map');
    if (state.activeRealm !== grace.realm) {
      updateMapRealm(grace.realm);
      const realmBtn = dom.mapRealmTabs.querySelector(`[data-realm="${grace.realm}"]`);
      if (realmBtn) {
        dom.mapRealmTabs.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        realmBtn.classList.add('active');
      }
    }
    centerMap(grace.map_coords.x, grace.map_coords.y);
    setTimeout(() => openItemDrawer(grace, 'grace'), 250);
  }

  // ==========================================
  // STATS DASHBOARD RENDERING
  // ==========================================
  function updateStats() {
    const total = state.graces.length;
    const discTotal = state.discoveredSet.size;
    const pctTotal = total > 0 ? (discTotal / total * 100).toFixed(1) : '0.0';

    if (dom.statTotalCount) dom.statTotalCount.textContent = `${discTotal} / ${total}`;
    if (dom.statTotalPct) dom.statTotalPct.textContent = `%${pctTotal}`;
    if (dom.statTotalBar) dom.statTotalBar.style.width = `${pctTotal}%`;
  }

  function renderStatsDashboard() {
    const total = state.graces.length;
    const discTotal = state.discoveredSet.size;
    const pctTotal = total > 0 ? (discTotal / total * 100).toFixed(1) : '0.0';

    dom.dashTotalVal.textContent = `${discTotal} / ${total}`;
    dom.dashTotalPct.textContent = `%${pctTotal} Tamamlandı`;

    // Base vs DLC
    const baseGraces = state.graces.filter(g => g.realm === 'The Lands Between');
    const baseDisc = baseGraces.filter(g => state.discoveredSet.has(g.id)).length;
    const basePct = baseGraces.length > 0 ? (baseDisc / baseGraces.length * 100).toFixed(1) : '0.0';
    dom.dashBaseVal.textContent = `${baseDisc} / ${baseGraces.length}`;
    dom.dashBasePct.textContent = `%${basePct} Tamamlandı`;

    const dlcGraces = state.graces.filter(g => g.realm === 'Shadow of the Erdtree');
    const dlcDisc = dlcGraces.filter(g => state.discoveredSet.has(g.id)).length;
    const dlcPct = dlcGraces.length > 0 ? (dlcDisc / dlcGraces.length * 100).toFixed(1) : '0.0';
    dom.dashDlcVal.textContent = `${dlcDisc} / ${dlcGraces.length}`;
    dom.dashDlcPct.textContent = `%${dlcPct} Tamamlandı`;

    // Bosses
    const totalBosses = state.bosses.length;
    const defBosses = state.defeatedBossesSet.size;
    const bossPct = totalBosses > 0 ? (defBosses / totalBosses * 100).toFixed(1) : '0.0';
    dom.dashBossVal.textContent = `${defBosses} / ${totalBosses}`;
    dom.dashBossPct.textContent = `%${bossPct} Mağlup Edildi`;

    // Regions Grid
    const regionMap = new Map();
    state.graces.forEach(g => {
      const reg = g.region_tr;
      if (!regionMap.has(reg)) {
        regionMap.set(reg, { total: 0, disc: 0, graces: [] });
      }
      const item = regionMap.get(reg);
      item.total++;
      item.graces.push(g);
      if (state.discoveredSet.has(g.id)) item.disc++;
    });

    dom.regionsProgressGrid.innerHTML = '';
    const sorted = Array.from(regionMap.entries()).sort((a, b) => a[0].localeCompare(b[0], 'tr'));

    sorted.forEach(([name, data]) => {
      const pct = (data.disc / data.total * 100).toFixed(0);
      const card = document.createElement('div');
      card.className = 'region-progress-card';

      card.innerHTML = `
        <div class="region-card-header">
          <span class="region-card-name">${name}</span>
          <span class="region-card-stats">${data.disc} / ${data.total} (%${pct})</span>
        </div>
        <div class="region-progress-track">
          <div class="region-progress-bar" style="width: ${pct}%"></div>
        </div>
      `;

      card.addEventListener('click', () => {
        state.activeRegion = name;
        dom.selectRegion.value = name;
        switchView('list');
      });

      dom.regionsProgressGrid.appendChild(card);
    });
  }

  // ==========================================
  // EVENT LISTENERS & SHORTCUTS
  // ==========================================
  function setupEventListeners() {
    // View switching
    dom.btnViewMap.addEventListener('click', () => switchView('map'));
    dom.btnViewList.addEventListener('click', () => switchView('list'));
    dom.btnViewStats.addEventListener('click', () => switchView('stats'));

    // Audio toggle
    dom.btnAudioToggle.addEventListener('click', () => {
      state.audioEnabled = !state.audioEnabled;
      dom.audioIcon.textContent = state.audioEnabled ? '🔔' : '🔕';
      showToast(state.audioEnabled ? 'Lütuf sesleri açıldı 🔔' : 'Sesler sessize alındı 🔕');
    });

    // Manual Save
    dom.btnSaveManual.addEventListener('click', () => triggerSave(true));

    // Content Layer Checkboxes
    if (dom.toggleLayerGraces) {
      dom.toggleLayerGraces.addEventListener('change', (e) => {
        state.layers.graces = e.target.checked;
        renderMapPins();
      });
    }
    if (dom.toggleLayerBosses) {
      dom.toggleLayerBosses.addEventListener('change', (e) => {
        state.layers.bosses = e.target.checked;
        renderMapPins();
      });
    }
    if (dom.toggleLayerCustom) {
      dom.toggleLayerCustom.addEventListener('change', (e) => {
        state.layers.custom = e.target.checked;
        renderMapPins();
      });
    }

    // Add Marker Mode Button
    if (dom.btnAddMarkerMode) {
      dom.btnAddMarkerMode.addEventListener('click', () => {
        setAddMarkerMode(!state.addMarkerMode);
      });
    }
    if (dom.btnCancelAddMarkerMode) {
      dom.btnCancelAddMarkerMode.addEventListener('click', () => {
        setAddMarkerMode(false);
      });
    }

    // Manage Custom Markers Button
    if (dom.btnManageCustomMarkers) {
      dom.btnManageCustomMarkers.addEventListener('click', openManageMarkersModal);
    }
    if (dom.btnCloseManageModal) {
      dom.btnCloseManageModal.addEventListener('click', closeManageMarkersModal);
    }
    if (dom.btnClearAllCustomMarkers) {
      dom.btnClearAllCustomMarkers.addEventListener('click', () => {
        if (state.customMarkers.length === 0) return;
        if (confirm('Tüm özel işaretleriniz silinecek! Emin misiniz?')) {
          state.customMarkers = [];
          triggerSave();
          renderMapPins();
          updateCustomMarkerCounter();
          renderManageMarkersList();
          showToast('Tüm özel işaretler temizlendi.');
        }
      });
    }

    // Custom Marker Modal Form & Palette
    if (dom.btnCloseMarkerModal) dom.btnCloseMarkerModal.addEventListener('click', closeMarkerModal);
    if (dom.btnCancelMarkerForm) dom.btnCancelMarkerForm.addEventListener('click', closeMarkerModal);
    if (dom.formCustomMarker) dom.formCustomMarker.addEventListener('submit', handleSaveCustomMarker);

    if (dom.markerColorPalette) {
      dom.markerColorPalette.querySelectorAll('.color-swatch').forEach(btn => {
        btn.addEventListener('click', () => {
          selectColorSwatch(btn.dataset.color);
        });
      });
    }

    // Map dragging & panning & click-to-add
    dom.mapViewport.addEventListener('mousedown', (e) => {
      if (e.button !== 0) return;
      state.isDraggingMap = true;
      state.dragStart.x = e.clientX - state.mapPan.x;
      state.dragStart.y = e.clientY - state.mapPan.y;
    });

    window.addEventListener('mousemove', (e) => {
      if (!state.isDraggingMap) return;
      state.mapPan.x = e.clientX - state.dragStart.x;
      state.mapPan.y = e.clientY - state.dragStart.y;
      updateMapTransform();
    });

    window.addEventListener('mouseup', () => {
      state.isDraggingMap = false;
    });

    // Map Click (for Add Marker Mode)
    dom.mapViewport.addEventListener('click', (e) => {
      if (!state.addMarkerMode) return;

      // Ensure we clicked inside mapWorld
      const worldRect = dom.mapWorld.getBoundingClientRect();
      if (
        e.clientX >= worldRect.left &&
        e.clientX <= worldRect.right &&
        e.clientY >= worldRect.top &&
        e.clientY <= worldRect.bottom
      ) {
        const pctX = ((e.clientX - worldRect.left) / worldRect.width) * 100;
        const pctY = ((e.clientY - worldRect.top) / worldRect.height) * 100;
        openCreateMarkerModal(pctX, pctY);
      }
    });

    // Map Zooming
    dom.mapViewport.addEventListener('wheel', (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.15 : 0.87;
      const newZoom = Math.min(3.5, Math.max(0.4, state.mapZoom * zoomFactor));

      const rect = dom.mapViewport.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;

      state.mapPan.x = mouseX - (mouseX - state.mapPan.x) * (newZoom / state.mapZoom);
      state.mapPan.y = mouseY - (mouseY - state.mapPan.y) * (newZoom / state.mapZoom);
      state.mapZoom = newZoom;
      updateMapTransform();
    }, { passive: false });

    dom.btnZoomIn.addEventListener('click', () => {
      state.mapZoom = Math.min(3.5, state.mapZoom * 1.25);
      updateMapTransform();
    });

    dom.btnZoomOut.addEventListener('click', () => {
      state.mapZoom = Math.max(0.4, state.mapZoom / 1.25);
      updateMapTransform();
    });

    dom.btnZoomReset.addEventListener('click', () => {
      state.mapZoom = 0.85;
      centerMap();
    });

    if (dom.btnFullscreenMap) {
      dom.btnFullscreenMap.addEventListener('click', () => {
        dom.viewMap.classList.toggle('fullscreen');
        const isFull = dom.viewMap.classList.contains('fullscreen');
        dom.btnFullscreenMap.textContent = isFull ? '✕' : '⛶';
        centerMap();
      });
    }

    // Map search & filters
    dom.mapSearchInput.addEventListener('input', renderMapPins);
    dom.mapToggleUndiscovered.addEventListener('change', (e) => {
      state.layers.undiscovered = e.target.checked;
      renderMapPins();
    });

    // Map Realm Tabs (Lands Between vs Shadow of Erdtree)
    dom.mapRealmTabs.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        dom.mapRealmTabs.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        updateMapRealm(btn.dataset.realm);
      });
    });

    // Map Mode Tabs (Real In-Game vs Parchment)
    if (dom.mapModeTabs) {
      dom.mapModeTabs.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          dom.mapModeTabs.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          state.mapMode = btn.dataset.mode;

          if (state.mapMode === 'real') {
            dom.mapImageLayer.style.display = 'block';
            dom.mapCanvas.style.display = 'none';
          } else {
            dom.mapImageLayer.style.display = 'none';
            dom.mapCanvas.style.display = 'block';
            renderMapCanvas();
          }
        });
      });
    }

    // List search & filters
    dom.listSearchInput.addEventListener('input', (e) => {
      state.searchQuery = e.target.value.trim();
      dom.btnClearSearch.style.display = state.searchQuery ? 'block' : 'none';
      renderCards();
    });

    dom.btnClearSearch.addEventListener('click', () => {
      dom.listSearchInput.value = '';
      state.searchQuery = '';
      dom.btnClearSearch.style.display = 'none';
      renderCards();
    });

    // Realm Pills
    dom.pillsRealm.querySelectorAll('.pill').forEach(btn => {
      btn.addEventListener('click', () => {
        dom.pillsRealm.querySelectorAll('.pill').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.activeRealm = btn.dataset.realm;
        renderCards();
      });
    });

    // Status Pills
    dom.pillsStatus.querySelectorAll('.pill').forEach(btn => {
      btn.addEventListener('click', () => {
        dom.pillsStatus.querySelectorAll('.pill').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.activeStatus = btn.dataset.status;
        renderCards();
      });
    });

    // Type Pills
    dom.pillsType.querySelectorAll('.pill').forEach(btn => {
      btn.addEventListener('click', () => {
        dom.pillsType.querySelectorAll('.pill').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.activeType = btn.dataset.type;
        renderCards();
      });
    });

    dom.selectRegion.addEventListener('change', (e) => {
      state.activeRegion = e.target.value;
      renderCards();
    });

    dom.selectSort.addEventListener('change', (e) => {
      state.sortOrder = e.target.value;
      renderCards();
    });

    dom.btnResetFilters.addEventListener('click', () => {
      state.searchQuery = '';
      dom.listSearchInput.value = '';
      dom.btnClearSearch.style.display = 'none';
      state.activeRealm = 'all';
      state.activeStatus = 'all';
      state.activeType = 'all';
      state.activeRegion = 'all';
      dom.selectRegion.value = 'all';

      dom.pillsRealm.querySelector('[data-realm="all"]').click();
      dom.pillsStatus.querySelector('[data-status="all"]').click();
      dom.pillsType.querySelector('[data-type="all"]').click();
      renderCards();
    });

    // Batch Actions
    dom.btnBatchDiscover.addEventListener('click', () => {
      const list = getFilteredGraces();
      if (list.length === 0) return;
      list.forEach(g => state.discoveredSet.add(g.id));
      playGraceChime();
      triggerSave();
      updateStats();
      renderCards();
      showToast(`${list.length} lütuf keşfedildi olarak işaretlendi! ✦`);
    });

    dom.btnBatchReset.addEventListener('click', () => {
      const list = getFilteredGraces();
      if (list.length === 0) return;
      if (!confirm(`${list.length} adet lütuf sıfırlansın mı?`)) return;
      list.forEach(g => state.discoveredSet.delete(g.id));
      triggerSave();
      updateStats();
      renderCards();
      showToast(`${list.length} lütuf sıfırlandı.`);
    });

    // Drawer Buttons & Inputs
    dom.btnCloseDrawer.addEventListener('click', closeGraceDrawer);
    dom.modalBackdrop.addEventListener('click', (e) => {
      if (e.target === dom.modalBackdrop) closeGraceDrawer();
    });

    dom.drawerBtnToggleDisc.addEventListener('click', () => {
      toggleDrawerItemStatus();
    });

    dom.drawerBtnToggleFav.addEventListener('click', () => {
      if (state.selectedItem && state.selectedItemType === 'grace') {
        toggleFavorite(state.selectedItem.id);
      }
    });

    dom.drawerBtnEditCustom.addEventListener('click', () => {
      if (state.selectedItem && state.selectedItemType === 'custom') {
        openEditMarkerModal(state.selectedItem);
      }
    });

    dom.drawerBtnDeleteCustom.addEventListener('click', () => {
      if (state.selectedItem && state.selectedItemType === 'custom') {
        if (confirm(`"${state.selectedItem.title}" işaretini haritadan kaldırmak istediğinize emin misiniz?`)) {
          deleteCustomMarker(state.selectedItem.id);
        }
      }
    });

    dom.drawerNotes.addEventListener('input', (e) => {
      if (!state.selectedItem) return;
      state.notesMap[state.selectedItem.id] = e.target.value;
      if (state.selectedItemType === 'custom') {
        state.selectedItem.notes = e.target.value;
      }
      triggerSave();
    });

    // Export & Import
    dom.btnExportSave.addEventListener('click', () => {
      const payload = {
        exported_at: new Date().toISOString(),
        discovered: Array.from(state.discoveredSet),
        favorites: Array.from(state.favoriteSet),
        defeated_bosses: Array.from(state.defeatedBossesSet),
        custom_markers: state.customMarkers,
        notes: state.notesMap
      };
      const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `elden_ring_graces_save_${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
      URL.revokeObjectURL(url);
      showToast('İlerleme dosyası indirildi! 📤');
    });

    dom.inputImportSave.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const parsed = JSON.parse(event.target.result);
          if (parsed.discovered && Array.isArray(parsed.discovered)) {
            state.discoveredSet = new Set(parsed.discovered);
          }
          if (parsed.favorites && Array.isArray(parsed.favorites)) {
            state.favoriteSet = new Set(parsed.favorites);
          }
          if (parsed.defeated_bosses && Array.isArray(parsed.defeated_bosses)) {
            state.defeatedBossesSet = new Set(parsed.defeated_bosses);
          }
          if (parsed.custom_markers && Array.isArray(parsed.custom_markers)) {
            state.customMarkers = parsed.custom_markers;
          }
          if (parsed.notes && typeof parsed.notes === 'object') {
            state.notesMap = parsed.notes;
          }
          triggerSave(true);
          updateStats();
          updateCustomMarkerCounter();
          renderCards();
          renderMapPins();
          showToast('İlerleme başarıyla içe aktarıldı! 📥');
        } catch (err) {
          alert('Hata: Geçersiz JSON dosyası!');
        }
      };
      reader.readAsText(file);
      e.target.value = '';
    });

    dom.btnResetAll.addEventListener('click', () => {
      if (confirm('DİKKAT: Tüm keşif ilerlemeniz, işaretleriniz ve notlarınız sıfırlanacak! Emin misiniz?')) {
        state.discoveredSet.clear();
        state.favoriteSet.clear();
        state.defeatedBossesSet.clear();
        state.customMarkers = [];
        state.notesMap = {};
        fetch('/api/reset', { method: 'POST' });
        localStorage.removeItem('er_grace_progress');
        updateStats();
        updateCustomMarkerCounter();
        renderCards();
        renderMapPins();
        showToast('Tüm ilerleme sıfırlandı.');
      }
    });

    // Global Key Shortcuts
    window.addEventListener('keydown', (e) => {
      if (e.key === '/' && document.activeElement !== dom.listSearchInput && document.activeElement !== dom.drawerNotes && document.activeElement !== dom.mapSearchInput) {
        e.preventDefault();
        switchView('list');
        dom.listSearchInput.focus();
      } else if (e.key === 'Escape') {
        if (state.addMarkerMode) {
          setAddMarkerMode(false);
        } else if (dom.modalMarkerBackdrop.style.display === 'flex') {
          closeMarkerModal();
        } else if (dom.modalManageBackdrop.style.display === 'flex') {
          closeManageMarkersModal();
        } else {
          closeGraceDrawer();
        }
      }
    });
  }

  // ==========================================
  // EMBERS PARTICLE ANIMATION
  // ==========================================
  function initEmbers() {
    const canvas = dom.embersCanvas;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    window.addEventListener('resize', () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    });

    const particles = [];
    const count = 45;

    for (let i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        radius: Math.random() * 2.2 + 0.8,
        speedY: Math.random() * 0.7 + 0.3,
        speedX: (Math.random() - 0.5) * 0.4,
        alpha: Math.random() * 0.7 + 0.2,
        pulseSpeed: Math.random() * 0.02 + 0.005
      });
    }

    function animate() {
      ctx.clearRect(0, 0, width, height);

      particles.forEach(p => {
        p.y -= p.speedY;
        p.x += p.speedX;
        p.alpha += Math.sin(Date.now() * p.pulseSpeed) * 0.008;

        if (p.y < -10) {
          p.y = height + 10;
          p.x = Math.random() * width;
        }

        ctx.fillStyle = `rgba(245, 211, 114, ${Math.max(0.1, Math.min(0.85, p.alpha))})`;
        ctx.shadowColor = '#ffd700';
        ctx.shadowBlur = 8;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fill();
      });

      requestAnimationFrame(animate);
    }

    animate();
  }

  // Start app
  window.addEventListener('DOMContentLoaded', init);
})();
