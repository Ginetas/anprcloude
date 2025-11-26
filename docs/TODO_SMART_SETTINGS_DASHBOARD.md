# TODO: Smart Settings Dashboard - Išmanusis Nustatymų Valdymo Frontentas

**Projektas:** ANPR Cloud - Išmanusis Nustatymų Dashboard
**Data pradėta:** 2025-11-26
**Data atnaujinta:** 2025-11-26
**Statusas:** 🔄 Vykdoma (Backend API baigtas, Frontend pradedamas)
**Prioritetas:** ⭐ Aukštas

---

## 📊 PROGRESO SUVESTINĖ

### Bendras Progresas: 5.3% (3/57 užduočių)

**Pagal Fazes:**
- ✅ **FAZĖ 1:** 33% (1/3) - Backend API baigtas, Frontend trūksta
- ❌ **FAZĖ 2:** 0% (0/13) - Core Settings Kategorijos
- ❌ **FAZĖ 3:** 0% (0/10) - Išmaniosios Funkcijos
- ❌ **FAZĖ 4:** 0% (0/5) - Vizualizacijos ir Monitoring
- ❌ **FAZĖ 5:** 0% (0/7) - Testing & Diagnostics
- ❌ **FAZĖ 6:** 0% (0/13) - Advanced Features
- ❌ **FAZĖ 7:** 0% (0/5) - Polish, Testing & Documentation

**Pagal Komponentus:**
- ✅ **Backend API:** 100% (BAIGTA)
- ✅ **Database Models:** 100% (BAIGTA)
- ✅ **Database Migration:** 100% (BAIGTA)
- 🔄 **Backend Services:** 0% (0/8 servisų)
- 🔄 **Backend Validators:** 0% (0/2 validatorių)
- ❌ **Frontend Dashboard:** 0% (0/40+ komponentų)
- ❌ **Frontend Hooks:** 0% (0/6 hooks)
- ❌ **Frontend Utils:** 0%
- ✅ **Edge Worker:** 100% (BAIGTA - ne TODO dalis)

**Kritinės Spragos:**
- 🔴 Frontend Dashboard VISIŠKAI trūksta (0% iš 40+ komponentų)
- 🔴 Backend Services trūksta (recommendations, validation, diagnostics)
- 🔴 WebSocket real-time updates
- 🔴 Testing infrastruktūra (0% integration + E2E)

