# ANPR Engine - Backend API Documentation

**Base URL:** `http://localhost:8000`
**API Version:** v1
**Documentation:** http://localhost:8000/docs (Swagger UI)

## Table of Contents

1. [Authentication](#authentication)
2. [Events API](#events-api)
3. [Config API](#config-api)
4. [Exporters API](#exporters-api)
5. [Health Check](#health-check)
6. [WebSocket Endpoints](#websocket-endpoints)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)

---

## Authentication

### Overview

The ANPR Engine backend uses JWT (JSON Web Token) authentication for API endpoints. Edge workers authenticate using API keys.

### JWT Token

**Endpoint:** `POST /auth/token`

**Request Body:**
```json
{
  "username": "admin",
  "password": "your-password"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Error (401 Unauthorized):**
```json
{
  "detail": "Invalid credentials"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your-password"
  }'
```

### API Key Authentication (Edge Worker)

Edge workers use API keys for authentication. Include the API key in the `X-API-Key` header:

```bash
curl -X POST http://localhost:8000/events/ingest \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{...}'
```

### Token Usage

Include the JWT token in the `Authorization` header for all subsequent requests:

```bash
curl -X GET http://localhost:8000/config/cameras \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## Events API

### Ingest Event from Edge

**Endpoint:** `POST /events/ingest`

**Authentication:** API Key or JWT Token
**Content-Type:** `application/json` or `multipart/form-data`
**Rate Limit:** 1000 requests/minute

**Request Body (JSON):**
```json
{
  "event_id": "evt-20231215-001-cam1",
  "timestamp": "2023-12-15T14:30:45.123Z",
  "camera_id": "cam-001",
  "zone_id": "zone-entrance",
  "plate_text": "ABC123",
  "confidence": 0.95,
  "raw_candidates": [
    {
      "text": "ABC123",
      "confidence": 0.95,
      "model": "paddle-ocr"
    },
    {
      "text": "ABC123",
      "confidence": 0.92,
      "model": "tesseract"
    }
  ],
  "vehicle_info": {
    "color": "white",
    "type": "sedan",
    "confidence": 0.87
  },
  "tpms_status": {
    "sensors": 4,
    "temperature": 42,
    "pressure": 2.1,
    "status": "ok"
  },
  "metadata": {
    "edge_worker_id": "edge-001",
    "processing_time_ms": 245,
    "frame_number": 1523
  }
}
```

**Request Body (Multipart - with images):**
```
POST /events/ingest HTTP/1.1
Host: localhost:8000
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary
X-API-Key: your-api-key

------WebKitFormBoundary
Content-Disposition: form-data; name="event"

{
  "event_id": "evt-20231215-001-cam1",
  "timestamp": "2023-12-15T14:30:45.123Z",
  ...
}
------WebKitFormBoundary
Content-Disposition: form-data; name="frame"; filename="frame.jpg"
Content-Type: image/jpeg

[JPEG binary data]
------WebKitFormBoundary
Content-Disposition: form-data; name="crop"; filename="crop.jpg"
Content-Type: image/jpeg

[JPEG binary data]
------WebKitFormBoundary--
```

**Response (202 Accepted):**
```json
{
  "id": "evt-20231215-001-cam1",
  "status": "accepted",
  "timestamp": "2023-12-15T14:30:45.123Z",
  "message": "Event queued for processing"
}
```

**Response (409 Conflict - Duplicate Event):**
```json
{
  "detail": "Event with ID evt-20231215-001-cam1 already exists"
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Invalid event data",
  "errors": [
    {
      "field": "plate_text",
      "message": "plate_text is required"
    }
  ]
}
```

**cURL Examples:**

```bash
# JSON request
curl -X POST http://localhost:8000/events/ingest \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "event_id": "evt-20231215-001-cam1",
    "timestamp": "2023-12-15T14:30:45.123Z",
    "camera_id": "cam-001",
    "zone_id": "zone-entrance",
    "plate_text": "ABC123",
    "confidence": 0.95,
    "raw_candidates": [],
    "metadata": {}
  }'

# Multipart request with images
curl -X POST http://localhost:8000/events/ingest \
  -H "X-API-Key: your-api-key" \
  -F "event={\"event_id\":\"evt-001\",\"plate_text\":\"ABC123\"}" \
  -F "frame=@frame.jpg" \
  -F "crop=@crop.jpg"
```

---

### List Events

**Endpoint:** `GET /events`

**Authentication:** JWT Token
**Query Parameters:**
- `skip` (int, default: 0) - Number of records to skip
- `limit` (int, default: 100, max: 1000) - Number of records to return
- `camera_id` (string, optional) - Filter by camera ID
- `zone_id` (string, optional) - Filter by zone ID
- `plate_text` (string, optional) - Filter by plate text (partial match)
- `start_date` (ISO 8601 datetime, optional) - Filter events after this timestamp
- `end_date` (ISO 8601 datetime, optional) - Filter events before this timestamp
- `min_confidence` (float, 0-1, optional) - Filter by minimum confidence
- `sort_by` (string, default: "timestamp") - Sort field: "timestamp", "confidence", "plate_text"
- `sort_order` (string, default: "desc") - Sort order: "asc" or "desc"

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "evt-20231215-001-cam1",
      "event_id": "evt-20231215-001-cam1",
      "timestamp": "2023-12-15T14:30:45.123Z",
      "camera_id": "cam-001",
      "zone_id": "zone-entrance",
      "plate_text": "ABC123",
      "confidence": 0.95,
      "raw_candidates": [
        {
          "text": "ABC123",
          "confidence": 0.95,
          "model": "paddle-ocr"
        }
      ],
      "frame_url": "http://localhost:9000/anpr-events/evt-20231215-001-cam1/frame.jpg",
      "crop_url": "http://localhost:9000/anpr-events/evt-20231215-001-cam1/crop.jpg",
      "vehicle_info": {
        "color": "white",
        "type": "sedan",
        "confidence": 0.87
      },
      "tpms_status": {
        "sensors": 4,
        "temperature": 42,
        "pressure": 2.1,
        "status": "ok"
      },
      "metadata": {
        "edge_worker_id": "edge-001",
        "processing_time_ms": 245
      },
      "created_at": "2023-12-15T14:30:45.123Z"
    }
  ],
  "total": 1523,
  "skip": 0,
  "limit": 100
}
```

**Response (401 Unauthorized):**
```json
{
  "detail": "Not authenticated"
}
```

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/events?camera_id=cam-001&limit=50&sort_order=desc" \
  -H "Authorization: Bearer your-jwt-token"
```

---

### Get Event Details

**Endpoint:** `GET /events/{id}`

**Authentication:** JWT Token
**Path Parameters:**
- `id` (string) - Event ID

**Response (200 OK):**
```json
{
  "id": "evt-20231215-001-cam1",
  "event_id": "evt-20231215-001-cam1",
  "timestamp": "2023-12-15T14:30:45.123Z",
  "camera_id": "cam-001",
  "zone_id": "zone-entrance",
  "plate_text": "ABC123",
  "confidence": 0.95,
  "raw_candidates": [
    {
      "text": "ABC123",
      "confidence": 0.95,
      "model": "paddle-ocr"
    },
    {
      "text": "ABC123",
      "confidence": 0.92,
      "model": "tesseract"
    },
    {
      "text": "ABC123",
      "confidence": 0.89,
      "model": "easy-ocr"
    }
  ],
  "frame_url": "http://localhost:9000/anpr-events/evt-20231215-001-cam1/frame.jpg",
  "crop_url": "http://localhost:9000/anpr-events/evt-20231215-001-cam1/crop.jpg",
  "vehicle_info": {
    "color": "white",
    "type": "sedan",
    "confidence": 0.87,
    "bbox": {
      "x": 100,
      "y": 150,
      "width": 300,
      "height": 200
    }
  },
  "tpms_status": {
    "sensors": 4,
    "temperature": 42,
    "pressure": 2.1,
    "status": "ok"
  },
  "metadata": {
    "edge_worker_id": "edge-001",
    "processing_time_ms": 245,
    "frame_number": 1523
  },
  "created_at": "2023-12-15T14:30:45.123Z"
}
```

**Response (404 Not Found):**
```json
{
  "detail": "Event not found"
}
```

**cURL Example:**
```bash
curl -X GET http://localhost:8000/events/evt-20231215-001-cam1 \
  -H "Authorization: Bearer your-jwt-token"
```

---

### Get Event Statistics

**Endpoint:** `GET /events/stats`

**Authentication:** JWT Token
**Query Parameters:**
- `camera_id` (string, optional) - Filter by camera ID
- `zone_id` (string, optional) - Filter by zone ID
- `start_date` (ISO 8601 datetime, optional) - Start date for statistics
- `end_date` (ISO 8601 datetime, optional) - End date for statistics
- `interval` (string, default: "hour") - Aggregation interval: "minute", "hour", "day", "week"

**Response (200 OK):**
```json
{
  "total_events": 15342,
  "avg_confidence": 0.92,
  "min_confidence": 0.65,
  "max_confidence": 0.99,
  "unique_plates": 4521,
  "event_rate": {
    "per_second": 1.2,
    "per_minute": 72,
    "per_hour": 4320
  },
  "by_camera": {
    "cam-001": {
      "count": 7521,
      "avg_confidence": 0.93
    },
    "cam-002": {
      "count": 7821,
      "avg_confidence": 0.91
    }
  },
  "by_zone": {
    "zone-entrance": {
      "count": 10000,
      "avg_confidence": 0.92
    },
    "zone-exit": {
      "count": 5342,
      "avg_confidence": 0.93
    }
  },
  "timeline": [
    {
      "timestamp": "2023-12-15T14:00:00Z",
      "count": 185,
      "avg_confidence": 0.91
    },
    {
      "timestamp": "2023-12-15T15:00:00Z",
      "count": 192,
      "avg_confidence": 0.92
    }
  ]
}
```

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/events/stats?camera_id=cam-001&interval=hour" \
  -H "Authorization: Bearer your-jwt-token"
```

---

## Config API

### Cameras

#### List Cameras

**Endpoint:** `GET /config/cameras`

**Authentication:** JWT Token
**Query Parameters:**
- `skip` (int, default: 0) - Number of records to skip
- `limit` (int, default: 100) - Number of records to return
- `enabled` (boolean, optional) - Filter by enabled status

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "cam-001",
      "name": "Entrance Main",
      "rtsp_url": "rtsp://admin:password@192.168.1.100:554/stream1",
      "enabled": true,
      "zone_id": "zone-entrance",
      "fps": 10,
      "resolution": {
        "width": 1920,
        "height": 1080
      },
      "detection_model": "yolov8-vehicle",
      "ocr_models": [
        "paddle-ocr-lt",
        "tesseract-lt",
        "easy-ocr"
      ],
      "metadata": {
        "location": "Main gate",
        "manufacturer": "Hikvision"
      },
      "created_at": "2023-12-10T10:00:00Z",
      "updated_at": "2023-12-15T14:30:00Z"
    }
  ],
  "total": 2,
  "skip": 0,
  "limit": 100
}
```

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/config/cameras?enabled=true" \
  -H "Authorization: Bearer your-jwt-token"
```

---

#### Create Camera

**Endpoint:** `POST /config/cameras`

**Authentication:** JWT Token
**Request Body:**
```json
{
  "name": "Entrance Main",
  "rtsp_url": "rtsp://admin:password@192.168.1.100:554/stream1",
  "enabled": true,
  "zone_id": "zone-entrance",
  "fps": 10,
  "resolution": {
    "width": 1920,
    "height": 1080
  },
  "detection_model": "yolov8-vehicle",
  "ocr_models": [
    "paddle-ocr-lt",
    "tesseract-lt"
  ],
  "metadata": {
    "location": "Main gate",
    "manufacturer": "Hikvision"
  }
}
```

**Response (201 Created):**
```json
{
  "id": "cam-001",
  "name": "Entrance Main",
  "rtsp_url": "rtsp://admin:password@192.168.1.100:554/stream1",
  "enabled": true,
  "zone_id": "zone-entrance",
  "fps": 10,
  "resolution": {
    "width": 1920,
    "height": 1080
  },
  "detection_model": "yolov8-vehicle",
  "ocr_models": [
    "paddle-ocr-lt",
    "tesseract-lt"
  ],
  "metadata": {
    "location": "Main gate",
    "manufacturer": "Hikvision"
  },
  "created_at": "2023-12-15T14:30:00Z",
  "updated_at": "2023-12-15T14:30:00Z"
}
```

**Response (400 Bad Request):**
```json
{
  "detail": "Validation error",
  "errors": [
    {
      "field": "rtsp_url",
      "message": "Invalid RTSP URL format"
    }
  ]
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/config/cameras \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "name": "Entrance Main",
    "rtsp_url": "rtsp://admin:password@192.168.1.100:554/stream1",
    "enabled": true,
    "zone_id": "zone-entrance",
    "fps": 10,
    "resolution": {"width": 1920, "height": 1080},
    "detection_model": "yolov8-vehicle",
    "ocr_models": ["paddle-ocr-lt", "tesseract-lt"],
    "metadata": {"location": "Main gate"}
  }'
```

---

#### Get Camera

**Endpoint:** `GET /config/cameras/{id}`

**Authentication:** JWT Token
**Path Parameters:**
- `id` (string) - Camera ID

**Response (200 OK):**
```json
{
  "id": "cam-001",
  "name": "Entrance Main",
  "rtsp_url": "rtsp://admin:password@192.168.1.100:554/stream1",
  "enabled": true,
  "zone_id": "zone-entrance",
  "fps": 10,
  "resolution": {
    "width": 1920,
    "height": 1080
  },
  "detection_model": "yolov8-vehicle",
  "ocr_models": [
    "paddle-ocr-lt",
    "tesseract-lt"
  ],
  "metadata": {
    "location": "Main gate"
  },
  "created_at": "2023-12-10T10:00:00Z",
  "updated_at": "2023-12-15T14:30:00Z"
}
```

**cURL Example:**
```bash
curl -X GET http://localhost:8000/config/cameras/cam-001 \
  -H "Authorization: Bearer your-jwt-token"
```

---

#### Update Camera

**Endpoint:** `PUT /config/cameras/{id}`

**Authentication:** JWT Token
**Path Parameters:**
- `id` (string) - Camera ID

**Request Body:**
```json
{
  "name": "Entrance Main (Updated)",
  "enabled": false,
  "fps": 15,
  "metadata": {
    "location": "Main gate - Updated"
  }
}
```

**Response (200 OK):**
```json
{
  "id": "cam-001",
  "name": "Entrance Main (Updated)",
  "rtsp_url": "rtsp://admin:password@192.168.1.100:554/stream1",
  "enabled": false,
  "zone_id": "zone-entrance",
  "fps": 15,
  "resolution": {
    "width": 1920,
    "height": 1080
  },
  "detection_model": "yolov8-vehicle",
  "ocr_models": [
    "paddle-ocr-lt",
    "tesseract-lt"
  ],
  "metadata": {
    "location": "Main gate - Updated"
  },
  "created_at": "2023-12-10T10:00:00Z",
  "updated_at": "2023-12-15T15:00:00Z"
}
```

**cURL Example:**
```bash
curl -X PUT http://localhost:8000/config/cameras/cam-001 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "name": "Entrance Main (Updated)",
    "enabled": false,
    "fps": 15
  }'
```

---

#### Delete Camera

**Endpoint:** `DELETE /config/cameras/{id}`

**Authentication:** JWT Token
**Path Parameters:**
- `id` (string) - Camera ID

**Response (204 No Content)**

**Response (404 Not Found):**
```json
{
  "detail": "Camera not found"
}
```

**cURL Example:**
```bash
curl -X DELETE http://localhost:8000/config/cameras/cam-001 \
  -H "Authorization: Bearer your-jwt-token"
```

---

#### Test Camera Connection

**Endpoint:** `POST /config/cameras/{id}/test`

**Authentication:** JWT Token
**Path Parameters:**
- `id` (string) - Camera ID

**Query Parameters:**
- `timeout` (int, default: 10) - Connection timeout in seconds

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "RTSP stream connection successful",
  "response_time_ms": 1234,
  "stream_info": {
    "codec": "H.264",
    "width": 1920,
    "height": 1080,
    "fps": 25
  }
}
```

**Response (503 Service Unavailable):**
```json
{
  "status": "failed",
  "message": "Failed to connect to RTSP stream: Connection timeout",
  "error": "Connection timeout",
  "response_time_ms": 10000
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/config/cameras/cam-001/test \
  -H "Authorization: Bearer your-jwt-token"
```

---

### Zones

#### List Zones

**Endpoint:** `GET /config/zones`

**Authentication:** JWT Token
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `camera_id` (string, optional)

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "zone-001",
      "name": "Entrance Zone",
      "camera_id": "cam-001",
      "type": "enter",
      "geometry": {
        "type": "polygon",
        "points": [
          {"x": 100, "y": 200},
          {"x": 500, "y": 200},
          {"x": 500, "y": 600},
          {"x": 100, "y": 600}
        ]
      },
      "metadata": {
        "description": "Main entrance area"
      },
      "created_at": "2023-12-10T10:00:00Z",
      "updated_at": "2023-12-15T14:30:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/config/zones?camera_id=cam-001" \
  -H "Authorization: Bearer your-jwt-token"
```

---

#### Create Zone

**Endpoint:** `POST /config/zones`

**Authentication:** JWT Token
**Request Body:**
```json
{
  "name": "Entrance Zone",
  "camera_id": "cam-001",
  "type": "enter",
  "geometry": {
    "type": "polygon",
    "points": [
      {"x": 100, "y": 200},
      {"x": 500, "y": 200},
      {"x": 500, "y": 600},
      {"x": 100, "y": 600}
    ]
  },
  "metadata": {
    "description": "Main entrance area"
  }
}
```

**Response (201 Created):**
```json
{
  "id": "zone-001",
  "name": "Entrance Zone",
  "camera_id": "cam-001",
  "type": "enter",
  "geometry": {
    "type": "polygon",
    "points": [
      {"x": 100, "y": 200},
      {"x": 500, "y": 200},
      {"x": 500, "y": 600},
      {"x": 100, "y": 600}
    ]
  },
  "metadata": {
    "description": "Main entrance area"
  },
  "created_at": "2023-12-15T14:30:00Z",
  "updated_at": "2023-12-15T14:30:00Z"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/config/zones \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "name": "Entrance Zone",
    "camera_id": "cam-001",
    "type": "enter",
    "geometry": {
      "type": "polygon",
      "points": [
        {"x": 100, "y": 200},
        {"x": 500, "y": 200},
        {"x": 500, "y": 600},
        {"x": 100, "y": 600}
      ]
    },
    "metadata": {"description": "Main entrance area"}
  }'
```

---

#### Get Zone

**Endpoint:** `GET /config/zones/{id}`

**Authentication:** JWT Token

**Response (200 OK):**
```json
{
  "id": "zone-001",
  "name": "Entrance Zone",
  "camera_id": "cam-001",
  "type": "enter",
  "geometry": {
    "type": "polygon",
    "points": [
      {"x": 100, "y": 200},
      {"x": 500, "y": 200},
      {"x": 500, "y": 600},
      {"x": 100, "y": 600}
    ]
  },
  "metadata": {
    "description": "Main entrance area"
  },
  "created_at": "2023-12-10T10:00:00Z",
  "updated_at": "2023-12-15T14:30:00Z"
}
```

**cURL Example:**
```bash
curl -X GET http://localhost:8000/config/zones/zone-001 \
  -H "Authorization: Bearer your-jwt-token"
```

---

#### Update Zone

**Endpoint:** `PUT /config/zones/{id}`

**Authentication:** JWT Token
**Request Body:**
```json
{
  "name": "Entrance Zone (Updated)",
  "geometry": {
    "type": "polygon",
    "points": [
      {"x": 100, "y": 200},
      {"x": 600, "y": 200},
      {"x": 600, "y": 700},
      {"x": 100, "y": 700}
    ]
  }
}
```

**Response (200 OK):** Returns updated zone object

**cURL Example:**
```bash
curl -X PUT http://localhost:8000/config/zones/zone-001 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "name": "Entrance Zone (Updated)",
    "geometry": {
      "type": "polygon",
      "points": [
        {"x": 100, "y": 200},
        {"x": 600, "y": 200},
        {"x": 600, "y": 700},
        {"x": 100, "y": 700}
      ]
    }
  }'
```

---

#### Delete Zone

**Endpoint:** `DELETE /config/zones/{id}`

**Authentication:** JWT Token

**Response (204 No Content)**

**cURL Example:**
```bash
curl -X DELETE http://localhost:8000/config/zones/zone-001 \
  -H "Authorization: Bearer your-jwt-token"
```

---

### Models

#### List Models

**Endpoint:** `GET /config/models`

**Authentication:** JWT Token
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `type` (string, optional) - Filter by type: "detector", "ocr"

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "model-001",
      "name": "YOLOv8 Vehicle Detector",
      "type": "detector",
      "version": "8.0.0",
      "weights_path": "/models/yolov8-vehicle.pt",
      "parameters": {
        "confidence_threshold": 0.5,
        "iou_threshold": 0.45,
        "input_size": 640,
        "framework": "PyTorch"
      },
      "metadata": {
        "description": "Vehicle detection model",
        "supported_devices": ["cpu", "cuda", "coral"]
      },
      "created_at": "2023-12-10T10:00:00Z",
      "updated_at": "2023-12-15T14:30:00Z"
    },
    {
      "id": "model-002",
      "name": "PaddleOCR Lithuanian",
      "type": "ocr",
      "version": "2.7.0",
      "weights_path": "/models/paddle-ocr-lt.tar.gz",
      "parameters": {
        "language": "lt",
        "confidence_threshold": 0.5,
        "framework": "PaddlePaddle"
      },
      "metadata": {
        "description": "OCR model optimized for Lithuanian plates"
      },
      "created_at": "2023-12-10T10:00:00Z",
      "updated_at": "2023-12-15T14:30:00Z"
    }
  ],
  "total": 2,
  "skip": 0,
  "limit": 100
}
```

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/config/models?type=ocr" \
  -H "Authorization: Bearer your-jwt-token"
```

---

#### Create Model

**Endpoint:** `POST /config/models`

**Authentication:** JWT Token
**Request Body:**
```json
{
  "name": "YOLOv8 Vehicle Detector",
  "type": "detector",
  "version": "8.0.0",
  "weights_path": "/models/yolov8-vehicle.pt",
  "parameters": {
    "confidence_threshold": 0.5,
    "iou_threshold": 0.45,
    "input_size": 640,
    "framework": "PyTorch"
  },
  "metadata": {
    "description": "Vehicle detection model",
    "supported_devices": ["cpu", "cuda", "coral"]
  }
}
```

**Response (201 Created):** Returns created model object

**cURL Example:**
```bash
curl -X POST http://localhost:8000/config/models \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "name": "YOLOv8 Vehicle Detector",
    "type": "detector",
    "version": "8.0.0",
    "weights_path": "/models/yolov8-vehicle.pt",
    "parameters": {
      "confidence_threshold": 0.5,
      "iou_threshold": 0.45,
      "input_size": 640,
      "framework": "PyTorch"
    },
    "metadata": {"description": "Vehicle detection model"}
  }'
