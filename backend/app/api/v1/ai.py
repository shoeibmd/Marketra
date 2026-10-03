import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.auth_service import get_current_user
from app.db.session import get_db, get_postgres_db
from app.models.domain import AIDocument, AIDocumentChunk, User
from app.schemas.ai import (
    AIDocumentUploadRequest,
    AIResponse,
    RAGQueryRequest,
    ResearchRequest,
    SourceGroundedAnswer,
)
from app.services.ai.mock import MockAIProvider
from app.services.rag.pipeline import rag_pipeline
from app.services.rag.query_parser import ResearchQueryParser
from app.services.rag.retrieval_engine import RAGRetrievalEngine

router = APIRouter(prefix="/ai", tags=["AI & RAG"])
mock_ai = MockAIProvider()

_MOCK_QUERY_HISTORY: list[dict[str, Any]] = []


@router.post("/research", response_model=SourceGroundedAnswer)
async def execute_source_grounded_research(
    req: ResearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SourceGroundedAnswer:
    """Phase 11: Execute source-grounded AI financial research query with conversational follow-up context."""
    # 1. Parse natural language query
    parsed = ResearchQueryParser.parse_query(req.query, req.context)

    # 2. Retrieve multi-source evidence
    try:
        evidence = await RAGRetrievalEngine.retrieve_evidence(parsed, db, user_id=current_user.id)
    except Exception:
        evidence = {
            "parsed_query": parsed.model_dump(),
            "symbol": parsed.symbol,
            "company_name": None,
            "financial_events": [],
            "news_articles": [],
            "relationships": [],
            "market_data": None,
            "evidence_confidence": "LOW",
        }

    # 3. Generate source-grounded answer
    try:
        res = await mock_ai.generate_source_grounded_research(req.query, evidence)
    except Exception:
        res = SourceGroundedAnswer(
            answer_summary="AI analysis is temporarily unavailable. The following verified platform data is available.",
            key_facts=[f"Query: '{req.query}'"],
            recent_events=evidence.get("financial_events", []),
            ai_analysis="AI service unreachable.",
            potential_impact="UNCLEAR",
            uncertainties=["AI Provider Timeout"],
            sources=[],
            related_companies=[],
            market_context=evidence.get("market_data"),
            evidence_confidence="LOW",
        )

    _MOCK_QUERY_HISTORY.append(
        {
            "id": str(uuid.uuid4()),
            "query": req.query,
            "answer": res.answer_summary,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    )
    return res


@router.post("/query", response_model=AIResponse)
async def execute_rag_query(
    req: RAGQueryRequest,
    current_user: User = Depends(get_current_user),
) -> AIResponse:
    """Execute RAG query against indexed documents and return structured response with citations."""
    res = await rag_pipeline.run_query(req.query, req.instrument_id)
    _MOCK_QUERY_HISTORY.append(
        {
            "id": str(uuid.uuid4()),
            "query": req.query,
            "answer": res.answer,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    )
    return res


@router.post("/summarize/company/{symbol}", response_model=AIResponse)
async def summarize_company(
    symbol: str,
    current_user: User = Depends(get_current_user),
) -> AIResponse:
    """Generate AI company summary for an instrument."""
    return await rag_pipeline.run_query(f"Summarize financial performance and business model of {symbol}", symbol)


@router.post("/summarize/news", response_model=AIResponse)
async def summarize_news(
    symbol: str = "RELIANCE",
    current_user: User = Depends(get_current_user),
) -> AIResponse:
    """Generate AI news summary for an instrument."""
    return await rag_pipeline.run_query(f"Summarize recent news coverage and market sentiment for {symbol}", symbol)


@router.get("/queries", response_model=list[dict[str, Any]])
async def get_query_history(
    current_user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """Fetch user's AI query history."""
    return _MOCK_QUERY_HISTORY


@router.post("/documents", response_model=dict[str, Any])
async def upload_rag_document(
    req: AIDocumentUploadRequest,
    db: AsyncSession = Depends(get_postgres_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Upload and chunk document for RAG indexing."""
    inst_uuid = uuid.UUID(req.instrument_id) if req.instrument_id else None
    doc = AIDocument(
        id=uuid.uuid4(),
        title=req.title,
        document_type=req.document_type,
        instrument_id=inst_uuid,
        content=req.content,
        metadata_json={},
        created_at=datetime.now(UTC),
    )
    db.add(doc)

    chunks = rag_pipeline.chunk_document(req.content)
    for idx, text in enumerate(chunks):
        chunk_obj = AIDocumentChunk(
            id=uuid.uuid4(),
            document_id=doc.id,
            chunk_index=idx,
            chunk_text=text,
        )
        db.add(chunk_obj)

    await db.commit()
    return {"status": "indexed", "document_id": str(doc.id), "chunks_created": len(chunks)}
