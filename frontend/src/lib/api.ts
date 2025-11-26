/**
 * API Client for ANPR Backend
 */

import type {
  Camera,
  CameraCreate,
  Zone,
  ZoneCreate,
  Model,
  Exporter,
  PlateEvent,
  ApiError,
  Setting,
  SettingCreate,
  SettingUpdate,
  SettingValueUpdate,
  SettingsBulkUpdate,
  SettingsCategory,
  SettingsValidation,
  SettingsRecommendation,
  SettingsHistory,
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        detail: `HTTP error ${response.status}`,
      }));
      throw new Error(error.detail);
    }

    return response.json();
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    return this.request('/healthz');
  }

  // Cameras
  async getCameras(): Promise<Camera[]> {
    return this.request('/api/cameras');
  }

  async getCamera(id: number): Promise<Camera> {
    return this.request(`/api/cameras/${id}`);
  }

  async createCamera(camera: CameraCreate): Promise<Camera> {
    return this.request('/api/cameras', {
      method: 'POST',
      body: JSON.stringify(camera),
    });
  }

  async updateCamera(
    id: number,
    camera: Partial<CameraCreate>
  ): Promise<Camera> {
    return this.request(`/api/cameras/${id}`, {
      method: 'PUT',
      body: JSON.stringify(camera),
    });
  }

  async deleteCamera(id: number): Promise<{ message: string }> {
    return this.request(`/api/cameras/${id}`, {
      method: 'DELETE',
    });
  }

  // Zones
  async getZones(): Promise<Zone[]> {
    return this.request('/api/zones');
  }

  async getZone(id: number): Promise<Zone> {
    return this.request(`/api/zones/${id}`);
  }

  async createZone(zone: ZoneCreate): Promise<Zone> {
    return this.request('/api/zones', {
      method: 'POST',
      body: JSON.stringify(zone),
    });
  }

  async updateZone(id: number, zone: Partial<ZoneCreate>): Promise<Zone> {
    return this.request(`/api/zones/${id}`, {
      method: 'PUT',
      body: JSON.stringify(zone),
    });
  }

  async deleteZone(id: number): Promise<{ message: string }> {
    return this.request(`/api/zones/${id}`, {
      method: 'DELETE',
    });
  }

  // Models
  async getModels(): Promise<Model[]> {
    return this.request('/api/models');
  }

  async getModel(id: number): Promise<Model> {
    return this.request(`/api/models/${id}`);
  }

  // Exporters
  async getExporters(): Promise<Exporter[]> {
    return this.request('/api/exporters');
  }

  async getExporter(id: number): Promise<Exporter> {
    return this.request(`/api/exporters/${id}`);
  }

  // Plate Events
  async getPlateEvents(params?: {
    skip?: number;
    limit?: number;
    camera_id?: number;
    plate_text?: string;
  }): Promise<PlateEvent[]> {
    const queryParams = new URLSearchParams();
    if (params?.skip !== undefined) queryParams.set('skip', String(params.skip));
    if (params?.limit !== undefined)
      queryParams.set('limit', String(params.limit));
    if (params?.camera_id)
      queryParams.set('camera_id', String(params.camera_id));
    if (params?.plate_text) queryParams.set('plate_text', params.plate_text);

    const query = queryParams.toString();
    return this.request(`/api/plate-events${query ? `?${query}` : ''}`);
  }

  async getPlateEvent(id: number): Promise<PlateEvent> {
    return this.request(`/api/plate-events/${id}`);
  }

  // Settings
  async getSettings(params?: {
    category?: string;
    search?: string;
    skip?: number;
    limit?: number;
  }): Promise<Setting[]> {
    const queryParams = new URLSearchParams();
    if (params?.category) queryParams.set('category', params.category);
    if (params?.search) queryParams.set('search', params.search);
    if (params?.skip !== undefined) queryParams.set('skip', String(params.skip));
    if (params?.limit !== undefined) queryParams.set('limit', String(params.limit));

    const query = queryParams.toString();
    return this.request(`/api/settings${query ? `?${query}` : ''}`);
  }

  async getSettingsByCategory(): Promise<SettingsCategory[]> {
    return this.request('/api/settings/categories');
  }

  async getSetting(id: number): Promise<Setting> {
    return this.request(`/api/settings/${id}`);
  }

  async getSettingByKey(key: string): Promise<Setting> {
    return this.request(`/api/settings/key/${encodeURIComponent(key)}`);
  }

  async createSetting(setting: SettingCreate): Promise<Setting> {
    return this.request('/api/settings', {
      method: 'POST',
      body: JSON.stringify(setting),
    });
  }

  async updateSetting(id: number, setting: SettingUpdate): Promise<Setting> {
    return this.request(`/api/settings/${id}`, {
      method: 'PUT',
      body: JSON.stringify(setting),
    });
  }

  async updateSettingValue(
    id: number,
    update: SettingValueUpdate
  ): Promise<Setting> {
    return this.request(`/api/settings/${id}/value`, {
      method: 'PATCH',
      body: JSON.stringify(update),
    });
  }

  async bulkUpdateSettings(
    bulkUpdate: SettingsBulkUpdate
  ): Promise<{ success: boolean; updated_count: number; errors: string[] }> {
    return this.request('/api/settings/bulk-update', {
      method: 'POST',
      body: JSON.stringify(bulkUpdate),
    });
  }

  async deleteSetting(id: number): Promise<void> {
    return this.request(`/api/settings/${id}`, {
      method: 'DELETE',
    });
  }

  async exportSettings(params?: {
    format?: 'json' | 'yaml' | 'env';
    category?: string;
    exclude_sensitive?: boolean;
  }): Promise<{ format: string; data: any; exported_at: string }> {
    const queryParams = new URLSearchParams();
    if (params?.format) queryParams.set('format', params.format);
    if (params?.category) queryParams.set('category', params.category);
    if (params?.exclude_sensitive !== undefined)
      queryParams.set('exclude_sensitive', String(params.exclude_sensitive));

    const query = queryParams.toString();
    return this.request(`/api/settings/export${query ? `?${query}` : ''}`, {
      method: 'POST',
    });
  }

  async importSettings(data: {
    format: string;
    data: any;
    overwrite_existing?: boolean;
    changed_by?: string;
  }): Promise<{
    success: boolean;
    imported_count: number;
    skipped_count: number;
    errors: string[];
    message: string;
  }> {
    return this.request('/api/settings/import', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async validateSetting(
    key: string,
    value: any
  ): Promise<SettingsValidation> {
    return this.request('/api/settings/validate', {
      method: 'POST',
      body: JSON.stringify({ key, value }),
    });
  }

  async getSettingsRecommendations(): Promise<{
    recommendations: SettingsRecommendation[];
    total_count: number;
    categories: Record<string, number>;
  }> {
    return this.request('/api/settings/recommendations/get');
  }

  async getSettingsHistory(params?: {
    setting_key?: string;
    skip?: number;
    limit?: number;
  }): Promise<SettingsHistory[]> {
    const queryParams = new URLSearchParams();
    if (params?.setting_key)
      queryParams.set('setting_key', params.setting_key);
    if (params?.skip !== undefined) queryParams.set('skip', String(params.skip));
    if (params?.limit !== undefined)
      queryParams.set('limit', String(params.limit));

    const query = queryParams.toString();
    return this.request(`/api/settings/history${query ? `?${query}` : ''}`);
  }

  async rollbackSetting(
    historyId: number,
    changedBy?: string
  ): Promise<Setting> {
    return this.request('/api/settings/rollback', {
      method: 'POST',
      body: JSON.stringify({
        history_id: historyId,
        changed_by: changedBy,
      }),
    });
  }
}

export const api = new ApiClient();
export default api;
