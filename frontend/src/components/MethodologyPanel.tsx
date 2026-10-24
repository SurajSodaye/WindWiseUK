import React from 'react';
import { Layers, Clock, AlertTriangle, Database, HelpCircle } from 'lucide-react';

export const MethodologyPanel: React.FC = () => {
  return (
    <footer className="app-footer">
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
        <HelpCircle size={18} style={{ color: 'var(--accent-wind-blue)' }} />
        <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-main)' }}>
          Methodology, Data Resolution & Compliance Specifications
        </h3>
      </div>
      <p style={{ color: 'var(--text-secondary)', maxWidth: '900px' }}>
        WindWise UK adheres strictly to official Elexon Insights Solution (BMRS API v1) conventions and UK power market standards for verifiable day-ahead accuracy auditing.
      </p>

      <div className="methodology-grid">
        {/* Item 1: Resolution Alignment */}
        <div className="methodology-item">
          <h4>
            <Layers size={16} style={{ color: 'var(--accent-wind-blue)' }} />
            Resolution Alignment (Hourly Outturn)
          </h4>
          <p>
            Actual generation is reported in 30-minute settlement periods (<code>FUELHH</code>, periods 1–48). Day-ahead forecasts (<code>WINDFOR</code>) are published at 60-minute resolution. To avoid artificially inflating observation sample counts, the two corresponding half-hourly actual MW values are averaged into an hourly value <strong>only when both settlement periods are present</strong>.
          </p>
        </div>

        {/* Item 2: Day-Ahead Cutoff & No Look-Ahead */}
        <div className="methodology-item">
          <h4>
            <Clock size={16} style={{ color: 'var(--accent-indigo)' }} />
            Strict No-Lookahead Filter
          </h4>
          <p>
            For delivery day $D$, trading decisions occur on day $D-1$. The selected cutoff (e.g. 11:00 EPEX gate or 12:00 Elexon reference gate) strictly filters the forecast pool to publications $\le$ cutoff time on $D-1$. Any forecast issued after the gate closure timestamp is excluded from evaluation.
          </p>
        </div>

        {/* Item 3: Timezones & UTC Standards */}
        <div className="methodology-item">
          <h4>
            <Database size={16} style={{ color: 'var(--accent-green)' }} />
            UTC & Greenwich Mean Time
          </h4>
          <p>
            All timestamps are retrieved, processed, and stored in ISO 8601 UTC (<code>Z</code>). In January, the United Kingdom operates on Greenwich Mean Time (GMT = UTC+0), meaning UK local time matches UTC without daylight saving clock shifts.
          </p>
        </div>

        {/* Item 4: Regulatory Disclaimer */}
        <div className="methodology-item">
          <h4>
            <AlertTriangle size={16} style={{ color: 'var(--accent-amber)' }} />
            Trading & Procurement Notice
          </h4>
          <p>
            This dashboard objectively verifies the physical predictive accuracy of national wind generation forecasts against metered outturn. It does not calculate commercial electricity trading settlement cashflows, imbalance prices, or supplier procurement volumes.
          </p>
        </div>
      </div>

      <div style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
        WindWise UK · Official Elexon Insights Solution (BMRS API v1) · React + Vite + FastAPI Stack
      </div>
    </footer>
  );
};