```

---

#### Get Model

**Endpoint:** `GET /config/models/{id}`

**Authentication:** JWT Token

**Response (200 OK):** Returns model object

**cURL Example:**
```bash
curl -X GET http://localhost:8000/config/models/model-001 \
  -H "Authorization: Bearer your-jwt-token"
```

---

#### Update Model

**Endpoint:** `PUT /config/models/{id}`

**Authentication:** JWT Token

**Request Body:** Same as Create Model

**Response (200 OK):** Returns updated model object

**cURL Example:**
```bash
curl -X PUT http://localhost:8000/config/models/model-001 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "parameters": {
      "confidence_threshold": 0.6
    }
  }'
```

---

#### Delete Model

**Endpoint:** `DELETE /config/models/{id}`

**Authentication:** JWT Token

**Response (204 No Content)**

**cURL Example:**
```bash
curl -X DELETE http://localhost:8000/config/models/model-001 \
  -H "Authorization: Bearer your-jwt-token"
```

---

### Sensors

#### List Sensors

**Endpoint:** `GET /config/sensors`

**Authentication:** JWT Token
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `type` (string, optional) - Filter by type: "tpms", "barrier", "rfid"
- `camera_id` (string, optional)

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "sensor-001",
      "name": "TPMS Sensor - Camera 1",
      "type": "tpms",
      "camera_id": "cam-001",
      "zone_id": null,
      "config": {
        "sensor_port": "COM3",
        "baudrate": 115200,
        "threshold": {
          "pressure_min": 1.8,
          "pressure_max": 2.5,
          "temperature_max": 60
        }
      },
      "metadata": {
        "description": "Tire pressure monitoring sensor"
      },
      "created_at": "2023-12-10T10:00:00Z",
      "updated_at": "2023-12-15T14:30:00Z"
    },
    {
      "id": "sensor-002",
      "name": "Barrier - Entrance",
      "type": "barrier",
      "camera_id": "cam-001",
      "zone_id": "zone-001",
      "config": {
        "relay_pin": 17,
        "pulse_duration_ms": 500,
        "require_plate": true
      },
      "metadata": {
        "description": "Automatic barrier control"
      },
      "created_at": "2023-12-10T10:00:00Z",
      "updated_at": "2023-12-15T14:30:00Z"
    }
  ],
  "total": 2,
  "skip": 0,
  "limit": 100
}
```

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/config/sensors?type=tpms" \
  -H "Authorization: Bearer your-jwt-token"
