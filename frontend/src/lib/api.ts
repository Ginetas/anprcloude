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
}

export const api = new ApiClient();
export default api;
