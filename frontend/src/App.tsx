import React, { useState, useEffect, useCallback } from 'react';
import { Header } from './components/Header';
import { FilterBar } from './components/FilterBar';
import { KpiCards } from './components/KpiCards';
import { TimeseriesChart } from './components/TimeseriesChart';
import { ErrorChart } from './components/ErrorChart';
import { DailyAccuracyView } from './components/DailyAccuracyView';
import { ForecastEvolutionView } from './components/ForecastEvolutionView';
import { MethodologyPanel } from './components/MethodologyPanel';

import { apiService } from './services/api';
import type {
  HealthResponse,
  MetricsResponse,
  TimeseriesResponse,
  ForecastEvolutionResponse,
  FilterState,
} from './types';
import { AlertCircle, RefreshCw } from 'lucide-react';

export const App: React.FC = () => {
  // Global filter state
  const [filters, setFilters] = useState<FilterState>({
    startDate: '2026-01-01',
    endDate: '2026-01-31',
    cutoff: '12:00',
    selectedDate: '2026-01-15',
  });

  // API states
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthLoading, setHealthLoading] = useState<boolean>(true);
  const [healthError, setHealthError] = useState<string | null>(null);

  const [metricsData, setMetricsData] = useState<MetricsResponse | null>(null);
  const [metricsLoading, setMetricsLoading] = useState<boolean>(true);
  const [metricsError, setMetricsError] = useState<string | null>(null);

  const [timeseriesData, setTimeseriesData] = useState<TimeseriesResponse | null>(null);
  const [timeseriesLoading, setTimeseriesLoading] = useState<boolean>(true);
  const [timeseriesError, setTimeseriesError] = useState<string | null>(null);

  const [evolutionData, setEvolutionData] = useState<ForecastEvolutionResponse | null>(null);
  const [evolutionLoading, setEvolutionLoading] = useState<boolean>(true);
  const [evolutionError, setEvolutionError] = useState<string | null>(null);

  // 1. Check API Health
  const checkApiHealth = useCallback(async () => {
    setHealthLoading(true);
    setHealthError(null);
    try {
      const data = await apiService.checkHealth();
      setHealth(data);
    } catch (err: any) {
      setHealthError(err.message || 'Unable to connect to WindWise UK API');
    } finally {
      setHealthLoading(false);
    }
  }, []);

  // 2. Fetch Metrics (Summary + Daily)
  const fetchMetrics = useCallback(async () => {
    if (filters.startDate > filters.endDate) return;
    setMetricsLoading(true);
    setMetricsError(null);
    try {
      const data = await apiService.getMetrics(filters.cutoff, filters.startDate, filters.endDate);
      setMetricsData(data);
    } catch (err: any) {
      setMetricsError(err.message || 'Failed to fetch verification metrics');
    } finally {
      setMetricsLoading(false);
    }
  }, [filters.cutoff, filters.startDate, filters.endDate]);

  // 3. Fetch Timeseries for selected day
  const fetchTimeseries = useCallback(async () => {
    setTimeseriesLoading(true);
    setTimeseriesError(null);
    try {
      const data = await apiService.getTimeseries(filters.selectedDate, filters.cutoff);
      setTimeseriesData(data);
    } catch (err: any) {
      setTimeseriesError(err.message || `Failed to fetch hourly timeseries for ${filters.selectedDate}`);
    } finally {
      setTimeseriesLoading(false);
    }
  }, [filters.selectedDate, filters.cutoff]);

  // 4. Fetch Forecast Evolution for selected day
  const fetchEvolution = useCallback(async () => {
    setEvolutionLoading(true);
    setEvolutionError(null);
    try {
      const data = await apiService.getForecastEvolution(filters.selectedDate);
      setEvolutionData(data);
    } catch (err: any) {
      setEvolutionError(err.message || `Failed to fetch forecast evolution for ${filters.selectedDate}`);
    } finally {
      setEvolutionLoading(false);
    }
  }, [filters.selectedDate]);

  // Initial mount
  useEffect(() => {
    checkApiHealth();
  }, [checkApiHealth]);

  useEffect(() => {
    fetchMetrics();
  }, [fetchMetrics]);

  useEffect(() => {
    fetchTimeseries();
    fetchEvolution();
  }, [fetchTimeseries, fetchEvolution]);

  const handleFilterChange = (newFilters: Partial<FilterState>) => {
    setFilters((prev) => {
      const updated = { ...prev, ...newFilters };
      // Ensure selectedDate is kept within new range if applicable
      if (newFilters.startDate && updated.selectedDate < newFilters.startDate) {
        updated.selectedDate = newFilters.startDate;
      }
      if (newFilters.endDate && updated.selectedDate > newFilters.endDate) {
        updated.selectedDate = newFilters.endDate;
      }
      return updated;
    });
  };

  const handleSelectDay = (dateStr: string) => {
    setFilters((prev) => ({ ...prev, selectedDate: dateStr }));
    // Smooth scroll up to hourly chart
    const el = document.getElementById('hourly-chart-section');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const handleRefreshAll = () => {
    checkApiHealth();
    fetchMetrics();
    fetchTimeseries();
    fetchEvolution();
  };

  return (
    <div>
      <Header
        health={health}
        healthLoading={healthLoading}
        healthError={healthError}
        startDate={filters.startDate}
        endDate={filters.endDate}
      />

      <main className="app-container">
        {/* Connection Failure Alert */}
        {healthError && (
          <div className="error-banner">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <AlertCircle size={20} />
              <div>
                <strong>Backend Connection Error:</strong> {healthError}. Ensure the Python FastAPI server is running on{' '}
                <code>http://localhost:8000</code>.
              </div>
            </div>
            <button className="btn-secondary" onClick={checkApiHealth}>
              <RefreshCw size={14} /> Retry Connection
            </button>
          </div>
        )}

        {/* Metrics Error Alert */}
        {metricsError && (
          <div className="error-banner">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <AlertCircle size={20} />
              <div>
                <strong>Metrics Error:</strong> {metricsError}
              </div>
            </div>
            <button className="btn-secondary" onClick={fetchMetrics}>
              <RefreshCw size={14} /> Retry Metrics
            </button>
          </div>
        )}

        {/* Evolution Error Alert */}
        {evolutionError && (
          <div className="error-banner">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <AlertCircle size={20} />
              <div>
                <strong>Evolution Forecast Error:</strong> {evolutionError}
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <FilterBar
          filters={filters}
          onFilterChange={handleFilterChange}
          onRefresh={handleRefreshAll}
          isLoading={metricsLoading || timeseriesLoading}
        />

        {/* Global KPI Cards */}
        <KpiCards summary={metricsData?.summary || null} isLoading={metricsLoading} />

        {/* Hourly Actual vs Forecast Timeseries Section */}
        <div id="hourly-chart-section">
          {timeseriesError ? (
            <div className="error-banner">
              <AlertCircle size={18} />
              <span>{timeseriesError}</span>
            </div>
          ) : (
            <TimeseriesChart
              date={filters.selectedDate}
              cutoff={filters.cutoff}
              intervals={timeseriesData?.intervals || []}
              daySummary={timeseriesData?.daySummary || null}
              onDateChange={(d) => handleFilterChange({ selectedDate: d })}
              isLoading={timeseriesLoading}
            />
          )}
        </div>

        {/* Forecast Error Delta Chart */}
        <ErrorChart
          date={filters.selectedDate}
          intervals={timeseriesData?.intervals || []}
          isLoading={timeseriesLoading}
        />

        {/* Daily Breakdown across the evaluation period */}
        <DailyAccuracyView
          dailyMetrics={metricsData?.dailyMetrics || []}
          selectedDate={filters.selectedDate}
          onSelectDate={handleSelectDay}
          isLoading={metricsLoading}
        />

        {/* Gate Closure Evolution View */}
        <ForecastEvolutionView
          evolution={evolutionData}
          date={filters.selectedDate}
          isLoading={evolutionLoading}
        />

        {/* Methodology & Specifications */}
        <MethodologyPanel />
      </main>
    </div>
  );
};

export default App;
