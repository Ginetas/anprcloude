/**
 * Type definitions for ANPR System
 */

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface PlateEvent {
  id: number;
  camera_id: number;
  plate_text: string;
  confidence: number;
  detection_confidence?: number;
  ocr_confidence?: number;
  bbox?: BoundingBox;
  timestamp: string;
  processed_at: string;
  image_path?: string;
  metadata?: Record<string, any>;
}

export interface PlateEventWithCamera extends PlateEvent {
  camera_name: string;
  camera_location?: string;
}

export interface Camera {
  id: number;
  name: string;
  rtsp_url: string;
  location?: string;
  zone_id?: number;
  enabled: boolean;
  fps: number;
  resolution_width: number;
  resolution_height: number;
  created_at: string;
  updated_at?: string;
}

export interface CameraCreate {
  name: string;
  rtsp_url: string;
  location?: string;
  zone_id?: number;
  enabled?: boolean;
  fps?: number;
  resolution_width?: number;
  resolution_height?: number;
}

export interface Zone {
  id: number;
  name: string;
  description?: string;
  created_at: string;
  updated_at?: string;
}

export interface ZoneCreate {
  name: string;
  description?: string;
}

export interface Model {
  id: number;
  name: string;
  model_type: 'detection' | 'ocr';
  file_path: string;
  version?: string;
  enabled: boolean;
  confidence_threshold: number;
  description?: string;
  created_at: string;
  updated_at?: string;
}

export interface Exporter {
  id: number;
  name: string;
  exporter_type: 'webhook' | 'rest' | 'mqtt';
  endpoint_url?: string;
  enabled: boolean;
  config?: Record<string, any>;
  created_at: string;
  updated_at?: string;
}

export interface ApiError {
  detail: string;
}
