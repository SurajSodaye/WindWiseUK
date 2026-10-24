from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    timestamp: str
    cachedActualsCount: int = 0
    cachedForecastsCount: int = 0
    cacheDatabase: str


class FuelHHRecord(BaseModel):
    dataset: str = "FUELHH"
    publishTime: str
    startTime: str
    settlementDate: str
    settlementPeriod: int
    fuelType: str
    generation: float


class WindforRecord(BaseModel):
    dataset: str = "WINDFOR"
    publishTime: str
    startTime: str
    generation: float


class HourlyInterval(BaseModel):
    startTime: str = Field(description="ISO 8601 start timestamp in UTC (YYYY-MM-DDTHH:00:00Z)")
    settlementDate: str = Field(description="Delivery date (YYYY-MM-DD)")
    hour: int = Field(ge=0, le=23, description="Hour of the day (0 to 23)")
    actualMW: Optional[float] = Field(None, description="Average actual generation across the two half-hours in MW")
    actualPeriodsCount: int = Field(description="Number of half-hourly periods available (0, 1, or 2)")
    forecastMW: Optional[float] = Field(None, description="Day-ahead forecast generation in MW")
    forecastPublishTime: Optional[str] = Field(None, description="ISO timestamp when the selected forecast was published")
    errorMW: Optional[float] = Field(None, description="Forecast Error: Forecast MW - Actual MW")
    absoluteErrorMW: Optional[float] = Field(None, description="Absolute Forecast Error in MW")
    isMatched: bool = Field(description="True if both actual and forecast values are present")


class MetricsSummary(BaseModel):
    startDate: str
    endDate: str
    cutoff: str
    totalHours: int = Field(description="Total calendar hours in the requested date range")
    matchedHours: int = Field(description="Number of hours with both valid actual and forecast observations")
    missingActualHours: int = Field(description="Number of hours where actual generation could not be determined")
    missingForecastHours: int = Field(description="Number of hours where no eligible forecast was available before cutoff")
    meanActualMW: Optional[float] = None
    meanForecastMW: Optional[float] = None
    totalActualGWh: Optional[float] = None
    totalForecastGWh: Optional[float] = None
    maeMW: Optional[float] = Field(None, description="Mean Absolute Error in MW")
    rmseMW: Optional[float] = Field(None, description="Root Mean Square Error in MW")
    biasMW: Optional[float] = Field(None, description="Forecast Bias: Mean(Forecast - Actual) in MW")
    biasPct: Optional[float] = Field(None, description="Forecast Bias as a percentage of Mean Actual")
    wapePct: Optional[float] = Field(None, description="Weighted Absolute Percentage Error in percent")


class DailyMetrics(BaseModel):
    date: str
    totalHours: int = 24
    matchedHours: int
    meanActualMW: Optional[float] = None
    meanForecastMW: Optional[float] = None
    maeMW: Optional[float] = None
    rmseMW: Optional[float] = None
    biasMW: Optional[float] = None
    biasPct: Optional[float] = None
    wapePct: Optional[float] = None


class MetricsResponse(BaseModel):
    summary: MetricsSummary
    dailyMetrics: List[DailyMetrics]


class TimeseriesResponse(BaseModel):
    date: str
    cutoff: str
    intervals: List[HourlyInterval]
    daySummary: Optional[MetricsSummary] = None


class CutoffEvolutionItem(BaseModel):
    cutoff: str
    matchedHours: int
    maeMW: Optional[float] = None
    rmseMW: Optional[float] = None
    biasMW: Optional[float] = None
    biasPct: Optional[float] = None
    wapePct: Optional[float] = None


class ForecastEvolutionResponse(BaseModel):
    date: str
    cutoffs: List[CutoffEvolutionItem]
    intervals: List[Dict[str, Any]]