```

---

#### Create Sensor

**Endpoint:** `POST /config/sensors`

**Authentication:** JWT Token
**Request Body:**
```json
{
  "name": "TPMS Sensor - Camera 1",
  "type": "tpms",
  "camera_id": "cam-001",
  "zone_id": null,
  "config": {
    "sensor_port": "COM3",
    "baudrate": 115200,
    "threshold": {
      "pressure_min": 1.8,
      "pressure_max": 2.5,
      "temperature_max": 60
    }
  },
  "metadata": {
    "description": "Tire pressure monitoring sensor"
  }
}
```

**Response (201 Created):** Returns created sensor object

**cURL Example:**
```bash
curl -X POST http://localhost:8000/config/sensors \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "name": "TPMS Sensor - Camera 1",
    "type": "tpms",
    "camera_id": "cam-001",
    "config": {
      "sensor_port": "COM3",
      "baudrate": 115200,
      "threshold": {
        "pressure_min": 1.8,
        "pressure_max": 2.5,
        "temperature_max": 60
      }
    },
    "metadata": {"description": "Tire pressure monitoring sensor"}
  }'
```

---

#### Get Sensor

**Endpoint:** `GET /config/sensors/{id}`

**Authentication:** JWT Token

**Response (200 OK):** Returns sensor object

**cURL Example:**
```bash
curl -X GET http://localhost:8000/config/sensors/sensor-001 \
  -H "Authorization: Bearer your-jwt-token"
