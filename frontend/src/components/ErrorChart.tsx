import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  Cell,
} from 'recharts';
import type { HourlyInterval } from '../types';

interface ErrorChartProps {
  date: string;
  intervals: HourlyInterval[];
  isLoading: boolean;
}

export const ErrorChart: React.FC<ErrorChartProps> = ({ date, intervals, isLoading }) => {
  const chartData = intervals.map((interval) => ({
    hour: `${String(interval.hour).padStart(2, '0')}:00`,
    errorMW: interval.errorMW,
    absErrorMW: interval.absoluteErrorMW,
    actualMW: interval.actualMW,
    forecastMW: interval.forecastMW,
  }));

  const CustomErrorTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const isOver = (data.errorMW || 0) > 0;
      return (
        <div className="custom-tooltip">
          <div className="tooltip-title">{`${date} @ ${label} UTC`}</div>
          <div className="tooltip-row">
            <span className="tooltip-label">Error (Forecast - Actual):</span>
            <span
              className="tooltip-value"
              style={{ color: isOver ? '#d97706' : '#6366f1' }}
            >
              {data.errorMW !== null ? `${data.errorMW > 0 ? '+' : ''}${data.errorMW.toLocaleString()} MW` : 'N/A'}
            </span>
          </div>
          <div className="tooltip-row">
            <span className="tooltip-label">Classification:</span>
            <span className="tooltip-value">
              {data.errorMW === 0
                ? 'Zero Error'
                : isOver
                ? 'Overforecasting (+)'
                : 'Underforecasting (-)'}
            </span>
          </div>
          <div className="tooltip-row">
            <span className="tooltip-label">Actual vs Forecast:</span>
            <span className="tooltip-value">
              {data.actualMW?.toLocaleString()} MW vs {data.forecastMW?.toLocaleString()} MW
            </span>
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
          <h2>Forecast Error Distribution (Hourly Delta)</h2>
          <p className="panel-description">
            Hourly forecast error defined as <code>Forecast MW − Actual MW</code>. Positive bars indicate overforecasting; negative bars indicate underforecasting.
          </p>
        </div>
      </div>

      {isLoading ? (
        <div className="chart-container loading-skeleton" />
      ) : (
        <div className="chart-container">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
              <XAxis dataKey="hour" stroke="#64748b" fontSize={11} tickLine={false} />
              <YAxis
                stroke="#64748b"
                fontSize={11}
                tickLine={false}
                unit=" MW"
                tickFormatter={(val) => `${val > 0 ? '+' : ''}${val}`}
              />
              <Tooltip content={<CustomErrorTooltip />} />
              <ReferenceLine y={0} stroke="#475569" strokeWidth={1.5} strokeDasharray="3 3" />
              <Bar dataKey="errorMW" radius={[4, 4, 0, 0]}>
                {chartData.map((entry, index) => {
                  const val = entry.errorMW || 0;
                  // Amber for overforecast, Indigo for underforecast
                  const fillColor = val >= 0 ? '#d97706' : '#6366f1';
                  return <Cell key={`cell-${index}`} fill={fillColor} />;
                })}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};
