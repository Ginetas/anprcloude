# TODO: Smart Settings Dashboard - Išmanusis Nustatymų Valdymo Frontentas

**Projektas:** ANPR Cloud - Išmanusis Nustatymų Dashboard
**Data:** 2025-11-26
**Statusas:** Planuojama
**Prioritetas:** Aukštas

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

### **FAZĖ 1: Pagrindas ir Architektūra (3 užduotys)**

#### ☐ 1. Dashboard Component Architecture
- [ ] Sukurti base layout su navigation
- [ ] Settings kategorijų sidebar
- [ ] Main content area su tabs
- [ ] Breadcrumb navigation
- [ ] Quick search bar
- **Technologijos:** Next.js 14, React 18, TypeScript
- **Komponentai:** SettingsLayout, SettingsSidebar, SettingsContent

#### ☐ 2. Backend Settings API Endpoints
- [ ] GET /api/settings - visų nustatymų sąrašas
- [ ] GET /api/settings/:category - kategorijos nustatymai
- [ ] PUT /api/settings/:id - atnaujinti nustatymą
- [ ] POST /api/settings/bulk - bulk update
- [ ] GET /api/settings/recommendations - rekomendacijos
- [ ] GET /api/settings/validation/:id - validuoti nustatymą
- [ ] GET /api/settings/templates - nustatymų templates
- [ ] POST /api/settings/export - eksportuoti konfigūraciją
- [ ] POST /api/settings/import - importuoti konfigūraciją
- **Backend:** FastAPI, Pydantic schemas
- **Failas:** `backend/app/api/routes/settings.py`

#### ☐ 3. Real-time WebSocket Connection
- [ ] WebSocket endpoint `/ws/settings`
- [ ] Settings updates broadcasting
- [ ] System status streaming
- [ ] Performance metrics streaming
- [ ] Error/warning notifications
- [ ] Reconnection logic su exponential backoff
- **Frontend hook:** `useSettingsWebSocket()`
- **Backend:** WebSocket manager

---

### **FAZĖ 2: Core Settings Kategorijos (13 užduočių)**

#### ☐ 4. System Overview Dashboard
**Komponentas:** `components/settings/SystemOverview.tsx`
- [ ] Worker ID ir aplinkos informacija
- [ ] System uptime
- [ ] Current hardware status (GPU/NPU/CPU)
- [ ] Active cameras count
- [ ] Active models info
- [ ] System health indicator (🟢🟡🔴)
- [ ] Quick actions (restart, refresh)
- **Real-time data:** WebSocket updates

#### ☐ 5. Hardware & Performance Settings
**Komponentas:** `components/settings/HardwareSettings.tsx`
- [ ] Hardware type selector (CPU/GPU/Coral/Hailo/NPU)
- [ ] Device ID input
- [ ] CUDA settings (enabled, device ID)
- [ ] Thread count slider (1-32)
- [ ] GPU memory limit
- [ ] NPU power mode
- [ ] Hardware detection button
- [ ] Performance recommendations
- **Nustatymai:** 12+ hardware config options

#### ☐ 6. Camera Management Interface
**Komponentas:** `components/settings/CameraManagement.tsx`
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

#### ☐ 7. Detection Zones Visual Editor
**Komponentas:** `components/settings/ZoneEditor.tsx`
- [ ] Canvas su camera feed
- [ ] Polygon drawing tool
- [ ] Zone types: detection, exclusion, parking
- [ ] Zone properties panel
- [ ] Multiple zones per camera
- [ ] Zone testing (highlight detections)
- [ ] Save/load zones
- **Biblioteka:** Fabric.js arba Konva.js

#### ☐ 8. Detection Models Configuration
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

#### ☐ 9. OCR Configuration Panel
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

#### ☐ 10. Video Pipeline Settings
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

#### ☐ 11. Object Tracking & Filtering
**Komponentas:** `components/settings/TrackingSettings.tsx`
- [ ] Max disappeared slider (10-200 frames)
- [ ] Max distance slider (10-200 pixels)
- [ ] Cooldown seconds input (0-3600)
- [ ] Tracking algorithm selector
- [ ] Visual tracking preview
- **Nustatymai:** 5+ tracking settings

#### ☐ 12. Data Export Configuration
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

#### ☐ 13. Storage & Database Settings
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

#### ☐ 14. Monitoring & Metrics Dashboard
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

#### ☐ 15. Security & Access Settings
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

#### ☐ 16. Notifications Configuration
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

#### ☐ 17. Advanced Settings Panel
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

#### ☐ 18. Smart Recommendations Engine
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

#### ☐ 19. Settings Validation System
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

#### ☐ 20. Contextual Help & Descriptions
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