```

---

#### Update Sensor

**Endpoint:** `PUT /config/sensors/{id}`

**Authentication:** JWT Token

**Request Body:** Same as Create Sensor

**Response (200 OK):** Returns updated sensor object

**cURL Example:**
```bash
curl -X PUT http://localhost:8000/config/sensors/sensor-001 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "config": {
      "threshold": {
        "pressure_min": 1.9,
        "pressure_max": 2.4
      }
    }
  }'
```

---

#### Delete Sensor

**Endpoint:** `DELETE /config/sensors/{id}`

**Authentication:** JWT Token

**Response (204 No Content)**

**cURL Example:**
```bash
curl -X DELETE http://localhost:8000/config/sensors/sensor-001 \
  -H "Authorization: Bearer your-jwt-token"
```

---

## Exporters API

### List Exporters

**Endpoint:** `GET /config/exporters`

**Authentication:** JWT Token
**Query Parameters:**
- `skip` (int, default: 0)
- `limit` (int, default: 100)
- `enabled` (boolean, optional)

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "exporter-001",
      "name": "Backend REST Exporter",
      "type": "rest",
      "url": "http://localhost:8000/events/ingest",
      "enabled": true,
      "headers": {
        "Content-Type": "application/json",
        "Authorization": "Bearer token"
      },
      "auth": {
        "type": "bearer",
        "token": "your-api-key"
      },
      "retry_config": {
        "enabled": true,
        "max_attempts": 5,
        "backoff_strategy": "exponential",
        "initial_delay_ms": 1000,
        "max_delay_ms": 60000
      },
      "metadata": {
        "description": "Primary backend REST endpoint"
      },
      "created_at": "2023-12-10T10:00:00Z",
      "updated_at": "2023-12-15T14:30:00Z"
    },
    {
      "id": "exporter-002",
      "name": "MQTT Exporter",
      "type": "mqtt",
      "url": "mqtt://broker.example.com:1883",
      "enabled": true,
      "config": {
        "topic": "anpr/events",
        "qos": 1,
        "username": "mqtt_user",
        "password": "mqtt_password"
      },
      "retry_config": {
        "enabled": true,
        "max_attempts": 3,
        "backoff_strategy": "linear"
      },
      "metadata": {
        "description": "MQTT broker integration"
      },
      "created_at": "2023-12-10T10:00:00Z",
      "updated_at": "2023-12-15T14:30:00Z"
    }
  ],
  "total": 2,
  "skip": 0,
  "limit": 100
}
```

