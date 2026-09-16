import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_postgres_db
from app.models.domain import AIDocument, AIDocumentChunk
from app.schemas.ai import (
    AIDocumentUploadRequest,
    AIResponse,
    RAGQueryRequest,
)
from app.services.rag.pipeline import rag_pipeline

router = APIRouter(prefix="/ai", tags=["AI & RAG"])

_MOCK_QUERY_HISTORY: list[dict[str, Any]] = []


@router.post("/query", response_model=AIResponse)
async def execute_rag_query(req: RAGQueryRequest) -> AIResponse:
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
async def summarize_company(symbol: str) -> AIResponse:
    """Generate AI company summary for an instrument."""
    return await rag_pipeline.run_query(f"Summarize financial performance and business model of {symbol}", symbol)


@router.post("/summarize/news", response_model=AIResponse)
async def summarize_news(symbol: str = "AAPL") -> AIResponse:
    """Generate AI news summary for an instrument."""
    return await rag_pipeline.run_query(f"Summarize recent news coverage and market sentiment for {symbol}", symbol)


@router.get("/queries", response_model=list[dict[str, Any]])
async def get_query_history() -> list[dict[str, Any]]:
    """Fetch user's AI query history."""
    return _MOCK_QUERY_HISTORY


@router.post("/documents", response_model=dict[str, Any])
async def upload_rag_document(
    req: AIDocumentUploadRequest,
    db: AsyncSession = Depends(get_postgres_db),
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
