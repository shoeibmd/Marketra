import logging
from datetime import UTC, datetime, time, timedelta
from typing import Any
import zoneinfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import FinancialEvent, EventMarketObservation, Instrument, OHLCV, Quote

logger = logging.getLogger("terminal.analytics")

IST = zoneinfo.ZoneInfo("Asia/Kolkata")
MARKET_OPEN_TIME = time(9, 15)
MARKET_CLOSE_TIME = time(15, 30)

# Known Indian Market Holidays (subset for testing/runtime)
KNOWN_MARKET_HOLIDAYS = {
    "2026-01-26", # Republic Day
    "2026-08-15", # Independence Day
    "2026-10-02", # Gandhi Jayanti
}


def classify_trading_session(dt: datetime) -> str:
    """Classify event timestamp into PRE_MARKET, INTRADAY, POST_MARKET, WEEKEND, or MARKET_HOLIDAY in IST."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)

    dt_ist = dt.astimezone(IST)
    date_str = dt_ist.strftime("%Y-%m-%d")

    # Check weekend
    if dt_ist.weekday() in (5, 6):  # Saturday or Sunday
        return "WEEKEND"

    # Check holiday
    if date_str in KNOWN_MARKET_HOLIDAYS:
        return "MARKET_HOLIDAY"

    t = dt_ist.time()
    if t < MARKET_OPEN_TIME:
        return "PRE_MARKET"
    elif t > MARKET_CLOSE_TIME:
        return "POST_MARKET"
    else:
        return "INTRADAY"


class EventMarketAnalyticsService:
    """Calculates factual historical market observations around financial events using OHLCV data."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def calculate_event_observation(
        self,
        event: FinancialEvent,
        instrument: Instrument,
    ) -> EventMarketObservation:
        """Calculate historical market observations (1D, 3D, 5D, 10D, 20D, volume change) for an event."""
        session_class = classify_trading_session(event.event_date)

        # Query historical daily OHLCV bars around event_date
        stmt = (
            select(OHLCV)
            .where(
                OHLCV.instrument_id == instrument.id,
                OHLCV.interval == "1d",
            )
            .order_by(OHLCV.timestamp.asc())
        )
        res = await self.db.execute(stmt)
        bars = res.scalars().all()

        if not bars:
            return EventMarketObservation(
                event_id=event.id,
                instrument_id=instrument.id,
                event_timestamp=event.event_date,
                session_classification=session_class,
                data_status="INSUFFICIENT",
                calculation_method="PREVIOUS_CLOSE_BASELINE",
                metadata_json={"note": "No OHLCV bars available for instrument"},
            )

        # Find baseline bar (last available bar before or on event_date)
        event_utc = event.event_date if event.event_date.tzinfo else event.event_date.replace(tzinfo=UTC)
        baseline_bar = None
        after_bars: list[OHLCV] = []

        for bar in bars:
            bar_utc = bar.timestamp if bar.timestamp.tzinfo else bar.timestamp.replace(tzinfo=UTC)
            if bar_utc <= event_utc:
                baseline_bar = bar
            else:
                after_bars.append(bar)

        if not baseline_bar:
            baseline_bar = bars[0]
            after_bars = bars[1:]

        baseline_price = baseline_bar.close
        baseline_time = baseline_bar.timestamp

        # Calculate returns over windows
        r1d = self._calc_pct_change(baseline_price, after_bars[0].close) if len(after_bars) >= 1 else None
        r3d = self._calc_pct_change(baseline_price, after_bars[2].close) if len(after_bars) >= 3 else None
        r5d = self._calc_pct_change(baseline_price, after_bars[4].close) if len(after_bars) >= 5 else None
        r10d = self._calc_pct_change(baseline_price, after_bars[9].close) if len(after_bars) >= 10 else None
        r20d = self._calc_pct_change(baseline_price, after_bars[19].close) if len(after_bars) >= 20 else None

        # Calculate volume change (baseline bar volume vs average volume of first 3 days after)
        vol_before = baseline_bar.volume
        vol_after = (sum(b.volume for b in after_bars[:3]) / len(after_bars[:3])) if after_bars else None
        vol_change_pct = self._calc_pct_change(vol_before, vol_after) if vol_before and vol_after else None

        data_status = "AVAILABLE" if len(after_bars) >= 1 else "INSUFFICIENT"

        obs = EventMarketObservation(
            event_id=event.id,
            instrument_id=instrument.id,
            event_timestamp=event.event_date,
            session_classification=session_class,
            baseline_timestamp=baseline_time,
            baseline_price=baseline_price,
            price_at_event=baseline_price,
            return_1d_pct=r1d,
            return_3d_pct=r3d,
            return_5d_pct=r5d,
            return_10d_pct=r10d,
            return_20d_pct=r20d,
            volume_before=vol_before,
            volume_after=vol_after,
            volume_change_pct=vol_change_pct,
            calculation_method="PREVIOUS_CLOSE_BASELINE",
            data_status=data_status,
            metadata_json={
                "session_classification": session_class,
                "baseline_date": baseline_time.isoformat(),
                "bars_after_count": len(after_bars),
                "disclaimer": "Historical observations are factual measurements and do not imply causation or future predictions.",
            },
        )
        return obs

    @staticmethod
    def _calc_pct_change(base: float, current: float) -> float | None:
        if not base or base == 0:
            return None
        return round(((current - base) / base) * 100.0, 2)

    @staticmethod
    def compute_aggregate_statistics(observations: list[EventMarketObservation], window: str = "1d") -> dict[str, Any]:
        """Compute factual aggregate statistics with strict sample size threshold (n < 5)."""
        valid_returns: list[float] = []

        attr_map = {
            "1d": "return_1d_pct",
            "3d": "return_3d_pct",
            "5d": "return_5d_pct",
            "10d": "return_10d_pct",
            "20d": "return_20d_pct",
        }
        attr = attr_map.get(window, "return_1d_pct")

        for obs in observations:
            val = getattr(obs, attr, None)
            if val is not None:
                valid_returns.append(val)

        sample_size = len(valid_returns)

        if sample_size < 5:
            return {
                "window": window,
                "sample_size": sample_size,
                "insufficient_sample": True,
                "message": "Insufficient historical sample for meaningful aggregate statistics.",
                "disclaimer": "Historical observations are for informational analysis only.",
            }

        valid_returns.sort()
        avg_ret = round(sum(valid_returns) / sample_size, 2)
        med_ret = round(valid_returns[sample_size // 2], 2)
        min_ret = min(valid_returns)
        max_ret = max(valid_returns)
        positive_count = sum(1 for r in valid_returns if r > 0)
        negative_count = sum(1 for r in valid_returns if r < 0)

        return {
            "window": window,
            "sample_size": sample_size,
            "insufficient_sample": False,
            "mean_return_pct": avg_ret,
            "median_return_pct": med_ret,
            "min_return_pct": min_ret,
            "max_return_pct": max_ret,
            "positive_observations": positive_count,
            "negative_observations": negative_count,
            "disclaimer": "Historical aggregate statistics reflect past observations and do not predict future performance.",
        }