**cURL Example:**
```bash
curl -X GET "http://localhost:8000/config/exporters?enabled=true" \
  -H "Authorization: Bearer your-jwt-token"
```

---

### Create Exporter

**Endpoint:** `POST /config/exporters`

**Authentication:** JWT Token
**Request Body:**
```json
{
  "name": "Backend REST Exporter",
  "type": "rest",
  "url": "http://localhost:8000/events/ingest",
  "enabled": true,
  "headers": {
    "Content-Type": "application/json"
  },
  "auth": {
    "type": "bearer",
    "token": "your-api-key"
  },
  "retry_config": {
    "enabled": true,
    "max_attempts": 5,
    "backoff_strategy": "exponential",
    "initial_delay_ms": 1000,
    "max_delay_ms": 60000
  },
  "metadata": {
    "description": "Primary backend REST endpoint"
  }
}
```

**Response (201 Created):**
```json
{
  "id": "exporter-001",
  "name": "Backend REST Exporter",
  "type": "rest",
  "url": "http://localhost:8000/events/ingest",
  "enabled": true,
  "headers": {
    "Content-Type": "application/json"
  },
  "auth": {
    "type": "bearer",
    "token": "your-api-key"
  },
  "retry_config": {
    "enabled": true,
    "max_attempts": 5,
    "backoff_strategy": "exponential",
    "initial_delay_ms": 1000,
    "max_delay_ms": 60000
  },
  "metadata": {
    "description": "Primary backend REST endpoint"
  },
  "created_at": "2023-12-15T14:30:00Z",
  "updated_at": "2023-12-15T14:30:00Z"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/config/exporters \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "name": "Backend REST Exporter",
    "type": "rest",
    "url": "http://localhost:8000/events/ingest",
    "enabled": true,
    "auth": {
      "type": "bearer",
      "token": "your-api-key"
    },
    "retry_config": {
      "enabled": true,
      "max_attempts": 5,
      "backoff_strategy": "exponential",
      "initial_delay_ms": 1000,
      "max_delay_ms": 60000
    }
  }'
```

