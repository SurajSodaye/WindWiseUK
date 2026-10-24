import React from 'react';
import { Calendar, Clock, RefreshCw, Check, AlertCircle } from 'lucide-react';
import type { CutoffTime, FilterState } from '../types';

interface FilterBarProps {
  filters: FilterState;
  onFilterChange: (newFilters: Partial<FilterState>) => void;
  onRefresh: () => void;
  isLoading: boolean;
}

const CUTOFF_OPTIONS: { value: CutoffTime; label: string; desc: string }[] = [
  { value: '09:00', label: '09:00 UTC', desc: 'Early Morning Trading Gate' },
  { value: '11:00', label: '11:00 UTC', desc: 'EPEX SPOT GB Day-Ahead Auction Close' },
  { value: '12:00', label: '12:00 UTC (Default)', desc: 'Standard Elexon Reference Gate Closure' },
  { value: '14:00', label: '14:00 UTC', desc: 'Post-Auction Optimization' },
  { value: '17:00', label: '17:00 UTC', desc: 'Late Afternoon Day-Ahead Rebalancing' },
];

const PRESETS = [
  { label: 'Full Month (Jan 1–31)', start: '2026-01-01', end: '2026-01-31' },
  { label: 'Week 1 (Jan 1–7)', start: '2026-01-01', end: '2026-01-07' },
  { label: 'Week 2 (Jan 8–14)', start: '2026-01-08', end: '2026-01-14' },
  { label: 'Week 3 (Jan 15–21)', start: '2026-01-15', end: '2026-01-21' },
  { label: 'Week 4 (Jan 22–28)', start: '2026-01-22', end: '2026-01-28' },
  { label: 'Jan 15 Focus Day', start: '2026-01-15', end: '2026-01-15' },
];

export const FilterBar: React.FC<FilterBarProps> = ({
  filters,
  onFilterChange,
  onRefresh,
  isLoading,
}) => {
  const isInvalidDateRange = filters.startDate > filters.endDate;

  return (
    <div className="filter-bar">
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1.25rem', alignItems: 'flex-end' }}>
          {/* Start Date */}
          <div className="filter-group">
            <label className="filter-label" htmlFor="start-date-input">
              <Calendar size={14} /> Start Date
            </label>
            <input
              id="start-date-input"
              type="date"
              className="filter-input"
              value={filters.startDate}
              min="2026-01-01"
              max="2026-01-31"
              onChange={(e) => onFilterChange({ startDate: e.target.value })}
            />
          </div>

          {/* End Date */}
          <div className="filter-group">
            <label className="filter-label" htmlFor="end-date-input">
              <Calendar size={14} /> End Date
            </label>
            <input
              id="end-date-input"
              type="date"
              className="filter-input"
              value={filters.endDate}
              min="2026-01-01"
              max="2026-01-31"
              onChange={(e) => onFilterChange({ endDate: e.target.value })}
            />
          </div>

          {/* Cutoff Selector */}
          <div className="filter-group">
            <label className="filter-label" htmlFor="cutoff-select">
              <Clock size={14} /> Day-Ahead Cutoff (D-1 UTC)
            </label>
            <select
              id="cutoff-select"
              className="filter-select"
              value={filters.cutoff}
              onChange={(e) => onFilterChange({ cutoff: e.target.value as CutoffTime })}
            >
              {CUTOFF_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label} — {opt.desc}
                </option>
              ))}
            </select>
          </div>

          {/* Refresh Action */}
          <button
            className="btn-primary"
            onClick={onRefresh}
            disabled={isLoading || isInvalidDateRange}
            aria-label="Refresh Dashboard Data"
          >
            <RefreshCw size={15} className={isLoading ? 'status-dot' : ''} />
            {isLoading ? 'Recalculating...' : 'Refresh Metrics'}
          </button>
        </div>

        {/* Date Presets */}
        <div className="date-presets">
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', alignSelf: 'center', fontWeight: 600 }}>
            QUICK PRESETS:
          </span>
          {PRESETS.map((p) => {
            const isActive = filters.startDate === p.start && filters.endDate === p.end;
            return (
              <button
                key={p.label}
                className={`preset-pill ${isActive ? 'active' : ''}`}
                onClick={() => onFilterChange({ startDate: p.start, endDate: p.end })}
              >
                {isActive && <Check size={11} style={{ marginRight: 3, display: 'inline' }} />}
                {p.label}
              </button>
            );
          })}
        </div>

        {isInvalidDateRange && (
          <div style={{ color: 'var(--accent-rose)', fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <AlertCircle size={14} /> Start date cannot be after end date.
          </div>
        )}
      </div>

      {/* Cutoff Explanation Note */}
      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', maxWidth: '340px', lineHeight: '1.4' }}>
        <strong>No-Lookahead Guarantee:</strong> At cutoff <code>{filters.cutoff} UTC</code> on day $D-1$, only forecasts published on or before that exact timestamp are evaluated. All later updates are strictly excluded.
      </div>
    </div>
  );
};
