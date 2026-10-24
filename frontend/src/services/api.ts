import type {
  HealthResponse,
  MetricsSummary,
  MetricsResponse,
  TimeseriesResponse,
  ForecastEvolutionResponse,
  CutoffTime,
} from '../types';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '');

class ApiError extends Error {
  statusCode?: number;
  constructor(message: string, statusCode?: number) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = `API error (${response.status}): ${response.statusText}`;
    try {
      const errorJson = await response.json();
      if (errorJson && errorJson.detail) {
        errorMessage = typeof errorJson.detail === 'string' 
          ? errorJson.detail 
          : JSON.stringify(errorJson.detail);
      }
    } catch {
      // Body is not JSON, use status text
    }
    throw new ApiError(errorMessage, response.status);
  }
  return response.json();
}

export const apiService = {
  /**
   * Check backend health and cache status
   */
  async checkHealth(): Promise<HealthResponse> {
    const url = `${API_BASE_URL}/api/health`;
    const response = await fetch(url);
    return handleResponse<HealthResponse>(response);
  },

  /**
   * Fetch verification summary metrics
   */
  async getSummary(
    cutoff: CutoffTime,
    startDate: string,
    endDate: string
  ): Promise<MetricsSummary> {
    const params = new URLSearchParams({
      cutoff,
      startDate,
      endDate,
    });
    const url = `${API_BASE_URL}/api/summary?${params.toString()}`;
    const response = await fetch(url);
    return handleResponse<MetricsSummary>(response);
  },

  /**
   * Fetch summary and daily metrics breakdown
   */
  async getMetrics(
    cutoff: CutoffTime,
    startDate: string,
    endDate: string
  ): Promise<MetricsResponse> {
    const params = new URLSearchParams({
      cutoff,
      startDate,
      endDate,
    });
    const url = `${API_BASE_URL}/api/metrics?${params.toString()}`;
    const response = await fetch(url);
    return handleResponse<MetricsResponse>(response);
  },

  /**
   * Fetch 24-hour time series for a single delivery day
   */
  async getTimeseries(
    date: string,
    cutoff: CutoffTime
  ): Promise<TimeseriesResponse> {
    const params = new URLSearchParams({
      date,
      cutoff,
    });
    const url = `${API_BASE_URL}/api/timeseries?${params.toString()}`;
    const response = await fetch(url);
    return handleResponse<TimeseriesResponse>(response);
  },

  /**
   * Fetch forecast evolution across cutoffs for a single delivery day
   */
  async getForecastEvolution(
    date: string
  ): Promise<ForecastEvolutionResponse> {
    const params = new URLSearchParams({
      date,
    });
    const url = `${API_BASE_URL}/api/forecast-evolution?${params.toString()}`;
    const response = await fetch(url);
    return handleResponse<ForecastEvolutionResponse>(response);
  },
};
