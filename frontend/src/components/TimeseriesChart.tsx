import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { Calendar, ChevronLeft, ChevronRight } from 'lucide-react';
import type { HourlyInterval, MetricsSummary } from '../types';

interface TimeseriesChartProps {
  date: string;
  cutoff: string;
  intervals: HourlyInterval[];
  daySummary: MetricsSummary | null;
  onDateChange: (newDate: string) => void;
  isLoading: boolean;
}

export const TimeseriesChart: React.FC<TimeseriesChartProps> = ({
  date,
  cutoff,
  intervals,
  daySummary,
  onDateChange,
  isLoading,
}) => {
  // Navigation for previous/next day
  const handlePrevDay = () => {
    const d = new Date(date);
    d.setDate(d.getDate() - 1);
    const prevStr = d.toISOString().split('T')[0];
    if (prevStr >= '2026-01-01') {
      onDateChange(prevStr);
    }
  };

  const handleNextDay = () => {
    const d = new Date(date);
    d.setDate(d.getDate() + 1);
    const nextStr = d.toISOString().split('T')[0];
    if (nextStr <= '2026-01-31') {
      onDateChange(nextStr);
    }
  };

  // Format data for Recharts
  const chartData = intervals.map((interval) => ({
    hour: `${String(interval.hour).padStart(2, '0')}:00`,
    actualMW: interval.actualMW,
    forecastMW: interval.forecastMW,
    publishTime: interval.forecastPublishTime
      ? interval.forecastPublishTime.replace('T', ' ').replace('Z', ' UTC')
      : 'N/A',
    actualPeriods: interval.actualPeriodsCount,
    errorMW: interval.errorMW,
  }));

  const CustomTooltipContent = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const dataPoint = payload[0].payload;
      return (
        <div className="custom-tooltip">
          <div className="tooltip-title">{`${date} @ ${label} UTC`}</div>
          <div className="tooltip-row">
            <span className="tooltip-label" style={{ color: '#059669' }}>
              ● Actual Generation:
            </span>
            <span className="tooltip-value">
              {dataPoint.actualMW !== null ? `${dataPoint.actualMW.toLocaleString()} MW` : 'Missing data'}
            </span>
          </div>
          <div className="tooltip-row">
            <span className="tooltip-label" style={{ color: '#0284c7' }}>
              ● Day-Ahead Forecast:
            </span>
            <span className="tooltip-value">
              {dataPoint.forecastMW !== null ? `${dataPoint.forecastMW.toLocaleString()} MW` : 'No forecast'}
            </span>
          </div>
          {dataPoint.errorMW !== null && (
            <div className="tooltip-row">
              <span className="tooltip-label" style={{ color: dataPoint.errorMW > 0 ? '#d97706' : '#6366f1' }}>
                Delta (Forecast - Actual):
              </span>
              <span className="tooltip-value">
                {dataPoint.errorMW > 0 ? `+${dataPoint.errorMW}` : dataPoint.errorMW} MW
              </span>
            </div>
          )}
          <div
            style={{
              marginTop: '0.45rem',
              paddingTop: '0.35rem',
              borderTop: '1px solid rgba(255,255,255,0.15)',
              fontSize: '0.72rem',
              color: '#94a3b8',
            }}
          >
            Selected Forecast Published: {dataPoint.publishTime}
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="section-panel">
      <div className="panel-header">
        <div className="panel-title-group">
          <h2>
            Day-Ahead Forecast vs Actual Generation
            <span className="badge-tag" style={{ background: '#0284c7', color: '#fff' }}>
              {cutoff} UTC Cutoff
            </span>
          </h2>
          <p className="panel-description">
            Hourly profile comparing National Grid ESO Day-Ahead wind forecast against actual metered outturn.
          </p>
        </div>

        {/* Day Navigator */}
        <div className="panel-controls">
          <button
            className="btn-secondary"
            onClick={handlePrevDay}
            disabled={date <= '2026-01-01'}
            title="Previous Day"
          >
            <ChevronLeft size={16} />
          </button>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Calendar size={15} style={{ color: 'var(--text-muted)' }} />
            <input
              type="date"
              className="filter-input"
              value={date}
              min="2026-01-01"
              max="2026-01-31"
              onChange={(e) => onDateChange(e.target.value)}
              style={{ padding: '0.35rem 0.65rem' }}
            />
          </div>

          <button
            className="btn-secondary"
            onClick={handleNextDay}
            disabled={date >= '2026-01-31'}
            title="Next Day"
          >
            <ChevronRight size={16} />
          </button>
        </div>
      </div>

      {/* Day Summary Pill */}
      {daySummary && (
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '1rem',
            padding: '0.65rem 1rem',
            backgroundColor: 'var(--bg-subtle)',
            borderRadius: 'var(--radius-sm)',
            marginBottom: '1rem',
            fontSize: '0.82rem',
          }}
        >
          <span>
            Daily MAE: <strong>{daySummary.maeMW?.toLocaleString()} MW</strong>
          </span>
          <span>
            RMSE: <strong>{daySummary.rmseMW?.toLocaleString()} MW</strong>
          </span>
          <span>
            Bias: <strong>{daySummary.biasMW && daySummary.biasMW > 0 ? `+${daySummary.biasMW}` : daySummary.biasMW} MW</strong> ({daySummary.biasPct}%)
          </span>
          <span>
            WAPE: <strong>{daySummary.wapePct}%</strong>
          </span>
          <span>
            Day Energy: <strong>{daySummary.totalActualGWh} GWh</strong> actual / <strong>{daySummary.totalForecastGWh} GWh</strong> forecast
          </span>
        </div>
      )}

      {/* Chart */}
      {isLoading ? (
        <div className="chart-container loading-skeleton" />
      ) : (
        <div className="chart-container">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
              <defs>
                <linearGradient id="actualGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#059669" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#059669" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="forecastGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0284c7" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#0284c7" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
              <XAxis dataKey="hour" stroke="#64748b" fontSize={11} tickLine={false} />
              <YAxis
                stroke="#64748b"
                fontSize={11}
                tickLine={false}
                tickFormatter={(val) => `${(val / 1000).toFixed(0)}k`}
                unit=" MW"
                domain={['auto', 'auto']}
              />
              <Tooltip content={<CustomTooltipContent />} />
              <Legend
                verticalAlign="top"
                height={36}
                formatter={(val) => (
                  <span style={{ color: 'var(--text-main)', fontSize: '0.82rem', fontWeight: 600 }}>
                    {val === 'actualMW' ? 'Actual Generation (MW)' : 'Day-Ahead Forecast (MW)'}
                  </span>
                )}
              />
              <Area
                type="monotone"
                dataKey="actualMW"
                stroke="#059669"
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#actualGradient)"
                connectNulls={false}
                name="actualMW"
              />
              <Area
                type="monotone"
                dataKey="forecastMW"
                stroke="#0284c7"
                strokeWidth={2.5}
                strokeDasharray="4 2"
                fillOpacity={1}
                fill="url(#forecastGradient)"
                connectNulls={false}
                name="forecastMW"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};
