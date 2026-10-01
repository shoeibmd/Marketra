import logging
import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import BacktestJob, BacktestResult, Instrument, OHLCV

logger = logging.getLogger("terminal.backtest_engine")


class StrategyRegistry:
    """Server-side registry for pre-built, trusted backtest strategies. Strictly prohibits arbitrary code execution."""

    @staticmethod
    def get_supported_strategies() -> list[dict[str, Any]]:
        return [
            {
                "name": "SMA_CROSSOVER",
                "description": "Simple Moving Average crossover strategy (Short SMA vs Long SMA)",
                "parameters": {
                    "short_window": {"type": "int", "default": 5, "min": 1, "max": 50},
                    "long_window": {"type": "int", "default": 20, "min": 2, "max": 200},
                    "position_size": {"type": "float", "default": 0.20, "min": 0.01, "max": 1.0},
                },
            },
            {
                "name": "EVENT_REACTION_RESEARCH",
                "description": "Simulate positions around historical financial disclosures",
                "parameters": {
                    "event_type": {"type": "str", "default": "ACQUISITION"},
                    "hold_days": {"type": "int", "default": 5, "min": 1, "max": 30},
                    "position_size": {"type": "float", "default": 0.10, "min": 0.01, "max": 1.0},
                },
            },
        ]


class BacktestEngine:
    """Deterministic, look-ahead bias protected backtesting engine."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def run_backtest(
        self,
        job: BacktestJob,
        slippage_pct: Decimal = Decimal("0.0005"),
        fee_amount: Decimal = Decimal("20.00"),
    ) -> BacktestResult:
        """Run backtest simulation with strict look-ahead bias protection."""
        stmt = select(Instrument).where(Instrument.symbol == job.symbol.upper())
        res = await self.db.execute(stmt)
        inst = res.scalar_one_or_none()

        if not inst:
            raise ValueError(f"Instrument {job.symbol} not found")

        ohlcv_stmt = (
            select(OHLCV)
            .where(OHLCV.instrument_id == inst.id, OHLCV.interval == "1d")
            .order_by(OHLCV.timestamp.asc())
        )
        ohlcv_res = await self.db.execute(ohlcv_stmt)
        bars = ohlcv_res.scalars().all()

        if len(bars) < 10:
            raise ValueError(f"Insufficient historical OHLCV data for {job.symbol} (found {len(bars)} bars, minimum 10 required)")

        # Strategy parameters
        params = job.parameters_json
        short_w = int(params.get("short_window", 5))
        long_w = int(params.get("long_window", 20))

        initial_cash = Decimal(str(job.initial_capital))
        cash = initial_cash
        position_qty = Decimal("0")
        entry_price = Decimal("0")

        equity_curve: list[dict[str, Any]] = []
        trades: list[dict[str, Any]] = []

        winning_trades = 0
        losing_trades = 0
        peak_equity = initial_cash
        max_drawdown_pct = Decimal("0.00")

        # Look-ahead protection: Loop sequentially up to index t, generate signal at t, execute at t+1 open/close
        for t in range(long_w, len(bars) - 1):
            current_bar = bars[t]
            next_bar = bars[t + 1]  # Execution bar

            # Calculate short & long SMA using data available up to t ONLY
            short_sma = sum(b.close for b in bars[t - short_w + 1 : t + 1]) / short_w
            long_sma = sum(b.close for b in bars[t - long_w + 1 : t + 1]) / long_w

            prev_short_sma = sum(b.close for b in bars[t - short_w : t]) / short_w
            prev_long_sma = sum(b.close for b in bars[t - long_w : t]) / long_w

            # BUY signal at t -> execute at t+1 Open/Close
            signal = "HOLD"
            if prev_short_sma <= prev_long_sma and short_sma > long_sma:
                signal = "BUY"
            elif prev_short_sma >= prev_long_sma and short_sma < long_sma:
                signal = "SELL"

            exec_price = Decimal(str(next_bar.open))

            if signal == "BUY" and position_qty == Decimal("0"):
                trade_alloc = cash * Decimal("0.5")  # allocate 50% cash
                eff_price = exec_price * (Decimal("1") + slippage_pct)
                qty = (trade_alloc - fee_amount) / eff_price
                if qty > Decimal("0"):
                    qty = round(qty, 4)
                    cost = (qty * eff_price) + fee_amount
                    cash -= cost
                    position_qty = qty
                    entry_price = eff_price
                    trades.append(
                        {
                            "bar_time": next_bar.timestamp.isoformat(),
                            "side": "BUY",
                            "quantity": float(qty),
                            "execution_price": float(eff_price),
                            "fee": float(fee_amount),
                        }
                    )

            elif signal == "SELL" and position_qty > Decimal("0"):
                eff_price = exec_price * (Decimal("1") - slippage_pct)
                proceeds = (position_qty * eff_price) - fee_amount
                realized_pnl = round(((eff_price - entry_price) * position_qty) - fee_amount, 2)
                cash += proceeds

                if realized_pnl > Decimal("0"):
                    winning_trades += 1
                else:
                    losing_trades += 1

                trades.append(
                    {
                        "bar_time": next_bar.timestamp.isoformat(),
                        "side": "SELL",
                        "quantity": float(position_qty),
                        "execution_price": float(eff_price),
                        "fee": float(fee_amount),
                        "realized_pnl": float(realized_pnl),
                    }
                )
                position_qty = Decimal("0")
                entry_price = Decimal("0")

            # Record snapshot
            current_close = Decimal(str(next_bar.close))
            curr_equity = cash + (position_qty * current_close)
            if curr_equity > peak_equity:
                peak_equity = curr_equity
            dd = ((peak_equity - curr_equity) / peak_equity) * Decimal("100") if peak_equity > Decimal("0") else Decimal("0.00")
            if dd > max_drawdown_pct:
                max_drawdown_pct = dd

            equity_curve.append(
                {
                    "timestamp": next_bar.timestamp.isoformat(),
                    "equity": float(curr_equity),
                    "drawdown_pct": float(dd),
                }
            )

        final_equity = cash + (position_qty * Decimal(str(bars[-1].close)))
        total_pnl = final_equity - initial_cash
        total_return_pct = round((total_pnl / initial_cash) * Decimal("100"), 2)

        total_trades = winning_trades + losing_trades
        win_rate_pct = round((Decimal(winning_trades) / Decimal(total_trades)) * Decimal("100"), 2) if total_trades > 0 else Decimal("0.00")

        result = BacktestResult(
            id=uuid.uuid4(),
            job_id=job.id,
            initial_capital=initial_cash,
            final_equity=round(final_equity, 2),
            total_pnl=round(total_pnl, 2),
            total_return_pct=total_return_pct,
            max_drawdown_pct=round(max_drawdown_pct, 2),
            trade_count=total_trades,
            win_rate_pct=win_rate_pct,
            metrics_json={
                "winning_trades": winning_trades,
                "losing_trades": losing_trades,
                "slippage_pct": float(slippage_pct),
                "fee_amount": float(fee_amount),
                "disclaimer": "HISTORICAL SIMULATION RESULTS ONLY — PAST PERFORMANCE DOES NOT GUARANTEE FUTURE RESULTS",
            },
            equity_curve_json=equity_curve,
            trades_json=trades,
        )

        job.status = "COMPLETED"
        self.db.add(result)
        await self.db.commit()
        await self.db.refresh(result)
        return result
