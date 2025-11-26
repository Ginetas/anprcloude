# ANPR Engine - Automatinio Valstybinių Numerių Atpažinimo Sistema

<div align="center">

**Pilnas ALPR/ANPR sprendimas su Edge įrenginiais, Backend API ir Web valdymo sąsaja**

[Dokumentacija](docs/) | [Instaliacija](docs/INSTALLATION.md) | [API](docs/API.md) | [Architektūra](docs/ARCHITECTURE.md)

</div>

---

## 📋 Turinys

- [Apžvalga](#apžvalga)
- [Pagrindinės funkcijos](#pagrindinės-funkcijos)
- [Sistemos architektūra](#sistemos-architektūra)
- [Greita pradžia](#greita-pradžia)
- [Instaliacija](#instaliacija)
- [Konfigūracija](#konfigūracija)
- [Dokumentacija](#dokumentacija)
- [Plėtojimas](#plėtojimas)
- [Licencija](#licencija)

---

## 🎯 Apžvalga

**ANPR Engine** – tai pilnas automatinio valstybinių numerių atpažinimo (ALPR/ANPR) sprendimas, skirtas real-time numerių lentelių atpažinimui iš video srautų. Sistema veikia su:

- **Edge įrenginiais** (Raspberry Pi + Coral TPU / Hailo-8L / GPU / CPU)
- **Centraliniu Backend** (FastAPI + PostgreSQL)
- **Web valdymo sąsaja** (Next.js)

### Tipiniai naudojimo atvejai

- 🅿️ **Parkavimo sistemos** – automatinis įvažiavimo/išvažiavimo fiksavimas
- 🔐 **Prieigos kontrolė** – užtvarų valdymas pagal numerius
- 🚔 **Saugumo sistemos** – įtartinų numerių aptikimas
- 📊 **Srautų analizė** – transporto statistika
- 🏢 **Verslo apskaita** – klientų vizitų registracija

---

## ✨ Pagrindinės funkcijos

### Edge Worker
- ✅ **RTSP video ingest** su GStreamer
- ✅ **Objektų detekcija** (automobilio ir numerio zonos)
- ✅ **Multi-modelio OCR ensemble** su consensus algoritmu
- ✅ **Centroid tracking** – objektų sekimas tarp kadrų
- ✅ **Zonų valdymas** – enter/exit/custom zonos
- ✅ **Hardware akceleracija**:
  - Google Coral Edge TPU
  - Hailo-8L NPU
  - NVIDIA GPU (CUDA)
  - CPU fallback
- ✅ **Event retry queue** – neprarandami eventai jei nutrūksta ryšys
- ✅ **Konfigūruojami exporteriai** (REST, WebSocket, MQTT, Kafka)

### Backend API
- ✅ **FastAPI** su automatine dokumentacija (Swagger/ReDoc)
- ✅ **PostgreSQL** duomenų bazė su SQLModel ORM
- ✅ **Real-time WebSocket stream** frontendui
- ✅ **RESTful API** visoms operacijoms:
  - Event ingest
  - Kamerų, zonų, modelių valdymas
  - Jutiklių (TPMS, barjerai) integracija
  - Eksporterių konfigūracija
- ✅ **Health checks** ir monitoring
- ✅ **S3/Local file storage** nuotraukoms

### Frontend (Web UI)
- ✅ **Next.js App Router** su TypeScript
- ✅ **Real-time dashboard**:
  - Live event stream
  - Kamerų statusas
  - Sistema statistika
- ✅ **Pilnas konfigūravimo UI**:
  - Kamerų valdymas su RTSP test
  - Vizualus zonų redaktorius
  - Modelių konfigūracija
  - Jutiklių nustatymai
- ✅ **Integracijų valdymas**:
  - Eksporterių konfigūracija
  - Connection testing
  - Retry policy nustatymai
- ✅ **Responsive dizainas** su Tailwind CSS
- ✅ **Global state** su Zustand
- ✅ **Toast notifikacijos** (sėkmės/klaidos/perspėjimai)

---

## 🏗️ Sistemos architektūra

```
┌─────────────────────────────────────────────────────────────────┐
│                         ANPR SYSTEM                              │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Camera 1    │      │  Camera 2    │      │  Camera N    │
│  (RTSP)      │      │  (RTSP)      │      │  (RTSP)      │
└──────┬───────┘      └──────┬───────┘      └──────┬───────┘
       │                     │                     │
       └─────────────────────┴─────────────────────┘
                             │
                   ┌─────────▼──────────┐
                   │   Edge Worker(s)   │
                   │  ┌──────────────┐  │
                   │  │  GStreamer   │  │
                   │  │   Pipeline   │  │
                   │  └──────┬───────┘  │
                   │         │          │
                   │  ┌──────▼───────┐  │
                   │  │  Detection   │  │
                   │  │  + Tracking  │  │
                   │  └──────┬───────┘  │
                   │         │          │
                   │  ┌──────▼───────┐  │
                   │  │OCR Ensemble  │  │
                   │  │(Multi-model) │  │
                   │  └──────┬───────┘  │
                   │         │          │
                   │  ┌──────▼───────┐  │
                   │  │  Dispatcher  │  │
                   │  │  (Exporters) │  │
                   │  └──────┬───────┘  │
                   └─────────┼──────────┘
                             │
                    REST/WebSocket/MQTT
                             │
                   ┌─────────▼──────────┐
                   │   Backend API      │
                   │  ┌──────────────┐  │
                   │  │   FastAPI    │  │
                   │  │  + SQLModel  │  │
                   │  └──────┬───────┘  │
                   │         │          │
                   │  ┌──────▼───────┐  │
                   │  │ PostgreSQL   │  │
                   │  │   Database   │  │
                   │  └──────────────┘  │
                   └─────────┬──────────┘
                             │
                       REST + WebSocket
                             │
                   ┌─────────▼──────────┐
                   │   Frontend UI      │
                   │  ┌──────────────┐  │
                   │  │   Next.js    │  │
                   │  │  Dashboard   │  │
                   │  │  + Config    │  │
                   │  └──────────────┘  │
                   └────────────────────┘
```

**Komponentai:**

1. **Edge Worker** (`edge/`)
   - Python + GStreamer + TensorFlow/PyTorch
   - Vykdomas ant Raspberry Pi / Linux įrenginio
   - Real-time video processing ir OCR

2. **Backend** (`backend/`)
   - FastAPI + SQLModel + PostgreSQL
   - Event storage ir API
   - WebSocket real-time stream

3. **Frontend** (`frontend/`)
   - Next.js 14 (App Router) + TypeScript
   - Dashboard ir konfigūravimo UI
   - Real-time updates per WebSocket

---

## 🚀 Greita pradžia

### Su Docker Compose (rekomenduojama developmentui)

```bash
# 1. Klonuoti repo
git clone https://github.com/yourusername/anpr-engine.git
cd anpr-engine

# 2. Nukopijuoti ir pritaikyti konfigūraciją
cp .env.example .env
# Redaguoti .env pagal savo poreikius

# 3. Paleisti visus servisus
docker-compose up -d

# 4. Atidaryti naršyklėje
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

### Edge įrenginio instaliacija

#### Raspberry Pi + Hailo-8L
```bash
curl -sSL https://raw.githubusercontent.com/yourusername/anpr-engine/main/edge/install/install_rpi_hailo.sh | bash
```

#### Raspberry Pi + Google Coral
```bash
curl -sSL https://raw.githubusercontent.com/yourusername/anpr-engine/main/edge/install/install_rpi_coral.sh | bash
```

#### Linux su GPU/CPU
```bash
curl -sSL https://raw.githubusercontent.com/yourusername/anpr-engine/main/edge/install/install_linux.sh | bash
```

---

## 📦 Instaliacija

### Reikalavimai

#### Edge Worker
- **Hardware**:
  - Raspberry Pi 4/5 (4GB+ RAM) + Coral TPU / Hailo-8L **arba**
  - Linux įrenginys su GPU (NVIDIA) **arba**
  - Linux įrenginys su CPU (x86_64)
- **OS**: Raspberry Pi OS / Ubuntu 20.04+ / Debian 11+
- **Python**: 3.9+
- **Dependencijos**: GStreamer, OpenCV, TensorFlow Lite / PyTorch

#### Backend
- **Python**: 3.9+
- **PostgreSQL**: 13+
- **RAM**: 2GB+
- **Disk**: 10GB+ (priklausomai nuo eventų kiekio)

#### Frontend
- **Node.js**: 18+
- **npm/yarn/pnpm**

### Detalios instrukcijos

Žiūrėkite [INSTALLATION.md](docs/INSTALLATION.md) dėl detalių instaliavimo instrukcijų kiekvienam komponentui.

---

## ⚙️ Konfigūracija

### Edge Worker

Pagrindinė konfigūracija: `edge/config/config.yaml`

```yaml
# Kameros
cameras:
  - id: cam-001
    name: "Įvažiavimas pagrindinis"
    rtsp_url: "rtsp://admin:password@192.168.1.100:554/stream1"
    fps: 10
    resolution: [1920, 1080]
    zone_id: zone-entrance
    detection_model: yolov8-vehicle
    ocr_models:
      - paddle-ocr-lt
      - tesseract-lt
      - easy-ocr

# Zonos
zones:
  - id: zone-entrance
    name: "Įvažiavimo zona"
    camera_id: cam-001
    type: enter
    geometry:
      type: polygon
      points: [[100, 200], [500, 200], [500, 600], [100, 600]]

# Exporteriai
exporters:
  - type: rest
    url: "http://backend:8000/events/ingest"
    retry:
      max_attempts: 5
      backoff: exponential
```

### Backend

Aplinkos kintamieji `.env`:

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/anpr
REDIS_URL=redis://localhost:6379
S3_BUCKET=anpr-events
S3_ENDPOINT=http://localhost:9000
JWT_SECRET=your-secret-key
```

### Frontend

Aplinkos kintamieji `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

---

## 📚 Dokumentacija

Detalesnė dokumentacija:

- [**Architektūra**](docs/ARCHITECTURE.md) – sistemos architektūros aprašymas
- [**Instaliacija**](docs/INSTALLATION.md) – detalios instaliavimo instrukcijos
- [**API dokumentacija**](docs/API.md) – Backend API endpointai
- [**Deployment**](docs/DEPLOYMENT.md) – production deployment gidas
- [**Edge Worker**](edge/README.md) – edge komponento dokumentacija
- [**Backend**](backend/README.md) – backend dokumentacija
- [**Frontend**](frontend/README.md) – frontend dokumentacija

---

## 🛠️ Plėtojimas

### Development setup

```bash
# 1. Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# 2. Frontend
cd frontend
npm install
npm run dev

# 3. Edge (testuoti lokaliai)
cd edge
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python pipeline.py --config config/config.yaml
```

### Testai

```bash
# Backend testai
cd backend
pytest

# Frontend testai
cd frontend
npm test

# Edge testai
cd edge
pytest
```

### Code style

Projektas naudoja:
- **Python**: `black`, `isort`, `flake8`, `mypy`
- **TypeScript**: `prettier`, `eslint`

```bash
# Python formatting
black .
isort .

# TypeScript formatting
npm run format
```

---

## 🤝 Prisidėjimas

Contributions yra laukiami! Prašome:

1. Fork'inti projektą
2. Sukurti feature branch (`git checkout -b feature/amazing-feature`)
3. Commit'inti pakeitimus (`git commit -m 'Add amazing feature'`)
4. Push'inti į branch (`git push origin feature/amazing-feature`)
5. Atidaryti Pull Request

---

## 📄 Licencija

Šis projektas yra platinamas su MIT licencija. Žiūrėkite `LICENSE` failą dėl detalių.

---

## 🙏 Padėkos

- [OpenCV](https://opencv.org/)
- [GStreamer](https://gstreamer.freedesktop.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/)
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [YOLOv8](https://github.com/ultralytics/ultralytics)

---

## 📧 Kontaktai

Klausimams ir pagalbai:
- GitHub Issues: [https://github.com/yourusername/anpr-engine/issues](https://github.com/yourusername/anpr-engine/issues)
- Email: support@your-domain.com

---

<div align="center">

**Sukurta su ❤️ naudojant Python, TypeScript ir AI**

</div>