---

### Get Exporter

**Endpoint:** `GET /config/exporters/{id}`

**Authentication:** JWT Token

**Response (200 OK):** Returns exporter object

**cURL Example:**
```bash
curl -X GET http://localhost:8000/config/exporters/exporter-001 \
  -H "Authorization: Bearer your-jwt-token"
```

---

### Update Exporter

**Endpoint:** `PUT /config/exporters/{id}`

**Authentication:** JWT Token
**Request Body:** Same as Create Exporter

**Response (200 OK):** Returns updated exporter object

**cURL Example:**
```bash
curl -X PUT http://localhost:8000/config/exporters/exporter-001 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "enabled": false,
    "retry_config": {
      "max_attempts": 3
    }
  }'
```

---

### Delete Exporter

**Endpoint:** `DELETE /config/exporters/{id}`

**Authentication:** JWT Token

**Response (204 No Content)**

**cURL Example:**
```bash
curl -X DELETE http://localhost:8000/config/exporters/exporter-001 \
  -H "Authorization: Bearer your-jwt-token"
```

---

### Test Exporter Connection

**Endpoint:** `POST /config/exporters/{id}/test`

**Authentication:** JWT Token

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Connection test successful",
  "response_time_ms": 234,
  "http_status": 200
}
```

**Response (503 Service Unavailable):**
```json
{
  "status": "failed",
  "message": "Connection test failed",
  "error": "Connection refused",
  "response_time_ms": 5000
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/config/exporters/exporter-001/test \
  -H "Authorization: Bearer your-jwt-token"
```

---

## Health Check

### Health Status

**Endpoint:** `GET /healthz`

**Authentication:** None (Public)

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2023-12-15T14:30:45.123Z",
  "version": "1.0.0",
  "components": {
    "database": {
      "status": "healthy",
      "response_time_ms": 12
    },
    "cache": {
      "status": "healthy",
      "response_time_ms": 3
    },
    "s3_storage": {
      "status": "healthy",
      "response_time_ms": 145
    }
  },
  "uptime_seconds": 86400
}
```

**Response (503 Service Unavailable):**
```json
{
  "status": "unhealthy",
  "timestamp": "2023-12-15T14:30:45.123Z",
  "version": "1.0.0",
  "components": {
    "database": {
      "status": "unhealthy",
      "error": "Connection refused"
    },
    "cache": {
      "status": "healthy"
    },
    "s3_storage": {
      "status": "healthy"
    }
  },
  "uptime_seconds": 3600
}
```

**cURL Example:**
```bash
curl -X GET http://localhost:8000/healthz
```

---

### Detailed Health Status

**Endpoint:** `GET /healthz/detailed`

**Authentication:** JWT Token

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2023-12-15T14:30:45.123Z",
  "version": "1.0.0",
  "components": {
    "database": {
      "status": "healthy",
      "response_time_ms": 12,
      "details": {
        "connections_active": 5,
        "connections_max": 20,
        "last_check": "2023-12-15T14:30:43.123Z"
      }
    },
    "cache": {
      "status": "healthy",
      "response_time_ms": 3,
      "details": {
        "memory_used_mb": 256,
        "memory_max_mb": 512,
        "keys_count": 1523
      }
    },
    "s3_storage": {
      "status": "healthy",
      "response_time_ms": 145,
      "details": {
        "bucket": "anpr-events",
        "accessible": true
      }
    }
  },
  "uptime_seconds": 86400,
  "metrics": {
    "events_total": 15342,
    "events_per_minute": 2.1,
    "avg_processing_time_ms": 245
  }
}
```

**cURL Example:**
```bash
curl -X GET http://localhost:8000/healthz/detailed \
  -H "Authorization: Bearer your-jwt-token"
