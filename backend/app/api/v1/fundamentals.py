from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth.auth_service import get_current_user
from app.schemas.market_data import NormalizedFundamental
from app.services.providers.mock import MockProvider

router = APIRouter(prefix="/fundamentals", tags=["Fundamentals"])
mock_provider = MockProvider()


@router.get("/{symbol}", response_model=NormalizedFundamental)
async def get_instrument_fundamentals(
    symbol: str,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> NormalizedFundamental:
    """Fetch fundamental metrics for an instrument."""
    inst = await mock_provider.get_instrument_by_symbol(symbol)
    if not inst:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instrument {symbol} not found",
        )

    fund = await mock_provider.get_fundamentals(inst)
    if not fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fundamentals for {symbol} not found",
        )
    return NormalizedFundamental.model_validate(fund)


@router.get("/{symbol}/statements")
async def get_financial_statements(
    symbol: str,
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Fetch income statement, balance sheet, and cash flow overview."""
    inst = await mock_provider.get_instrument_by_symbol(symbol)
    if not inst:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instrument {symbol} not found",
        )

    return {
        "symbol": inst.symbol,
        "currency": inst.currency,
        "period": "Annual",
        "income_statement": {
            "total_revenue": 383285000000,
            "net_income": 96995000000,
            "operating_income": 114301000000,
        },
        "balance_sheet": {
            "total_assets": 352583000000,
            "total_liabilities": 290437000000,
            "total_stockholder_equity": 62146000000,
        },
        "cash_flow": {
            "operating_cash_flow": 110543000000,
            "capital_expenditures": -10959000000,
            "free_cash_flow": 99584000000,
        },
    }
