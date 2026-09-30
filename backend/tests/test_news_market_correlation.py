import pytest
from app.api.v1.news import _get_market_context_for_symbol


@pytest.mark.asyncio
async def test_market_context_correlation() -> None:
    context = await _get_market_context_for_symbol("RELIANCE")

    assert context is not None
    assert context["symbol"] == "RELIANCE"
    assert context["current_price"] > 0
    assert context["previous_close"] > 0
    assert "change_percent" in context
    assert "volume" in context
    assert context["sector"] is not None
    assert "Price movement occurred around the same period" in context["market_relevance_note"]
    assert "does not imply direct causation" in context["market_relevance_note"]


@pytest.mark.asyncio
async def test_non_existent_symbol_correlation() -> None:
    context = await _get_market_context_for_symbol("NON_EXISTENT_XYZ")
    assert context is None
