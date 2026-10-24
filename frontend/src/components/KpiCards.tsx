import React from 'react';
import { Target, Activity, TrendingUp, Percent, Zap, CheckCircle2, AlertCircle } from 'lucide-react';
import type { MetricsSummary } from '../types';

interface KpiCardsProps {
  summary: MetricsSummary | null;
  isLoading: boolean;
}

export const KpiCards: React.FC<KpiCardsProps> = ({ summary, isLoading }) => {
  if (isLoading || !summary) {
    return (
      <div className="kpi-grid">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="kpi-card loading-skeleton" style={{ height: '140px' }} />
        ))}
      </div>
    );
  }

  const isOverforecast = (summary.biasMW || 0) > 0;
  const isZeroBias = (summary.biasMW || 0) === 0;

  return (
    <div className="kpi-grid">
      {/* 1. MAE */}
      <div className="kpi-card mae">
        <div className="kpi-header">
          <span className="kpi-title">Mean Absolute Error</span>
          <div className="kpi-icon">
            <Target size={18} style={{ color: 'var(--accent-wind-blue)' }} />
          </div>
        </div>
        <div className="kpi-value-row">
          <span className="kpi-value tabular-nums">
            {summary.maeMW !== null ? summary.maeMW.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 }) : '—'}
          </span>
          <span className="kpi-unit">MW</span>
        </div>
        <div className="kpi-subtext">
          <span>Avg magnitude of prediction deviation</span>
        </div>
      </div>

      {/* 2. RMSE */}
      <div className="kpi-card rmse">
        <div className="kpi-header">
          <span className="kpi-title">Root Mean Square Error</span>
          <div className="kpi-icon">
            <Activity size={18} style={{ color: 'var(--accent-indigo)' }} />
          </div>
        </div>
        <div className="kpi-value-row">
          <span className="kpi-value tabular-nums">
            {summary.rmseMW !== null ? summary.rmseMW.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 }) : '—'}
          </span>
          <span className="kpi-unit">MW</span>
        </div>
        <div className="kpi-subtext">
          <span>Higher penalty for severe error outliers</span>
        </div>
      </div>

      {/* 3. Forecast Bias */}
      <div className="kpi-card bias">
        <div className="kpi-header">
          <span className="kpi-title">Forecast Bias (Mean Error)</span>
          <div className="kpi-icon">
            <TrendingUp size={18} style={{ color: 'var(--accent-amber)' }} />
          </div>
        </div>
        <div className="kpi-value-row">
          <span className="kpi-value tabular-nums" style={{ color: isOverforecast ? 'var(--accent-amber)' : 'var(--accent-indigo)' }}>
            {summary.biasMW !== null
              ? `${summary.biasMW > 0 ? '+' : ''}${summary.biasMW.toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 })}`
              : '—'}
          </span>
          <span className="kpi-unit">MW</span>
        </div>
        <div className="kpi-subtext">
          {summary.biasPct !== null && (
            <span style={{ fontWeight: 600 }}>
              {summary.biasPct > 0 ? '+' : ''}{summary.biasPct}% vs actual mean
            </span>
          )}
          {isZeroBias ? (
            <span className="badge-underforecast">Unbiased</span>
          ) : isOverforecast ? (
            <span className="badge-overforecast">Overforecasting</span>
          ) : (
            <span className="badge-underforecast">Underforecasting</span>
          )}
        </div>
      </div>

      {/* 4. WAPE */}
      <div className="kpi-card wape">
        <div className="kpi-header">
          <span className="kpi-title">WAPE</span>
          <div className="kpi-icon">
            <Percent size={18} style={{ color: 'var(--accent-green)' }} />
          </div>
        </div>
        <div className="kpi-value-row">
          <span className="kpi-value tabular-nums">
            {summary.wapePct !== null ? `${summary.wapePct.toFixed(2)}` : '—'}
          </span>
          <span className="kpi-unit">%</span>
        </div>
        <div className="kpi-subtext">
          <span>Weighted Absolute Percentage Error (industry standard)</span>
        </div>
      </div>

      {/* 5. Total Generation Volume */}
      <div className="kpi-card energy">
        <div className="kpi-header">
          <span className="kpi-title">Total Wind Generation</span>
          <div className="kpi-icon">
            <Zap size={18} style={{ color: '#0284c7' }} />
          </div>
        </div>
        <div className="kpi-value-row">
          <span className="kpi-value tabular-nums">
            {summary.totalActualGWh !== null ? summary.totalActualGWh.toLocaleString() : '—'}
          </span>
          <span className="kpi-unit">GWh Actual</span>
        </div>
        <div className="kpi-subtext">
          <span>
            Forecasted: <strong>{summary.totalForecastGWh?.toLocaleString()} GWh</strong> (
            Mean: {summary.meanActualMW?.toLocaleString()} MW)
          </span>
        </div>
      </div>

      {/* 6. Evaluation Sample & Quality */}
      <div className="kpi-card quality">
        <div className="kpi-header">
          <span className="kpi-title">Data Quality & Sample</span>
          <div className="kpi-icon">
            {summary.missingActualHours === 0 && summary.missingForecastHours === 0 ? (
              <CheckCircle2 size={18} style={{ color: '#10b981' }} />
            ) : (
              <AlertCircle size={18} style={{ color: 'var(--accent-amber)' }} />
            )}
          </div>
        </div>
        <div className="kpi-value-row">
          <span className="kpi-value tabular-nums">
            {summary.matchedHours} / {summary.totalHours}
          </span>
          <span className="kpi-unit">Hours</span>
        </div>
        <div className="kpi-subtext">
          <span>
            {summary.missingActualHours === 0 && summary.missingForecastHours === 0
              ? '100% complete hourly coverage (0 missing)'
              : `Missing: ${summary.missingActualHours} actuals, ${summary.missingForecastHours} forecasts`}
          </span>
        </div>
      </div>
    </div>
  );
};
