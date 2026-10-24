import React from 'react';
import { Wind, Activity } from 'lucide-react';
import type { HealthResponse } from '../types';

interface HeaderProps {
  health: HealthResponse | null;
  healthLoading: boolean;
  healthError: string | null;
  startDate: string;
  endDate: string;
}

export const Header: React.FC<HeaderProps> = ({
  health,
  healthLoading,
  healthError,
  startDate,
  endDate,
}) => {
  return (
    <header className="app-header">
      <div className="header-content">
        <div className="brand-wrapper">
          <div className="brand-icon">
            <Wind size={26} strokeWidth={2.2} />
          </div>
          <div className="brand-title-group">
            <h1>
              WindWise UK
              <span className="badge-tag">BMRS Verified</span>
            </h1>
            <p className="brand-subtitle">
              UK Electricity Day-Ahead Wind Generation Forecast & Accuracy Dashboard
            </p>
          </div>
        </div>

        <div className="header-right">
          <div className="api-status-badge">
            {healthLoading ? (
              <>
                <div className="status-dot status-online" style={{ opacity: 0.5 }} />
                <span>Connecting to API...</span>
              </>
            ) : healthError ? (
              <>
                <div className="status-dot status-offline" />
                <span style={{ color: '#f87171' }}>API Disconnected</span>
              </>
            ) : (
              <>
                <div className="status-dot status-online" />
                <span>
                  Live BMRS Cache: {health?.cachedActualsCount?.toLocaleString() || 0} actuals /{' '}
                  {health?.cachedForecastsCount?.toLocaleString() || 0} forecasts
                </span>
              </>
            )}
          </div>

          <div
            className="api-status-badge"
            style={{ backgroundColor: 'rgba(2, 132, 199, 0.2)', borderColor: 'rgba(56, 189, 248, 0.3)' }}
          >
            <Activity size={14} style={{ color: '#38bdf8' }} />
            <span style={{ color: '#e0f2fe' }}>
              Period: {startDate} to {endDate}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