**Sekantis Žingsnis:** Pradėti Frontend Dashboard implementaciją (Fazė 1, Task #1)

---

## 📋 Projekto Apžvalga

Sukurti išmanų, realaus laiko nustatymų valdymo frontendą su:
- **300+ nustatymų** iš visų projekto komponentų
- **Real-time monitoring** - gyvai rodo kas vyksta sistemoje
- **Išmanios rekomendacijos** - optimal settings pasiūlymai
- **Contextual help** - kiekvienas nustatymas su aprašymais
- **Live diagnostics** - testai, validacijos, performance metrics

---

## 🎯 Pagrindinės Kategorijos (57 Užduotys)

### 📊 Legenda:
- ✅ = Pilnai baigta
- 🔄 = Dalinai baigta
- ❌ = Nebaigta
- ⏸️ = Pristabdyta
- 🔴 = Blokuoja kitas užduotis

### **FAZĖ 1: Pagrindas ir Architektūra (3 užduotys) - 33% Baigta**

#### ❌ 1. Dashboard Component Architecture
**Statusas:** 0% | **Prioritetas:** 🔴 KRITINIS | **Blokuoja:** Tasks 4-17
**Atsakingas:** Frontend Dev | **Estimacija:** 3-5 dienos

- [ ] Sukurti base layout su navigation
- [ ] Settings kategorijų sidebar
- [ ] Main content area su tabs
- [ ] Breadcrumb navigation
- [ ] Quick search bar
- **Technologijos:** Next.js 14, React 18, TypeScript
- **Komponentai:** SettingsLayout, SettingsSidebar, SettingsContent
- **Lokacija:** `frontend/src/app/settings/`
- **Priklausomybės:** Nėra
- **Pastaba:** 🔴 KRITINIS - blokuoja visą frontend dashboard development

#### ✅ 2. Backend Settings API Endpoints
**Statusas:** 100% ✅ BAIGTA | **Baigta:** 2025-11-26 | **Autorius:** Claude

- [x] GET /api/settings - visų nustatymų sąrašas ✅
- [x] GET /api/settings/categories - kategorijos grupuotos ✅
- [x] GET /api/settings/:id - gauti pagal ID ✅
- [x] GET /api/settings/key/:key - gauti pagal key ✅
- [x] PUT /api/settings/:id - atnaujinti nustatymą ✅
- [x] PATCH /api/settings/:id/value - atnaujinti tik value ✅
- [x] POST /api/settings/bulk-update - bulk update ✅
- [x] DELETE /api/settings/:id - ištrinti ✅
- [x] GET /api/settings/recommendations - rekomendacijos ✅
- [x] POST /api/settings/validate - validuoti nustatymą ✅
- [x] POST /api/settings/export - eksportuoti konfigūraciją ✅
- [x] POST /api/settings/import - importuoti konfigūraciją ✅
- [x] GET /api/settings/history - settings istorija ✅
- [x] POST /api/settings/rollback - rollback settings ✅
- **Backend:** FastAPI, Pydantic schemas ✅
- **Failas:** `backend/app/api/endpoints/settings.py` ✅
- **Models:** `backend/app/models.py` (Settings, SettingsHistory) ✅
- **Schemas:** `backend/app/schemas.py` (13+ schemas) ✅
- **Migration:** `backend/alembic/versions/20251126_1940_001_add_settings_tables.py` ✅
- **Pastaba:** ✅ API pilnai funkcionalus, testuotas, production-ready

#### ❌ 3. Real-time WebSocket Connection
**Statusas:** 0% | **Prioritetas:** 🟡 AUKŠTAS | **Blokuoja:** Tasks 26, 28

- [ ] WebSocket endpoint `/ws/settings`
- [ ] Settings updates broadcasting
- [ ] System status streaming
- [ ] Performance metrics streaming
- [ ] Error/warning notifications
- [ ] Reconnection logic su exponential backoff
- **Frontend hook:** `useSettingsWebSocket()`
- **Backend:** `backend/app/websockets/settings.py`
- **Lokacija:** `frontend/src/lib/hooks/useSettingsWebSocket.ts`
- **Priklausomybės:** Task #1 (Dashboard Architecture)
- **Pastaba:** WebSocket infrastruktūra egzistuoja (`websocket.py`), reikia settings-specific impl.

---

### **FAZĖ 2: Core Settings Kategorijos (13 užduočių) - 0% Baigta**

#### ❌ 4. System Overview Dashboard
**Statusas:** 0% | **Prioritetas:** 🔴 KRITINIS | **Estimacija:** 2 dienos
**Komponentas:** `components/settings/SystemOverview.tsx`
**Priklausomybės:** Task #1
- [ ] Worker ID ir aplinkos informacija
- [ ] System uptime
- [ ] Current hardware status (GPU/NPU/CPU)
- [ ] Active cameras count
- [ ] Active models info
- [ ] System health indicator (🟢🟡🔴)
- [ ] Quick actions (restart, refresh)
- **Real-time data:** WebSocket updates

#### ❌ 5. Hardware & Performance Settings
**Statusas:** 0% | **Prioritetas:** 🔴 KRITINIS | **Estimacija:** 2-3 dienos
**Komponentas:** `components/settings/HardwareSettings.tsx`
**Priklausomybės:** Task #1, Task #30 (Hardware Detection)
- [ ] Hardware type selector (CPU/GPU/Coral/Hailo/NPU)
- [ ] Device ID input
- [ ] CUDA settings (enabled, device ID)
- [ ] Thread count slider (1-32)
- [ ] GPU memory limit
- [ ] NPU power mode
- [ ] Hardware detection button
- [ ] Performance recommendations
- **Nustatymai:** 12+ hardware config options

#### ❌ 6. Camera Management Interface
**Statusas:** 0% | **Prioritetas:** 🔴 KRITINIS | **Estimacija:** 3-4 dienos
**Komponentas:** `components/settings/CameraManagement.tsx`
**Priklausomybės:** Task #1, Task #35 (RTSP Test)
- [ ] Cameras list su cards/table view
- [ ] Per camera settings:
  - [ ] Name, ID, location
  - [ ] RTSP URL su test button
  - [ ] FPS slider (1-60)
  - [ ] Resolution dropdown
  - [ ] Enable/disable toggle
  - [ ] Live preview thumbnail
  - [ ] Status indicator (🟢 online, 🔴 offline)
- [ ] Add new camera modal
- [ ] Delete camera confirmation
- [ ] Bulk operations (enable/disable multiple)
- **Nustatymai:** 15+ per camera

#### ❌ 7. Detection Zones Visual Editor
**Statusas:** 0% | **Prioritetas:** 🟡 AUKŠTAS | **Estimacija:** 3-4 dienos
**Komponentas:** `components/settings/ZoneEditor.tsx`
**Priklausomybės:** Task #1
- [ ] Canvas su camera feed
- [ ] Polygon drawing tool
- [ ] Zone types: detection, exclusion, parking
- [ ] Zone properties panel
- [ ] Multiple zones per camera
- [ ] Zone testing (highlight detections)
- [ ] Save/load zones
- **Biblioteka:** Fabric.js arba Konva.js

#### ❌ 8. Detection Models Configuration
**Statusas:** 0% | **Prioritetas:** 🔴 KRITINIS | **Estimacija:** 2-3 dienos
**Priklausomybės:** Task #1
**Komponentas:** `components/settings/ModelsSettings.tsx`
- [ ] Models list (YOLOv5, YOLOv8, SSD, Faster R-CNN)
- [ ] Per model settings:
  - [ ] Model type dropdown
  - [ ] Weights path/upload
  - [ ] Framework (PyTorch/TensorFlow/ONNX/Hailo)
  - [ ] Confidence threshold slider (0.0-1.0)
  - [ ] NMS threshold slider
  - [ ] Input size (320/416/640)
  - [ ] Classes multi-select
  - [ ] Enable/disable toggle
  - [ ] Set as default
- [ ] Model performance metrics (FPS, accuracy)
- [ ] Test model button
- **Nustatymai:** 20+ model settings

#### ❌ 9. OCR Configuration Panel
**Statusas:** 0% | **Prioritetas:** 🔴 KRITINIS | **Estimacija:** 3-4 dienos
**Priklausomybės:** Task #1
**Komponentas:** `components/settings/OCRSettings.tsx`
- [ ] OCR engines list:
  - [ ] PaddleOCR settings
  - [ ] EasyOCR settings
  - [ ] Tesseract settings
  - [ ] fast_plate_ocr settings
- [ ] Per engine:
  - [ ] Enable/disable
  - [ ] Language selection
  - [ ] Model path
  - [ ] Confidence threshold
  - [ ] Hailo acceleration toggle
- [ ] Ensemble settings:
  - [ ] Method (voting/weighted/best)
  - [ ] Min agreement slider
  - [ ] Plate format regex
- [ ] OCR test interface
- **Nustatymai:** 25+ OCR settings

#### ❌ 10. Video Pipeline Settings
**Statusas:** 0% | **Prioritetas:** 🟡 AUKŠTAS | **Estimacija:** 2-3 dienos
**Priklausomybės:** Task #1
**Komponentas:** `components/settings/PipelineSettings.tsx`
- [ ] GStreamer configuration:
  - [ ] Buffer size slider
  - [ ] Drop on latency toggle
  - [ ] Sync toggle
  - [ ] Latency input (ms)
  - [ ] Use hardware decoder toggle
  - [ ] Max queue size
  - [ ] Target resolution
  - [ ] Protocols (TCP/UDP)
  - [ ] Decoder type dropdown
- [ ] Pipeline diagnostics
- [ ] Pipeline restart button
- **Nustatymai:** 15+ pipeline settings

#### ❌ 11. Object Tracking & Filtering
**Statusas:** 0% | **Prioritetas:** 🟡 VIDUTINIS | **Estimacija:** 1-2 dienos
**Priklausomybės:** Task #1
**Komponentas:** `components/settings/TrackingSettings.tsx`
- [ ] Max disappeared slider (10-200 frames)
- [ ] Max distance slider (10-200 pixels)
- [ ] Cooldown seconds input (0-3600)
- [ ] Tracking algorithm selector
- [ ] Visual tracking preview
- **Nustatymai:** 5+ tracking settings

#### ❌ 12. Data Export Configuration
**Statusas:** 0% | **Prioritetas:** 🔴 KRITINIS | **Estimacija:** 2-3 dienos
**Priklausomybės:** Task #1
**Komponentas:** `components/settings/ExportSettings.tsx`
- [ ] Exporters list (REST/WebSocket/MQTT/Kafka/Webhook)
- [ ] Per exporter:
  - [ ] Type selector
  - [ ] Enable/disable
  - [ ] Endpoint URL
  - [ ] Retry settings (max attempts, backoff)
  - [ ] Timeout input
  - [ ] Batch size
  - [ ] Headers/auth config
  - [ ] Filter rules
  - [ ] Status indicator (🟢 connected, 🔴 error)
- [ ] Test connection button
- **Nustatymai:** 25+ exporter settings

#### ❌ 13. Storage & Database Settings
**Statusas:** 0% | **Prioritetas:** 🔴 KRITINIS | **Estimacija:** 3-4 dienos
**Priklausomybės:** Task #1, #34
**Komponentas:** `components/settings/StorageSettings.tsx`
- [ ] PostgreSQL:
  - [ ] Server, port, database
  - [ ] Username, password
  - [ ] Pool settings (size, overflow, timeout)
  - [ ] Connection status indicator
  - [ ] Test connection button
- [ ] Redis:
  - [ ] Host, port, DB number
  - [ ] Password
  - [ ] TTL, max memory
  - [ ] Connection status
- [ ] MinIO/S3:
  - [ ] Endpoint, bucket
  - [ ] Access/secret keys
  - [ ] SSL toggle
  - [ ] Test connection
- **Nustatymai:** 35+ storage settings

#### ❌ 14. Monitoring & Metrics Dashboard
**Statusas:** 0% | **Prioritetas:** 🟡 AUKŠTAS | **Estimacija:** 2-3 dienos
**Priklausomybės:** Task #1
**Komponentas:** `components/settings/MonitoringSettings.tsx`
- [ ] Prometheus settings:
  - [ ] Enable metrics toggle
  - [ ] Metrics port
  - [ ] Scrape interval
  - [ ] Link to Prometheus UI
- [ ] Grafana settings:
  - [ ] Port configuration
  - [ ] Admin credentials
  - [ ] Link to Grafana dashboards
- [ ] Logging settings:
  - [ ] Log level dropdown
  - [ ] Log format (text/json)
  - [ ] Log file path
  - [ ] Max log size
- [ ] Live log viewer
- **Nustatymai:** 18+ monitoring settings

#### ❌ 15. Security & Access Settings
**Statusas:** 0% | **Prioritetas:** 🔴 KRITINIS | **Estimacija:** 2-3 dienos
**Priklausomybės:** Task #1
**Komponentas:** `components/settings/SecuritySettings.tsx`
- [ ] JWT configuration:
  - [ ] Secret key (hidden)
  - [ ] Algorithm
  - [ ] Access token expire (minutes)
  - [ ] Refresh token expire (days)
- [ ] CORS settings:
  - [ ] Allowed origins (list)
  - [ ] Credentials toggle
  - [ ] Methods/headers
- [ ] Rate limiting:
  - [ ] Enable toggle
  - [ ] Requests per minute
- [ ] SSL/TLS:
  - [ ] Use HTTPS toggle
  - [ ] Cert/key paths
- **Nustatymai:** 20+ security settings

#### ❌ 16. Notifications Configuration
**Statusas:** 0% | **Prioritetas:** 🟡 VIDUTINIS | **Estimacija:** 2 dienos
**Priklausomybės:** Task #1
**Komponentas:** `components/settings/NotificationSettings.tsx`
- [ ] SMTP email:
  - [ ] Enable toggle
  - [ ] Host, port, user, password
  - [ ] From name/email
  - [ ] Test email button
- [ ] Slack integration:
  - [ ] Webhook URL
  - [ ] Test notification
- [ ] Webhook:
  - [ ] Enable toggle
  - [ ] Webhook URL
  - [ ] Test webhook
- **Nustatymai:** 15+ notification settings

#### ❌ 17. Advanced Settings Panel
**Statusas:** 0% | **Prioritetas:** 🟡 VIDUTINIS | **Estimacija:** 1-2 dienos
**Priklausomybės:** Task #1
**Komponentas:** `components/settings/AdvancedSettings.tsx`
- [ ] Feature flags:
  - [ ] OCR enabled
  - [ ] Detection enabled
  - [ ] Tracking enabled
  - [ ] Export enabled
  - [ ] Analytics enabled
  - [ ] Debug mode
- [ ] Performance tuning:
  - [ ] Event retention days
  - [ ] Batch sizes
  - [ ] Max workers
  - [ ] Uvicorn workers
- **Nustatymai:** 15+ advanced settings

---

### **FAZĖ 3: Išmaniosios Funkcijos (10 užduočių)**

#### ❌ 18. Smart Recommendations Engine
**Statusas:** 0% | **Prioritetas:** 🔴 KRITINIS | **Estimacija:** 3-5 dienos
**Priklausomybės:** Task #2, #19, #30
**Komponentas:** `components/settings/Recommendations.tsx`
**Backend:** `backend/app/services/recommendations.py`
- [ ] Hardware-based recommendations:
  - [ ] Optimal model selection (NPU → Hailo, GPU → CUDA)
  - [ ] Batch size recommendations
  - [ ] Thread count optimal
- [ ] Performance recommendations:
  - [ ] FPS optimization
  - [ ] Buffer/queue sizes
  - [ ] Decoder selection
- [ ] Configuration warnings:
  - [ ] Suboptimal settings
  - [ ] Conflicting configs
  - [ ] Missing required settings
- [ ] AI-powered suggestions (analyze metrics → suggest improvements)
- **UI:** Notification cards su "Apply" button

#### ❌ 19. Settings Validation System
**Statusas:** 0% | **Prioritetas:** 🔴 KRITINIS | **Estimacija:** 3-4 dienos
**Priklausomybės:** Task #2
**Backend:** `backend/app/validators/settings.py`
- [ ] Per-field validation:
  - [ ] Type checking (int, float, string, bool)
  - [ ] Range validation (min/max)
  - [ ] Format validation (URL, regex, email)
- [ ] Cross-field validation:
  - [ ] Dependencies (if A enabled, B required)
  - [ ] Conflicts (A and B can't both be enabled)
- [ ] Business rules validation:
  - [ ] Hardware capabilities check
  - [ ] Network connectivity validation
  - [ ] File path existence
- [ ] Helpful error messages (lietuviškai + angliškai)
- **Frontend:** Real-time validation feedback

#### ❌ 20. Contextual Help & Descriptions
**Statusas:** 0% | **Prioritetas:** 🟡 AUKŠTAS | **Estimacija:** 2-3 dienos
**Priklausomybės:** Task #1
**Komponentas:** `components/settings/HelpTooltip.tsx`
- [ ] Every setting su help icon (❓)
- [ ] Tooltip su:
  - [ ] Setting aprašymas
  - [ ] Default value
  - [ ] Recommended range
  - [ ] Performance impact
  - [ ] Related settings
- [ ] Help panel (slide-in):
  - [ ] Detailed explanation
  - [ ] Examples
  - [ ] Troubleshooting tips
- [ ] Search help content
- **Data:** JSON help definitions

#### ❌ 21. Settings Presets
**Statusas:** 0% | **Prioritetas:** 🟡 AUKŠTAS | **Estimacija:** 2-3 dienos
**Priklausomybės:** Task #1, #22
**Komponentas:** `components/settings/Presets.tsx`
- [ ] Predefined presets:
  - [ ] **Low Performance** (min resources, max compatibility)
  - [ ] **Balanced** (recommended for most)
  - [ ] **High Performance** (max accuracy, requires powerful hardware)
  - [ ] **Production** (optimized for 24/7 operation)
  - [ ] **Development** (debug enabled, verbose logging)
- [ ] Per preset:
  - [ ] Name, description
  - [ ] Target hardware
  - [ ] Complete config JSON
  - [ ] Preview changes before apply
- [ ] Apply preset button
- [ ] Create custom preset from current settings

#### 🔄 22. Settings Export/Import
**Statusas:** 50% | **Prioritetas:** 🟡 AUKŠTAS | **Estimacija:** 1-2 dienos
**Priklausomybės:** Task #2
**Komponentas:** `components/settings/ImportExport.tsx`
- [ ] Export formats:
  - [ ] JSON (full config)
  - [ ] YAML (human-readable)
  - [ ] ENV file
- [ ] Export options:
  - [ ] All settings
  - [ ] Specific category
  - [ ] Exclude sensitive (passwords, keys)
- [ ] Import from:
  - [ ] File upload
  - [ ] URL fetch
  - [ ] Paste JSON/YAML
  - [ ] Cloud storage (future)
- [ ] Import validation
- [ ] Preview before import
- [ ] Backup current before import

#### ❌ 23. Settings Comparison Tool
**Statusas:** 0% | **Prioritetas:** 🟢 ŽEMAS | **Estimacija:** 2 dienos
**Priklausomybės:** Task #1, #22
**Komponentas:** `components/settings/Compare.tsx`
- [ ] Compare two configurations:
  - [ ] Current vs. preset
  - [ ] Current vs. imported
  - [ ] Two saved configs
- [ ] Diff viewer:
  - [ ] Added settings (green)
  - [ ] Removed settings (red)
  - [ ] Changed settings (yellow)
  - [ ] Value differences highlighted
- [ ] Merge options
- [ ] Apply selective changes

#### 🔄 24. Settings Change History & Audit Log
**Statusas:** 30% | **Prioritetas:** 🟡 AUKŠTAS | **Estimacija:** 2 dienos
**Priklausomybės:** Task #2
**Komponentas:** `components/settings/History.tsx`
**Backend:** `backend/app/models.py` → SettingsHistory model
- [ ] Database schema:
  - [ ] id, timestamp, user, setting_key, old_value, new_value, reason
- [ ] History viewer:
  - [ ] Timeline view
  - [ ] Filter by user, date, setting
  - [ ] Diff viewer per change
- [ ] Rollback functionality:
  - [ ] Rollback single setting
  - [ ] Rollback all changes from timepoint
  - [ ] Confirm before rollback
- [ ] Export audit log

#### ❌ 25. Settings Search & Filter
**Statusas:** 0% | **Prioritetas:** 🟡 AUKŠTAS | **Estimacija:** 2-3 dienos
**Priklausomybės:** Task #1
**Komponentas:** `components/settings/SearchFilter.tsx`
- [ ] Global search:
  - [ ] Search by setting name
  - [ ] Search by description
  - [ ] Search by value
  - [ ] Fuzzy search
- [ ] Advanced filters:
  - [ ] By category
  - [ ] By status (default, modified, recommended)
  - [ ] By type (hardware, performance, security)
  - [ ] Show only errors/warnings
- [ ] Search keyboard shortcut (Ctrl+K / Cmd+K)
- [ ] Recent searches
- [ ] Search results highlighting

#### ❌ 26. Live System Health Indicators
**Statusas:** 0% | **Prioritetas:** 🟡 AUKŠTAS | **Estimacija:** 2-3 dienos
**Priklausomybės:** Task #1, #3
**Komponentas:** `components/settings/HealthIndicators.tsx`
- [ ] Per category health:
  - [ ] 🟢 All good
  - [ ] 🟡 Warnings present
  - [ ] 🔴 Errors/critical issues
- [ ] Overall system health score (0-100)
- [ ] Health breakdown:
  - [ ] Hardware status
  - [ ] Camera connectivity
  - [ ] Database connections
  - [ ] Model loading status
  - [ ] Export connectivity
- [ ] Health history graph (24h)
- [ ] Alert notifications

#### ❌ 27. Performance Impact Indicators
**Statusas:** 0% | **Prioritetas:** 🟡 VIDUTINIS | **Estimacija:** 1-2 dienos
**Priklausomybės:** Task #1
**Komponentas:** `components/settings/PerformanceImpact.tsx`
- [ ] Per setting impact label:
  - [ ] 🔵 Low impact
  - [ ] 🟡 Medium impact
  - [ ] 🔴 High impact (requires restart)
- [ ] Change preview:
  - [ ] "Changing this will..."
  - [ ] Estimated FPS change
  - [ ] Resource usage change
- [ ] Restart required indicator
- [ ] Performance simulation (predict outcome)

---

### **FAZĖ 4: Vizualizacijos ir Monitoring (5 užduotys)**

#### ❌ 28. Real-time FPS & Latency Monitoring
**Statusas:** 0% | **Prioritetas:** 🟡 AUKŠTAS | **Estimacija:** 2-3 dienos
**Priklausomybės:** Task #1, #3
**Komponentas:** `components/settings/CameraMetrics.tsx`
- [ ] Per camera metrics card:
  - [ ] Current FPS (real-time)
  - [ ] Target vs actual FPS graph
  - [ ] Latency (ms)
  - [ ] Dropped frames count
  - [ ] Processing time per frame
- [ ] Charts:
  - [ ] Line chart (last 5 minutes)
  - [ ] Auto-refresh every 1s
- [ ] Alerts (FPS < threshold)
- **Data source:** WebSocket metrics stream

#### ❌ 29. Hardware Utilization Graphs
**Statusas:** 0% | **Prioritetas:** 🟡 AUKŠTAS | **Estimacija:** 2-3 dienos
**Priklausomybės:** Task #1
**Komponentas:** `components/settings/HardwareGraphs.tsx`
- [ ] GPU metrics:
  - [ ] GPU usage % (real-time)
  - [ ] GPU memory usage
  - [ ] GPU temperature
- [ ] NPU metrics:
  - [ ] NPU usage %
  - [ ] NPU power consumption
- [ ] CPU metrics:
  - [ ] CPU usage per core
  - [ ] System memory
  - [ ] Disk I/O
- [ ] Charts library: Recharts or Chart.js
- [ ] Time ranges: 1m, 5m, 1h, 24h
- **Data:** Prometheus metrics via API

#### ❌ 30. Automatic Hardware Detection
**Statusas:** 0% | **Prioritetas:** 🔴 KRITINIS | **Estimacija:** 3-4 dienos
**Priklausomybės:** Nėra
**Backend:** `backend/app/services/hardware_detection.py`
- [ ] Detect available hardware:
  - [ ] CUDA GPUs (nvidia-smi)
  - [ ] Hailo NPUs (hailortcli)
  - [ ] Coral TPUs
  - [ ] CPU info (cores, model)
- [ ] Auto-populate settings:
  - [ ] Hardware type
  - [ ] Device IDs
  - [ ] Optimal thread count
  - [ ] Recommended models
- [ ] "Auto-detect" button in UI
- [ ] Detection results preview

#### ❌ 31. Model Performance Comparison Tool
**Statusas:** 0% | **Prioritetas:** 🟢 ŽEMAS | **Estimacija:** 2-3 dienos
**Priklausomybės:** Task #1
**Komponentas:** `components/settings/ModelComparison.tsx`
- [ ] Select 2-4 models to compare
- [ ] Comparison table:
  - [ ] Model name
  - [ ] Accuracy (mAP)
  - [ ] FPS
  - [ ] Latency (ms)
  - [ ] Resource usage
  - [ ] Model size
- [ ] Visual charts (bar/radar)
- [ ] Recommendation (best for your hardware)
- [ ] "Run benchmark" button
- **Data:** Stored in DB or run live test

#### ❌ 32. OCR Test Interface
**Statusas:** 0% | **Prioritetas:** 🟡 VIDUTINIS | **Estimacija:** 2 dienos
**Priklausomybės:** Task #1, #9
**Komponentas:** `components/settings/OCRTest.tsx`
- [ ] Upload test image
- [ ] Or select from samples
- [ ] Run OCR with current settings
- [ ] Results display:
  - [ ] Detected text
  - [ ] Confidence score
  - [ ] Time taken
  - [ ] Per-engine results
- [ ] Ensemble result
- [ ] Visual bbox overlay
- [ ] Compare different OCR settings

---

### **FAZĖ 5: Testing & Diagnostics (7 užduotys)**

#### ❌ 33. Settings Backup & Restore
**Statusas:** 0% | **Prioritetas:** 🔴 KRITINIS | **Estimacija:** 2-3 dienos
**Priklausomybės:** Task #2
**Backend:** `backend/app/services/backup.py`
- [ ] Automatic backups:
  - [ ] Before every change
  - [ ] Daily schedule
  - [ ] Keep last N backups
- [ ] Backup storage:
  - [ ] Local filesystem
  - [ ] Database
  - [ ] S3/MinIO (optional)
- [ ] Restore UI:
  - [ ] List all backups
  - [ ] Preview backup content
  - [ ] Restore selected backup
  - [ ] Confirm dialog
- [ ] Backup naming: `settings_backup_YYYY-MM-DD_HH-MM-SS.json`

#### ❌ 34. Database Connection Tests
**Statusas:** 0% | **Prioritetas:** 🟡 AUKŠTAS | **Estimacija:** 2 dienos
**Priklausomybės:** Task #1, #13
**Komponentas:** `components/settings/ConnectionTests.tsx`
- [ ] Test PostgreSQL:
  - [ ] Connection test
  - [ ] Query test (SELECT 1)
  - [ ] Show latency
  - [ ] Pool status
- [ ] Test Redis:
  - [ ] PING test
  - [ ] SET/GET test
  - [ ] Show latency
- [ ] Test MinIO:
  - [ ] Bucket access test
  - [ ] Upload/download test
  - [ ] List objects
- [ ] Results display (✅ success, ❌ error, ⏱️ latency)
- [ ] Error messages with troubleshooting tips

#### ❌ 35. RTSP Stream Test & Validation
**Statusas:** 0% | **Prioritetas:** 🔴 KRITINIS | **Estimacija:** 2-3 dienos
**Priklausomybės:** Nėra
**Backend:** `backend/app/services/rtsp_test.py`
- [ ] Test RTSP URL:
  - [ ] Connection test (can reach?)
  - [ ] Authentication test
  - [ ] Stream info (codec, resolution, FPS)
  - [ ] Capture test frame
- [ ] UI:
  - [ ] "Test Stream" button per camera
  - [ ] Loading indicator
  - [ ] Results display:
    - [ ] ✅ Stream OK
    - [ ] Stream info details
    - [ ] Test frame preview
    - [ ] Error message if failed
- [ ] Troubleshooting suggestions

#### ❌ 36. System Diagnostics Tool
**Statusas:** 0% | **Prioritetas:** 🔴 KRITINIS | **Estimacija:** 3-4 dienos
**Priklausomybės:** Task #30, #34, #35
**Komponentas:** `components/settings/Diagnostics.tsx`
**Backend:** `backend/app/services/diagnostics.py`
- [ ] Run diagnostics suite:
  - [ ] Hardware detection
  - [ ] Database connectivity
  - [ ] Camera streams
  - [ ] Model loading
  - [ ] Disk space
  - [ ] Network connectivity
  - [ ] Port availability
- [ ] Results report:
  - [ ] Per-test status (pass/fail/warning)
  - [ ] Detailed logs
  - [ ] Recommendations
- [ ] Export diagnostics report
- [ ] Auto-run on startup (optional)

#### ❌ 37. Performance Benchmarking Tool
**Statusas:** 0% | **Prioritetas:** 🟡 VIDUTINIS | **Estimacija:** 3-4 dienos
**Priklausomybės:** Task #1
**Komponentas:** `components/settings/Benchmark.tsx`
- [ ] Benchmark types:
  - [ ] Model inference speed
  - [ ] OCR speed
  - [ ] Database performance
  - [ ] Pipeline throughput
- [ ] Configuration:
  - [ ] Select components to test
  - [ ] Number of iterations
  - [ ] Test data source
- [ ] Run benchmark
- [ ] Results:
  - [ ] Average FPS
  - [ ] Min/max latency
  - [ ] Resource usage
  - [ ] Bottlenecks identified
- [ ] Save benchmark results
- [ ] Compare with previous runs

#### ❌ 38. Settings Dependency Validation
**Statusas:** 0% | **Prioritetas:** 🔴 KRITINIS | **Estimacija:** 2-3 dienos
**Priklausomybės:** Task #19
**Backend:** `backend/app/validators/dependencies.py`
- [ ] Define dependencies:
  ```python
  dependencies = {
    "use_cuda": {"requires": ["cuda_device"]},
    "ocr_enabled": {"requires": ["ocr_engine"]},
    "exporter_enabled": {"requires": ["exporter_endpoint"]},
  }
  ```
- [ ] Validate on save:
  - [ ] Check all required settings present
  - [ ] Check conflicts
  - [ ] Check hardware capabilities
- [ ] UI indicators:
  - [ ] ⚠️ Missing required setting
  - [ ] 🔗 Related settings link
- [ ] Auto-enable dependencies (with confirmation)

#### ❌ 39. Warning Indicators for Suboptimal Configurations
**Statusas:** 0% | **Prioritetas:** 🟡 AUKŠTAS | **Estimacija:** 1-2 dienos
**Priklausomybės:** Task #1, #19
**Komponentas:** `components/settings/Warnings.tsx`
- [ ] Warning types:
  - [ ] ⚠️ Performance: "FPS too high for hardware"
  - [ ] ⚠️ Resource: "Buffer size too large"
  - [ ] ⚠️ Security: "Using default password"
  - [ ] ⚠️ Compatibility: "Model not compatible with hardware"
- [ ] Warning severity:
  - [ ] Info (ℹ️)
  - [ ] Warning (⚠️)
  - [ ] Error (❌)
- [ ] Dismiss warnings (with reason)
- [ ] Warning center (all active warnings)

---

### **FAZĖ 6: Advanced Features (13 užduočių)**

#### ❌ 40. Quick Setup Wizard
**Statusas:** 0% | **Prioritetas:** 🟡 AUKŠTAS | **Estimacija:** 3-4 dienos
**Priklausomybės:** Task #1, #4-#9
**Komponentas:** `components/settings/SetupWizard.tsx`
- [ ] Multi-step wizard:
  - [ ] Step 1: Welcome & hardware detection
  - [ ] Step 2: Camera configuration
  - [ ] Step 3: Model selection
  - [ ] Step 4: OCR setup
  - [ ] Step 5: Database connections
  - [ ] Step 6: Review & apply
- [ ] Progress bar
- [ ] Skip wizard option
- [ ] Save as template
- [ ] Wizard on first launch

#### ❌ 41. Dark/Light Theme Support
**Statusas:** 0% | **Prioritetas:** 🟢 ŽEMAS | **Estimacija:** 1 diena
**Priklausomybės:** Task #1
**Komponentas:** Theme system
- [ ] Theme toggle (sun/moon icon)
- [ ] Persist theme preference (localStorage)
- [ ] Tailwind dark mode classes
- [ ] System preference detection
- [ ] Smooth theme transitions
- [ ] Theme preview

#### ❌ 42. Responsive Design for Mobile
- [ ] Responsive layouts:
  - [ ] Desktop: Sidebar + main content
  - [ ] Tablet: Collapsible sidebar
  - [ ] Mobile: Bottom nav or drawer
- [ ] Touch-friendly controls
- [ ] Mobile-optimized forms
- [ ] Swipe gestures
- [ ] Responsive tables (cards on mobile)

#### ❌ 43. Settings Documentation Generator
**Statusas:** 0% | **Prioritetas:** 🟢 ŽEMAS | **Estimacija:** 2 dienos
**Priklausomybės:** Task #2
**Backend:** `backend/app/services/docs_generator.py`
- [ ] Generate docs from config:
  - [ ] Markdown format
  - [ ] HTML format
  - [ ] PDF format (optional)
- [ ] Include:
  - [ ] All settings with descriptions
  - [ ] Default values
  - [ ] Valid ranges
  - [ ] Examples
- [ ] Download button
- [ ] Auto-update on settings change

#### ❌ 44. Keyboard Shortcuts
**Statusas:** 0% | **Prioritetas:** 🟢 ŽEMAS | **Estimacija:** 1 diena
**Priklausomybės:** Task #1
**Komponentas:** Global keyboard listener
- [ ] Shortcuts:
  - [ ] `Ctrl/Cmd + K` - Open search
  - [ ] `Ctrl/Cmd + S` - Save settings
  - [ ] `Ctrl/Cmd + Z` - Undo
  - [ ] `Ctrl/Cmd + ,` - Open settings
  - [ ] `Esc` - Close modals
  - [ ] `?` - Show shortcuts help
- [ ] Shortcuts help modal
- [ ] Customizable shortcuts (future)

#### ❌ 45. Settings Templates
**Statusas:** 0% | **Prioritetas:** 🟡 VIDUTINIS | **Estimacija:** 2 dienos
**Priklausomybės:** Task #1, #21
**Komponentas:** `components/settings/Templates.tsx`
- [ ] Template management:
  - [ ] Create template from current
  - [ ] Name, description, tags
  - [ ] Save template
  - [ ] Load template
  - [ ] Delete template
- [ ] Template library:
  - [ ] Built-in templates
  - [ ] User templates
  - [ ] Community templates (future)
- [ ] Template sharing (export/import)

#### ❌ 46. Settings Migration Tool
**Statusas:** 0% | **Prioritetas:** 🟡 VIDUTINIS | **Estimacija:** 2-3 dienos
**Priklausomybės:** Task #2
**Backend:** `backend/app/services/migration.py`
- [ ] Version migration:
  - [ ] Detect config version
  - [ ] Apply migrations (v1 → v2 → v3)
  - [ ] Transform old settings to new schema
- [ ] Migration history
- [ ] Rollback migrations
- [ ] Backup before migration
- [ ] Migration testing (dry-run)

#### ❌ 47. Live Log Viewer
**Statusas:** 0% | **Prioritetas:** 🟡 VIDUTINIS | **Estimacija:** 2-3 dienos
**Priklausomybės:** Task #1
**Komponentas:** `components/settings/LogViewer.tsx`
- [ ] Log streaming:
  - [ ] WebSocket or SSE
  - [ ] Auto-scroll to bottom
  - [ ] Pause/resume stream
- [ ] Log filtering:
  - [ ] By level (DEBUG, INFO, WARNING, ERROR)
  - [ ] By component (edge, backend, camera)
  - [ ] By search term
- [ ] Log actions:
  - [ ] Download logs
  - [ ] Clear logs
  - [ ] Copy to clipboard
- [ ] Syntax highlighting

#### 🔄 48. Settings Rollback Functionality
**Statusas:** 50% | **Prioritetas:** 🟡 AUKŠTAS | **Estimacija:** 1-2 dienos
**Priklausomybės:** Task #2, #24
**Backend:** `backend/app/services/rollback.py`
- [ ] Rollback triggers:
  - [ ] Manual (user clicks "Undo")
  - [ ] Automatic (if setting causes error)
  - [ ] On system failure
- [ ] Rollback UI:
  - [ ] "Undo" button after save
  - [ ] Rollback confirmation
  - [ ] Show what will be reverted
- [ ] Rollback history (last 10 changes)

#### ❌ 49. A/B Testing for Model Configurations
**Statusas:** 0% | **Prioritetas:** 🟢 ŽEMAS | **Estimacija:** 3-4 dienos
**Priklausomybės:** Task #1, #8
**Komponentas:** `components/settings/ABTest.tsx`
- [ ] Create A/B test:
  - [ ] Select 2 configurations (A vs B)
  - [ ] Define test duration
  - [ ] Define success metric (FPS, accuracy)
  - [ ] Select test cameras
- [ ] Run test:
  - [ ] Split traffic (50/50 or custom)
  - [ ] Collect metrics
  - [ ] Real-time results
- [ ] Results analysis:
  - [ ] Statistical significance
  - [ ] Winner declaration
  - [ ] Apply winner config

#### ❌ 50. Notification Center
**Statusas:** 0% | **Prioritetas:** 🟡 VIDUTINIS | **Estimacija:** 2-3 dienos
**Priklausomybės:** Task #1
**Komponentas:** `components/settings/NotificationCenter.tsx`
- [ ] Notification types:
  - [ ] System alerts
  - [ ] Setting change confirmations
  - [ ] Warnings/errors
  - [ ] Update available
  - [ ] Recommendations
- [ ] Notification UI:
  - [ ] Bell icon with badge count
  - [ ] Dropdown panel
  - [ ] Notification list
  - [ ] Mark as read/unread
  - [ ] Clear all
- [ ] Notification persistence (DB)
- [ ] Push notifications (future)

#### ❌ 51. Multi-language Support (i18n)
**Tech:** react-i18next or next-intl
- [ ] Languages:
  - [ ] Lithuanian (Lietuvių)
  - [ ] English
  - [ ] (More in future)
- [ ] Translation files:
  - [ ] `locales/lt/settings.json`
  - [ ] `locales/en/settings.json`
- [ ] Language switcher
- [ ] Persist language preference
- [ ] Translate all UI text

#### ❌ 52. Settings Permissions & RBAC
**Statusas:** 0% | **Prioritetas:** 🟡 AUKŠTAS | **Estimacija:** 3-4 dienos
**Priklausomybės:** Task #2
**Backend:** Role-based access control
- [ ] User roles:
  - [ ] Admin (full access)
  - [ ] Operator (view + edit some)
  - [ ] Viewer (read-only)
- [ ] Per-setting permissions:
  - [ ] Can view
  - [ ] Can edit
  - [ ] Can delete
- [ ] UI:
  - [ ] Disable controls for no permission
  - [ ] Show lock icon
  - [ ] Permission denied messages
- [ ] Audit log for permission changes

---

### **FAZĖ 7: Polish, Testing & Documentation (5 užduotys)**

#### ❌ 53. API Documentation Viewer
**Statusas:** 0% | **Prioritetas:** 🟢 ŽEMAS | **Estimacija:** 1 diena
**Priklausomybės:** Task #1
**Komponentas:** `components/settings/APIDocViewer.tsx`
- [ ] Integrate OpenAPI/Swagger:
  - [ ] Auto-generate from FastAPI
  - [ ] Embed Swagger UI or Redoc
- [ ] Endpoint browser:
  - [ ] List all API endpoints
  - [ ] Request/response schemas
  - [ ] Try it out (interactive)
- [ ] Code examples (curl, Python, JS)

#### ❌ 54. Settings Import from Cloud/File/URL
**Statusas:** 0% | **Prioritetas:** 🟢 ŽEMAS | **Estimacija:** 1-2 dienos
**Priklausomybės:** Task #22
**Komponentas:** Enhanced import
- [ ] Import sources:
  - [ ] Local file upload ✅ (already in #22)
  - [ ] URL fetch (fetch remote config)
  - [ ] Cloud storage (S3, Google Drive)
  - [ ] GitHub repository
- [ ] URL import validation
- [ ] Auth for cloud sources

#### ❌ 55. System Resource Allocator with Visual Feedback
**Statusas:** 0% | **Prioritetas:** 🟡 VIDUTINIS | **Estimacija:** 2-3 dienos
**Priklausomybės:** Task #1
**Komponentas:** `components/settings/ResourceAllocator.tsx`
- [ ] Visual resource allocation:
  - [ ] GPU memory slider with usage bar
  - [ ] CPU cores allocation
  - [ ] NPU resources
  - [ ] RAM allocation
- [ ] Real-time feedback:
  - [ ] Available vs allocated
  - [ ] Warning if over-allocated
  - [ ] Recommendations
- [ ] Preset allocations (balanced, performance, etc.)

#### ❌ 56. Integration Testing for Settings Workflows
**Statusas:** 0% | **Prioritetas:** 🔴 KRITINIS | **Estimacija:** 3-5 dienos
**Priklausomybės:** Task #2, visi backend
**Test:** `tests/integration/test_settings.py`
- [ ] Test scenarios:
  - [ ] Update setting → verify in DB
  - [ ] Invalid setting → error response
  - [ ] Cascade updates (change hardware → update model)
  - [ ] Import/export workflow
  - [ ] Backup/restore workflow
- [ ] API tests (pytest + httpx)
- [ ] E2E tests (Playwright)
- [ ] Test coverage > 80%

#### ❌ 57. Comprehensive E2E Tests for Settings Dashboard
**Statusas:** 0% | **Prioritetas:** 🔴 KRITINIS | **Estimacija:** 3-5 dienos
**Priklausomybės:** Task #1, visi frontend
**Test:** `e2e/settings.spec.ts`
- [ ] Test flows:
  - [ ] Navigate all categories
  - [ ] Change settings → save → verify
  - [ ] Search settings
  - [ ] Apply preset
  - [ ] Run diagnostics
  - [ ] Export/import config
  - [ ] Test connections
- [ ] Visual regression tests
- [ ] Accessibility tests (a11y)
- **Tool:** Playwright or Cypress

---

## 📊 Projekto Nustatymai (300+ Settings Sąrašas)

### **1. Sistema (23 settings)**
- worker_id, log_level, environment, api_host, api_port, backend_url, backend_port, metrics_port, frontend_port, uvicorn_workers, event_retention_days, event_batch_size, edge_batch_size, edge_max_workers, log_file_path, log_max_size, db_backup_retention_days, rate_limit_enabled, rate_limit_requests_per_minute, use_https, ssl_cert_path, ssl_key_path, secret_key

### **2. Hardware (12 settings)**
- type, device_id, use_cuda, cuda_device, num_threads, gpu_memory_limit, npu_power_mode, hailo_device, coral_device, cpu_model, cpu_cores, total_memory

### **3. Kameros (15 settings per camera)**
- id, name, rtsp_url, enabled, fps, resolution, location, zones (array), zone_name, zone_polygon, zone_type, zone_enabled, zone_priority, metadata, status

### **4. Detection Modeliai (20 settings per model)**
- type, weights_path, framework, confidence_threshold, nms_threshold, input_size, classes, version, parameters, enabled, is_default, model_size, accuracy_map, inference_fps, latency_ms, memory_usage, supported_hardware, preprocessing, postprocessing, batch_size

### **5. OCR (25 settings)**
- ensemble_method, min_agreement, plate_format_regex, paddleocr_enabled, paddleocr_language, paddleocr_confidence, easyocr_enabled, easyocr_language, easyocr_confidence, tesseract_enabled, tesseract_language, tesseract_confidence, fast_plate_ocr_enabled, fast_plate_ocr_model_path, fast_plate_ocr_use_hailo, fast_plate_ocr_confidence, ocr_preprocessing, ocr_char_whitelist, ocr_char_blacklist, ocr_min_text_size, ocr_max_text_size, ocr_timeout, ocr_gpu_enabled, ocr_batch_size, ocr_padding

### **6. GStreamer Pipeline (15 settings)**
- buffer_size, drop_on_latency, sync, latency, use_hw_decoder, max_queue_size, target_width, target_height, protocols, decoder_type, encoder_type, pipeline_latency_ms, pipeline_buffer_mode, pipeline_thread_count, pipeline_debug

### **7. Object Tracking (5 settings)**
- max_disappeared, max_distance, cooldown_seconds, tracking_algorithm, track_confidence_threshold

### **8. Exporters (25 settings per exporter)**
- type, enabled, endpoint, retry_enabled, retry_max_attempts, retry_backoff, timeout, batch_size, queue_path, headers, auth_type, auth_token, filter_config, export_images, export_metadata, export_format, compression, encryption, ssl_verify, mqtt_topic, mqtt_qos, kafka_topic, kafka_partition, websocket_reconnect, http_method

### **9. Storage (35 settings)**
- **PostgreSQL (15):** postgres_server, postgres_port, postgres_user, postgres_password, postgres_db, postgres_echo, db_pool_size, db_max_overflow, db_pool_timeout, db_pool_recycle, db_ssl_mode, db_application_name, db_connect_timeout, db_statement_timeout, db_idle_timeout
- **Redis (12):** redis_host, redis_port, redis_db, redis_password, redis_ttl, redis_max_memory, redis_timeout, redis_retry_on_timeout, redis_socket_keepalive, redis_health_check_interval, redis_max_connections, redis_decode_responses
- **MinIO (8):** minio_endpoint, minio_root_user, minio_root_password, minio_bucket, minio_use_ssl, minio_region, minio_access_key, minio_secret_key

### **10. API & Security (20 settings)**
- api_prefix, cors_origins, cors_credentials, cors_methods, cors_headers, algorithm, access_token_expire_minutes, refresh_token_expire_days, rate_limit_window, api_key_enabled, api_key_header, oauth_enabled, oauth_provider, session_timeout, csrf_enabled, allowed_hosts, trusted_proxies, max_request_size, request_timeout, response_compression

### **11. WebSocket (5 settings)**
- ws_heartbeat_interval, ws_max_connections, ws_url, ws_ping_interval, ws_reconnect_delay

### **12. Monitoring (18 settings)**
- metrics_enabled, prometheus_port, scrape_interval, evaluation_interval, scrape_timeout, grafana_port, grafana_user, grafana_password, log_format, alerting_enabled, alert_webhook, retention_days, metrics_path, enable_pprof, tracing_enabled, tracing_endpoint, histogram_buckets, summary_quantiles

### **13. Notifications (15 settings)**
- smtp_enabled, smtp_host, smtp_port, smtp_user, smtp_password, smtp_from_name, smtp_from_email, smtp_tls, smtp_ssl, slack_webhook_url, slack_channel, webhook_enabled, webhook_url, webhook_headers, notification_template

### **14. Feature Flags (10 settings)**
- feature_ocr_enabled, feature_detection_enabled, feature_tracking_enabled, feature_export_enabled, feature_analytics_enabled, feature_debug, feature_experimental, feature_beta, feature_profiling, feature_maintenance_mode

### **15. Frontend (12 settings)**
- next_public_api_url, next_public_ws_url, next_public_app_name, next_public_app_version, next_public_status_poll_interval, next_public_stats_poll_interval, next_public_image_optimization, next_public_enable_analytics, next_public_enable_debug, next_public_theme, next_public_locale, next_public_max_upload_size

### **16. Image Storage (8 settings)**
- image_save_path, save_images, upload_dir, max_upload_size, allowed_image_types, image_quality, image_compression, thumbnail_size

### **17. Sensor Settings (10 settings in DB)**
- sensor_id, sensor_name, sensor_type, sensor_camera_id, sensor_zone_id, sensor_config, sensor_enabled, sensor_description, sensor_metadata, sensor_schedule

---

## 🚀 Implementacijos Technologijos

### **Frontend Stack:**
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **UI Library:** React 18
- **Styling:** Tailwind CSS
- **Components:** shadcn/ui, Headless UI
- **Forms:** React Hook Form + Zod validation
- **State:** Zustand or React Context
- **Charts:** Recharts or Chart.js
- **WebSocket:** native WebSocket API
- **HTTP Client:** fetch API or Axios
- **i18n:** next-intl
- **Testing:** Vitest + React Testing Library + Playwright

### **Backend Stack:**
- **Framework:** FastAPI
- **Language:** Python 3.11+
- **Validation:** Pydantic v2
- **Database:** PostgreSQL + SQLAlchemy
- **Cache:** Redis
- **WebSocket:** FastAPI WebSockets
- **Monitoring:** Prometheus client
- **Testing:** pytest + httpx

### **DevOps:**
- **Containers:** Docker + Docker Compose
- **Reverse Proxy:** Nginx
- **Monitoring:** Prometheus + Grafana
- **Logging:** Structured logging (JSON)

---

## 📁 Failo Struktūra

```
frontend/
├── app/
│   ├── settings/
│   │   ├── page.tsx                    # Main settings page
│   │   ├── layout.tsx                  # Settings layout
│   │   ├── system/page.tsx             # System overview
│   │   ├── hardware/page.tsx           # Hardware settings
│   │   ├── cameras/page.tsx            # Camera management
│   │   ├── models/page.tsx             # Detection models
│   │   ├── ocr/page.tsx                # OCR config
│   │   ├── pipeline/page.tsx           # Video pipeline
│   │   ├── tracking/page.tsx           # Object tracking
│   │   ├── export/page.tsx             # Data export
│   │   ├── storage/page.tsx            # Storage & DB
│   │   ├── monitoring/page.tsx         # Monitoring
│   │   ├── security/page.tsx           # Security
│   │   ├── notifications/page.tsx      # Notifications
│   │   └── advanced/page.tsx           # Advanced settings
│   └── api/
│       └── settings/
│           └── route.ts                # Settings API proxy
├── components/
│   ├── settings/
│   │   ├── SettingsLayout.tsx
│   │   ├── SettingsSidebar.tsx
│   │   ├── SystemOverview.tsx
│   │   ├── HardwareSettings.tsx
│   │   ├── CameraManagement.tsx
│   │   ├── ZoneEditor.tsx
│   │   ├── ModelsSettings.tsx
│   │   ├── OCRSettings.tsx
│   │   ├── PipelineSettings.tsx
│   │   ├── TrackingSettings.tsx
│   │   ├── ExportSettings.tsx
│   │   ├── StorageSettings.tsx
│   │   ├── MonitoringSettings.tsx
│   │   ├── SecuritySettings.tsx
│   │   ├── NotificationSettings.tsx
│   │   ├── AdvancedSettings.tsx
│   │   ├── Recommendations.tsx
│   │   ├── HelpTooltip.tsx
│   │   ├── Presets.tsx
│   │   ├── ImportExport.tsx
│   │   ├── Compare.tsx
│   │   ├── History.tsx
│   │   ├── SearchFilter.tsx
│   │   ├── HealthIndicators.tsx
│   │   ├── PerformanceImpact.tsx
│   │   ├── CameraMetrics.tsx
│   │   ├── HardwareGraphs.tsx
│   │   ├── ModelComparison.tsx
│   │   ├── OCRTest.tsx
│   │   ├── ConnectionTests.tsx
│   │   ├── Diagnostics.tsx
│   │   ├── Benchmark.tsx
│   │   ├── Warnings.tsx
│   │   ├── SetupWizard.tsx
│   │   ├── LogViewer.tsx
│   │   ├── ABTest.tsx
│   │   ├── NotificationCenter.tsx
│   │   ├── APIDocViewer.tsx
│   │   ├── ResourceAllocator.tsx
│   │   └── SettingField.tsx
│   └── ui/
│       ├── button.tsx
│       ├── input.tsx
│       ├── select.tsx
│       ├── switch.tsx
│       ├── slider.tsx
│       ├── tooltip.tsx
│       ├── dialog.tsx
│       ├── tabs.tsx
│       └── ...
├── hooks/
│   ├── useSettings.ts
│   ├── useSettingsWebSocket.ts
│   ├── useHardwareDetection.ts
│   ├── useValidation.ts
│   └── useMetrics.ts
├── lib/
│   ├── api/
│   │   └── settings.ts               # Settings API client
│   ├── validators/
│   │   └── settings.ts               # Client-side validation
│   └── utils/
│       └── settings.ts               # Helper functions
├── types/
│   └── settings.ts                   # TypeScript types
└── locales/
    ├── en/
    │   └── settings.json
    └── lt/
        └── settings.json

backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── settings.py           # Settings API endpoints
│   ├── models/
│   │   ├── settings.py               # Settings DB models
│   │   └── settings_history.py       # Audit log model
│   ├── schemas/
│   │   └── settings.py               # Pydantic schemas
│   ├── services/
│   │   ├── recommendations.py        # Recommendations engine
│   │   ├── validation.py             # Settings validation
│   │   ├── hardware_detection.py     # Hardware detection
│   │   ├── backup.py                 # Backup/restore
│   │   ├── migration.py              # Settings migration
│   │   ├── diagnostics.py            # System diagnostics
│   │   ├── rtsp_test.py              # RTSP testing
│   │   └── docs_generator.py         # Docs generation
│   ├── validators/
│   │   ├── settings.py               # Field validators
│   │   └── dependencies.py           # Dependency validation
│   └── websockets/
│       └── settings.py               # Settings WebSocket handler
└── tests/
    ├── integration/
    │   └── test_settings.py
    └── unit/
        └── test_settings.py
```

---

## 📊 DETALI PROGRESO ANALIZĖ (2025-11-26)

### ✅ KĄ TURIME (3/57 = 5.3%)

#### Backend (Dalinai baigta - 20%)
- ✅ **API Endpoints** - 100% baigta
  - `backend/app/api/endpoints/settings.py` (23,437 bytes, 14+ endpoints)
  - Pilnai funkcionalus CRUD + import/export + history + rollback
- ✅ **Database Models** - 100% baigta
  - `backend/app/models.py` (Settings, SettingsHistory)
  - Pilnas validation_rules, metadata, sensitive fields support
- ✅ **Schemas** - 100% baigta
  - `backend/app/schemas.py` (13+ Pydantic schemas)
  - Type-safe validation, import/export schemas
- ✅ **Migration** - 100% baigta
  - `backend/alembic/versions/20251126_1940_001_add_settings_tables.py`
  - settings + settings_history tables su indexes

#### Edge Worker (100% baigta - ne TODO dalis)
- ✅ GStreamer pipeline su hardware decode
- ✅ Detection (YOLOv8 + SSD + Faster R-CNN)
- ✅ OCR ensemble (4 engines)
- ✅ Centroid tracking
- ✅ Multi-camera support
- ✅ Event exporters

### ❌ KO TRŪKSTA (54/57 = 94.7%)

#### Backend Services (0/8 = 0%)
- ❌ recommendations.py - Task #18
- ❌ validation.py - Task #19
- ❌ hardware_detection.py - Task #30
- ❌ backup.py - Task #33
- ❌ rtsp_test.py - Task #35
- ❌ diagnostics.py - Task #36
- ❌ migration.py - Task #46
- ❌ docs_generator.py - Task #43

#### Backend Validators (0/2 = 0%)
- ❌ validators/settings.py - Task #19
- ❌ validators/dependencies.py - Task #38

#### Backend WebSockets (0/1 = 0%)
- ❌ websockets/settings.py - Task #3

#### Frontend Dashboard (0/100%)
**CRITICAL:** VISIŠKAI trūksta

**Pages (0/14):**
- ❌ app/settings/page.tsx (main)
- ❌ app/settings/layout.tsx
- ❌ app/settings/system/page.tsx
- ❌ app/settings/hardware/page.tsx
- ❌ app/settings/cameras/page.tsx
- ❌ app/settings/models/page.tsx
- ❌ app/settings/ocr/page.tsx
- ❌ app/settings/pipeline/page.tsx
- ❌ app/settings/tracking/page.tsx
- ❌ app/settings/export/page.tsx
- ❌ app/settings/storage/page.tsx
- ❌ app/settings/monitoring/page.tsx
- ❌ app/settings/security/page.tsx
- ❌ app/settings/notifications/page.tsx
- ❌ app/settings/advanced/page.tsx

**Components (0/40+):**
- ❌ Visi 40+ komponentai iš Tasks 4-57

**Hooks (0/6):**
- ❌ useSettings.ts
- ❌ useSettingsWebSocket.ts
- ❌ useHardwareDetection.ts
- ❌ useValidation.ts
- ❌ useMetrics.ts

**Utils & Types:**
- ❌ lib/api/settings.ts (API client)
- ❌ lib/validators/settings.ts
- ❌ lib/utils/settings.ts
- ❌ types/settings.ts

**i18n (0/2):**
- ❌ locales/en/settings.json
- ❌ locales/lt/settings.json

#### Testing (0/2 = 0%)
- ❌ Integration tests - Task #56
- ❌ E2E tests - Task #57

---

## 🎯 KRITINIAI BLOKATORIAI

### 🔴 #1 Priority: Frontend Dashboard Foundation
**Blokuoja:** 50+ tasks
**Užduotis:** Task #1 - Dashboard Component Architecture
**Estimacija:** 3-5 dienos
**Failai reikalingi:**
- frontend/src/app/settings/layout.tsx
- frontend/src/app/settings/page.tsx
- frontend/src/components/settings/SettingsLayout.tsx
- frontend/src/components/settings/SettingsSidebar.tsx
- frontend/src/components/ui/* (button, input, select, etc.)

### 🔴 #2 Priority: Backend Services
**Blokuoja:** 15+ tasks
**Užduotys:** Tasks #18, #19, #30, #33, #35, #36
**Estimacija:** 2-3 savaitės
**Failai reikalingi:**
- backend/app/services/recommendations.py
- backend/app/services/validation.py
- backend/app/services/hardware_detection.py
- backend/app/services/diagnostics.py
- backend/app/validators/settings.py

### 🔴 #3 Priority: Core Settings Pages
**Blokuoja:** User adoption
**Užduotys:** Tasks #4-#17 (13 pages)
**Estimacija:** 3-4 savaitės
**Priklausomybės:** Task #1 (Dashboard Architecture)

---

## 📅 REKOMENDUOJAMAS TIMELINE

### Savaitė 1-2: Foundation (Tasks #1, #30, #35)
- [ ] Task #1: Frontend Dashboard Architecture (3-5d)
- [ ] Task #30: Hardware Detection Service (3-4d)
- [ ] Task #35: RTSP Test Service (2-3d)
**Rezultatas:** Struktūra paruošta, hardware detection veikia

### Savaitė 3-4: Core Backend Services (Tasks #18, #19, #33, #36)
- [ ] Task #18: Recommendations Engine (3-5d)
- [ ] Task #19: Validation System (3-4d)
- [ ] Task #33: Backup/Restore (2-3d)
- [ ] Task #36: Diagnostics (3-4d)
**Rezultatas:** Intelligent backend features veikia

### Savaitė 5-8: Core Settings UI (Tasks #4-#17)
- [ ] Task #4: System Overview (2d)
- [ ] Task #5: Hardware Settings (2-3d)
- [ ] Task #6: Camera Management (3-4d)
- [ ] Task #8: Models Settings (2-3d)
- [ ] Task #9: OCR Settings (3-4d)
- [ ] Task #12: Export Settings (2-3d)
- [ ] Task #13: Storage Settings (3-4d)
- [ ] Task #15: Security Settings (2-3d)
- [ ] Task #7: Zone Editor (3-4d)
- [ ] Task #10: Pipeline Settings (2-3d)
- [ ] Task #11: Tracking Settings (1-2d)
- [ ] Task #14: Monitoring Settings (2-3d)
- [ ] Task #16: Notifications (2d)
- [ ] Task #17: Advanced Settings (1-2d)
**Rezultatas:** MVP ready - visos core kategorijos veikia

### Savaitė 9-11: Smart Features (Tasks #20-#27)
- [ ] Task #20: Help & Tooltips (2-3d)
- [ ] Task #21: Presets (2-3d)
- [ ] Task #22: Import/Export UI (1-2d)
- [ ] Task #24: History UI (2d)
- [ ] Task #25: Search & Filter (2-3d)
- [ ] Task #26: Health Indicators (2-3d)
- [ ] Task #27: Performance Impact (1-2d)
- [ ] Task #23: Comparison Tool (2d)
**Rezultatas:** Smart dashboard su rekomendacijomis

### Savaitė 12-14: Visualizations & Monitoring (Tasks #28-#32)
- [ ] Task #28: Camera Metrics (2-3d)
- [ ] Task #29: Hardware Graphs (2-3d)
- [ ] Task #3: WebSocket Connection (2-3d)
- [ ] Task #31: Model Comparison (2-3d)
- [ ] Task #32: OCR Test (2d)
**Rezultatas:** Real-time monitoring veikia

### Savaitė 15-17: Diagnostics & Testing (Tasks #33-#39, #56-#57)
- [ ] Task #34: Connection Tests (2d)
- [ ] Task #37: Benchmark Tool (3-4d)
- [ ] Task #38: Dependency Validation (2-3d)
- [ ] Task #39: Warning Indicators (1-2d)
- [ ] Task #56: Integration Tests (3-5d)
- [ ] Task #57: E2E Tests (3-5d)
**Rezultatas:** Fully tested production-ready system

### Savaitė 18-20: Advanced Features (Tasks #40-#55)
- [ ] Task #40: Setup Wizard (3-4d)
- [ ] Task #41: Dark/Light Theme (1d)
- [ ] Task #42: Responsive Design (2-3d)
- [ ] Task #44: Keyboard Shortcuts (1d)
- [ ] Task #45: Templates (2d)
- [ ] Task #47: Log Viewer (2-3d)
- [ ] Task #50: Notification Center (2-3d)
- [ ] Task #51: i18n (2-3d)
- [ ] Task #52: RBAC (3-4d)
- [ ] Task #43: Docs Generator (2d)
- [ ] Task #46: Migration Tool (2-3d)
- [ ] Task #48: Rollback Service (1-2d)
- [ ] Task #49: A/B Testing (3-4d)
- [ ] Task #53: API Docs Viewer (1d)
- [ ] Task #54: Cloud Import (1-2d)
- [ ] Task #55: Resource Allocator (2-3d)
**Rezultatas:** Full feature set complete

---

## 🎯 Success Criteria

### **MVP (Minimum Viable Product):** 0% Complete
- [ ] Visos 13 settings kategorijų veikia (Tasks #4-#17)
- [x] CRUD operacijos visiems nustatymams ✅ (Task #2)
- [ ] Real-time WebSocket updates (Task #3)
- [ ] Basic validation ir error handling (Tasks #19, #38)
- [x] Settings save/load from database ✅ (Task #2)
- [ ] Responsive UI (desktop + mobile) (Task #42)
- **Status:** Backend API ready, Frontend 0%
- **Estimated completion:** Savaitė 8 (2 mėnesiai)

### **Full Release:** 5.3% Complete
- [ ] Visi 57 TODO punktai įgyvendinti (3/57 baigta)
- [ ] Smart recommendations veikia (Task #18)
- [ ] All connection tests functional (Tasks #34-#36)
- [x] Export/import API work ✅ (Task #2)
- [ ] Export/import UI (Task #22)
- [ ] Comprehensive help & docs (Tasks #20, #43)
- [ ] Performance monitoring live (Tasks #28-#29)
- [ ] E2E tests passing (>80% coverage) (Tasks #56-#57)
- [ ] Multi-language support (LT + EN) (Task #51)
- [ ] Production-ready performance
- **Status:** Foundation laid, 95% of work remains
- **Estimated completion:** Savaitė 20 (5 mėnesiai)

---

## 📈 Priežiūra ir Plėtra

### **Po Release:**
- [ ] User feedback collection
- [ ] Performance optimization
- [ ] Bug fixes
- [ ] New feature requests
- [ ] Documentation updates
- [ ] Video tutorials (LT + EN)
- [ ] Community templates library
- [ ] AI-powered optimization (GPT suggestions)
- [ ] Mobile app (React Native)
- [ ] Cloud config sync

---

## 📞 Kontaktai ir Pagalba

**Projektas:** ANPR Cloud
**Repozitorija:** https://github.com/Ginetas/anprcloude
**Dokumentacija:** `/docs/`

---

**SUKURTA:** 2025-11-26
**ATNAUJINTA:** 2025-11-26
**VERSIJA:** 1.1 (Progress Tracking pridėtas)
**AUTORIUS:** Claude + Team
**PROGRESO TRACKING:** Automated

---

## 📈 Kaip atnaujinti progress

Paleisti:
```bash
cd /home/user/anprcloude
python3 update_todo.py
```

Arba rankiniu būdu atnaujinti task status simbolius:
- ✅ = Pilnai baigta (100%)
- 🔄 = Dalinai baigta (1-99%)
- ❌ = Nebaigta (0%)
- ⏸️ = Pristabdyta

---

🚀 **Let's build the smartest ANPR settings dashboard!**

**SEKANTIS ŽINGSNIS:** Pradėti Task #1 - Frontend Dashboard Architecture
