import pytest
from app.schemas.ai import ResearchSessionContext
from app.services.rag.query_parser import ResearchQueryParser


def test_research_query_parser() -> None:
    parsed1 = ResearchQueryParser.parse_query("What are the latest events for RELIANCE?")
    assert parsed1.symbol == "RELIANCE"
    assert parsed1.intent == "COMPANY_RESEARCH"

    parsed2 = ResearchQueryParser.parse_query("Show recent acquisitions in the last 7 days.")
    assert parsed2.event_type == "ACQUISITION"
    assert parsed2.date_range_days == 7
    assert parsed2.intent == "EVENT_SEARCH"

    # Conversational Follow-Up test
    context = ResearchSessionContext(symbol="RELIANCE", company="Reliance Industries Ltd")
    parsed3 = ResearchQueryParser.parse_query("Show only acquisitions", previous_context=context)
    assert parsed3.symbol == "RELIANCE"
    assert parsed3.event_type == "ACQUISITION"


@pytest.mark.asyncio
async def test_ai_research_assistant_flow() -> None:
    from app.services.ai.mock import MockAIProvider
    from app.services.rag.retrieval_engine import RAGRetrievalEngine

    # Dummy Session test
    class DummySession:
        async def execute(self, stmt):
            class DummyResult:
                def scalar_one_or_none(self):
                    return None

                def scalars(self):
                    class ScalarList:
                        def all(self):
                            return []

                    return ScalarList()

                def all(self):
                    return []

            return DummyResult()

    parsed = ResearchQueryParser.parse_query("What happened to RELIANCE?")
    evidence = await RAGRetrievalEngine.retrieve_evidence(parsed, DummySession())  # type: ignore[arg-type]

    provider = MockAIProvider()
    res = await provider.generate_source_grounded_research("What happened to RELIANCE?", evidence)

    assert res.answer_summary is not None
    assert "RELIANCE" in res.context_used.symbol or "RELIANCE" in res.answer_summary
    assert res.potential_impact in ["POSITIVE", "NEGATIVE", "MIXED", "NEUTRAL", "UNCLEAR"]
