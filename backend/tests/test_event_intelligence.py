import pytest
from app.schemas.ai import StructuredFinancialEvent
from app.services.ai.mock import MockAIProvider


@pytest.mark.asyncio
async def test_financial_event_extraction_structure() -> None:
    provider = MockAIProvider()
    event: StructuredFinancialEvent = await provider.extract_financial_event(
        title="Reliance Industries announces Q3 FY25 Results and Board Approval",
        content="Revenue grew strongly with operating profit expansion.",
        company="Reliance Industries Ltd",
        symbol="RELIANCE",
    )

    assert event.event_type in ["RESULTS", "ACQUISITION", "DIVIDEND", "PARTNERSHIP", "REGULATORY_ACTION", "OTHER"]
    assert event.primary_company == "Reliance Industries Ltd"
    assert len(event.company_roles) > 0
    assert event.company_roles[0].role == "PRIMARY_SUBJECT"
    assert event.confidence >= 0.0 and event.confidence <= 1.0
    assert event.cluster_id is not None


def test_event_role_validation() -> None:
    event = StructuredFinancialEvent(
        event_type="ACQUISITION",
        event_title="Company A acquires Company B",
        event_summary="Acquisition deal signed.",
        primary_company="Company A",
        primary_symbol="COMPA",
        company_roles=[
            {"company_name": "Company A", "symbol": "COMPA", "role": "ACQUIRER"},
            {"company_name": "Company B", "symbol": "COMPB", "role": "TARGET"},
        ],  # type: ignore[arg-type]
    )

    assert len(event.company_roles) == 2
    assert event.company_roles[0].role == "ACQUIRER"
    assert event.company_roles[1].role == "TARGET"