```

---

## WebSocket Endpoints

### Real-time Event Stream

**Endpoint:** `WS /events/stream`

**Authentication:** Query parameter token or header
**URL Examples:**
- `ws://localhost:8000/events/stream?token=your-jwt-token`
- `ws://localhost:8000/events/stream?api_key=your-api-key`

**Connection Method:**
```javascript
const ws = new WebSocket('ws://localhost:8000/events/stream?token=your-jwt-token');

ws.onopen = (event) => {
  console.log('Connected to event stream');
};

ws.onmessage = (event) => {
  const plateEvent = JSON.parse(event.data);
  console.log('New event received:', plateEvent);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = (event) => {
  console.log('Disconnected from event stream');
};
```

**Message Format (Incoming):**
```json
{
  "type": "event",
  "data": {
    "id": "evt-20231215-001-cam1",
    "event_id": "evt-20231215-001-cam1",
    "timestamp": "2023-12-15T14:30:45.123Z",
    "camera_id": "cam-001",
    "zone_id": "zone-entrance",
    "plate_text": "ABC123",
    "confidence": 0.95,
    "raw_candidates": [
      {
        "text": "ABC123",
        "confidence": 0.95,
        "model": "paddle-ocr"
      }
    ],
    "frame_url": "http://localhost:9000/anpr-events/evt-20231215-001-cam1/frame.jpg",
    "crop_url": "http://localhost:9000/anpr-events/evt-20231215-001-cam1/crop.jpg",
    "vehicle_info": {
      "color": "white",
      "type": "sedan",
      "confidence": 0.87
    },
    "metadata": {
      "edge_worker_id": "edge-001",
      "processing_time_ms": 245
    },
    "created_at": "2023-12-15T14:30:45.123Z"
  }
}
```

