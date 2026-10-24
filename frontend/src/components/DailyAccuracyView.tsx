import React, { useState } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';
import type { DailyMetrics } from '../types';

interface DailyAccuracyViewProps {
  dailyMetrics: DailyMetrics[];
  selectedDate: string;
  onSelectDate: (date: string) => void;
  isLoading: boolean;
}

export const DailyAccuracyView: React.FC<DailyAccuracyViewProps> = ({
  dailyMetrics,
  selectedDate,
  onSelectDate,
  isLoading,
}) => {
  const [metricMode, setMetricMode] = useState<'mae' | 'wape'>('mae');

  const chartData = dailyMetrics.map((dm) => ({
    date: dm.date.substring(5), // "MM-DD" e.g. "01-15"
    fullDate: dm.date,
    maeMW: dm.maeMW,
    rmseMW: dm.rmseMW,
    wapePct: dm.wapePct,
    biasMW: dm.biasMW,
    matchedHours: dm.matchedHours,
  }));

  const CustomDailyTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="custom-tooltip">
          <div className="tooltip-title">{`Day: ${data.fullDate}`}</div>
          <div className="tooltip-row">
            <span className="tooltip-label">MAE:</span>
            <span className="tooltip-value">{data.maeMW?.toLocaleString()} MW</span>
          </div>
          <div className="tooltip-row">
            <span className="tooltip-label">RMSE:</span>
            <span className="tooltip-value">{data.rmseMW?.toLocaleString()} MW</span>
          </div>
          <div className="tooltip-row">
            <span className="tooltip-label">Forecast Bias:</span>
            <span className="tooltip-value">
              {data.biasMW > 0 ? `+${data.biasMW}` : data.biasMW} MW
            </span>
          </div>
          <div className="tooltip-row">
            <span className="tooltip-label">WAPE:</span>
            <span className="tooltip-value">{data.wapePct !== null ? `${data.wapePct}%` : 'N/A'}</span>
          </div>
          <div style={{ marginTop: '0.4rem', fontSize: '0.72rem', color: '#38bdf8' }}>
            Click row below to inspect hourly time-series
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
          <h2>Daily Accuracy Breakdown across Evaluation Window</h2>
          <p className="panel-description">
            Compare day-by-day accuracy metrics. Click any date or table row to inspect that day's 24-hour hourly profile.
          </p>
        </div>

        <div className="panel-controls">
          <div style={{ display: 'flex', gap: '0.35rem' }}>
            <button
              className={`btn-secondary ${metricMode === 'mae' ? 'active' : ''}`}
              style={metricMode === 'mae' ? { backgroundColor: 'var(--accent-wind-light)', borderColor: 'var(--accent-wind-blue)', color: 'var(--accent-wind-blue)', fontWeight: 600 } : {}}
              onClick={() => setMetricMode('mae')}
            >
              Show Daily MAE (MW)
            </button>
            <button
              className={`btn-secondary ${metricMode === 'wape' ? 'active' : ''}`}
              style={metricMode === 'wape' ? { backgroundColor: 'var(--accent-green-light)', borderColor: 'var(--accent-green)', color: 'var(--accent-green)', fontWeight: 600 } : {}}
              onClick={() => setMetricMode('wape')}
            >
              Show Daily WAPE (%)
            </button>
          </div>
        </div>
      </div>

      {/* Chart */}
      {isLoading ? (
        <div className="chart-container loading-skeleton" />
      ) : (
        <div className="chart-container" style={{ height: '260px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              margin={{ top: 10, right: 10, left: 10, bottom: 0 }}
              onClick={(e: any) => {
                if (e && e.activePayload && e.activePayload.length) {
                  onSelectDate(e.activePayload[0].payload.fullDate);
                }
              }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
              <XAxis dataKey="date" stroke="#64748b" fontSize={11} tickLine={false} />
              <YAxis
                stroke="#64748b"
                fontSize={11}
                tickLine={false}
                unit={metricMode === 'mae' ? ' MW' : '%'}
              />
              <Tooltip content={<CustomDailyTooltip />} />
              <Bar
                dataKey={metricMode === 'mae' ? 'maeMW' : 'wapePct'}
                fill={metricMode === 'mae' ? '#0284c7' : '#059669'}
                radius={[3, 3, 0, 0]}
                name={metricMode === 'mae' ? 'Daily MAE (MW)' : 'Daily WAPE (%)'}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Daily Table */}
      <div style={{ marginTop: '1.5rem' }}>
        <h3 style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '0.75rem', color: 'var(--text-secondary)' }}>
          Detailed Daily Accuracy Log (Select a row to inspect)
        </h3>
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Coverage</th>
                <th>Mean Actual</th>
                <th>Mean Forecast</th>
                <th>MAE (MW)</th>
                <th>RMSE (MW)</th>
                <th>Forecast Bias</th>
                <th>WAPE (%)</th>
              </tr>
            </thead>
            <tbody>
              {dailyMetrics.map((dm) => {
                const isSelected = dm.date === selectedDate;
                const isOver = (dm.biasMW || 0) > 0;
                return (
                  <tr
                    key={dm.date}
                    className={isSelected ? 'selected' : ''}
                    onClick={() => onSelectDate(dm.date)}
                    title="Click to view 24-hour hourly profile"
                  >
                    <td style={{ fontWeight: 600 }}>
                      {dm.date} {isSelected && <span style={{ color: 'var(--accent-wind-blue)' }}>●</span>}
                    </td>
                    <td className="tabular-nums">{dm.matchedHours} / 24 hrs</td>
                    <td className="tabular-nums">
                      {dm.meanActualMW !== null ? `${dm.meanActualMW.toLocaleString()} MW` : '—'}
                    </td>
                    <td className="tabular-nums">
                      {dm.meanForecastMW !== null ? `${dm.meanForecastMW.toLocaleString()} MW` : '—'}
                    </td>
                    <td className="tabular-nums" style={{ fontWeight: 600 }}>
                      {dm.maeMW !== null ? `${dm.maeMW.toLocaleString()} MW` : '—'}
                    </td>
                    <td className="tabular-nums">
                      {dm.rmseMW !== null ? `${dm.rmseMW.toLocaleString()} MW` : '—'}
                    </td>
                    <td className="tabular-nums" style={{ color: isOver ? 'var(--accent-amber)' : 'var(--accent-indigo)' }}>
                      {dm.biasMW !== null ? `${dm.biasMW > 0 ? '+' : ''}${dm.biasMW.toLocaleString()} MW` : '—'}{' '}
                      {dm.biasPct !== null && `(${dm.biasPct > 0 ? '+' : ''}${dm.biasPct}%)`}
                    </td>
                    <td className="tabular-nums" style={{ fontWeight: 600 }}>
                      {dm.wapePct !== null ? `${dm.wapePct}%` : 'N/A'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
