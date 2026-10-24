export type CutoffTime = '09:00' | '11:00' | '12:00' | '14:00' | '17:00';

export interface HealthResponse {
  status: string;
  timestamp: string;
  cachedActualsCount: number;
  cachedForecastsCount: number;
  cacheDatabase: string;
}

export interface HourlyInterval {
  startTime: string; // ISO 8601 UTC
  settlementDate: string; // YYYY-MM-DD
  hour: number; // 0-23
  actualMW: number | null;
  actualPeriodsCount: number; // 0, 1, or 2
  forecastMW: number | null;
  forecastPublishTime: string | null;
  errorMW: number | null; // Forecast - Actual
  absoluteErrorMW: number | null;
  isMatched: boolean;
}

export interface MetricsSummary {
  startDate: string;
  endDate: string;
  cutoff: string;
  totalHours: number;
  matchedHours: number;
  missingActualHours: number;
  missingForecastHours: number;
  meanActualMW: number | null;
  meanForecastMW: number | null;
  totalActualGWh: number | null;
  totalForecastGWh: number | null;
  maeMW: number | null;
  rmseMW: number | null;
  biasMW: number | null;
  biasPct: number | null;
  wapePct: number | null;
}

export interface DailyMetrics {
  date: string;
  totalHours: number;
  matchedHours: number;
  meanActualMW: number | null;
  meanForecastMW: number | null;
  maeMW: number | null;
  rmseMW: number | null;
  biasMW: number | null;
  biasPct: number | null;
  wapePct: number | null;
}

export interface MetricsResponse {
  summary: MetricsSummary;
  dailyMetrics: DailyMetrics[];
}

export interface TimeseriesResponse {
  date: string;
  cutoff: string;
  intervals: HourlyInterval[];
  daySummary: MetricsSummary | null;
}

export interface CutoffEvolutionItem {
  cutoff: string;
  matchedHours: number;
  maeMW: number | null;
  rmseMW: number | null;
  biasMW: number | null;
  biasPct: number | null;
  wapePct: number | null;
}

export interface ForecastEvolutionInterval {
  hour: number;
  startTime: string;
  actualMW: number | null;
  fc_0900?: number | null;
  fc_1100?: number | null;
  fc_1200?: number | null;
  fc_1400?: number | null;
  fc_1700?: number | null;
  [key: string]: any;
}

export interface ForecastEvolutionResponse {
  date: string;
  cutoffs: CutoffEvolutionItem[];
  intervals: ForecastEvolutionInterval[];
}

export interface FilterState {
  startDate: string;
  endDate: string;
  cutoff: CutoffTime;
  selectedDate: string; // Date for timeseries and evolution view
}
