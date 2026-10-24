import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import { Clock, ShieldCheck } from 'lucide-react';
import type { ForecastEvolutionResponse } from '../types';

interface ForecastEvolutionViewProps {
  evolution: ForecastEvolutionResponse | null;
  date: string;
  isLoading: boolean;
}

const CUTOFF_COLORS: Record<string, string> = {
  'fc_0900': '#94a3b8', // Gray/Slate (Earliest)
  'fc_1100': '#f59e0b', // Amber (11:00 EPEX Gate)
  'fc_1200': '#0284c7', // Sky Blue (12:00 Default)
  'fc_1400': '#6366f1', // Indigo (14:00)
  'fc_1700': '#059669', // Emerald (17:00 Latest)
};

export const ForecastEvolutionView: React.FC<ForecastEvolutionViewProps> = ({
  evolution,
  date,
  isLoading,
}) => {
  if (isLoading || !evolution) {
    return (
      <div className="section-panel">
        <div className="panel-header">
          <div className="panel-title-group">
            <h2>Forecast Evolution Across Day-Ahead Gate Closures ({date})</h2>
          </div>
        </div>
        <div className="chart-container loading-skeleton" />
      </div>
    );
  }

  const chartData = evolution.intervals.map((item) => ({
    hour: `${String(item.hour).padStart(2, '0')}:00`,
    actualMW: item.actualMW,
    '09:00 UTC Cutoff': item.fc_0900,
    '11:00 UTC Cutoff': item.fc_1100,
    '12:00 UTC Cutoff': item.fc_1200,
    '14:00 UTC Cutoff': item.fc_1400,
    '17:00 UTC Cutoff': item.fc_1700,
  }));

  return (
    <div className="section-panel">
      <div className="panel-header">
        <div className="panel-title-group">
          <h2>
            Forecast Evolution Across Day-Ahead Gate Closures ({date})
          </h2>
          <p className="panel-description">
            Visualizing how National Grid ESO's day-ahead forecast for {date} updated across cutoff gate closures on day $D-1$.
          </p>
        </div>
      </div>

      {/* Summary Evolution Metric Cards */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: '0.85rem',
          marginBottom: '1.25rem',
        }}
      >
        {evolution.cutoffs.map((c) => (
          <div
            key={c.cutoff}
            style={{
              padding: '0.85rem 1rem',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
              backgroundColor: 'var(--bg-subtle)',
            }}
          >
            <div style={{ fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              <Clock size={13} /> Cutoff {c.cutoff} UTC
            </div>
            <div style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '0.2rem' }}>
              MAE: {c.maeMW?.toLocaleString()} MW
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              RMSE: {c.rmseMW} MW | WAPE: {c.wapePct}%
            </div>
          </div>
        ))}
      </div>

      {/* Multi-Line Chart */}
      <div className="chart-container" style={{ height: '360px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
            <XAxis dataKey="hour" stroke="#64748b" fontSize={11} tickLine={false} />
            <YAxis
              stroke="#64748b"
              fontSize={11}
              tickLine={false}
              tickFormatter={(val) => `${(val / 1000).toFixed(0)}k`}
              unit=" MW"
            />
            <Tooltip
              content={({ active, payload, label }: any) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="custom-tooltip">
                      <div className="tooltip-title">{`${date} @ ${label} UTC`}</div>
                      {payload.map((p: any) => (
                        <div key={p.name} className="tooltip-row">
                          <span className="tooltip-label" style={{ color: p.color }}>
                            ● {p.name}:
                          </span>
                          <span className="tooltip-value">
                            {p.value !== null && p.value !== undefined ? `${p.value.toLocaleString()} MW` : 'N/A'}
                          </span>
                        </div>
                      ))}
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend verticalAlign="top" height={36} />
            {/* Bold Green Actual Generation line */}
            <Line
              type="monotone"
              dataKey="actualMW"
              stroke="#0f172a"
              strokeWidth={3}
              dot={false}
              name="Actual Metered (MW)"
            />
            <Line
              type="monotone"
              dataKey="09:00 UTC Cutoff"
              stroke={CUTOFF_COLORS.fc_0900}
              strokeWidth={1.5}
              strokeDasharray="5 5"
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="11:00 UTC Cutoff"
              stroke={CUTOFF_COLORS.fc_1100}
              strokeWidth={1.5}
              strokeDasharray="4 4"
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="12:00 UTC Cutoff"
              stroke={CUTOFF_COLORS.fc_1200}
              strokeWidth={2.2}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="14:00 UTC Cutoff"
              stroke={CUTOFF_COLORS.fc_1400}
              strokeWidth={1.5}
              strokeDasharray="3 3"
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="17:00 UTC Cutoff"
              stroke={CUTOFF_COLORS.fc_1700}
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="info-box">
        <ShieldCheck size={18} style={{ flexShrink: 0 }} />
        <span>
          <strong>Market Context:</strong> As forecast publication moves closer to delivery (from 09:00 to 17:00 on $D-1$), the meteorological forecast horizon contracts, typically improving predictive accuracy. Traders use this evolution to evaluate auction bidding vs intra-day balancing adjustments.
        </span>
      </div>
    </div>
  );
};