#### ☐ 21. Settings Presets
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

#### ☐ 22. Settings Export/Import
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

#### ☐ 23. Settings Comparison Tool
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

#### ☐ 24. Settings Change History & Audit Log
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

#### ☐ 25. Settings Search & Filter
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

#### ☐ 26. Live System Health Indicators
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

#### ☐ 27. Performance Impact Indicators
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

#### ☐ 28. Real-time FPS & Latency Monitoring
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

#### ☐ 29. Hardware Utilization Graphs
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

#### ☐ 30. Automatic Hardware Detection
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

#### ☐ 31. Model Performance Comparison Tool
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

#### ☐ 32. OCR Test Interface
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

#### ☐ 33. Settings Backup & Restore
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

#### ☐ 34. Database Connection Tests
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

#### ☐ 35. RTSP Stream Test & Validation
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

#### ☐ 36. System Diagnostics Tool
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

#### ☐ 37. Performance Benchmarking Tool
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

#### ☐ 38. Settings Dependency Validation
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

#### ☐ 39. Warning Indicators for Suboptimal Configurations
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

#### ☐ 40. Quick Setup Wizard
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

#### ☐ 41. Dark/Light Theme Support
**Komponentas:** Theme system
- [ ] Theme toggle (sun/moon icon)
- [ ] Persist theme preference (localStorage)
- [ ] Tailwind dark mode classes
- [ ] System preference detection
- [ ] Smooth theme transitions
- [ ] Theme preview

#### ☐ 42. Responsive Design for Mobile
- [ ] Responsive layouts:
  - [ ] Desktop: Sidebar + main content
  - [ ] Tablet: Collapsible sidebar
  - [ ] Mobile: Bottom nav or drawer
- [ ] Touch-friendly controls
- [ ] Mobile-optimized forms
- [ ] Swipe gestures
- [ ] Responsive tables (cards on mobile)

#### ☐ 43. Settings Documentation Generator
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

#### ☐ 44. Keyboard Shortcuts
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

#### ☐ 45. Settings Templates
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

#### ☐ 46. Settings Migration Tool
**Backend:** `backend/app/services/migration.py`
- [ ] Version migration:
  - [ ] Detect config version
  - [ ] Apply migrations (v1 → v2 → v3)
  - [ ] Transform old settings to new schema
- [ ] Migration history
- [ ] Rollback migrations
- [ ] Backup before migration
- [ ] Migration testing (dry-run)

#### ☐ 47. Live Log Viewer
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

#### ☐ 48. Settings Rollback Functionality
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

#### ☐ 49. A/B Testing for Model Configurations
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

#### ☐ 50. Notification Center
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

#### ☐ 51. Multi-language Support (i18n)
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

#### ☐ 52. Settings Permissions & RBAC
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

#### ☐ 53. API Documentation Viewer
**Komponentas:** `components/settings/APIDocViewer.tsx`
- [ ] Integrate OpenAPI/Swagger:
  - [ ] Auto-generate from FastAPI
  - [ ] Embed Swagger UI or Redoc
- [ ] Endpoint browser:
  - [ ] List all API endpoints
  - [ ] Request/response schemas
  - [ ] Try it out (interactive)
- [ ] Code examples (curl, Python, JS)

#### ☐ 54. Settings Import from Cloud/File/URL
**Komponentas:** Enhanced import
- [ ] Import sources:
  - [ ] Local file upload ✅ (already in #22)
  - [ ] URL fetch (fetch remote config)
  - [ ] Cloud storage (S3, Google Drive)
  - [ ] GitHub repository
- [ ] URL import validation
- [ ] Auth for cloud sources

#### ☐ 55. System Resource Allocator with Visual Feedback
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

#### ☐ 56. Integration Testing for Settings Workflows
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

#### ☐ 57. Comprehensive E2E Tests for Settings Dashboard
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

## 🎯 Success Criteria

### **MVP (Minimum Viable Product):**
✅ Visos 13 settings kategorijų veikia
✅ CRUD operacijos visiems nustatymams
✅ Real-time WebSocket updates
✅ Basic validation ir error handling
✅ Settings save/load from database
✅ Responsive UI (desktop + mobile)

### **Full Release:**
✅ Visi 57 TODO punktai įgyvendinti
✅ Smart recommendations veikia
✅ All connection tests functional
✅ Export/import/backup work
✅ Comprehensive help & docs
✅ Performance monitoring live
✅ E2E tests passing (>80% coverage)
✅ Multi-language support (LT + EN)
✅ Production-ready performance

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
**VERSIJA:** 1.0
**AUTORIUS:** Claude + Team

🚀 **Let's build the smartest ANPR settings dashboard!**
