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

// Settings Types
export interface Setting {
  id: number;
  key: string;
  value: any;
  category: string;
  description?: string;
  default_value?: any;
  value_type: 'string' | 'int' | 'float' | 'bool' | 'array' | 'object';
  validation_rules: Record<string, any>;
  is_sensitive: boolean;
  requires_restart: boolean;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface SettingCreate {
  key: string;
  value: any;
  category: string;
  description?: string;
  default_value?: any;
  value_type?: 'string' | 'int' | 'float' | 'bool' | 'array' | 'object';
  validation_rules?: Record<string, any>;
  is_sensitive?: boolean;
  requires_restart?: boolean;
  metadata?: Record<string, any>;
}

export interface SettingUpdate {
  value?: any;
  description?: string;
  default_value?: any;
  value_type?: string;
  validation_rules?: Record<string, any>;
  is_sensitive?: boolean;
  requires_restart?: boolean;
  metadata?: Record<string, any>;
}

export interface SettingValueUpdate {
  value: any;
  changed_by?: string;
  reason?: string;
}

export interface SettingsBulkUpdate {
  settings: Array<{ key: string; value: any }>;
  changed_by?: string;
  reason?: string;
}

export interface SettingsCategory {
  category: string;
  settings: Setting[];
  count: number;
}

export interface SettingsValidation {
  valid: boolean;
  errors: string[];
  warnings: string[];
  message: string;
}

export interface SettingsRecommendation {
  setting_key: string;
  current_value: any;
  recommended_value: any;
  reason: string;
  impact: 'low' | 'medium' | 'high';
  category: string;
}

export interface SettingsHistory {
  id: number;
  setting_key: string;
  old_value: any;
  new_value: any;
  changed_by?: string;
  reason?: string;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface SystemHealth {
  status: 'healthy' | 'warning' | 'error';
  worker_id: string;
  uptime: number;
  hardware_type: string;
  active_cameras: number;
  active_models: number;
  system_info: Record<string, any>;
}