**Filter by Camera (Optional):**
```javascript
const ws = new WebSocket('ws://localhost:8000/events/stream?token=your-jwt-token&camera_id=cam-001');
```

**Filter by Zone (Optional):**
```javascript
const ws = new WebSocket('ws://localhost:8000/events/stream?token=your-jwt-token&zone_id=zone-entrance');
```

**cURL Example (to upgrade connection):**
```bash
curl -i -N -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
  -H "Sec-WebSocket-Version: 13" \
  "ws://localhost:8000/events/stream?token=your-jwt-token"
```

**JavaScript Example with Reconnection:**
```javascript
class EventStreamClient {
  constructor(baseUrl, token) {
    this.baseUrl = baseUrl.replace('http', 'ws');
    this.token = token;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
  }

  connect() {
    const url = `${this.baseUrl}/events/stream?token=${this.token}`;
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log('Connected to event stream');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'event') {
        this.onEvent(message.data);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('Disconnected from event stream');
      this.reconnect();
    };
  }

  reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
      console.log(`Reconnecting in ${delay}ms...`);
      setTimeout(() => {
        this.reconnectAttempts++;
        this.connect();
      }, delay);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  onEvent(event) {
    // Override this method to handle events
    console.log('Event received:', event);
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

// Usage
const client = new EventStreamClient('http://localhost:8000', 'your-jwt-token');
client.onEvent = (event) => {
  console.log('Plate detected:', event.plate_text, 'Confidence:', event.confidence);
};
client.connect();
```

---

## Error Handling

### Standard Error Response

All errors follow this format:

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2023-12-15T14:30:45.123Z",
  "request_id": "req-12345"
}
```

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | Successful GET request |
| 201 | Created | Successful POST request |
| 202 | Accepted | Event queued for processing |
| 204 | No Content | Successful DELETE request |
| 400 | Bad Request | Invalid request body |
| 401 | Unauthorized | Missing or invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Duplicate event ID |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Common Error Codes

```
INVALID_REQUEST - Request format or parameters are invalid
AUTHENTICATION_FAILED - Authentication token is invalid or expired
RESOURCE_NOT_FOUND - Requested resource does not exist
VALIDATION_ERROR - Request validation failed
DUPLICATE_RESOURCE - Resource with same ID already exists
INTERNAL_ERROR - Internal server error
SERVICE_UNAVAILABLE - Service is temporarily unavailable
RATE_LIMIT_EXCEEDED - Request rate limit exceeded
```

---

## Rate Limiting

### Limits by Endpoint Category

| Category | Limit | Window |
|----------|-------|--------|
| Events API | 1000 req/min | Per edge worker |
| Config API | 100 req/min | Per user |
| Exporters API | 100 req/min | Per user |
| Health Check | Unlimited | - |
| WebSocket | 1 connection/edge | Persistent |

### Rate Limit Headers

Responses include the following headers:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1702646445
```

### Rate Limit Response (429)

```json
{
  "detail": "Rate limit exceeded",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after_seconds": 60,
  "limit": 1000,
  "window_seconds": 60
}
```

---

## Best Practices

### Event Submission

1. Always use unique `event_id` values
2. Include `raw_candidates` from all OCR models for consensus
3. Attach images when possible for archival and debugging
4. Use appropriate timestamps in ISO 8601 format
5. Include metadata for traceability

### Error Handling

1. Implement exponential backoff for retries
2. Handle WebSocket disconnections gracefully
3. Log all API errors for debugging
4. Monitor health check endpoint regularly

### Performance

1. Use batch operations where available
2. Filter events by camera/zone to reduce payload
3. Implement caching for configuration endpoints
4. Use WebSocket for real-time updates instead of polling

### Security

1. Never expose API keys in client-side code
2. Rotate JWT tokens regularly
3. Use HTTPS/WSS in production
4. Validate all incoming data
5. Implement request signing for sensitive operations

---

## API Versioning

Current API version: **v1**

The API follows semantic versioning. Breaking changes will increment the major version.

---

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/anpr-engine/issues
- Documentation: http://localhost:8000/docs
- Email: support@your-domain.com

---

<div align="center">

**Last Updated:** 2023-12-15
**API Version:** 1.0.0

</div>
